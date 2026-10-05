"""API 层：组件访问与解析编排。只读——本连接器不提供任何写操作。
"""

from __future__ import annotations

from . import config, parser
from .auth import login
from .transport import Transport


class Sis:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or config.load_config()
        self.transport = Transport(relogin=self._relogin)

    # ---- 会话 ----
    def _relogin(self) -> None:
        username, password = config.resolve_credentials(self.cfg, None, None)
        login(self.transport, username, password)

    def ensure_session(self) -> bool:
        if self.transport.load_session():
            return True
        self._relogin()
        return True

    def login(self, username: str, password: str, *, store: bool) -> dict:
        info = login(self.transport, username, password)
        if store:
            self.cfg.update({"username": username, "password": password})
            config.save_config(self.cfg)
        else:
            self.cfg.pop("password", None)
            if username:
                self.cfg["username"] = username
            config.save_config(self.cfg)
        return info

    def logout(self) -> None:
        from .auth import logout
        logout(self.transport)
        self.cfg.pop("password", None)
        config.save_config(self.cfg)

    # ---- 组件 ----
    def component_html(self, name: str) -> str:
        comp, nav = config.COMPONENTS[name]
        return self.transport.get_content(comp, nav)

    def term_query(self, name: str, term: str | None = None) -> dict:
        """term 交互组件：GET 搜索页 → 选学期 POST Continue → 返回 {terms, term, html}。

        term=None 取页面第一个（最新）；传子串（如 'Term 2'）模糊匹配学期名。
        """
        html = self.component_html(name)
        terms = parser.parse_terms(html)
        if not terms:
            return {"terms": [], "term": None, "html": html}  # 无 radio：页面即结果
        pick = terms[0]
        if term:
            for t in terms:
                if term.lower() in t["term"].lower():
                    pick = t
                    break
            else:
                raise SystemExit(f"学期不匹配：{term!r}；可用：{[t['term'] for t in terms]}")
        result = self.transport.submit_search(html, pick["idx"])
        return {"terms": terms, "term": pick["term"], "html": result}

    def schedule(self) -> dict:
        return parser.parse_weekly(self.component_html("schedule"))

    def schedule_with_days(self) -> dict:
        """周课表 + 学生中心页的星期归属（center 页为权威源）。"""
        data = self.schedule()
        data["timetable"] = parser.parse_center_schedule(self.component_html("center"))
        return data

    def grades(self, term: str | None = None) -> dict:
        q = self.term_query("grades", term)
        report = parser.parse_grade_report(q["html"])
        report["term"] = report["term"] or q["term"] or ""
        report["terms_available"] = [t["term"] for t in q["terms"]]
        return report

    def appt(self, term: str | None = None) -> dict:
        q = self.term_query("appt", term)
        data = parser.parse_appt(q["html"])
        data["terms_available"] = [t["term"] for t in q["terms"]]
        return data

    def exam(self, term: str | None = None) -> dict:
        q = self.term_query("exam", term)
        return {"term": q["term"], "rows": parser.parse_exam(q["html"]),
                "terms_available": [t["term"] for t in q["terms"]]}

    def history(self) -> list[dict]:
        return parser.parse_history(self.component_html("history"))

    def raw(self, url: str) -> str:
        return self.transport.follow_shell(self.transport.request("GET", url)).text
