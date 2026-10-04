"""传输层：curl_cffi 会话 + PS_DEVICEFEATURES + 壳页 JS 跳转跟随 + cookie 写穿。

SIS/PeopleSoft 三个实证要点（2026-10-05）：
- psc 直击组件时服务端先回 bootstrap 壳（self.location 指向 psp 版 URL），
  跟随后可达真身或门户框架页（TargetContent iframe）；
- PORTAL-PSJSESSIONID 随响应滚动换发，跨进程旧 jar 会撞回登录壳——
  故每次请求后立即写穿 session.json；
- 会话仅分钟级，调用方须备好重登回调。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from curl_cffi import requests as creq

from . import config


class TransportError(Exception):
    pass


class DeadSession(TransportError):
    """响应是 PeopleSoft 登录壳（会话过期/未建立）。"""


class Transport:
    def __init__(self, relogin=None):
        self._sess = creq.Session(impersonate=config.IMPERSONATE)
        self._sess.cookies.set("PS_DEVICEFEATURES", config.PS_DEVICEFEATURES,
                               domain="sis.cuhk.edu.cn", path="/")
        self._relogin = relogin
        self._in_relogin = False

    # ---- 会话持久化（写穿） ----
    def export_cookies(self) -> list[dict]:
        return [
            {"name": c.name, "value": c.value, "domain": c.domain, "path": c.path}
            for c in self._sess.cookies.jar
        ]

    def save_session(self) -> None:
        p = config.session_path()
        p.write_text(json.dumps(self.export_cookies(), ensure_ascii=False, indent=1),
                     encoding="utf-8")

    def load_session(self) -> bool:
        p = config.session_path()
        if not p.exists():
            return False
        try:
            jar = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        if not isinstance(jar, list) or not jar:
            return False
        for c in jar:
            self._sess.cookies.set(c["name"], c["value"],
                                   domain=c.get("domain", ""), path=c.get("path", "/"))
        # 设备特征 cookie 不随 jar 走，恒重种
        self._sess.cookies.set("PS_DEVICEFEATURES", config.PS_DEVICEFEATURES,
                               domain="sis.cuhk.edu.cn", path="/")
        return any(c["name"] == "PS_TOKEN" and c["value"] for c in jar)

    def clear_cookies(self) -> None:
        self._sess.cookies.jar.clear()
        self._sess.cookies.set("PS_DEVICEFEATURES", config.PS_DEVICEFEATURES,
                               domain="sis.cuhk.edu.cn", path="/")

    # ---- 请求 ----
    def request(self, method: str, url: str, *, absolute: bool = False, **kw):
        if not absolute:
            url = urljoin(config.SIS_HOST + "/", url.lstrip("/"))
        kw.setdefault("timeout", config.REQUEST_TIMEOUT)
        if config.proxy():
            kw["proxy"] = config.proxy()
        kw.setdefault("allow_redirects", True)
        r = self._sess.request(method, url, **kw)
        self.save_session()  # PSJSESSIONID 滚动换发，写穿
        return r

    def follow_shell(self, r, max_hops: int = 4):
        """跟随 PeopleSoft 壳页的 self.location JS 跳转（bootstrap/登录壳）。"""
        for _ in range(max_hops):
            m = re.search(r"self\.location='([^']+)'", r.text)
            if not m:
                break
            target = m.group(1)
            if not target.startswith("http"):
                target = urljoin(config.SIS_HOST, target)
            r = self.request("GET", target, absolute=True)
        return r

    # ---- 页面判定 ----
    @staticmethod
    def page_title(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.title.get_text() if soup.title else ""

    @staticmethod
    def is_signon_shell(html: str) -> bool:
        """登录壳特征：Oracle PeopleSoft 登录/Sign-in 标题的瘦页面。"""
        if len(html) > 6000:
            return False
        t = Transport.page_title(html)
        return "登录" in t or "Sign-in" in t

    # ---- 组件取件 ----
    def get_content(self, comp: str, nav: str) -> str:
        """psc+PTCNAV 直击组件，跟壳、下钻 TargetContent，返回内容真身 HTML。

        会话死亡抛 DeadSession；已设 relogin 回调时自动重登一次并重放。
        """
        for attempt in (1, 2):
            url = f"{config.SIS_HOST}/psc/csprd/EMPLOYEE/HRMS/c/{comp}?PORTALPARAM_PTCNAV={nav}"
            r = self.follow_shell(self.request("GET", url))
            html = r.text
            if self.is_signon_shell(html):
                if self._relogin and not self._in_relogin and attempt == 1:
                    self._in_relogin = True
                    try:
                        self.clear_cookies()
                        self._relogin()
                    finally:
                        self._in_relogin = False
                    continue
                raise DeadSession("会话过期且重登无效（登录页结构可能已变化）")
            soup = BeautifulSoup(html, "html.parser")
            frame = soup.find("iframe", id="ptifrmtgtframe")
            if frame and self.page_title(html) == "Employee-facing registry content":
                html = self.request("GET", frame["src"]).text  # 门户框架页 → 内容真身
            d = config.debug_dir()
            if d:
                (Path(d) / f"content-{comp.split('.')[-2] if '.' in comp else comp}.html") \
                    .write_text(html, encoding="utf-8", errors="replace")
            return html
        raise DeadSession("unreachable")

    def download(self, url: str, dest: Path) -> int:
        raise NotImplementedError("v0.1 未含下载；报表导出走 raw 手工验证后再封")
