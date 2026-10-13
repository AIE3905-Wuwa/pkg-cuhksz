import os
import re


def verify(ctx):
    issues = []
    idp = os.path.join(ctx.root, "wiki", "cuhksz", "identity.md")
    if not os.path.exists(idp):
        issues.append(("error", "wiki/cuhksz/identity.md missing — create it per the identity constitution (sis block from transcript)"))
    else:
        text = open(idp, encoding="utf-8").read()
        if not re.search(r"^type:\s*cuhksz\s*$", text, re.M):
            issues.append(("error", "identity.md missing `type: cuhksz`"))
        if "student_id" not in text:
            issues.append(("error", "identity.md missing the sis block mapping (student_id ...)"))
    for d, tool in (("~/.bb-cli", "bb-cli"), ("~/.sis-cli", "sis-cli")):
        if not os.path.isdir(os.path.expanduser(d)):
            issues.append(("warning", f"{tool} not logged in yet ({d} absent) — guide the user at first pull"))
    return issues
