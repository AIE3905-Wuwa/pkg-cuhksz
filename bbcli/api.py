"""Learn REST API 封装（/learn/api/public/v1，全部 GET，学生会话 cookie 鉴权）。

分页：跟随 paging.nextPage，防自指与失控（上限 10000 页）。
课程定位：resolve_course 接受课程 id（_18038_1）、课程代码或名称子串。
"""

from __future__ import annotations

from urllib.parse import urljoin

from . import config
from .transport import ApiError, Transport, TransportError

API = "/learn/api/public/v1"


class BBClient:
    def __init__(self, transport: Transport):
        self.t = transport
        self._me = None

    # ---- 基础 ----
    def get(self, path: str, params: dict | None = None) -> dict:
        return self.t.get_json(path, params=params)

    def _paginate(self, path: str, params: dict | None = None) -> list[dict]:
        params = dict(params or {})
        params.setdefault("limit", 100)
        results: list[dict] = []
        url = path
        seen: set[str] = set()
        for _ in range(10000):
            if url in seen:
                break
            seen.add(url)
            data = self.get(url, params=params if url == path else None)
            results.extend(data.get("results") or [])
            nxt = (data.get("paging") or {}).get("nextPage")
            if not nxt:
                break
            url = urljoin(config.BB_HOST + "/", nxt.lstrip("/"))
        return results

    # ---- 身份与课程 ----
    def me(self) -> dict:
        if self._me is None:
            self._me = self.get(f"{API}/users/me")
        return self._me

    def terms(self) -> list[dict]:
        return self._paginate(f"{API}/terms")

    def my_courses(self) -> list[dict]:
        uid = self.me()["id"]
        rows = self._paginate(f"{API}/users/{uid}/courses", {"expand": "course"})
        out = []
        for r in rows:
            c = r.get("course") or {}
            c["membershipId"] = r.get("id")
            c["courseRoleId"] = r.get("courseRoleId")
            out.append(c)
        return out

    def resolve_course(self, arg: str) -> dict:
        courses = self.my_courses()
        if arg.startswith("_"):
            for c in courses:
                if c.get("id") == arg:
                    return c
        low = arg.lower()
        hits = [
            c for c in courses
            if low in (c.get("name") or "").lower()
            or low in (c.get("courseId") or "").lower()
            or low in (c.get("externalId") or "").lower()
        ]
        if len(hits) == 1:
            return hits[0]
        if not hits:
            raise SystemExit(f"未匹配到课程：{arg}（先 `bb-cli courses` 查看清单）")
        raise SystemExit("课程匹配歧义，请用更长子串或课程 id：\n" + "\n".join(
            f"  {c['id']}  {c.get('name')}" for c in hits
        ))

    # ---- 内容树与附件 ----
    def contents(self, cid: str) -> list[dict]:
        return self._paginate(f"{API}/courses/{cid}/contents")

    def children(self, cid: str, content_id: str) -> list[dict]:
        return self._paginate(f"{API}/courses/{cid}/contents/{content_id}/children")

    def walk(self, cid: str, max_depth: int = 12):
        """生成 (路径段列表, 节点)；防环 + 深度限制。"""
        seen: set[str] = set()

        def rec(parent_ids: list[str], nodes: list[dict], depth: int):
            for n in sorted(nodes, key=lambda x: (x.get("position") or 0, x.get("title") or "")):
                nid = n.get("id") or ""
                if nid in seen:
                    continue
                seen.add(nid)
                path = parent_ids + [n.get("title") or nid]
                yield path, n
                if n.get("hasChildren") and depth < max_depth:
                    yield from rec(path, self.children(cid, nid), depth + 1)

        yield from rec([], self.contents(cid), 1)

    def attachments(self, cid: str, content_id: str) -> list[dict]:
        try:
            return self._paginate(f"{API}/courses/{cid}/contents/{content_id}/attachments")
        except Exception:
            return []  # 无附件资源节点返回 4xx，视为空

    @staticmethod
    def download_url(cid: str, content_id: str, attachment_id: str) -> str:
        return f"{API}/courses/{cid}/contents/{content_id}/attachments/{attachment_id}/download"

    # ---- 公告 ----
    def announcements(self, cid: str | None = None) -> list[dict]:
        if cid:
            return self._paginate(f"{API}/courses/{cid}/announcements")
        return self._paginate(f"{API}/announcements")  # 机构级

    def course_announcements_all(self) -> tuple[list[dict], list[dict]]:
        """逐课拉公告；单课失败（如公告工具关闭 400）跳过记入 skipped，不连坐整体。"""
        out, skipped = [], []
        for c in self.my_courses():
            try:
                rows = self._paginate(f"{API}/courses/{c['id']}/announcements")
            except (ApiError, TransportError) as e:
                skipped.append({"course": c.get("name"), "id": c.get("id"), "error": str(e)[:120]})
                continue
            for a in rows:
                a["courseName"] = c.get("name")
                out.append(a)
        return out, skipped

    # ---- 成绩册 ----
    def grade_columns(self, cid: str) -> list[dict]:
        return self._paginate(f"{API}/courses/{cid}/gradebook/columns")

    def column_status(self, cid: str, col_id: str) -> dict | None:
        uid = self.me()["id"]
        r = self.t.request("GET", f"{API}/courses/{cid}/gradebook/columns/{col_id}/users/{uid}")
        if r.status_code == 404:
            return {"status": "None", "score": None}  # 未提交（bbwatch 语义化）
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except ValueError:
            return None

    # ---- 日历 / 花名册 ----
    def calendar_items(self) -> list[dict]:
        return self._paginate(f"{API}/calendars/items")

    def roster(self, cid: str) -> list[dict]:
        return self._paginate(f"{API}/courses/{cid}/users")
