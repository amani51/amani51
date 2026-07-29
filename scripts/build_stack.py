#!/usr/bin/env python3
"""Build assets/stack.svg from the icon sources in assets/icons.

Each icon gets two nested groups: the outer one plays a one-off entrance, the
inner one floats forever. They are kept separate so the two transforms never
fight over the same element. Float delays step across each row, so the motion
reads as a wave travelling left to right rather than everything bobbing in
unison.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, "assets", "icons")
OUT = os.path.join(ROOT, "assets", "stack.svg")

ROWS = [
    ("FRONTEND", ["ts", "js", "react", "nextjs", "tailwind", "html", "css", "bootstrap"]),
    ("BACKEND", ["py", "django", "cs", "dotnet", "nodejs", "express", "matlab"]),
    ("DATA AND OPS", ["postgres", "mongodb", "git", "github", "postman", "vercel", "netlify", "heroku"]),
]
NAMES = {
    "ts": "TypeScript", "js": "JavaScript", "react": "React", "nextjs": "Next.js",
    "tailwind": "Tailwind CSS", "html": "HTML", "css": "CSS", "bootstrap": "Bootstrap",
    "py": "Python", "django": "Django", "cs": "C#", "dotnet": ".NET", "nodejs": "Node.js",
    "express": "Express", "matlab": "MATLAB", "postgres": "PostgreSQL", "mongodb": "MongoDB",
    "git": "Git", "github": "GitHub", "postman": "Postman", "vercel": "Vercel",
    "netlify": "Netlify", "heroku": "Heroku",
}

SIZE, GAP, LABEL_X, ICON_X = 62, 18, 52, 212
HEIGHT = 428
PRACTICES = ("Test-driven development   ·   REST API design   ·   Remote pair-programming"
             "   ·   Code review   ·   Mentoring")
FLOAT_PERIOD = 3.4      # seconds for one full bob
FLOAT_STEP = 0.16       # phase offset between neighbours, makes the wave
FLOAT_RISE = 7          # pixels


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(slug, index, x, y):
    """Return the icon inlined, with every id namespaced so icons cannot collide."""
    with open(os.path.join(ICONS, slug + ".svg"), encoding="utf-8") as fh:
        raw = fh.read()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    for ident in sorted(set(re.findall(r'id="([^"]+)"', inner)), key=len, reverse=True):
        new = "i{}_{}".format(index, ident)
        inner = (inner.replace('id="%s"' % ident, 'id="%s"' % new)
                      .replace("url(#%s)" % ident, "url(#%s)" % new)
                      .replace('xlink:href="#%s"' % ident, 'xlink:href="#%s"' % new)
                      .replace('href="#%s"' % ident, 'href="#%s"' % new))
    # outer group = entrance, inner group = perpetual float
    return (
        '<g class="in" style="animation-delay:{ed:.2f}s">'
        '<g class="fl" style="animation-delay:{fd:.2f}s">'
        "<title>{name}</title>"
        '<svg x="{x}" y="{y}" width="{s}" height="{s}" viewBox="0 0 256 256">{body}</svg>'
        "</g></g>"
    # negative delay: every icon is already mid-cycle at load, so the wave is
    # running from the first frame instead of icons waking up one by one
    ).format(ed=index * 0.055, fd=-(index * FLOAT_STEP), name=esc(NAMES[slug]),
             x=x, y=y, s=SIZE, body=inner)


def build():
    described = "; ".join(
        "%s: %s" % (label, ", ".join(NAMES[s] for s in slugs)) for label, slugs in ROWS)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 1200 {h}" width="1200" height="{h}" role="img" aria-label="Stack. {d}">'
        .format(h=HEIGHT, d=esc(described)),
        "<title>Stack</title>",
        """<style>
  .in{{animation:enter .5s cubic-bezier(.2,.7,.3,1) both}}
  .fl{{animation:float {p}s ease-in-out infinite}}
  @keyframes enter{{from{{opacity:0;transform:translateY(10px) scale(.92)}}to{{opacity:1;transform:none}}}}
  @keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-{r}px)}}}}
  @media (prefers-reduced-motion:reduce){{.in,.fl{{animation:none}}}}
 </style>""".format(p=FLOAT_PERIOD, r=FLOAT_RISE),
        """<defs>
<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0C2149"/><stop offset="55%" stop-color="#091A38"/><stop offset="100%" stop-color="#061228"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2BA8E0"/><stop offset="100%" stop-color="#3EB54A"/></linearGradient>
<clipPath id="rc"><rect x="1" y="1" width="1198" height="{i}" rx="16"/></clipPath>
</defs>""".format(i=HEIGHT - 2),
        '<g clip-path="url(#rc)"><rect width="1200" height="{h}" fill="url(#card)"/>'
        '<rect x="0" y="0" width="5" height="{h}" fill="url(#edge)"/></g>'.format(h=HEIGHT),
        '<rect x="1" y="1" width="1198" height="{}" rx="16" fill="none" stroke="#17376A" '
        'stroke-width="1.5"/>'.format(HEIGHT - 2),
        '<text x="52" y="52" font-family="SFMono-Regular, Consolas, Menlo, monospace" '
        'font-size="13" font-weight="600" letter-spacing="4.5" fill="#2BA8E0">STACK</text>',
        '<line x1="128" y1="47" x2="1148" y2="47" stroke="#17376A" stroke-width="1"/>',
    ]

    index, y = 0, 86
    for row_i, (label, slugs) in enumerate(ROWS):
        parts.append(
            '<text x="{x}" y="{y}" font-family="SFMono-Regular, Consolas, Menlo, monospace" '
            'font-size="12.5" letter-spacing="2.6" fill="#7E93B2">{l}</text>'
            .format(x=LABEL_X, y=y + SIZE / 2 + 4, l=esc(label)))
        for col_i, slug in enumerate(slugs):
            parts.append(inline(slug, index, ICON_X + col_i * (SIZE + GAP), y))
            index += 1
        if row_i < len(ROWS) - 1:
            rule = y + SIZE + 14
            parts.append('<line x1="52" y1="{0}" x2="1148" y2="{0}" stroke="#102C57" '
                         'stroke-width="1"/>'.format(rule))
        y += SIZE + 28

    # practices footer, so "how I work" sits inside the card instead of orphaned below it
    rule_y = y - 4
    parts.append('<line x1="52" y1="{0}" x2="1148" y2="{0}" stroke="#102C57" '
                 'stroke-width="1"/>'.format(rule_y))
    parts.append('<text x="{x}" y="{y}" font-family="SFMono-Regular, Consolas, Menlo, monospace" '
                 'font-size="12.5" letter-spacing="2.6" fill="#7E93B2">HOW I WORK</text>'
                 .format(x=LABEL_X, y=rule_y + 32))
    parts.append('<text x="{x}" y="{y}" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" '
                 'font-size="13.5" fill="#93A8C6">{t}</text>'
                 .format(x=ICON_X, y=rule_y + 32, t=esc(PRACTICES)))

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg + "\n")
    print("wrote assets/stack.svg (%d KB)" % (len(svg) // 1024))
