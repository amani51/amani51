#!/usr/bin/env python3
"""Build the static presentation cards: assets/tagline.svg and assets/trajectory.svg.

These hold no live data, so they only need rebuilding when the copy changes.
The data-driven cards live in build_cards.py.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INK_A, INK_B, INK_C = "#0C2149", "#091A38", "#061228"
BLUE, GREEN = "#2BA8E0", "#3EB54A"
BORDER, HAIRLINE = "#17376A", "#102C57"
LABEL, MUTED, VALUE = "#7E93B2", "#5F779A", "#E6EDF6"
TILE = "#0B2044"

MONO = "SFMono-Regular, Consolas, Menlo, monospace"
SANS = "Helvetica Neue, Helvetica, Arial, sans-serif"

TAGLINES = [
    "Electrical engineer turned full-stack developer",
    "I build production systems, not demos",
    "Django  ·  ASP.NET Core  ·  React  ·  PostgreSQL",
    "Measure, don't guess.",
]

TRAJECTORY = [
    ("01", "RF Engineer", "SESAME Synchrotron", "Jun 2021 &#8594; Jul 2022",
     ["Analysed RF cavities and wrote MATLAB and Python simulations to optimise",
      "system performance. Learned to trust instruments over intuition."]),
    ("02", "Teaching Assistant, Coding Program", "ASAC", "Mar 2023 &#8594; Mar 2024",
     ["Mentored bootcamp developers, shaped curriculum, and assessed progress",
      "through technical interviews. Teaching is how you find out what you know."]),
    ("03", "AI Prompt Engineer", "MENADEVS", "Mar 2024 &#8594; Dec 2024",
     ["Designed and iterated prompts for generative models across several",
      "industries, running structured evaluations to make outputs reliable."]),
    ("04", "BTEC IT Internal Verifier", "ISO Education Schools", "Jan 2025 &#8594; Present",
     ["Verify assessment against BTEC and Pearson standards and hold grading",
      "consistent. Quality assurance, applied to people instead of code."]),
]

EDUCATION = [
    ("ASAC / Code Fellows", "Full Stack Web Development, 900-hour intensive", "2022 to 2023"),
    ("University of Jordan", "BSc Electrical Engineering", "2014 to 2019"),
]


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unesc(text):
    """Strip entities for the aria-label, which must be plain text."""
    return text.replace("&#8594;", "to").replace("&amp;", "and")


def chrome(height, label, rule_to, right_text=None):
    """Card background, border, section label and top rule."""
    parts = ["""<defs>
<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{a}"/><stop offset="55%" stop-color="{b}"/><stop offset="100%" stop-color="{c}"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{bl}"/><stop offset="100%" stop-color="{gr}"/></linearGradient>
<clipPath id="rc"><rect x="1" y="1" width="1198" height="{i}" rx="16"/></clipPath>
</defs>""".format(a=INK_A, b=INK_B, c=INK_C, bl=BLUE, gr=GREEN, i=height - 2),
        '<g clip-path="url(#rc)"><rect width="1200" height="{h}" fill="url(#card)"/>'
        '<rect x="0" y="0" width="5" height="{h}" fill="url(#edge)"/></g>'.format(h=height),
        '<rect x="1" y="1" width="1198" height="{}" rx="16" fill="none" stroke="{}" '
        'stroke-width="1.5"/>'.format(height - 2, BORDER),
        '<text x="52" y="52" font-family="{m}" font-size="13" font-weight="600" '
        'letter-spacing="4.5" fill="{c}">{l}</text>'.format(m=MONO, c=BLUE, l=label),
        '<line x1="{f}" y1="47" x2="{t}" y2="47" stroke="{c}" stroke-width="1"/>'
        .format(f=52 + len(label) * 13 + 24, t=rule_to, c=BORDER)]
    if right_text:
        parts.append('<circle cx="{}" cy="47" r="4" fill="{}"/>'.format(rule_to + 18, GREEN))
        parts.append('<text x="1148" y="52" text-anchor="end" font-family="{m}" font-size="12.5" '
                     'letter-spacing="1.6" fill="{c}">{t}</text>'.format(m=MONO, c=LABEL, t=right_text))
    return parts


def build_tagline():
    """Cross-fading lines. Each holds, then hands over to the next."""
    n = len(TAGLINES)
    hold = 3.6
    total = hold * n
    H = 56
    # visible for one slot, invisible for the rest
    pct_in, pct_hold, pct_out = 2.0, 100.0 / n - 4.0, 100.0 / n
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {h}" width="1200" '
             'height="{h}" role="img" aria-label="{a}">'.format(h=H, a=esc(" / ".join(TAGLINES))),
             "<title>Tagline</title>",
             """<style>
  .l{{opacity:0;animation:cycle {t}s ease-in-out infinite}}
  @keyframes cycle{{
    0%{{opacity:0;transform:translateY(4px)}}
    {i:.1f}%{{opacity:1;transform:none}}
    {h:.1f}%{{opacity:1;transform:none}}
    {o:.1f}%{{opacity:0;transform:translateY(-4px)}}
    100%{{opacity:0}}
  }}
  @media (prefers-reduced-motion:reduce){{.l{{animation:none}}.l:first-of-type{{opacity:1}}}}
 </style>""".format(t=total, i=pct_in, h=pct_hold, o=pct_out)]
    for i, line in enumerate(TAGLINES):
        parts.append('<text class="l" style="animation-delay:{d:.2f}s" x="600" y="34" '
                     'text-anchor="middle" font-family="{m}" font-size="19" font-weight="500" '
                     'letter-spacing="0.4" fill="{c}">{t}</text>'
                     .format(d=i * hold, m=MONO, c=BLUE, t=esc(line)))
    parts.append("</svg>")
    return "\n".join(parts)


def build_trajectory():
    TOP, ROW = 96, 92
    EDU_TOP = TOP + len(TRAJECTORY) * ROW + 26
    H = EDU_TOP + len(EDUCATION) * 34 + 34
    LINE_X, TEXT_X = 92, 138

    described = "; ".join(
        "%s, %s at %s, %s" % (n, role, org, unesc(when)) for n, role, org, when, _ in TRAJECTORY)
    described += ". Education: " + "; ".join("%s, %s, %s" % e for e in EDUCATION)

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {h}" width="1200" '
             'height="{h}" role="img" aria-label="Trajectory. {d}">'.format(h=H, d=esc(described)),
             "<title>Trajectory</title>",
             """<style>
  .e{animation:slide .55s cubic-bezier(.2,.7,.3,1) both}
  @keyframes slide{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
  @media (prefers-reduced-motion:reduce){.e{animation:none}}
 </style>"""]
    parts += chrome(H, "TRAJECTORY", 820, "FOUR DISCIPLINES, ONE DIRECTION")

    # spine
    spine_top, spine_bottom = TOP - 12, TOP + (len(TRAJECTORY) - 1) * ROW + 14
    parts.append('<line x1="{x}" y1="{a}" x2="{x}" y2="{b}" stroke="{c}" stroke-width="2"/>'
                 .format(x=LINE_X, a=spine_top, b=spine_bottom, c="#153A6E"))

    for i, (num, role, org, when, desc) in enumerate(TRAJECTORY):
        y = TOP + i * ROW
        accent = BLUE if i % 2 == 0 else GREEN
        g = ['<g class="e" style="animation-delay:{:.2f}s">'.format(i * 0.1)]
        g.append('<circle cx="{}" cy="{}" r="15" fill="{}" stroke="{}" stroke-width="2"/>'
                 .format(LINE_X, y, TILE, accent))
        g.append('<text x="{}" y="{}" text-anchor="middle" font-family="{}" font-size="11" '
                 'font-weight="700" letter-spacing="0.5" fill="{}">{}</text>'
                 .format(LINE_X, y + 4, MONO, accent, num))
        g.append('<text x="{}" y="{}" font-family="{}" font-size="17" font-weight="700" '
                 'fill="{}">{}</text>'.format(TEXT_X, y - 4, SANS, VALUE, esc(role)))
        g.append('<text x="{}" y="{}" font-family="{}" font-size="11.5" letter-spacing="1.8" '
                 'fill="{}">{}  <tspan fill="{}">·</tspan>  {}</text>'
                 .format(TEXT_X, y + 15, MONO, LABEL, esc(org).upper(), MUTED, when.upper()))
        for li, line in enumerate(desc):
            g.append('<text x="{}" y="{}" font-family="{}" font-size="12.5" fill="{}">{}</text>'
                     .format(TEXT_X, y + 37 + li * 17, SANS, "#93A8C6", esc(line)))
        g.append("</g>")
        parts += g

    parts.append('<line x1="52" y1="{0}" x2="1148" y2="{0}" stroke="{1}" stroke-width="1"/>'
                 .format(EDU_TOP - 26, HAIRLINE))
    parts.append('<text x="52" y="{}" font-family="{}" font-size="12.5" letter-spacing="2.6" '
                 'fill="{}">EDUCATION</text>'.format(EDU_TOP + 2, MONO, LABEL))
    for i, (school, what, when) in enumerate(EDUCATION):
        y = EDU_TOP + i * 34
        parts.append('<text x="{}" y="{}" font-family="{}" font-size="14.5" font-weight="700" '
                     'fill="{}">{}</text>'.format(TEXT_X + 42, y + 2, SANS, VALUE, esc(school)))
        parts.append('<text x="{}" y="{}" font-family="{}" font-size="13" fill="{}">{}</text>'
                     .format(TEXT_X + 232, y + 2, SANS, "#93A8C6", esc(what)))
        parts.append('<text x="1148" y="{}" text-anchor="end" font-family="{}" font-size="11.5" '
                     'letter-spacing="1.6" fill="{}">{}</text>'.format(y + 2, MONO, MUTED, when))
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    for name, body in (("tagline", build_tagline()), ("trajectory", build_trajectory())):
        path = os.path.join(ROOT, "assets", name + ".svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body + "\n")
        print("wrote assets/%s.svg (%d bytes)" % (name, len(body)))
