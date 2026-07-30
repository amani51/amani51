#!/usr/bin/env python3
"""Generate every profile card, at desktop width and again at phone width.

    python3 scripts/build.py

Live contribution figures come from the GitHub GraphQL API and need a token
that can see private contributions (METRICS_TOKEN in CI, `gh auth token`
locally). Everything else comes from scripts/content.py.
"""

import base64
import datetime
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cardkit as k                                    # noqa: E402
import content as C                                    # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
ICONS = os.path.join(ASSETS, "icons")
USER = os.environ.get("PROFILE_USER", "amani51")
FIRST_YEAR = 2022


# ----------------------------------------------------------------- live data

def token():
    for var in ("METRICS_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception:
        sys.exit("No token. Set METRICS_TOKEN or run `gh auth login`.")


def graphql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "bearer " + token(),
                 "Content-Type": "application/json",
                 "User-Agent": "profile-card-builder"})
    with urllib.request.urlopen(req, timeout=45) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit("GraphQL error: %s" % body["errors"])
    return body["data"]


def calendar(frm, to):
    data = graphql("""
    { user(login:"%s") { contributionsCollection(from:"%sT00:00:00Z", to:"%sT23:59:59Z") {
        contributionCalendar { totalContributions
          weeks { contributionDays { date contributionCount } } } } } }
    """ % (USER, frm, to))
    return data["user"]["contributionsCollection"]["contributionCalendar"]


def fetch():
    today = datetime.date.today()
    days = {}
    for year in range(FIRST_YEAR, today.year + 1):
        end = today if year == today.year else datetime.date(year, 12, 31)
        cal = calendar("%d-01-01" % year, end.isoformat())
        for w in cal["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    recent = calendar((today - datetime.timedelta(days=364)).isoformat(), today.isoformat())
    longest = run = 0
    for key in sorted(days):
        run = run + 1 if days[key] > 0 else 0
        longest = max(longest, run)
    return {
        "days": days,
        "weeks": recent["weeks"],
        "last12": recent["totalContributions"],
        "total": sum(days.values()),
        "active": sum(1 for v in days.values() if v > 0),
        "longest": longest,
    }


# ------------------------------------------------------------------- helpers

def marked(value, arrow=k.GREEN, punct="#54708F"):
    """Turn 'A |·| B |>| C' into tspans, colouring the separators."""
    out, parts = [], value.split("|")
    for i, chunk in enumerate(parts):
        if i % 2:
            glyph = "&#8594;" if chunk == ">" else k.esc(chunk)
            out.append('<tspan fill="%s">%s</tspan>' % (arrow if chunk == ">" else punct, glyph))
        else:
            out.append(k.esc(chunk))
    return "".join(out)


def plain(value):
    return re.sub(r"\s+", " ", value.replace("|>|", "to").replace("|", "")).strip()


def anim(name, keyframes, selector, extra=""):
    return k.style_block(
        "%s{animation:%s %s}\n  @keyframes %s{%s}\n  %s"
        % (selector, name, extra, name, keyframes, k.REDUCED % selector))


# --------------------------------------------------------------------- cards

def build_tagline(lay):
    n = len(C.TAGLINES)
    hold, size = 3.6, (13 if lay.narrow else 19)
    total = hold * n
    height = 40 if lay.narrow else 56
    style = k.style_block(
        ".l{opacity:0;animation:cyc %ss ease-in-out infinite}\n"
        "  @keyframes cyc{0%%{opacity:0;transform:translateY(4px)}%.1f%%{opacity:1;transform:none}"
        "%.1f%%{opacity:1;transform:none}%.1f%%{opacity:0;transform:translateY(-4px)}100%%{opacity:0}}\n"
        "  @media (prefers-reduced-motion:reduce){.l{animation:none}.l:first-of-type{opacity:1}}"
        % (total, 2.0, 100.0 / n - 4.0, 100.0 / n))
    p = k.open_svg(lay, height, " / ".join(C.TAGLINES), "Tagline", style)
    for i, line in enumerate(C.TAGLINES):
        p.append(k.text(lay.w / 2, height / 2 + size * 0.35, k.esc(line), font=k.MONO,
                        size=size, fill=k.BLUE, weight="500", anchor="middle")
                 .replace("<text ", '<text class="l" style="animation-delay:%.2fs" ' % (i * hold)))
    p.append("</svg>")
    return "\n".join(p)


def build_calibration(lay, stats):
    strap = "%s CONTRIBUTIONS SINCE JUL %d" % (format(stats["total"], ","), FIRST_YEAR)
    y = k.head_bottom(lay, strap) + (16 if lay.narrow else 24)
    rows, avail = [], lay.right - lay.value_x
    for key, val in C.CALIBRATION:
        lines = k.wrap(plain(val), lay.value_size,
                       lay.w - 2 * lay.pad if lay.stacked else avail)
        rows.append((key, val, lines, y))
        y += (20 + len(lines) * 18 + 12) if lay.stacked else 38
    height = int(y + (12 if lay.narrow else 16))

    aria = "Calibration. " + "; ".join("%s, %s" % (a, plain(b)) for a, b in C.CALIBRATION)
    p = k.open_svg(lay, height, aria + ". " + strap, "Calibration")
    p += k.chrome(lay, height, "CALIBRATION", strap, uid="ca")
    for key, val, lines, yy in rows:
        if lay.stacked:
            p.append(k.text(lay.pad, yy, key, font=k.MONO, size=lay.label_size,
                            fill=k.LABEL, spacing=2.2))
            for i, ln in enumerate(lines):
                p.append(k.text(lay.pad, yy + 19 + i * 18,
                                marked(val) if len(lines) == 1 else k.esc(ln),
                                font=k.SANS, size=lay.value_size, fill=k.VALUE))
        else:
            p.append(k.text(lay.pad, yy, key, font=k.MONO, size=lay.label_size,
                            fill=k.LABEL, spacing=2.6))
            p.append(k.text(lay.value_x, yy, marked(val), font=k.SANS,
                            size=lay.value_size, fill=k.VALUE))
            if yy != rows[-1][3]:
                p.append(k.rule(lay, yy + 15))
    p.append("</svg>")
    return "\n".join(p)


def inline_icon(slug, index, x, y, size, name):
    with open(os.path.join(ICONS, slug + ".svg"), encoding="utf-8") as fh:
        inner = re.search(r"<svg[^>]*>(.*)</svg>", fh.read(), re.S).group(1)
    for ident in sorted(set(re.findall(r'id="([^"]+)"', inner)), key=len, reverse=True):
        new = "s%d_%s" % (index, ident)
        inner = (inner.replace('id="%s"' % ident, 'id="%s"' % new)
                      .replace("url(#%s)" % ident, "url(#%s)" % new)
                      .replace('href="#%s"' % ident, 'href="#%s"' % new))
    return ('<g class="in" style="animation-delay:%.2fs"><g class="fl" style="animation-delay:%.2fs">'
            "<title>%s</title>"
            '<svg x="%d" y="%d" width="%d" height="%d" viewBox="0 0 256 256">%s</svg>'
            "</g></g>" % (index * 0.05, -(index * 0.16), k.esc(name), x, y, size, size, inner))


NAMES = {"ts": "TypeScript", "js": "JavaScript", "react": "React", "nextjs": "Next.js",
         "tailwind": "Tailwind CSS", "threejs": "Three.js", "html": "HTML", "css": "CSS",
         "py": "Python", "django": "Django", "cs": "C#", "dotnet": ".NET",
         "nodejs": "Node.js", "express": "Express", "postgres": "PostgreSQL",
         "mongodb": "MongoDB", "docker": "Docker", "git": "Git", "github": "GitHub",
         "githubactions": "GitHub Actions", "postman": "Postman", "vercel": "Vercel"}


def build_stack(lay):
    strap = C.STRAPS["stack"]
    size = 42 if lay.narrow else 62
    gap = 6 if lay.narrow else 18
    x0 = lay.pad if lay.stacked else 212
    per_row = max(1, int((lay.right - x0 + gap) // (size + gap)))

    style = k.style_block(
        ".in{animation:enter .5s cubic-bezier(.2,.7,.3,1) both}\n"
        "  .fl{animation:flt 3.4s ease-in-out infinite}\n"
        "  @keyframes enter{from{opacity:0;transform:translateY(10px) scale(.92)}to{opacity:1;transform:none}}\n"
        "  @keyframes flt{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}\n"
        "  @media (prefers-reduced-motion:reduce){.in,.fl{animation:none}}")

    aria = "Stack. " + "; ".join(
        "%s: %s" % (lbl, ", ".join(NAMES[s] for s in slugs)) for lbl, slugs in C.STACK_ROWS)
    body, index = [], 0
    y = k.head_bottom(lay, strap) + (10 if lay.narrow else 8)
    for lbl, slugs in C.STACK_ROWS:
        if lay.stacked:
            body.append(k.text(lay.pad, y + 10, lbl, font=k.MONO, size=lay.label_size,
                               fill=k.LABEL, spacing=2.2))
            y += 22
        else:
            body.append(k.text(lay.pad, y + size / 2 + 4, lbl, font=k.MONO,
                               size=lay.label_size, fill=k.LABEL, spacing=2.6))
        for i, slug in enumerate(slugs):
            col, row = i % per_row, i // per_row
            body.append(inline_icon(slug, index, x0 + col * (size + gap),
                                    y + row * (size + gap), size, NAMES[slug]))
            index += 1
        rows_used = (len(slugs) + per_row - 1) // per_row
        y += rows_used * (size + gap) + (6 if lay.narrow else 12)

    y += 2
    body.append(k.rule(lay, y))
    y += 26
    also = k.wrap(C.STACK_ALSO, lay.body_size, lay.right - (lay.pad if lay.stacked else x0))
    if lay.stacked:
        body.append(k.text(lay.pad, y, "ALSO", font=k.MONO, size=lay.label_size,
                           fill=k.LABEL, spacing=2.2))
        y += 19
    else:
        body.append(k.text(lay.pad, y, "ALSO", font=k.MONO, size=lay.label_size,
                           fill=k.LABEL, spacing=2.6))
    for i, ln in enumerate(also):
        body.append(k.text(lay.pad if lay.stacked else x0, y + i * 18, k.esc(ln),
                           font=k.SANS, size=lay.body_size, fill=k.BODY))
    y += len(also) * 18 + 14

    prac = k.wrap(C.STACK_PRACTICE, lay.body_size, lay.right - (lay.pad if lay.stacked else x0))
    if lay.stacked:
        body.append(k.text(lay.pad, y, "HOW I WORK", font=k.MONO, size=lay.label_size,
                           fill=k.LABEL, spacing=2.2))
        y += 19
    else:
        body.append(k.text(lay.pad, y, "HOW I WORK", font=k.MONO, size=lay.label_size,
                           fill=k.LABEL, spacing=2.6))
    for i, ln in enumerate(prac):
        body.append(k.text(lay.pad if lay.stacked else x0, y + i * 18, k.esc(ln),
                           font=k.SANS, size=lay.body_size, fill=k.BODY))
    height = int(y + len(prac) * 18 + (10 if lay.narrow else 18))

    p = k.open_svg(lay, height, aria, "Stack", style)
    p += k.chrome(lay, height, "STACK", strap, uid="st")
    p += body
    p.append("</svg>")
    return "\n".join(p)


def build_work(lay):
    strap = C.STRAPS["work"]
    style = k.style_block(
        ".t{animation:up .55s cubic-bezier(.2,.7,.3,1) both}\n"
        "  @keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}\n"
        "  %s" % (k.REDUCED % ".t"))
    cols = 1 if lay.narrow else 3
    gap = 14 if lay.narrow else 20
    tw = (lay.w - 2 * lay.pad - (cols - 1) * gap) // cols
    inner = tw - 52

    prepared = []
    for tag, title, desc, stack, accent in C.WORK:
        lines = k.wrap(" ".join(desc), lay.body_size, inner)
        prepared.append((tag, title, lines, stack, accent))
    per_tile = max(len(x[2]) for x in prepared)
    th = 118 + per_tile * 17

    top = k.head_bottom(lay, strap) + (8 if lay.narrow else 14)
    rows = (len(prepared) + cols - 1) // cols
    height = int(top + rows * th + (rows - 1) * gap + (16 if lay.narrow else 24))

    aria = "Selected systems. " + "; ".join("%s: %s" % (t[1], " ".join(t[2])) for t in prepared)
    p = k.open_svg(lay, height, aria, "Selected systems", style)
    p += k.chrome(lay, height, "WORK", strap, uid="wk")

    for i, (tag, title, lines, stack, accent) in enumerate(prepared):
        cx = lay.pad + (i % cols) * (tw + gap)
        cy = top + (i // cols) * (th + gap)
        col = k.BLUE if accent == "blue" else k.GREEN
        p.append('<g class="t" style="animation-delay:%.2fs">' % (i * 0.09))
        p.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" '
                 'stroke-width="1"/>' % (cx, cy, tw, th, k.TILE, k.BORDER))
        p.append('<rect x="%d" y="%d" width="42" height="3" rx="1.5" fill="%s"/>'
                 % (cx + 20, cy + 22, col))
        p.append(k.text(cx + tw - 20, cy + 26, k.esc(tag), font=k.MONO, size=10.5,
                        fill=col, weight="600", spacing=2.2, anchor="end"))
        p.append(k.text(cx + 20, cy + 56, k.esc(title), font=k.SANS,
                        size=lay.title_size, fill=k.VALUE, weight="700"))
        for li, ln in enumerate(lines):
            p.append(k.text(cx + 20, cy + 78 + li * 17, k.esc(ln), font=k.SANS,
                            size=lay.body_size, fill=k.BODY))
        ry = cy + th - 34
        p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (cx + 20, ry, cx + tw - 20, ry, "#153A6E"))
        p.append(k.text(cx + 20, ry + 20, k.esc(stack), font=k.MONO, size=10.5,
                        fill=k.MUTED, spacing=0.6))
        p.append("</g>")
    p.append("</svg>")
    return "\n".join(p)


def build_signal(lay, stats):
    weeks = stats["weeks"]
    counts = sorted(d["contributionCount"] for w in weeks
                    for d in w["contributionDays"] if d["contributionCount"] > 0)
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.80)] if counts else [1, 2, 3]

    def colour(v):
        if v <= 0:
            return k.EMPTY
        for i, t in enumerate(q):
            if v <= t:
                return k.RAMP[i]
        return k.RAMP[3]

    cell = 5 if lay.narrow else 16
    gap = 1.5 if lay.narrow else 4
    step = cell + gap
    x0 = lay.pad if lay.narrow else lay.pad
    strap = "%s IN THE LAST 12 MONTHS" % stats["last12"]
    top = k.head_bottom(lay, strap) + (22 if lay.narrow else 26)

    style = k.style_block(
        ".c{animation:fade .55s ease-out both}\n"
        "  @keyframes fade{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}\n"
        "  %s" % (k.REDUCED % ".c"))

    body, seen = [], None
    for wi, w in enumerate(weeks):
        d0 = datetime.date.fromisoformat(w["contributionDays"][0]["date"])
        if d0.month != seen and d0.day <= 14 and (not lay.narrow or d0.month % 3 == 1):
            body.append(k.text(x0 + wi * step, top - 8, MONTHS[d0.month - 1], font=k.MONO,
                               size=9 if lay.narrow else 11, fill=k.MUTED, spacing=1.0))
            seen = d0.month
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            di = datetime.date.fromisoformat(d["date"]).isoweekday() % 7
            body.append('<rect class="c" style="animation-delay:%.3fs" x="%.1f" y="%.1f" '
                        'width="%s" height="%s" rx="%s" fill="%s"/>'
                        % (wi * 0.022, x0 + wi * step, top + di * step, cell, cell,
                           1.5 if lay.narrow else 3.5, colour(d["contributionCount"])))

    sy = top + 7 * step + (26 if lay.narrow else 34)
    tiles = [(format(stats["total"], ","), "TOTAL SINCE JUL %d" % FIRST_YEAR),
             (str(stats["longest"]), "LONGEST STREAK, DAYS"),
             (str(stats["active"]), "ACTIVE DAYS")]
    if lay.narrow:
        for i, (num, lab) in enumerate(tiles):
            ty = sy + i * 34
            body.append(k.text(lay.pad, ty, num, font=k.SANS, size=17,
                               fill=k.VALUE, weight="700"))
            body.append(k.text(lay.pad + 72, ty, lab, font=k.MONO, size=9.5,
                               fill=k.MUTED, spacing=1.6))
        height = int(sy + len(tiles) * 34 + 6)
    else:
        for i, (num, lab) in enumerate(tiles):
            tx = lay.pad + i * 228
            body.append(k.text(tx, sy, num, font=k.SANS, size=21, fill=k.VALUE, weight="700"))
            body.append(k.text(tx, sy + 19, lab, font=k.MONO, size=10.5,
                               fill=k.MUTED, spacing=2))
        sw = lay.right - 5 * 20 - 44
        body.append(k.text(sw - 10, sy + 2, "LESS", font=k.MONO, size=10.5,
                           fill=k.MUTED, spacing=1.6, anchor="end"))
        for i, c in enumerate([k.EMPTY] + k.RAMP):
            body.append('<rect x="%d" y="%d" width="14" height="14" rx="3.5" fill="%s"/>'
                        % (sw + i * 20, sy - 11, c))
        body.append(k.text(sw + 102, sy + 2, "MORE", font=k.MONO, size=10.5,
                           fill=k.MUTED, spacing=1.6))
        height = int(sy + 40)

    aria = ("Contribution heatmap for the last twelve months. %s contributions in that period, "
            "%s since July %d, longest streak %d days, %d active days."
            % (stats["last12"], format(stats["total"], ","), FIRST_YEAR,
               stats["longest"], stats["active"]))
    p = k.open_svg(lay, height, aria, "Contribution signal", style)
    p += k.chrome(lay, height, "SIGNAL", strap, uid="sg")
    p += body
    p.append("</svg>")
    return "\n".join(p)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_trajectory(lay):
    strap = C.STRAPS["trajectory"]
    style = k.style_block(
        ".e{animation:sl .55s cubic-bezier(.2,.7,.3,1) both}\n"
        "  @keyframes sl{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}\n"
        "  %s" % (k.REDUCED % ".e"))
    spine_x = lay.pad + (14 if lay.narrow else 40)
    text_x = spine_x + (28 if lay.narrow else 46)
    avail = lay.right - text_x

    entries, y = [], k.head_bottom(lay, strap) + (30 if lay.narrow else 34)
    for num, role, org, when, desc in C.TRAJECTORY:
        rl = k.wrap(role, lay.title_size, avail)
        meta = "%s  ·  %s" % (org.upper(), plain(when).upper())
        ml = k.wrap(meta, 11.5 if not lay.narrow else 10, avail, mono=True, spacing=1.4)
        dl = k.wrap(" ".join(desc), lay.body_size, avail)
        entries.append((num, rl, ml, dl, y))
        y += len(rl) * 20 + len(ml) * 15 + len(dl) * 17 + (30 if lay.narrow else 34)

    edu_top = y + 6
    height = int(edu_top + len(C.EDUCATION) * (52 if lay.narrow else 34) + 30)

    aria = ("Trajectory. " + "; ".join(
        "%s %s at %s, %s" % (n, r, o, plain(w)) for n, r, o, w, _ in C.TRAJECTORY)
        + ". Education: " + "; ".join("%s, %s, %s" % e for e in C.EDUCATION))
    p = k.open_svg(lay, height, aria, "Trajectory", style)
    p += k.chrome(lay, height, "TRAJECTORY", strap, uid="tj")
    p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="2"/>'
             % (spine_x, entries[0][4] - 12, spine_x, entries[-1][4] + 14, k.SPINE))

    for i, (num, rl, ml, dl, yy) in enumerate(entries):
        col = k.BLUE if i % 2 == 0 else k.GREEN
        r = 12 if lay.narrow else 15
        p.append('<g class="e" style="animation-delay:%.2fs">' % (i * 0.1))
        p.append('<circle cx="%d" cy="%.1f" r="%d" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (spine_x, yy, r, k.TILE, col))
        p.append(k.text(spine_x, yy + 4, num, font=k.MONO, size=9.5 if lay.narrow else 11,
                        fill=col, weight="700", anchor="middle"))
        cy = yy - 4
        for ln in rl:
            p.append(k.text(text_x, cy, k.esc(ln), font=k.SANS, size=lay.title_size,
                            fill=k.VALUE, weight="700"))
            cy += 20
        cy += 1
        for ln in ml:
            p.append(k.text(text_x, cy + 10, k.esc(ln), font=k.MONO,
                            size=10 if lay.narrow else 11.5, fill=k.LABEL, spacing=1.4))
            cy += 15
        cy += 8
        for ln in dl:
            p.append(k.text(text_x, cy + 8, k.esc(ln), font=k.SANS, size=lay.body_size,
                            fill=k.BODY))
            cy += 17
        p.append("</g>")

    p.append(k.rule(lay, edu_top - 14))
    for i, (school, what, when) in enumerate(C.EDUCATION):
        if lay.narrow:
            yy = edu_top + 14 + i * 52
            p.append(k.text(lay.pad, yy, k.esc(school), font=k.SANS, size=13.5,
                            fill=k.VALUE, weight="700"))
            p.append(k.text(lay.pad, yy + 17, k.esc(what), font=k.SANS, size=11.5, fill=k.BODY))
            p.append(k.text(lay.pad, yy + 33, when, font=k.MONO, size=10,
                            fill=k.MUTED, spacing=1.4))
        else:
            yy = edu_top + 16 + i * 34
            p.append(k.text(lay.pad, yy, "EDUCATION" if i == 0 else "", font=k.MONO,
                            size=lay.label_size, fill=k.LABEL, spacing=2.6))
            p.append(k.text(text_x + 42, yy, k.esc(school), font=k.SANS, size=14.5,
                            fill=k.VALUE, weight="700"))
            p.append(k.text(text_x + 232, yy, k.esc(what), font=k.SANS, size=13, fill=k.BODY))
            p.append(k.text(lay.right, yy, when, font=k.MONO, size=11.5,
                            fill=k.MUTED, spacing=1.6, anchor="end"))
    p.append("</svg>")
    return "\n".join(p)


def build_header(lay):
    from PIL import Image
    bg = Image.open(os.path.join(ASSETS, "background.jpg")).convert("RGB")
    height = 150 if lay.narrow else 240
    ratio = lay.w / height
    ch = int(bg.size[0] / ratio)
    top = max(0, (bg.size[1] - ch) // 2 + (40 if not lay.narrow else 90))
    band = bg.crop((0, top, bg.size[0], min(bg.size[1], top + ch)))
    band = band.resize((lay.w * 2, height * 2), Image.LANCZOS)
    buf = io.BytesIO()
    band.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    bg64 = base64.b64encode(buf.getvalue()).decode()

    mark = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    box = mark.split()[3].getbbox()
    mark = mark.crop(box)
    side = max(mark.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(mark, ((side - mark.size[0]) // 2, (side - mark.size[1]) // 2))
    buf2 = io.BytesIO()
    canvas.resize((300, 300), Image.LANCZOS).save(buf2, "PNG", optimize=True)
    mk64 = base64.b64encode(buf2.getvalue()).decode()

    logo = 78 if lay.narrow else 156
    lx = lay.w - logo - (16 if lay.narrow else 54)
    ly = (height - logo) // 2
    name_size = 25 if lay.narrow else 47
    sub_size = 10.5 if lay.narrow else 15.5
    bar_x = 14 if lay.narrow else 62
    tx = bar_x + (18 if lay.narrow else 30)

    p = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         'viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
         'aria-label="%s, %s at SkillsBIT">' % (lay.w, height, lay.w, height,
                                                C.HERO_NAME.title(), C.HERO_ROLE.title()),
         "<title>%s</title>" % C.HERO_NAME.title(),
         """<defs>
<linearGradient id="hb" x1="0" y1="0" x2="0" y2="1"><stop offset="0%%" stop-color="#2BA8E0"/><stop offset="100%%" stop-color="#3EB54A"/></linearGradient>
<linearGradient id="hr" x1="0" y1="1" x2="1" y2="0"><stop offset="0%%" stop-color="#1E96D9"/><stop offset="100%%" stop-color="#3EB54A"/></linearGradient>
<linearGradient id="sc" x1="0" y1="0" x2="1" y2="0"><stop offset="0%%" stop-color="#050D1C" stop-opacity="0.9"/><stop offset="50%%" stop-color="#050D1C" stop-opacity="0.45"/><stop offset="100%%" stop-color="#050D1C" stop-opacity="0"/></linearGradient>
<radialGradient id="hl" cx="0.5" cy="0.5" r="0.5"><stop offset="0%%" stop-color="#04101F" stop-opacity="0.72"/><stop offset="55%%" stop-color="#04101F" stop-opacity="0.42"/><stop offset="100%%" stop-color="#04101F" stop-opacity="0"/></radialGradient>
<clipPath id="hc"><rect width="%d" height="%d"/></clipPath>
</defs>""" % (lay.w, height),
         '<g clip-path="url(#hc)">',
         '<image x="0" y="0" width="%d" height="%d" preserveAspectRatio="xMidYMid slice" '
         'xlink:href="data:image/jpeg;base64,%s"/>' % (lay.w, height, bg64),
         '<rect width="%d" height="%d" fill="url(#sc)"/>' % (lay.w, height),
         '<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="url(#hl)"/>'
         % (lx + logo // 2, height // 2, int(logo * 0.76), int(logo * 0.67)),
         '<image x="%d" y="%d" width="%d" height="%d" xlink:href="data:image/png;base64,%s"/>'
         % (lx, ly, logo, logo, mk64),
         "</g>",
         '<rect x="%d" y="%d" width="%s" height="%d" rx="2.5" fill="url(#hb)"/>'
         % (bar_x, height * 0.28, 4 if lay.narrow else 5, int(height * 0.44)),
         k.text(tx, height * 0.5, C.HERO_NAME, font=k.SANS, size=name_size,
                fill="#FFFFFF", weight="700", spacing=1.2),
         k.text(tx + 2, height * 0.5 + (22 if lay.narrow else 34), C.HERO_ROLE,
                font=k.MONO, size=sub_size, fill="#A9BCD4",
                spacing=2.6 if lay.narrow else 4.2)]
    if not lay.narrow:
        p.append(k.text(405, height * 0.5 + 34, C.HERO_ORG, font=k.MONO, size=sub_size,
                        fill=k.BLUE, spacing=4.2))
    p.append('<rect x="0" y="%d" width="%d" height="4" fill="url(#hr)"/>' % (height - 4, lay.w))
    p.append("</svg>")
    return "\n".join(p)


# ----------------------------------------------------------------------- run

def main():
    stats = fetch()
    print("total=%(total)d last12=%(last12)d longest=%(longest)d active=%(active)d" % stats)

    builders = {
        "header": lambda lay: build_header(lay),
        "tagline": lambda lay: build_tagline(lay),
        "calibration": lambda lay: build_calibration(lay, stats),
        "stack": lambda lay: build_stack(lay),
        "work": lambda lay: build_work(lay),
        "signal": lambda lay: build_signal(lay, stats),
        "trajectory": lambda lay: build_trajectory(lay),
    }
    for name, fn in builders.items():
        for width, suffix in ((k.WIDE, ""), (k.NARROW, "-narrow")):
            svg = fn(k.Layout(width))
            path = os.path.join(ASSETS, "%s%s.svg" % (name, suffix))
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(svg + "\n")
            print("  %-22s %6d bytes" % (name + suffix, len(svg)))


if __name__ == "__main__":
    main()
