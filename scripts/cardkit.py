#!/usr/bin/env python3
"""Shared layout kit for the profile cards.

Every card is generated at two widths. GitHub scales an SVG to the content
column, so a single 1200px card shrinks to about a third on a phone and its
12px body text lands at roughly 4px. Rather than scale, we lay the same content
out again at phone width and let <picture media="(max-width: ...)"> pick.

    WIDE   1200px, label column beside the value, used on desktop
    NARROW  420px, label stacked above the value, used below 600px viewport
"""

# palette, taken from the SkillsBIT logo
INK_A, INK_B, INK_C = "#0C2149", "#091A38", "#061228"
BLUE, GREEN = "#2BA8E0", "#3EB54A"
BORDER, HAIRLINE = "#17376A", "#102C57"
TILE, SPINE = "#0B2044", "#153A6E"
LABEL, MUTED, VALUE, BODY = "#7E93B2", "#5F779A", "#E6EDF6", "#93A8C6"
EMPTY = "#0E2547"
RAMP = ["#17456B", "#1E7FA8", "#2BA8E0", "#3EB54A"]

MONO = "SFMono-Regular, Consolas, Menlo, monospace"
SANS = "Helvetica Neue, Helvetica, Arial, sans-serif"

WIDE, NARROW = 1200, 420


class Layout:
    """Geometry that differs between the two widths."""

    def __init__(self, width):
        self.w = width
        self.narrow = width <= 600
        if self.narrow:
            self.pad = 18
            self.value_x = 18          # values sit under their label
            self.stacked = True
            self.radius = 14
            self.head_size = 11.5
            self.label_size = 10.5
            self.value_size = 13.5
            self.body_size = 12
            self.title_size = 15
        else:
            self.pad = 52
            self.value_x = 212         # values sit beside their label
            self.stacked = False
            self.radius = 16
            self.head_size = 13
            self.label_size = 12.5
            self.value_size = 16.5
            self.body_size = 12.5
            self.title_size = 17

    @property
    def right(self):
        return self.w - self.pad


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def mono_w(text, size, spacing=0.0):
    """Monospace advance width. DejaVu/Consolas sit near 0.60 em."""
    return len(text) * (size * 0.62 + spacing)


def sans_w(text, size):
    """Rough Helvetica advance. Wide glyphs cost more, so weight by character."""
    total = 0.0
    for ch in text:
        if ch in "iljtIf.,:;'|! ":
            total += size * 0.33
        elif ch in "mwMW@":
            total += size * 0.92
        elif ch.isupper():
            total += size * 0.74
        else:
            total += size * 0.59
    return total


def wrap(text, size, max_width, mono=False, spacing=0.0, safety=0.94):
    """Greedy wrap to a pixel width. Returns a list of lines.

    Advance widths are estimated, not measured, because the renderer picks the
    font at display time. `safety` keeps a margin so an under-estimate does not
    push a glyph past the card border.
    """
    max_width *= safety
    measure = (lambda s: mono_w(s, size, spacing)) if mono else (lambda s: sans_w(s, size))
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if measure(trial) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(x, y, content, *, font=SANS, size=13, fill=VALUE, weight=None,
         spacing=None, anchor=None):
    bits = ['<text x="%s" y="%s"' % (round(x, 1), round(y, 1))]
    if anchor:
        bits.append('text-anchor="%s"' % anchor)
    bits.append('font-family="%s" font-size="%s"' % (font, size))
    if weight:
        bits.append('font-weight="%s"' % weight)
    if spacing is not None:
        bits.append('letter-spacing="%s"' % spacing)
    bits.append('fill="%s">%s</text>' % (fill, content))
    return " ".join(bits)


def open_svg(lay, height, aria, title, style=""):
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">'
        % (lay.w, height, lay.w, height, esc(aria)),
        "<title>%s</title>" % esc(title),
        style,
    ]


def chrome(lay, height, section, strap=None, uid="c"):
    """Card background, gradient edge, section label, rule and optional strap.

    On narrow cards the strap moves to its own line, because there is no room
    to sit it opposite the section label.
    """
    inner = height - 2
    out = ["""<defs>
<linearGradient id="{u}bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{a}"/><stop offset="55%" stop-color="{b}"/><stop offset="100%" stop-color="{c}"/></linearGradient>
<linearGradient id="{u}ed" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{bl}"/><stop offset="100%" stop-color="{gr}"/></linearGradient>
<clipPath id="{u}cl"><rect x="1" y="1" width="{iw}" height="{ih}" rx="{r}"/></clipPath>
</defs>""".format(u=uid, a=INK_A, b=INK_B, c=INK_C, bl=BLUE, gr=GREEN,
                  iw=lay.w - 2, ih=inner, r=lay.radius),
        '<g clip-path="url(#{u}cl)"><rect width="{w}" height="{h}" fill="url(#{u}bg)"/>'
        '<rect x="0" y="0" width="{e}" height="{h}" fill="url(#{u}ed)"/></g>'
        .format(u=uid, w=lay.w, h=height, e=4 if lay.narrow else 5),
        '<rect x="1" y="1" width="{}" height="{}" rx="{}" fill="none" stroke="{}" '
        'stroke-width="1.5"/>'.format(lay.w - 2, inner, lay.radius, BORDER),
    ]
    head_y = 34 if lay.narrow else 52
    out.append(text(lay.pad, head_y, esc(section), font=MONO, size=lay.head_size,
                    fill=BLUE, weight="600", spacing=4.5 if not lay.narrow else 3.2))

    label_w = mono_w(section, lay.head_size, 4.5 if not lay.narrow else 3.2)
    rule_from = lay.pad + label_w + 18
    if lay.narrow:
        out.append('<line x1="%.1f" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                   % (rule_from, head_y - 5, lay.right, head_y - 5, BORDER))
        if strap:
            out.append(text(lay.pad, head_y + 20, esc(strap), font=MONO, size=9.5,
                            fill=MUTED, spacing=1.4))
    else:
        strap_w = mono_w(strap, 12.5, 1.6) if strap else 0
        rule_to = lay.right - strap_w - 40 if strap else lay.right
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                   % (rule_from, head_y - 5, rule_to, head_y - 5, BORDER))
        if strap:
            out.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>'
                       % (rule_to + 16, head_y - 5, GREEN))
            out.append(text(lay.right, head_y, esc(strap), font=MONO, size=12.5,
                            fill=LABEL, spacing=1.6, anchor="end"))
    return out


def head_bottom(lay, strap=None):
    """Y coordinate where card content may begin."""
    if lay.narrow:
        return 66 if strap else 52
    return 78


def rule(lay, y, colour=HAIRLINE):
    return ('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
            % (lay.pad, y, lay.right, y, colour))


REDUCED = "@media (prefers-reduced-motion:reduce){%s{animation:none}}"


def style_block(body):
    return "<style>\n  %s\n </style>" % body


def picture(name, alt, breakpoint_px=600):
    """The markdown snippet that swaps in the narrow card on small screens."""
    return (
        '<picture>\n'
        '  <source media="(max-width: %dpx)" srcset="assets/%s-narrow.svg" />\n'
        '  <img src="assets/%s.svg" width="100%%" alt="%s" />\n'
        '</picture>' % (breakpoint_px, name, name, alt)
    )
