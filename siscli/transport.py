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
        """登录壳特征：Oracle PeopleSoft 登录/Sign-in/Sign In 标题的瘦页面。

        两种形态都要抓：bootstrap 壳（title 'Oracle PeopleSoft 登录'）与
        语言选择登录页（title 'Sign In'，正文'学生信息系统'）。
        """
        if len(html) > 6000:
            return False
        t = Transport.page_title(html)
        return "登录" in t or "Sign-in" in t or "Sign In" in t

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

    # ---- ICAction POST 导航（查询类动作原语） ----
    def submit_icaction(self, comp: str, nav: str, action: str,
                        extra: dict[str, str] | None = None) -> str:
        """GET 组件页 → 收集 win0 表单 → 设 ICAction（+可选字段覆盖）→ POST。

        PeopleSoft 的下拉跳转、View Report、term 展开皆经此原语（issue #6 ①）。
        只允许查询类动作；数据变更按钮由调用纪律约束（skill Prohibitions）。
        """
        html = self.get_content(comp, nav)
        soup = BeautifulSoup(html, "html.parser")
        form = soup.find("form", attrs={"name": "win0"})
        if form is None or not form.get("action"):
            raise TransportError("未找到 win0 表单（页面结构变化）")
        fields: dict[str, str] = {}
        for i in form.find_all("input"):
            n = i.get("name")
            if n and i.get("type") in (None, "hidden", "text"):
                fields[n] = i.get("value") or ""
        for sel in form.find_all("select"):
            if sel.get("name") and sel.find("option"):
                fields[sel.get("name")] = sel.find("option").get("value") or ""
        fields["ICAction"] = action
        if extra:
            fields.update(extra)
        r = self._sess.post(form["action"], data=fields, allow_redirects=True,
                            timeout=config.REQUEST_TIMEOUT)
        self.save_session()
        if self.is_signon_shell(r.text):
            raise DeadSession("ICAction 提交后会话死亡")
        return r.text

    # ---- term 搜索页提交（查询动作，等同网页上选学期点 Continue） ----
    def submit_search(self, search_html: str, radio_value: str,
                      action: str = "DERIVED_SSS_SCT_SSR_PB_GO") -> str:
        """从搜索页 HTML 收集 win0 表单，设学期 radio + ICAction 后 POST，返回结果页。

        只用于查询类按钮（Continue/Change Term）；任何数据变更按钮禁止传入。
        """
        soup = BeautifulSoup(search_html, "html.parser")
        form = soup.find("form", attrs={"name": "win0"})
        if form is None or not form.get("action"):
            raise TransportError("未找到 win0 表单（搜索页结构变化）")
        fields: dict[str, str] = {}
        for i in form.find_all("input"):
            n = i.get("name")
            if n and i.get("type") in (None, "hidden", "text"):
                fields[n] = i.get("value") or ""
        for sel in form.find_all("select"):
            if sel.get("name") and sel.find("option"):
                fields[sel.get("name")] = sel.find("option").get("value") or ""
        fields["SSR_DUMMY_RECV1$sels$0"] = str(radio_value)
        fields["ICAction"] = action
        r = self._sess.post(form["action"], data=fields, allow_redirects=True,
                            timeout=config.REQUEST_TIMEOUT)
        self.save_session()
        if self.is_signon_shell(r.text):
            raise DeadSession("term 提交后会话死亡")
        return r.text

    def download(self, url: str, dest: Path) -> int:
        raise NotImplementedError("v0.1 未含下载；报表导出走 raw 手工验证后再封")
