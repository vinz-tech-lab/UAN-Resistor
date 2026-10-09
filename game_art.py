# -*- coding: utf-8 -*-
"""Animated SVG scenes for Resistor Lab: the bench, the QC stamp, the final score."""
import base64
import math

NAVY, TEAL, AMBER = "#1B2A4A", "#2A9D8F", "#E8A33D"
BG, PANEL, LINE = "#101B33", "#0A1326", "#24365C"
WIRE, TXT, MUTED, LEAD, RED = "#6F7FA3", "#E6ECF7", "#9FB0D0", "#5FD0C2", "#FF6B5E"
FONT = "Calibri, 'Segoe UI', Roboto, Arial, sans-serif"
MONO = "'Courier New', ui-monospace, monospace"

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
html,body{margin:0;padding:0;background:transparent;overflow:hidden}
svg{display:block;width:100%;height:auto;max-height:100vh;margin:0 auto}
.flow{fill:none;stroke:#FFC45A;stroke-width:4;stroke-linecap:round;stroke-dasharray:.1 16;
      animation:flow 1s linear infinite}
@keyframes flow{from{stroke-dashoffset:16.1}to{stroke-dashoffset:0}}
.sw{transform-origin:128px 170px;animation:swclose .28s ease-in both}
@keyframes swclose{from{transform:rotate(28deg)}to{transform:rotate(0deg)}}
.needle{animation:sweep 1.15s cubic-bezier(.3,1.45,.45,1) .25s both}
@keyframes sweep{from{transform:rotate(-60deg)}to{transform:rotate(var(--a))}}
.lead{stroke-dasharray:4 3;animation:leadin .5s ease-out both}
@keyframes leadin{from{opacity:0}to{opacity:1}}
.badge{animation:pop .35s cubic-bezier(.3,1.6,.5,1) both;transform-box:fill-box;transform-origin:center}
@keyframes pop{from{transform:scale(.2);opacity:0}to{transform:scale(1);opacity:1}}
.hot{animation:hot 1s ease-in-out infinite}
@keyframes hot{0%,100%{opacity:.15}50%{opacity:.85}}
.smoke{animation:smoke 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes smoke{from{transform:translateY(0) scale(.5);opacity:.75}to{transform:translateY(-34px) scale(1.9);opacity:0}}
.shake{animation:shake .5s linear 1}
@keyframes shake{0%,100%{transform:translate(0,0)}20%{transform:translate(-4px,1px)}40%{transform:translate(4px,-1px)}60%{transform:translate(-3px,0)}80%{transform:translate(2px,1px)}}
.blink{animation:blink .7s steps(2,start) infinite}
@keyframes blink{to{visibility:hidden}}
.stamp{transform-box:fill-box;transform-origin:center;animation:stamp .45s cubic-bezier(.2,1.5,.4,1) .15s both}
@keyframes stamp{from{transform:scale(2.8);opacity:0}to{transform:scale(1);opacity:1}}
.star{transform-box:fill-box;transform-origin:center;animation:pop .4s cubic-bezier(.3,1.7,.5,1) both}
.ring{animation:ring 1.4s cubic-bezier(.2,.8,.2,1) .2s both}
@keyframes ring{from{stroke-dashoffset:var(--c)}to{stroke-dashoffset:var(--o)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style></head><body>__SVG__
<script>
(function(){
  if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  var els=document.querySelectorAll('[data-count]');
  for(var i=0;i<els.length;i++){(function(e){
    var v=parseFloat(e.getAttribute('data-count')),d=parseInt(e.getAttribute('data-dec')||'0',10),
        pre=e.getAttribute('data-pre')||'',suf=e.getAttribute('data-suf')||'',t0=null;
    function f(ts){if(t0===null)t0=ts;var k=Math.min(1,(ts-t0)/900);k=1-Math.pow(1-k,3);
      e.textContent=pre+(v*k).toFixed(d)+suf;if(k<1)requestAnimationFrame(f);}
    requestAnimationFrame(f);})(els[i]);}
})();
</script></body></html>"""


def _page(svg):
    return PAGE.replace("__SVG__", svg)


def fmt_R(r):
    return f"{r / 1000:g} kΩ" if r >= 1000 else f"{r:g} Ω"


def _text(x, y, s, size=13, anchor="middle", weight="400", fill=TXT, font=FONT, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}" {extra}>{s}</text>')


def _flow_dur(i):
    """Dot period: faster for larger currents, on a log scale so 0.1 mA to 1 A all stay visible."""
    v = 14 + 22 * math.log10(max(i, 1e-5) / 1e-4)
    return 16.0 / min(max(v, 8.0), 110.0)


def _heat_fill(h):
    a, b = (58, 46, 22), (160, 44, 20)
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * min(max(h, 0), 1)) for i in range(3))


def bench_html(topo, E, R1, R2, tag, instr, place, labels, mode="idle", flow=None, heat=0.0, reading=None):
    """
    The whole bench as one animated scene.
    mode: idle (switch open), live (current flowing, needle swings), trip, burn.
    reading: dict(text, value, dec, unit, frac, ticks=(0, mid, full), n) when live.
    """
    p = []
    add = p.append
    live = mode == "live"
    add(f'<rect x="0.5" y="0.5" width="359" height="371" rx="14" fill="{BG}"/>')
    add('<g class="shake">' if mode == "burn" else "<g>")

    # ---- wires and current -------------------------------------------------
    if topo == "series":
        base = ["40,94 40,50 320,50 320,170 40,170 40,126"]
        flows = [("M40,94 L40,50 L320,50 L320,170 L40,170 L40,126", "I_tot")]
        nodes = []
    else:
        nx = 190 if topo == "parallel" else 205
        base = ["40,94 40,50 300,50 300,170 40,170 40,126", f"{nx},50 {nx},170"]
        flows = [(f"M40,94 L40,50 L{nx},50", "I_tot"),
                 (f"M{nx},50 L300,50 L300,170 L{nx},170", "I_Rx"),
                 (f"M{nx},50 L{nx},170", "I_R1"),
                 (f"M{nx},170 L40,170 L40,126", "I_tot")]
        nodes = [(nx, 50), (nx, 170)]
    for pts in base:
        add(f'<polyline points="{pts}" fill="none" stroke="{WIRE}" stroke-width="2.4" stroke-linejoin="round"/>')
    if live and flow:
        for d, key in flows:
            add(f'<path class="flow" d="{d}" fill="none" stroke="#FFC45A" stroke-width="4" stroke-linecap="round" '
                f'stroke-dasharray="0.1 16" style="animation-duration:{_flow_dur(flow[key]):.3f}s"/>')

    # ---- switch on the return wire ----------------------------------------
    add(f'<rect x="101" y="158" width="26" height="24" fill="{BG}"/>')
    add(f'<circle cx="100" cy="170" r="2.8" fill="{TXT}"/><circle cx="128" cy="170" r="2.8" fill="{TXT}"/>')
    if live:
        add(f'<line class="sw" x1="128" y1="170" x2="100" y2="170" stroke="{TXT}" stroke-width="2.8" stroke-linecap="round"/>')
    else:
        add(f'<line x1="128" y1="170" x2="100" y2="170" stroke="{TXT}" stroke-width="2.8" '
            f'stroke-linecap="round" transform="rotate(28 128 170)"/>')
    for x, y in nodes:
        add(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{TXT}"/>')

    # ---- components ---------------------------------------------------------
    def box(x, y, label, val, vertical=False, unknown=False):
        w, h = (22, 64) if vertical else (64, 22)
        if unknown:
            fill, stroke, lab_fill, val_fill = _heat_fill(heat if live else 0), AMBER, AMBER, "#FFE3A8"
            if mode == "burn":
                fill, stroke = "#262626", RED
            if live and heat > 0.5:
                add(f'<rect class="hot" x="{x - w / 2 - 4}" y="{y - h / 2 - 4}" width="{w + 8}" height="{h + 8}" '
                    f'rx="6" fill="none" stroke="{RED}" stroke-width="3" opacity=".5"/>')
        else:
            fill, stroke, lab_fill, val_fill = "#143642", TEAL, TXT, "#BFEDE6"
        add(f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="3.5" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="2"/>')
        if vertical:
            add(_text(x - 17, y - 2, label, 14, "end", "700", lab_fill))
            add(_text(x - 17, y + 13, val, 12, "end", "400", val_fill))
        else:
            add(_text(x, y - 17, label, 14, "middle", "700", lab_fill))
            add(_text(x, y + 4.5, val, 12, "middle", "400", val_fill))
        if unknown and mode == "burn":
            for k, dx in enumerate((-6, 5, 0)):
                add(f'<circle class="smoke" cx="{x + dx}" cy="{y - h / 2 - 2}" r="6" fill="#B9C2D6" '
                    f'opacity=".35" style="animation-delay:{k * 0.5:.1f}s"/>')

    src_probe = ("40,72 82,72 82,99", "82,121 82,148 40,148", (82, 110))
    rx_val = tag
    if topo == "series":
        box(140, 50, "R1", fmt_R(R1))
        box(245, 50, "Rx", rx_val, unknown=True)
        probes = {
            "V_R1": ("108,50 108,100 129,100", "151,100 172,100 172,50", (140, 100)),
            "V_Rx": ("213,50 213,100 234,100", "256,100 277,100 277,50", (245, 100)),
            "V_src": src_probe, "I_tot": (None, None, (320, 110)),
        }
    elif topo == "parallel":
        box(190, 108, "R1", fmt_R(R1), vertical=True)
        box(300, 108, "Rx", rx_val, vertical=True, unknown=True)
        probes = {"V_src": src_probe, "I_tot": (None, None, (120, 50)),
                  "I_R1": (None, None, (190, 155)), "I_Rx": (None, None, (300, 155))}
    else:
        box(125, 50, "R2", fmt_R(R2))
        box(205, 108, "R1", fmt_R(R1), vertical=True)
        box(300, 108, "Rx", rx_val, vertical=True, unknown=True)
        probes = {
            "V_R2": ("93,50 93,100 114,100", "136,100 157,100 157,50", (125, 100)),
            "V_par": ("300,50 335,50 335,97", "335,119 335,170 300,170", (335, 108)),
            "V_src": src_probe, "I_tot": (None, None, (181, 50)),
            "I_R1": (None, None, (205, 155)), "I_Rx": (None, None, (300, 155)),
        }

    # ---- supply ---------------------------------------------------------------
    s_stroke = RED if mode == "trip" else TXT
    cls = ' class="blink"' if mode == "trip" else ""
    add(f'<circle cx="40" cy="110" r="16" fill="{BG}" stroke="{s_stroke}" stroke-width="2.4"/>')
    add(_text(40, 107, "+", 14, "middle", "700"))
    add(_text(40, 122, "−", 14, "middle", "700"))
    add(_text(12, 107, "E", 14, "middle", "700"))
    add(_text(12, 120, f"{E:g} V", 9.5, "middle", "400", MUTED))
    if mode == "trip":
        add(f'<g{cls}>' + _text(40, 146, "OCP", 10, "middle", "700", RED) + "</g>")

    # ---- meter probe ----------------------------------------------------------
    if place in probes:
        a, b, (bx, by) = probes[place]
        if a:
            for pts in (a, b):
                add(f'<polyline class="lead" points="{pts}" fill="none" stroke="{LEAD}" stroke-width="1.7" '
                    f'stroke-dasharray="4 3" stroke-linejoin="round"/>')
        add(f'<g class="badge"><circle cx="{bx}" cy="{by}" r="11" fill="{AMBER}" stroke="{BG}" stroke-width="2"/>'
            + _text(bx, by + 4.5, instr, 13, "middle", "700", NAVY) + "</g>")
    add("</g>")

    # ---- meter panel ------------------------------------------------------------
    add(f'<rect x="8" y="208" width="344" height="156" rx="11" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>')
    add(_text(20, 229, labels["probe"], 12.5, "start", "700", TXT))
    cx, cy, r = 98, 350, 84

    def pol(rad, ang):
        a = math.radians(ang)
        return cx + rad * math.sin(a), cy - rad * math.cos(a)

    x1, y1 = pol(r, -60)
    x2, y2 = pol(r, 60)
    add(f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}" fill="none" stroke="{WIRE}" stroke-width="2"/>')
    for k in range(11):
        ang = -60 + 12 * k
        xa, ya = pol(r, ang)
        xb, yb = pol(r - (11 if k % 5 == 0 else 6), ang)
        add(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="{TXT if k % 5 == 0 else WIRE}" '
            f'stroke-width="{2 if k % 5 == 0 else 1.2}"/>')
    ticks = reading["ticks"] if (live and reading) else ("0", "", "")
    for ang, lab in zip((-60, 0, 60), ticks):
        xt, yt = pol(r + 11, ang)
        add(_text(round(xt, 1), round(yt + 3, 1), lab, 10, "middle", "400", MUTED))
    unit = reading["unit"] if (live and reading) else instr
    add(_text(cx, 322, unit, 12, "middle", "700", MUTED))
    ang = -60 + 120 * min(max(reading["frac"], 0), 1) if (live and reading) else -60
    needle = (f'<line x1="0" y1="8" x2="0" y2="-74" stroke="{AMBER}" stroke-width="2.6" stroke-linecap="round"/>')
    if live and reading:
        add(f'<g transform="translate({cx},{cy})"><g class="needle" transform="rotate({ang:.1f})" '
            f'style="--a:{ang:.1f}deg">{needle}</g></g>')
    else:
        add(f'<g transform="translate({cx},{cy})"><g transform="rotate(-60)">{needle}</g></g>')
    add(f'<circle cx="{cx}" cy="{cy}" r="6.5" fill="{TXT}"/>')
    # cover the needle tail below the panel edge
    # LCD
    add(f'<rect x="198" y="222" width="146" height="50" rx="7" fill="#050B18" stroke="{LINE}" stroke-width="1.5"/>')
    if live and reading:
        add(_text(336, 256, reading["text"], 25, "end", "700", AMBER, MONO,
                  f'data-count="{reading["value"]}" data-dec="{reading["dec"]}" data-suf=" {reading["unit"]}"'))
        add(_text(198, 289, f'{labels["range"]} {reading["ticks"][2]} {reading["unit"]}', 10.5, "start", "400", MUTED))
        add(_text(344, 289, f'{labels["reading"]} {reading["n"]}', 10.5, "end", "400", MUTED))
    elif mode == "trip":
        add('<g class="blink">' + _text(336, 256, "OCP", 25, "end", "700", RED, MONO) + "</g>")
    elif mode == "burn":
        add('<g class="blink">' + _text(336, 256, "HOT", 25, "end", "700", RED, MONO) + "</g>")
    else:
        add(_text(336, 256, "– – –", 25, "end", "700", "#5B6B8C", MONO))
        add(_text(198, 289, labels["open"], 10.5, "start", "400", MUTED))
    # heat bar
    add(_text(198, 314, labels["heat"], 10.5, "start", "400", MUTED))
    lit = 5 if mode == "burn" else (math.ceil(min(heat, 1) * 5 - 1e-9) if live else 0)
    seg_cols = [TEAL, TEAL, AMBER, AMBER, RED]
    for k in range(5):
        col = seg_cols[k] if k < lit else LINE
        add(f'<rect x="{198 + k * 29.5:.1f}" y="322" width="24" height="10" rx="2.5" fill="{col}"/>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 372" preserveAspectRatio="xMidYMin meet" '
           f'role="img" aria-label="circuit bench">{"".join(p)}</svg>')
    return _page(svg)


def _star(cx, cy, r, filled, delay):
    pts = []
    for k in range(10):
        rad = r if k % 2 == 0 else r * 0.42
        a = math.radians(-90 + 36 * k)
        pts.append(f"{cx + rad * math.cos(a):.1f},{cy + rad * math.sin(a):.1f}")
    fill = AMBER if filled else "none"
    stroke = AMBER if filled else "#4A5A7E"
    cls = f'class="star" style="animation-delay:{delay:.2f}s"' if filled else ""
    return f'<polygon {cls} points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'


def stamp_html(ok, word, stars, points, pts_label):
    col = LEAD if ok else RED
    p = [f'<rect x="0.5" y="0.5" width="359" height="129" rx="14" fill="{BG}"/>']
    size = 21 if len(word) <= 8 else 18
    p.append(f'<g transform="rotate(-9 92 65)"><g class="stamp">'
             f'<rect x="18" y="37" width="148" height="56" rx="9" fill="none" stroke="{col}" stroke-width="4.5"/>'
             f'<rect x="25" y="44" width="134" height="42" rx="5" fill="none" stroke="{col}" stroke-width="1.5"/>'
             + _text(92, 72.5, word, size, "middle", "700", col, FONT, 'letter-spacing="1.5"') + "</g></g>")
    for k in range(3):
        p.append(_star(214 + k * 42, 46, 16, k < stars, 0.55 + 0.22 * k))
    p.append(_text(256, 104, f"+{points}", 30, "middle", "700", TXT, FONT,
                   f'data-count="{points}" data-pre="+"'))
    p.append(_text(256, 121, pts_label, 11, "middle", "400", MUTED))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 130" preserveAspectRatio="xMidYMin meet">'
           f'{"".join(p)}</svg>')
    return _page(svg)


def final_html(total, max_total, stars, max_stars, rank, who):
    frac = total / max_total
    c = 2 * math.pi * 62
    p = [f'<rect x="0.5" y="0.5" width="359" height="199" rx="14" fill="{BG}"/>']
    p.append(f'<circle cx="96" cy="100" r="62" fill="none" stroke="{LINE}" stroke-width="13"/>')
    p.append(f'<circle class="ring" cx="96" cy="100" r="62" fill="none" stroke="{AMBER}" stroke-width="13" '
             f'stroke-linecap="round" stroke-dasharray="{c:.1f}" stroke-dashoffset="{c * (1 - frac):.1f}" '
             f'style="--c:{c:.1f};--o:{c * (1 - frac):.1f}" transform="rotate(-90 96 100)"/>')
    p.append(_text(96, 108, str(total), 38, "middle", "700", TXT, FONT, f'data-count="{total}"'))
    p.append(_text(96, 127, f"/ {max_total}", 12, "middle", "400", MUTED))
    words, lines, cur = rank.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > 17:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    y = 78 - 11 * (len(lines) - 1)
    for ln in lines:
        p.append(_text(262, y, ln, 19, "middle", "700", AMBER, "Cambria, Georgia, serif"))
        y += 23
    p.append(_star(222, y + 8, 11, True, 1.2))
    p.append(_text(240, y + 13, f"{stars} / {max_stars}", 15, "start", "700", TXT))
    p.append(_text(262, y + 40, who, 11.5, "middle", "400", MUTED))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 200" preserveAspectRatio="xMidYMin meet">'
           f'{"".join(p)}</svg>')
    return _page(svg)


def specimen_icon(form, dims, length, sealed=False):
    """Small schematic of a specimen; stroke and size follow its real dimensions on a log scale."""
    ink = "#8C97AD" if sealed else NAVY
    p = []
    if form == "wire":
        sw = 1.2 + 2.6 * (math.log10(dims["d"] / 0.05))          # 0.05 mm -> 1.2 px, 0.5 mm -> 3.8 px
        loops = max(2, min(7, round(2 + 2.2 * math.log10(length / 0.05))))
        pitch = 52 / loops
        x0 = 40 - pitch * (loops - 1) / 2
        p.append(f'<line x1="4" y1="34" x2="{x0:.1f}" y2="34" stroke="{ink}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
        p.append(f'<line x1="{x0 + pitch * (loops - 1):.1f}" y1="34" x2="76" y2="34" stroke="{ink}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
        for k in range(loops):
            p.append(f'<ellipse cx="{x0 + k * pitch:.1f}" cy="21" rx="5.5" ry="13" fill="none" stroke="{ink}" stroke-width="{sw:.1f}"/>')
    elif form == "rod":
        h = 8 + 14 * math.log10(dims["d"] / 0.5) / math.log10(4)
        w = 30 + 34 * math.log10(length / 0.01) / math.log10(15)
        x0, y0 = (80 - w) / 2, 22 - h / 2
        p.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" '
                 f'fill="#C9CFDB" stroke="{ink}" stroke-width="1.8"/>')
        p.append(f'<ellipse cx="{x0 + w - h / 4:.1f}" cy="22" rx="{h / 4:.1f}" ry="{h / 2:.1f}" fill="#E9ECF2" '
                 f'stroke="{ink}" stroke-width="1.4"/>')
    else:
        wd = 7 + 13 * math.log10(dims["w"] / 0.2) / math.log10(25)
        ln = 30 + 34 * math.log10(length / 0.002) / math.log10(50)
        tk = 1.2 + 2.8 * math.log10(dims["t"] / 0.1) / math.log10(500)
        x0 = (80 - ln) / 2
        sk = 10
        top = f"{x0 + sk:.1f},{22 - wd / 2:.1f} {x0 + ln + sk / 2:.1f},{22 - wd / 2:.1f} {x0 + ln - sk / 2:.1f},{22 + wd / 2:.1f} {x0:.1f},{22 + wd / 2:.1f}"
        p.append(f'<polygon points="{top}" fill="#F3D9A6" stroke="{ink}" stroke-width="1.5" stroke-linejoin="round"/>')
        p.append(f'<line x1="{x0:.1f}" y1="{22 + wd / 2 + tk / 2 + 0.6:.1f}" x2="{x0 + ln - sk / 2:.1f}" '
                 f'y2="{22 + wd / 2 + tk / 2 + 0.6:.1f}" stroke="{ink}" stroke-width="{tk:.1f}"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 44" width="160" height="88">{"".join(p)}</svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
