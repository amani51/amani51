#!/usr/bin/env python3
"""Regenerate the profile cards from live GitHub contribution data.

Writes assets/signal.svg and assets/calibration.svg.

Needs a token with read:user so private contributions are counted. In CI that
comes from the METRICS_TOKEN secret; locally it falls back to `gh auth token`.
"""

import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

USER = os.environ.get("PROFILE_USER", "amani51")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRST_YEAR = 2022

INK = "#0C2149"
EDGE_A, EDGE_B = "#2BA8E0", "#3EB54A"
BORDER = "#17376A"
HAIRLINE = "#102C57"
LABEL = "#7E93B2"
MUTED = "#5F779A"
VALUE = "#E6EDF6"
PUNCT = "#54708F"
EMPTY = "#0E2547"
RAMP = ["#17456B", "#1E7FA8", "#2BA8E0", "#3EB54A"]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CALIBRATION_ROWS = [
    ("ROLE", "Full-stack engineer, backend-leaning"),
    ("COMPANY", "SkillsBIT |·| IT Solutions |/| Services |/| Academy"),
    ("BASED", "Amman, Jordan |·| remote across MENA and EU"),
    ("CORE", "Django |·| ASP.NET Core |·| React |·| Next.js |·| PostgreSQL"),
    ("SHIPPING", "Vertical platforms|:| clinic, ERP, restaurant, EV, education"),
    ("ORIGIN", "BSc Electrical Engineering |>| RF systems |>| software"),
]


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
                 "User-Agent": "profile-card-builder"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit("GraphQL error: %s" % body["errors"])
    return body["data"]


def fetch():
    """Return (days_by_date, weeks_of_last_year, total_last_year)."""
    today = datetime.date.today()
    days, weeks, last_year_total = {}, [], 0

    for year in range(FIRST_YEAR, today.year + 1):
        start = "%d-01-01T00:00:00Z" % year
        end = ("%s T23:59:59Z" % today.isoformat()).replace(" ", "") \
            if year == today.year else "%d-12-31T23:59:59Z" % year
        data = graphql("""
        { user(login:"%s") { contributionsCollection(from:"%s", to:"%s") {
            contributionCalendar { totalContributions
              weeks { contributionDays { date contributionCount } } } } } }
        """ % (USER, start, end))
        cal = data["user"]["contributionsCollection"]["contributionCalendar"]
        for w in cal["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]

    frm = (today - datetime.timedelta(days=364)).isoformat()
    data = graphql("""
    { user(login:"%s") { contributionsCollection(from:"%sT00:00:00Z", to:"%sT23:59:59Z") {
        contributionCalendar { totalContributions
          weeks { contributionDays { date contributionCount } } } } } }
    """ % (USER, frm, today.isoformat()))
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    last_year_total = cal["totalContributions"]
    return days, weeks, last_year_total


def stats(days):
    total = sum(days.values())
    best_day, best_n = max(days.items(), key=lambda kv: kv[1]) if days else ("", 0)
    longest = run = 0
    for key in sorted(days):
        run = run + 1 if days[key] > 0 else 0
        longest = max(longest, run)
    return total, longest, best_day, best_n


def shell(head):
    """Common card chrome. `head` is the card height."""
    return """<defs>
<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{ink}"/><stop offset="55%" stop-color="#091A38"/><stop offset="100%" stop-color="#061228"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{a}"/><stop offset="100%" stop-color="{b}"/></linearGradient>
<clipPath id="r"><rect x="1" y="1" width="1198" height="{inner}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#r)"><rect width="1200" height="{h}" fill="url(#card)"/><rect x="0" y="0" width="5" height="{h}" fill="url(#edge)"/></g>
<rect x="1" y="1" width="1198" height="{inner}" rx="16" fill="none" stroke="{bd}" stroke-width="1.5"/>""".format(
        ink=INK, a=EDGE_A, b=EDGE_B, bd=BORDER, h=head, inner=head - 2)


def mono(x, y, size, ls, fill, text, anchor="start", weight="400"):
    return ('<text x="%s" y="%s" %sfont-family="SFMono-Regular, Consolas, Menlo, monospace" '
            'font-size="%s" font-weight="%s" letter-spacing="%s" fill="%s">%s</text>'
            % (x, y, 'text-anchor="%s" ' % anchor if anchor != "start" else "",
               size, weight, ls, fill, text))


def build_signal(weeks, last_year_total, total, longest, best_day, best_n):
    counts = sorted(d["contributionCount"] for w in weeks
                    for d in w["contributionDays"] if d["contributionCount"] > 0)
    q = [counts[int(len(counts) * p)] for p in (0.25, 0.5, 0.80)] if counts else [1, 2, 3]

    def colour(v):
        if v <= 0:
            return EMPTY
        if v <= q[0]:
            return RAMP[0]
        if v <= q[1]:
            return RAMP[1]
        if v <= q[2]:
            return RAMP[2]
        return RAMP[3]

    X0, Y0, CELL, GAP = 62, 104, 16, 4
    STEP = CELL + GAP
    H = 332
    label = ("Contribution signal: %s contributions in the last twelve months and %s "
             "since %d. Longest streak %d days." % (last_year_total, f"{total:,}", FIRST_YEAR, longest))
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 %d" width="1200" height="%d" '
         'role="img" aria-label="%s">' % (H, H, label),
         "<title>Contribution signal</title>",
         """<style>
  .c{animation:fade .55s ease-out both}
  @keyframes fade{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}
  @media (prefers-reduced-motion:reduce){.c{animation:none}}
 </style>""",
         shell(H),
         mono(52, 52, 13, 4.5, EDGE_A, "SIGNAL", weight="600"),
         '<line x1="140" y1="47" x2="742" y2="47" stroke="%s" stroke-width="1"/>' % BORDER,
         '<circle cx="760" cy="47" r="4" fill="%s"/>' % EDGE_B,
         mono(1148, 52, 12.5, 1.6, LABEL,
              "%s CONTRIBUTIONS IN THE LAST 12 MONTHS" % last_year_total, anchor="end")]

    seen = None
    for wi, w in enumerate(weeks):
        d0 = datetime.date.fromisoformat(w["contributionDays"][0]["date"])
        if d0.month != seen and d0.day <= 14:
            p.append(mono(X0 + wi * STEP, Y0 - 14, 11, 1.4, MUTED, MONTHS[d0.month - 1]))
            seen = d0.month
    for i, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p.append(mono(X0 - 12, Y0 + i * STEP + 12, 10.5, 0, MUTED, lbl, anchor="end"))

    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            di = datetime.date.fromisoformat(d["date"]).isoweekday() % 7
            p.append('<rect class="c" style="animation-delay:%.3fs" x="%d" y="%d" width="%d" '
                     'height="%d" rx="3.5" fill="%s"/>'
                     % (wi * 0.022, X0 + wi * STEP, Y0 + di * STEP, CELL, CELL,
                        colour(d["contributionCount"])))

    sy = Y0 + 7 * STEP + 34
    best = datetime.date.fromisoformat(best_day) if best_day else datetime.date.today()
    tiles = [(62, f"{total:,}", "TOTAL SINCE JUL %d" % FIRST_YEAR),
             (290, str(longest), "LONGEST STREAK, DAYS"),
             (520, str(best_n), "BUSIEST DAY, %d %s %d"
              % (best.day, MONTHS[best.month - 1].upper(), best.year))]
    for x, num, lab in tiles:
        p.append('<text x="%d" y="%d" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" '
                 'font-size="21" font-weight="700" fill="%s">%s</text>' % (x, sy, VALUE, num))
        p.append(mono(x, sy + 19, 10.5, 2, MUTED, lab))

    sw = 1006
    p.append(mono(sw - 10, sy + 2, 10.5, 1.6, MUTED, "LESS", anchor="end"))
    for i, c in enumerate([EMPTY] + RAMP):
        p.append('<rect x="%d" y="%d" width="14" height="14" rx="3.5" fill="%s"/>'
                 % (sw + i * 20, sy - 11, c))
    p.append(mono(sw + 5 * 20 + 2, sy + 2, 10.5, 1.6, MUTED, "MORE"))
    p.append("</svg>")
    return "\n".join(p)


def build_calibration(total):
    H = 336
    label = ("Calibration: %s. %s contributions since July %d."
             % ("; ".join("%s, %s" % (k, v.replace("|", "")) for k, v in CALIBRATION_ROWS),
                f"{total:,}", FIRST_YEAR))
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 %d" width="1200" height="%d" '
         'role="img" aria-label="%s">' % (H, H, label),
         "<title>Calibration</title>",
         shell(H),
         mono(52, 54, 13, 4.5, EDGE_A, "CALIBRATION", weight="600"),
         '<line x1="196" y1="49" x2="806" y2="49" stroke="%s" stroke-width="1"/>' % BORDER,
         '<circle cx="824" cy="49" r="4" fill="%s"/>' % EDGE_B,
         mono(1148, 54, 12.5, 1.6, LABEL,
              "%s CONTRIBUTIONS SINCE JUL %d" % (f"{total:,}", FIRST_YEAR), anchor="end")]

    y = 102
    for key, _ in CALIBRATION_ROWS:
        p.append(mono(52, y, 12.5, 2.6, LABEL, key))
        y += 38
    y = 102
    for _, val in CALIBRATION_ROWS:
        parts, out = val.split("|"), []
        for i, chunk in enumerate(parts):
            if i % 2:
                glyph = {">": "&#8594;"}.get(chunk, chunk)
                fill = EDGE_B if chunk == ">" else PUNCT
                out.append('<tspan fill="%s">%s</tspan>' % (fill, glyph))
            else:
                out.append(chunk)
        p.append('<text x="212" y="%d" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" '
                 'font-size="16.5" fill="%s">%s</text>' % (y, VALUE, "".join(out)))
        y += 38
    for i in range(1, len(CALIBRATION_ROWS)):
        yy = 102 + i * 38 - 23
        p.append('<line x1="52" y1="%d" x2="1148" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (yy, yy, HAIRLINE))
    p.append("</svg>")
    return "\n".join(p)


def main():
    days, weeks, last_year_total = fetch()
    total, longest, best_day, best_n = stats(days)
    print("total=%d last12=%d longest=%d busiest=%s(%d)"
          % (total, last_year_total, longest, best_day, best_n))
    out = {
        "assets/signal.svg": build_signal(weeks, last_year_total, total, longest, best_day, best_n),
        "assets/calibration.svg": build_calibration(total),
    }
    for rel, body in out.items():
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as fh:
            fh.write(body + "\n")
        print("wrote", rel)


if __name__ == "__main__":
    main()
