"""ADFS OAuth2 登录：sts.cuhk.edu.cn 授权码换 PeopleSoft 会话（2026-10-05 实测）。

流程与 bb-cli 同源（同一 ADFS、同一 cuhksz\\ 域前缀规则），差别在 code 消费端：
SIS 的 dologin.html 是静态页，由其 JS 构造表单 POST 到 /psp/csprd/?cmd=login
（固定服务账号 CUSZ_SSO_LOGIN + 随机密码，PeopleSoft 后端拿 code 换会话）——
CLI 照抄该表单即可。POST 前须先 GET cmd=login 预热 PSJSESSIONID。
成功判定：PS_TOKEN 落地。
"""

from __future__ import annotations

import random
import re
import string
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup

from . import config
from .transport import Transport, TransportError


class AuthError(Exception):
    pass


class CredentialError(AuthError):
    pass


def _dump(tag: str, html: str) -> None:
    d = config.debug_dir()
    if d:
        (d / f"{tag}.html").write_text(html, encoding="utf-8", errors="replace")


def _host(u: str) -> str:
    return urlparse(str(u)).hostname or ""


def login(transport: Transport, username: str, password: str) -> dict:
    """完整登录链，成功返回 cookie 状态摘要（无 REST 身份端点，以 PS_TOKEN 为准）。"""
    transport.clear_cookies()
    r = transport.request("GET", config.ADFS_AUTHORIZE_URL, absolute=True)
    if r.status_code != 200:
        raise TransportError(f"ADFS 授权页 HTTP {r.status_code}")
    _dump("01-adfs-authorize", r.text)

    # code：ADFS 已有会话则直接回发，否则表单登录
    if _host(str(r.url)) == "sts.cuhk.edu.cn":
        if not re.search(r"[@\\]", username):
            username = f"cuhksz\\{username}"  # 对齐登录页定制 JS 的域前缀规则
        soup = BeautifulSoup(r.text, "html.parser")
        pw_form = next((f for f in soup.find_all("form")
                        if f.find("input", {"type": "password"})), None)
        if pw_form is None:
            raise AuthError("未找到密码表单（登录页结构变化）")
        data = {i.get("name"): i.get("value", "")
                for i in pw_form.find_all("input", {"type": "hidden"}) if i.get("name")}
        data["UserName"] = username
        data["Password"] = password
        resp = transport._sess.post(urljoin(str(r.url), pw_form.get("action") or ""),
                                    data=data, allow_redirects=True,
                                    timeout=config.REQUEST_TIMEOUT,
                                    proxy=config.proxy() or None)
        _dump("02-adfs-post-final", resp.text)
        if _host(str(resp.url)) != "sis.cuhk.edu.cn":
            raise CredentialError("账号或密码被拒（提交后仍停留 ADFS）")
        code = parse_qs(urlparse(str(resp.url)).query).get("code", [None])[0]
    else:
        code = parse_qs(urlparse(str(r.url)).query).get("code", [None])[0]
    if not code:
        raise AuthError("OAuth 授权码缺失（SSO 链路变化）")

    # 消费 code：预热 PSJSESSIONID → POST 登录表单（照抄 dologin.html 的 JS）
    transport.request("GET", "/psp/csprd/?cmd=login")
    r3 = transport._sess.post(
        f"{config.SIS_HOST}/psp/csprd/?cmd=login&languageCd=ENG&code={code}",
        data={
            "timezoneOffset": "-480", "ptmode": "f", "ptlangcd": "ENG",
            "ptinstalledlang": "ENG,ZHT,ZHS", "userid": "CUSZ_SSO_LOGIN",
            "pwd": "".join(random.choices(string.ascii_uppercase, k=10)),
            "ptlangsel": "ENG",
        }, allow_redirects=True, timeout=config.REQUEST_TIMEOUT,
        proxy=config.proxy() or None)
    _dump("03-ps-login-final", r3.text)
    transport.follow_shell(r3, max_hops=2)  # 登录壳 → StartPage（portal tab 壳勿深跟，防循环）
    if not any(c.name == "PS_TOKEN" and c.value for c in transport._sess.cookies.jar):
        raise AuthError("登录链走完但 PS_TOKEN 未落地")
    transport.save_session()
    return {"authenticated": True, "host": "sis.cuhk.edu.cn"}


def logout(transport: Transport) -> None:
    try:
        transport.request("GET", "/psp/csprd/EMPLOYEE/HRMS/?cmd=logout")
    except TransportError:
        pass  # 尽力而为：本地会话必清
    transport.clear_cookies()
    p = config.session_path()
    if p.exists():
        p.unlink()
