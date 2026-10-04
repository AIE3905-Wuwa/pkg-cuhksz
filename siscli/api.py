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

    def schedule(self) -> dict:
        return parser.parse_weekly(self.component_html("schedule"))

    def grades_text(self) -> str:
        return parser.textify(self.component_html("grades"))

    def raw(self, url: str) -> str:
        return self.transport.follow_shell(self.transport.request("GET", url)).text
