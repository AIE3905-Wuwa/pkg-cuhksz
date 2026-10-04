"""内容页解析：周课表全解析，其余组件 v0.1 提供通用文本化。

解析锚点均来自 2026-10-05 实测页面结构（PeopleSoft CS 经典 PIA）。
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

_COURSE_CODE = re.compile(r"^[A-Z]{2,4}\s\d{3,4}\s-\s[A-Z]\d{2}")


def parse_weekly(html: str) -> dict:
    """周课表：本周事件清单 + 学期课程总表 + 周范围。

    事件块 = span.SSSTEXTWEEKLY 的父容器四行（编号/类型/时段/教室）；
    DOM 有重复渲染，按四元组去重。星期网格归属 v0.2（DOM 嵌套无列锚点）。
    """
    soup = BeautifulSoup(html, "html.parser")
    week = ""
    m = re.search(r"Week of \d{1,2}/\d{1,2}/\d{4} - \d{1,2}/\d{1,2}/\d{4}", html)
    if m:
        week = m.group(0)

    events, seen = [], set()
    for span in soup.find_all("span", class_="SSSTEXTWEEKLY"):
        if not _COURSE_CODE.match(span.get_text(" ", strip=True)):
            continue
        lines = [l.strip() for l in span.parent.get_text("\n", strip=True).split("\n")
                 if l.strip()][:4]
        if len(lines) < 4 or not _COURSE_CODE.match(lines[0]):
            continue
        key = tuple(lines[:4])
        if key in seen:
            continue
        seen.add(key)
        events.append({"class": lines[0], "type": lines[1],
                       "time": lines[2], "location": lines[3]})

    courses = []
    for tb in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in tb.find_all("th")]
        if "Course Title" not in headers:
            continue
        for row in tb.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
            if len(cells) >= 5 and _COURSE_CODE.match(cells[0].split(" (")[0]):
                courses.append({"class": cells[0], "title": cells[1],
                                "instructor": cells[2], "start": cells[3], "end": cells[4]})
    return {"week": week, "events": events, "courses": courses}


def textify(html: str, limit: int = 4000) -> str:
    """通用文本化兜底：逐行剔除门户菜单/导航短语，留近似正文（v0.1）。"""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "head"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    drop = {
        "English", "Simplified Chinese", "Traditional Chinese", "go to ...",
        "My Academics", "Personal Data Summary", "Student Center", "搜索:",
        "Menu", "主菜单", "My Favorites", "我的收藏夹", "t", "Help", "test",
        "Add to Favorites", "Sign out", "登出", "Data Language:",
        "Class Search / Browse Catalog", "Academic Planning", "Enrollment",
        "Academics Records", "My Application", "Campus Personal Information",
        "Academic Records", "Degree Progress/Graduation", "Faculty Center",
        "Personal Center", "Records and Enrollment", "Curriculum Management",
        "Worklist", "Reporting Tools", "PeopleTools", "New Window", "Close",
        "Default Local Node:", "DbName:", "Portal:", "Node:", "WorkCenter Id:",
        "Url:", "Related Content", "主页", "添加到收藏夹",
    }
    lines = []
    for l in text.split("\n"):
        s = l.strip()
        if s and s not in drop:
            lines.append(s)
        if sum(len(x) + 1 for x in lines) > limit:
            break
    return "\n".join(lines)
