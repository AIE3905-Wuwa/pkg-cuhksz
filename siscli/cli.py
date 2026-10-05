"""sis-cli 命令面：全只读。写操作（选课/退课/提交类）刻意不提供。
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys

from . import config, parser
from .api import Sis


def _fmt(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def cmd_status(sis: Sis, args) -> int:
    alive = sis.transport.load_session()
    print(_fmt({"authenticated": alive or _try_silent_login(sis),
                "host": "sis.cuhk.edu.cn",
                "components": sorted(config.COMPONENTS)}))
    return 0


def _try_silent_login(sis: Sis) -> bool:
    try:
        sis.ensure_session()
        return True
    except Exception:
        return False


def cmd_login(sis: Sis, args) -> int:
    username = args.username or input("学号: ").strip()
    password = os.environ.get(args.password_env) if args.password_env else None
    if not password:
        password = getpass.getpass("密码: ")
    info = sis.login(username, password, store=not args.no_store)
    print(_fmt(info))
    return 0


def cmd_logout(sis: Sis, args) -> int:
    sis.logout()
    print("logged out (本地会话与凭据已清)")
    return 0


def cmd_schedule(sis: Sis, args) -> int:
    data = sis.schedule_with_days() if args.days else sis.schedule()
    if args.format == "json":
        print(_fmt(data))
        return 0
    print(f"[{data['week'] or '当前周'}] 事件 {len(data['events'])} 条 / 课程 {len(data['courses'])} 门")
    for e in data["events"]:
        print(f"  {e['class']:<18} {e['type']:<12} {e['time']:<20} {e['location']}")
    if data.get("timetable"):
        print("课表（含星期，学生中心页）:")
        for t in data["timetable"]:
            print(f"  {t['class']:<16} {t['type']:<5} {t['days']:<6} {t['time']:<22} {t['location']}")
    if data["courses"]:
        print("学期课程:")
        for c in data["courses"]:
            print(f"  {c['class']:<28} {c['title'][:36]:<38} {c['start']}~{c['end']}")
    return 0


def cmd_grades(sis: Sis, args) -> int:
    data = sis.grades(args.term)
    if args.format == "json":
        print(_fmt(data))
        return 0
    print(f"[{data['term']}] 成绩行 {len(data['rows'])} 条")
    for r in data["rows"]:
        print(f"  {r['course']:<10} {r['description'][:34]:<36} {r['units']:>5} {r['grading'][:22]:<24} {r['grade']:>4} {r['points']:>7}")
    if data["gpa"]:
        print("GPA:", "  ".join(f"{k}={v}" for k, v in data["gpa"].items()))
    if not data["rows"]:
        print(f"(本学期暂无成绩；可选学期: {', '.join(data['terms_available'])})")
    return 0


def cmd_history(sis: Sis, args) -> int:
    rows = sis.history()
    if args.format == "json":
        print(_fmt(rows))
        return 0
    print(f"课程历史 {len(rows)} 门")
    for r in rows:
        print(f"  {r['course']:<10} {r['description'][:34]:<36} {r['term']:<18} {r['grade'] or '-':>4} {r['units']:>5}")
    return 0


def cmd_appt(sis: Sis, args) -> int:
    data = sis.appt(args.term)
    if args.format == "json":
        print(_fmt(data))
        return 0
    print(f"[{data['term']}] 注册窗口")
    for a in data["appointments"]:
        print(f"  {a['session']}: {a['begins']} {a['begin_time']} ~ {a['ends']} {a['end_time']}")
    for k, v in data["limits"].items():
        print(f"  {k}: {v}")
    if not data["appointments"]:
        print(f"(该学期无注册窗口信息；可选学期: {', '.join(data['terms_available'])})")
    return 0


def cmd_exam(sis: Sis, args) -> int:
    data = sis.exam(args.term)
    if args.format == "json":
        print(_fmt(data))
        return 0
    print(f"[{data['term']}] 考试安排 {len(data['rows'])} 条")
    for r in data["rows"]:
        print("  " + "  ".join(f"{k}={v}" for k, v in r.items() if v))
    return 0


def cmd_text_component(sis: Sis, args) -> int:
    html = sis.component_html(args.cmd)
    if args.format == "json":
        print(_fmt({"component": args.cmd, "text": parser.textify(html)}))
    else:
        print(parser.textify(html))
    return 0


def cmd_raw(sis: Sis, args) -> int:
    print(sis.raw(args.url))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="sis-cli",
                                 description="sis.cuhk.edu.cn 只读 CLI 连接器（PeopleSoft CS）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="会话状态与可用组件")
    sub.add_parser("logout", help="登出并清本地凭据/会话")

    p = sub.add_parser("login", help="交互登录")
    p.add_argument("--username", "-u")
    p.add_argument("--no-store", action="store_true", help="凭据不落盘（默认存 ~/.sis-cli）")
    p.add_argument("--password-env")

    p = sub.add_parser("schedule", help="我的每周课程表（--days 附学生中心页的星期归属）")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--days", action="store_true", help="附带星期/节次的课表总表")

    for comp, label in [
            ("grades", "查看我的成绩（按学期，--term 子串可选）"),
            ("appt", "注册日期 Enrollment Dates（--term 子串可选）"),
            ("exam", "我的考试计划（--term 子串可选）"),
            ("history", "我的课程历史记录（全量直出）")]:
        p = sub.add_parser(comp, help=label)
        p.add_argument("--format", choices=["text", "json"], default="text")
        if comp != "history":
            p.add_argument("--term", help="学期子串（缺省取最新；如 'Term 2'）")

    p = sub.add_parser("center", help="学生中心页（文本摘要）")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p = sub.add_parser("assignments", help="按作业查成绩（常无数据，观察中）")
    p.add_argument("--format", choices=["text", "json"], default="text")

    p = sub.add_parser("raw", help="任意 GET 透传（新需求先走这里验证再封命令）")
    p.add_argument("url")
    p.add_argument("--file", help="落盘到指定文件而非打印")

    args = ap.parse_args(argv)
    sis = Sis()

    handlers = {"status": cmd_status, "login": cmd_login, "logout": cmd_logout,
                "schedule": cmd_schedule, "grades": cmd_grades, "history": cmd_history,
                "appt": cmd_appt, "exam": cmd_exam, "raw": cmd_raw,
                "center": cmd_text_component, "assignments": cmd_text_component}

    if args.cmd not in ("login", "logout", "status"):
        sis.ensure_session()
    if args.cmd == "raw" and args.file:
        import pathlib
        out = sis.raw(args.url)
        pathlib.Path(args.file).write_text(out, encoding="utf-8", errors="replace")
        print(f"saved {args.file} ({len(out)}B)")
        return 0
    return handlers[args.cmd](sis, args)


if __name__ == "__main__":
    sys.exit(main())
