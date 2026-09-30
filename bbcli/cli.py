"""命令面：全只读。JSON 默认输出；raw 仅允许 GET（写操作不入 v1）。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__, auth, config
from .api import BBClient
from .transport import ApiError, Transport, TransportError


# ---- 输出 ----
def emit(obj, fmt: str, text_fn=None):
    if fmt == "text" and text_fn:
        lines = list(text_fn(obj)) or ["（无结果）"]
        for line in lines:
            print(line)
    else:
        print(json.dumps(obj, ensure_ascii=False, indent=2))


def strip_html(html: str) -> str:
    from bs4 import BeautifulSoup
    return BeautifulSoup(html or "", "html.parser").get_text("\n", strip=True)


def _sanitize(name: str) -> str:
    s = re.sub(r'[\\/:*?"<>|\r\n\t]', "_", name).strip(" .")
    return s[:80] or "_"


def _local_dt(iso: str | None) -> datetime | None:
    """API 原值为 UTC ISO（…Z）；无时区标记亦按 UTC。解析失败返回 None。"""
    if not iso:
        return None
    s = iso.strip()
    if s.endswith(("Z", "z")):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone()  # 本机时区


def _date_part(iso: str | None) -> str:
    dt = _local_dt(iso)
    return dt.strftime("%Y-%m-%d") if dt else (iso or "")[:10]


def _dt_part(iso: str | None) -> str:
    dt = _local_dt(iso)
    return dt.strftime("%Y-%m-%dT%H:%M") if dt else (iso or "")[:16]


# ---- 会话装配 ----
def build_client() -> tuple[BBClient, Transport, dict]:
    cfg = config.load_config()
    t = Transport()
    t.load_session()

    def relogin():
        username, password = config.resolve_credentials(cfg, None, None)
        auth.login(t, username, password)
        t.save_session()

    t._relogin = relogin
    return BBClient(t), t, cfg


def need_auth(client: BBClient):
    try:
        client.me()
    except Exception:
        print("未登录或会话过期：先 `bb-cli login`", file=sys.stderr)
        sys.exit(2)


# ---- 命令实现 ----
def cmd_login(args):
    import getpass
    import os

    cfg = config.load_config()
    username = args.username or os.environ.get(config.ENV_USERNAME) or cfg.get("username")
    if not username:
        username = input("学号/邮箱前缀: ").strip()
    if args.password_env:
        password = os.environ.get(args.password_env)
        if not password:
            sys.exit(f"环境变量 {args.password_env} 未设置")
    elif os.environ.get(config.ENV_PASSWORD):
        password = os.environ[config.ENV_PASSWORD]
    else:
        password = getpass.getpass("密码: ")
    t = Transport()
    me = auth.login(t, username, password)
    t.save_session()
    cfg["username"] = username
    if not args.no_store:
        cfg["password"] = password
        print(f"凭据已存 {config.config_path()}（仅本机用户目录）", file=sys.stderr)
    config.save_config(cfg)
    emit({"login": "ok", "user": me.get("name"), "id": me.get("id")}, args.format)


def cmd_logout(args):
    t = Transport()
    t.load_session()
    auth.logout(t)
    print("已登出并清除本地会话")


def cmd_whoami(args):
    c, _, _ = build_client()
    need_auth(c)
    emit(c.me(), args.format)


def cmd_status(args):
    c, t, _ = build_client()
    t._relogin = None  # 状态探测不触发自动重登，未登录如实报告
    has_file = config.session_path().exists()
    try:
        me = c.me()
        ok = True
    except Exception:
        me, ok = None, False
    emit({"session_file": has_file, "authenticated": ok,
          "user": (me or {}).get("name")}, args.format,
         lambda o: [f"session_file={'yes' if o['session_file'] else 'no'}  "
                    f"authenticated={'yes' if o['authenticated'] else 'no'}  "
                    f"user={((o.get('user') or {}).get('given')) or '-'}"])


def cmd_terms(args):
    c, _, _ = build_client()
    need_auth(c)
    emit(c.terms(), args.format,
         lambda ts: [f"{t['id']}  {t['name']}  {_date_part((t.get('availability') or {}).get('duration', {}).get('start'))}" for t in ts])


def cmd_courses(args):
    c, _, _ = build_client()
    need_auth(c)
    courses = c.my_courses()
    if args.term:
        terms = {t["id"]: t.get("name") or "" for t in c.terms()}
        low = args.term.lower()
        courses = [x for x in courses if low in terms.get(x.get("termId"), "").lower()]
    emit(courses, args.format,
         lambda cs: [f"{x['id']}  [{(x.get('termId') or '')}]  {x.get('name')}" for x in cs])


def cmd_tree(args):
    c, _, _ = build_client()
    need_auth(c)
    course = c.resolve_course(args.course)

    def node(n, depth):
        d = {"title": n.get("title"), "id": n.get("id"),
             "handler": (n.get("contentHandler") or {}).get("id"),
             "created": n.get("created"), "modified": n.get("modified")}
        kids = []
        if n.get("hasChildren") and depth < args.depth:
            kids = [node(k, depth + 1) for k in c.children(course["id"], n["id"])]
        if not kids and not args.no_attachments:
            atts = c.attachments(course["id"], n["id"])
            if atts:
                d["attachments"] = [a.get("fileName") for a in atts]
        if kids:
            d["children"] = kids
        return d

    top = c.contents(course["id"])
    emit({"course": course.get("name"), "id": course["id"],
          "children": [node(n, 1) for n in top]}, args.format)


def _walk_files(c: BBClient, cid: str, depth: int):
    for path, n in c.walk(cid, max_depth=depth):
        if n.get("hasChildren"):
            continue
        handler = (n.get("contentHandler") or {}).get("id") or ""
        if handler in ("resource/x-bb-folder", "resource/x-bb-lesson"):
            continue
        atts = c.attachments(cid, n["id"])
        if atts:
            yield {"path": " / ".join(path), "content_id": n["id"],
                   "modified": n.get("modified"),
                   "attachments": [{"id": a["id"], "fileName": a.get("fileName"),
                                    "mime": a.get("mimeType")} for a in atts]}


def _match_rows(rows: list[dict], pattern: str) -> list[dict]:
    """--match 同时作用于内容路径与附件文件名（不区分大小写）。"""
    rx = re.compile(pattern, re.I)

    def hay(r: dict) -> str:
        return r["path"] + " " + " ".join(a.get("fileName") or "" for a in r["attachments"])

    return [r for r in rows if rx.search(hay(r))]


def cmd_files(args):
    c, _, _ = build_client()
    need_auth(c)
    course = c.resolve_course(args.course)
    rows = list(_walk_files(c, course["id"], args.depth))
    if args.match:
        rows = _match_rows(rows, args.match)
    emit({"course": course.get("name"), "count": len(rows), "files": rows}, args.format,
          lambda o: [f"{r['path']}  [{', '.join(a['fileName'] or '' for a in r['attachments'])}]" for r in o["files"]])


def cmd_fetch(args):
    c, _, _ = build_client()
    need_auth(c)
    course = c.resolve_course(args.course)
    rows = list(_walk_files(c, course["id"], 12))
    if args.match:
        rows = _match_rows(rows, args.match)
    if args.since:
        rows = [r for r in rows if _date_part(r.get("modified")) >= args.since]
    plan = []
    used: set[str] = set()
    for r in rows:
        for a in r["attachments"]:
            rel = "/".join([_sanitize(p) for p in r["path"].split(" / ")[:-1]]
                           + [_sanitize(a["fileName"] or a["id"])])
            if rel in used:  # 同目录同名附件：尾缀附件 id 防覆盖
                stem, _, ext = rel.rpartition(".")
                rel = f"{stem}_{a['id'][:8]}.{ext}" if stem else f"{rel}_{a['id'][:8]}"
            used.add(rel)
            plan.append({"rel": rel, "content_id": r["content_id"], "attachment": a})
    if args.dry_run:
        emit({"dry_run": True, "course": course.get("name"), "count": len(plan), "plan": plan}, args.format)
        return
    outdir = Path(args.out or ".").expanduser()
    root = outdir / _sanitize(course.get("name") or course["id"])
    done, errors = [], []
    for p in plan:
        dest = root / Path(*p["rel"].split("/"))
        if dest.exists():
            done.append({"path": str(dest.relative_to(outdir)), "bytes": "exists"})
            continue
        try:
            n = c.t.download(c.download_url(course["id"], p["content_id"], p["attachment"]["id"]), dest)
            done.append({"path": str(dest.relative_to(outdir)), "bytes": n})
        except (ApiError, TransportError) as e:
            errors.append({"rel": p["rel"], "error": str(e)[:200]})
    emit({"course": course.get("name"), "out": str(outdir),
          "downloaded": done, "errors": errors}, args.format)


def cmd_announcements(args):
    c, _, _ = build_client()
    need_auth(c)
    if args.course and args.course != "all":
        course = c.resolve_course(args.course)
        rows = c.announcements(course["id"])
        for r in rows:
            r["courseName"] = course.get("name")
        skipped = []
    else:
        rows, skipped = c.course_announcements_all()
    rows.sort(key=lambda r: r.get("created") or "", reverse=True)
    if args.limit:
        rows = rows[: args.limit]
    if not args.html:
        for r in rows:
            r["bodyText"] = strip_html(r.get("body") or "")

    def _lines(o):
        out = [f"{_date_part(r.get('created'))}  {r.get('courseName', '(机构)')}  {r.get('title')}" for r in o["announcements"]]
        if o.get("skipped"):
            names = "、".join(s.get("course") or s.get("id") or "?" for s in o["skipped"])
            out.append(f"!! 跳过 {len(o['skipped'])} 课（拉取失败）：{names}")
        return out

    emit({"count": len(rows), "announcements": rows, "skipped": skipped}, args.format, _lines)


def cmd_dues(args):
    c, _, _ = build_client()
    need_auth(c)
    # 双源合并：日历端点 + 每课成绩册列（日历会漏项，成绩册兜底；同课同题保留日历条目）
    items = [{"course": r.get("calendarName"), "title": r.get("title"), "source": "calendar",
              "due": r.get("start"), "end": r.get("end"), "type": r.get("type")}
             for r in c.calendar_items()]
    skipped = []
    if args.course:
        course = c.resolve_course(args.course)
        courses = [course]
        low = (course.get("name") or "").lower()
        items = [x for x in items if low in (x["course"] or "").lower()]
    else:
        courses = c.my_courses()
    for course in courses:
        try:
            cols = c.grade_columns(course["id"])
        except (TransportError, ApiError) as e:
            skipped.append({"course": course.get("name"), "id": course.get("id"), "error": str(e)[:120]})
            continue
        for col in cols:
            due = (col.get("grading") or {}).get("due")
            if due:
                items.append({"course": course.get("name"), "title": col.get("name"),
                              "source": "gradebook", "due": due, "end": None, "type": None})
    dedup, seen = [], set()
    for x in sorted(items, key=lambda i: i["source"] != "calendar"):  # 稳定排序：日历条目先入
        k = (" ".join((x["course"] or "").split()), " ".join((x["title"] or "").split()))
        if k in seen:
            continue
        seen.add(k)
        dedup.append(x)
    items = dedup
    if args.from_:
        items = [x for x in items if _date_part(x.get("due")) >= args.from_]
    if args.to:
        items = [x for x in items if _date_part(x.get("due")) <= args.to]
    items.sort(key=lambda x: x.get("due") or "")

    def _lines(o):
        out = [f"{_date_part(r['due'])}  {r['course']}  {r['title']}  [{r['source']}]" for r in o["dues"]]
        if o.get("skipped"):
            names = "、".join(s.get("course") or s.get("id") or "?" for s in o["skipped"])
            out.append(f"!! 跳过 {len(o['skipped'])} 课成绩册（拉取失败）：{names}")
        return out

    emit({"count": len(items), "dues": items, "skipped": skipped}, args.format, _lines)


def cmd_assignments(args):
    c, _, _ = build_client()
    need_auth(c)
    course = c.resolve_course(args.course)
    rows = []
    for col in c.grade_columns(course["id"]):
        grading = col.get("grading") or {}
        if not grading.get("due"):
            continue
        st = c.column_status(course["id"], col["id"]) or {}
        rows.append({"name": col.get("name"), "due": grading.get("due"),
                     "possible": (col.get("score") or {}).get("possible"),
                     "status": st.get("status"), "score": st.get("score"),
                     "column_id": col.get("id"), "content_id": col.get("contentId")})
    rows.sort(key=lambda r: r.get("due") or "")
    emit({"course": course.get("name"), "assignments": rows}, args.format,
         lambda o: [f"{_dt_part(r['due'])}  {r['name']}  [{r['status'] or '-'}]" for r in o["assignments"]])


def cmd_grades(args):
    c, _, _ = build_client()
    need_auth(c)
    courses = [c.resolve_course(args.course)] if args.course else c.my_courses()
    out = []
    for course in courses:
        rows = []
        for col in c.grade_columns(course["id"]):
            if args.due_only and not (col.get("grading") or {}).get("due"):
                continue
            st = c.column_status(course["id"], col["id"]) or {}
            rows.append({"name": col.get("name"),
                         "due": (col.get("grading") or {}).get("due"),
                         "possible": (col.get("score") or {}).get("possible"),
                         "status": st.get("status"), "score": st.get("score"),
                         "column_id": col.get("id")})
        out.append({"course": course.get("name"), "columns": rows})
    emit(out if len(out) != 1 else out[0], args.format)


def cmd_roster(args):
    c, _, _ = build_client()
    need_auth(c)
    course = c.resolve_course(args.course)
    rows = c.roster(course["id"])
    slim = [{"userId": r.get("userId"), "role": r.get("courseRoleId"),
             "lastAccessed": r.get("lastAccessed")} for r in rows]
    emit({"course": course.get("name"), "count": len(slim), "members": slim}, args.format)


def cmd_raw(args):
    if args.method.upper() != "GET":
        sys.exit("v1 只读：raw 仅接受 GET")
    c, _, _ = build_client()
    need_auth(c)
    params = {}
    for kv in args.q or []:
        k, _, v = kv.partition("=")
        params[k] = v
    emit(c.get(args.path, params or None), args.format)


# ---- 参数解析 ----
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bb-cli", description="CUHK-SZ Blackboard 只读 CLI 连接器")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--format", choices=["json", "text"], default="json")
    common = argparse.ArgumentParser(add_help=False)  # 让 --format 也接受子命令后置
    common.add_argument("--format", choices=["json", "text"], default=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="cmd", required=True)

    def cmd(name: str, help_: str):
        return sub.add_parser(name, help=help_, parents=[common])

    s = cmd("login", "登录并保存会话")
    s.add_argument("--username")
    s.add_argument("--password-env", help="从该环境变量读密码")
    s.add_argument("--no-store", action="store_true", help="不把密码写入本机配置")
    s.set_defaults(fn=cmd_login)

    cmd("logout", "登出并清本地会话").set_defaults(fn=cmd_logout)
    cmd("whoami", "当前用户").set_defaults(fn=cmd_whoami)
    cmd("status", "会话状态").set_defaults(fn=cmd_status)
    cmd("terms", "学期列表").set_defaults(fn=cmd_terms)

    s = cmd("courses", "我的课程")
    s.add_argument("--term", help="按学期名过滤（子串）")
    s.set_defaults(fn=cmd_courses)

    s = cmd("tree", "课程内容树")
    s.add_argument("course")
    s.add_argument("--depth", type=int, default=12)
    s.add_argument("--no-attachments", action="store_true")
    s.set_defaults(fn=cmd_tree)

    s = cmd("files", "课件文件清单")
    s.add_argument("course")
    s.add_argument("--match", help="路径正则过滤（不区分大小写）")
    s.add_argument("--depth", type=int, default=12)
    s.set_defaults(fn=cmd_files)

    s = cmd("fetch", "下载课件（保留目录结构）")
    s.add_argument("course")
    s.add_argument("--match")
    s.add_argument("--since", help="只取内容修改日 >= YYYY-MM-DD")
    s.add_argument("-o", "--out", default=".")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_fetch)

    s = cmd("announcements", "公告（默认全部课程）")
    s.add_argument("--course", help="课程子串/id，或 all")
    s.add_argument("--limit", type=int)
    s.add_argument("--html", action="store_true", help="保留原始 HTML 正文")
    s.set_defaults(fn=cmd_announcements)

    s = cmd("dues", "跨课程截止（日历端点）")
    s.add_argument("--course")
    s.add_argument("--from", dest="from_")
    s.add_argument("--to")
    s.set_defaults(fn=cmd_dues)

    s = cmd("assignments", "作业清单（列×我的状态）")
    s.add_argument("course")
    s.set_defaults(fn=cmd_assignments)

    s = cmd("grades", "成绩册（默认全部课程）")
    s.add_argument("course", nargs="?")
    s.add_argument("--due-only", action="store_true")
    s.set_defaults(fn=cmd_grades)

    s = cmd("roster", "课程成员列表")
    s.add_argument("course")
    s.set_defaults(fn=cmd_roster)

    s = cmd("raw", "任意 REST GET 透传（/learn/api/public/v1/...）")
    s.add_argument("method")
    s.add_argument("path")
    s.add_argument("--q", action="append", help="查询参数 k=v（可重复）")
    s.set_defaults(fn=cmd_raw)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.fn(args)
    except (auth.CredentialError,) as e:
        print(f"凭据错误：{e}", file=sys.stderr)
        sys.exit(2)
    except auth.AuthError as e:
        print(f"登录失败：{e}", file=sys.stderr)
        sys.exit(2)
    except (TransportError, ApiError) as e:
        print(f"请求失败：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
