"""ADFS OAuth2 登录：sts.cuhk.edu.cn 授权码换 bb.cuhk.edu.cn 会话 cookie。

流程（2026-09-29 实测，学校定制分页式 ADFS）：
GET authorize → 解析 loginForm（hidden holders + 密码框）→ 用户名按页面
定制 JS 规则补 `cuhksz\\` 域前缀（已含 @ 或 \\ 则不改写）→ 单次 POST
→ 重定向链落回 bb.cuhk.edu.cn 即持会话。成功判定用正向检查
（/users/me 200）；失败页的错误文案常驻 HTML 模板，不能作判据。
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

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


def _parse_forms(html: str, base_url: str):
    """返回 [(action, hidden_fields, has_password, has_user_text)]，按文档序。

    页面输入框标签常跨行书写，grep 不可见，必须用 HTML 解析器。
    """
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for form in soup.find_all("form"):
        action = form.get("action") or ""
        hidden = {
            i.get("name"): i.get("value", "")
            for i in form.find_all("input", {"type": "hidden"})
            if i.get("name")
        }
        has_password = bool(form.find("input", {"type": "password"}))
        has_user = any(
            (i.get("type") in (None, "text", "email")) and i.get("name")
            for i in form.find_all("input")
        )
        out.append((urljoin(base_url, action), hidden, has_password, has_user))
    return out


def login(transport: Transport, username: str, password: str) -> dict:
    """单步密码提交（分页翻页是客户端行为，账号步不发请求）。

    - 定制 JS 把不含 @ 或 \\ 的用户名改写为 `cuhksz\\<输入>` 再提交
      （页面常量 contosoDomain = "cuhksz"，此处按同规则补前缀）；
    - 提交字段 = hidden holders（UserName/Kmsi/AuthMethod）+ 覆写 UserName/Password；
    - 到达 bb.cuhk.edu.cn 即成功，再正向验证 /users/me；
    - 仍回登录页 = 凭据被拒。
    """

    def host_of(u: str) -> str:
        return urlparse(u).hostname or ""

    def verify_and_return() -> dict:
        me = transport.request("GET", "/learn/api/public/v1/users/me")
        if me.status_code == 200:
            return me.json()
        raise AuthError("已落 BB 但 REST 401（会话未建立）")

    transport.clear_cookies()
    r = transport.request("GET", config.ADFS_AUTHORIZE_URL, absolute=True)
    if r.status_code != 200:
        raise TransportError(f"ADFS 授权页 HTTP {r.status_code}")
    _dump("01-authorize", r.text)
    if host_of(str(r.url)) == "bb.cuhk.edu.cn":  # 既有会话直接放行
        return verify_and_return()

    # 域前缀改写（对齐页面定制 JS；已带 @ 或 \ 的输入不处理）
    domain = "cuhksz"
    m = re.search(r'contosoDomain\s*=\s*"([^"]+)"', r.text)
    if m:
        domain = m.group(1)
    if not re.search(r"[@\\]", username):
        username = f"{domain}\\{username}"

    forms = _parse_forms(r.text, str(r.url))
    pw_form = next((f for f in forms if f[2]), None)
    if not pw_form:
        raise AuthError("未找到密码表单（登录页结构变化）")
    action, hidden, _, _ = pw_form
    data = dict(hidden)
    data["UserName"] = username
    data["Password"] = password
    resp = transport._sess.post(action, data=data, allow_redirects=True,
                                timeout=config.REQUEST_TIMEOUT,
                                proxy=config.proxy() or None)
    _dump("02-password-post", resp.text)
    if host_of(str(resp.url)) == "bb.cuhk.edu.cn":
        return verify_and_return()
    raise CredentialError("账号或密码被拒（提交后仍停留 ADFS）")


def logout(transport: Transport) -> None:
    try:
        transport.request("GET", "/webapps/login/?action=logout")
    except TransportError:
        pass  # 尽力而为：本地会话必清
    transport.clear_cookies()
    p = config.session_path()
    if p.exists():
        p.unlink()
