# -*- coding: utf-8 -*-
"""
Resistor Lab / Laboratorio de Resistencias
------------------------------------------
A Streamlit game. Each batch of unknown resistance material comes as three
specimens of the same material with different geometry. The player measures
two of them in series, parallel and series-parallel circuits, finds the
resistivity, names the material and predicts the resistance of the third.

Files: app.py (game), game_art.py (animated scenes), game_text.py (EN/ES text).
Run locally:   streamlit run app.py
"""
import csv
import hashlib
import io
import math
import random

import streamlit as st

from game_art import AMBER, NAVY, TEAL, bench_html, final_html, fmt_R, specimen_icon, stamp_html
from game_text import FREE_MEAS, T

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
# Resistivity at 20 °C in ohm·metre. TCR values are typical and depend on grade.
# Edit this table to add or change materials; everything else adapts.
MATERIALS = [
    dict(key="cu", en="Copper (annealed)", es="Cobre (recocido)", comp="Cu",
         rho=1.72e-8, tcr="+3900",
         use_en="Leads, terminations and end caps",
         use_es="Terminales, conexiones y casquillos", forms=("wire", "strip")),
    dict(key="cuni2", en="CuNi2 (Alloy 30)", es="CuNi2 (Aleación 30)", comp="Cu98 Ni2",
         rho=5.0e-8, tcr="≈ +1400",
         use_en="Very low-ohm resistors, fuses, heating cables",
         use_es="Resistencias de muy bajo valor, fusibles, cables calefactores",
         forms=("wire", "strip")),
    dict(key="ni", en="Nickel", es="Níquel", comp="Ni",
         rho=6.99e-8, tcr="≈ +6000",
         use_en="Nickel RTDs, ballast and compensation resistors",
         use_es="RTD de níquel, resistencias de balasto y compensación",
         forms=("wire", "strip")),
    dict(key="pt", en="Platinum", es="Platino", comp="Pt",
         rho=1.06e-7, tcr="+3850",
         use_en="Precision RTD sensors (Pt100), thin-film thermometers",
         use_es="Sensores RTD de precisión (Pt100), termómetros de película",
         forms=("wire", "strip")),
    dict(key="zer", en="Zeranin 30", es="Zeranin 30", comp="Cu Mn7 Sn2.3",
         rho=2.9e-7, tcr="±3",
         use_en="Current-sense shunts of very low value",
         use_es="Shunts de medición de corriente de muy bajo valor",
         forms=("wire", "strip")),
    dict(key="mang", en="Manganin", es="Manganina", comp="Cu86 Mn12 Ni2",
         rho=4.3e-7, tcr="±10",
         use_en="Precision shunts and standard resistors",
         use_es="Shunts de precisión y resistencias patrón",
         forms=("wire", "strip")),
    dict(key="const", en="Constantan", es="Constantán", comp="Cu55 Ni45",
         rho=4.9e-7, tcr="±40",
         use_en="Wirewound resistors, strain gauges, thermocouples",
         use_es="Resistencias bobinadas, galgas extensiométricas, termopares",
         forms=("wire", "strip")),
    dict(key="nicr", en="Nichrome 80/20", es="Nicromo 80/20", comp="Ni80 Cr20",
         rho=1.09e-6, tcr="≈ +100",
         use_en="Wirewound and metal-film resistors, heating elements",
         use_es="Resistencias bobinadas y de película metálica, calefactores",
         forms=("wire", "strip")),
    dict(key="evan", en="Evanohm / Karma", es="Evanohm / Karma", comp="Ni75 Cr20 Al Cu",
         rho=1.33e-6, tcr="±10",
         use_en="High-value precision wirewound and foil resistors",
         use_es="Resistencias de precisión bobinadas y de lámina de alto valor",
         forms=("wire", "strip")),
    dict(key="kanth", en="Kanthal A-1 (FeCrAl)", es="Kanthal A-1 (FeCrAl)", comp="Fe72 Cr22 Al5.8",
         rho=1.45e-6, tcr="≈ +50",
         use_en="Power and braking resistors, furnace elements",
         use_es="Resistencias de potencia y de frenado, elementos de horno",
         forms=("wire", "strip")),
    dict(key="tan", en="Tantalum nitride (film)", es="Nitruro de tantalio (película)", comp="Ta2N / TaN",
         rho=2.5e-6, tcr="≈ −100",
         use_en="Thin-film chip resistors and networks",
         use_es="Resistencias chip y redes de película delgada",
         forms=("strip",)),
    dict(key="c", en="Carbon (graphite)", es="Carbono (grafito)", comp="C",
         rho=3.5e-5, tcr="≈ −500",
         use_en="Carbon-film and carbon-composition resistors",
         use_es="Resistencias de película y de composición de carbono",
         forms=("rod", "strip")),
]
MAT = {m["key"]: m for m in MATERIALS}
TWINS = ("mang", "const", "evan", "kanth")      # look-alike pairs for the final station

R_STD = [1, 2.2, 4.7, 10, 22, 47, 100, 220, 470, 1000, 2200, 4700]   # known resistors, ohm
I_LIMIT = 1.0            # supply over-current protection, A
N_ROUNDS = 5
TAGS = ("A", "B", "C")   # A and B can be mounted; C stays sealed

LEVELS = {
    "apprentice": dict(sigma=0.0015, r_int=0.0),
    "technician": dict(sigma=0.0030, r_int=0.2),
    "engineer":   dict(sigma=0.0060, r_int=0.5),
}
ROUNDS = [
    dict(topos=["series"], instr=["V", "A"]),
    dict(topos=["series"], instr=["V"]),
    dict(topos=["parallel"], instr=["A"]),
    dict(topos=["mixed"], instr=["V"]),
    dict(topos=["series", "parallel", "mixed"], instr=["V", "A"]),
]
PLACES = {
    ("V", "series"): ["V_Rx", "V_R1", "V_src"],
    ("V", "parallel"): ["V_src"],
    ("V", "mixed"): ["V_par", "V_R2", "V_src"],
    ("A", "series"): ["I_tot"],
    ("A", "parallel"): ["I_Rx", "I_R1", "I_tot"],
    ("A", "mixed"): ["I_Rx", "I_R1", "I_tot"],
}

WIRE_D = [0.05, 0.063, 0.08, 0.10, 0.125, 0.16, 0.20, 0.25, 0.315, 0.40, 0.50]   # mm
ROD_D = [0.5, 0.7, 0.9, 1.3, 2.0]                                                # mm
STRIP_T = [0.1, 0.2, 0.5, 1, 2, 5, 10, 25, 50]                                   # µm
STRIP_W = [0.2, 0.5, 1.0, 2.0, 5.0]                                              # mm
L_LIMITS = {"wire": (0.05, 25.0), "rod": (0.01, 0.15), "strip": (0.002, 0.10)}   # m
LANGS = {"English": "en", "Español": "es"}


def t(key):
    return T[st.session_state.get("lang", "en")][key]


def mat_name(key):
    return MAT[key][st.session_state.get("lang", "en")]


# --------------------------------------------------------------------------
# Physics
# --------------------------------------------------------------------------
def gen_sample(rng, mat, form, r_lo, r_hi):
    """One specimen of the given form whose resistance falls between r_lo and r_hi, or None."""
    for _ in range(300):
        target = math.exp(rng.uniform(math.log(r_lo), math.log(r_hi)))
        if form in ("wire", "rod"):
            d = rng.choice(WIRE_D if form == "wire" else ROD_D)
            area = math.pi * (d * 1e-3) ** 2 / 4
            dims = {"d": d}
        else:
            tk, w = rng.choice(STRIP_T), rng.choice(STRIP_W)
            area = (w * 1e-3) * (tk * 1e-6)
            dims = {"w": w, "t": tk}
        length = target * area / mat["rho"]
        lo, hi = L_LIMITS[form]
        if lo <= length <= hi:
            length = float(f"{length:.3g}")
            return dict(form=form, dims=dims, area=area, L=length, R=mat["rho"] * length / area)
    return None


def gen_batch(rng, mat):
    """Three specimens of one material: different cross-sections, clearly different resistances."""
    forms = list(mat["forms"])
    for _ in range(500):
        picks = [rng.choice(forms) for _ in TAGS]
        if len(forms) > 1 and len(set(picks)) == 1:
            continue                                   # show at least two shapes when the material allows
        specs = [gen_sample(rng, mat, picks[0], 4, 600), gen_sample(rng, mat, picks[1], 4, 600),
                 gen_sample(rng, mat, picks[2], 1, 3000)]
        if any(s is None for s in specs):
            continue
        sections = {(s["form"], tuple(sorted(s["dims"].items()))) for s in specs}
        ratio = max(specs[0]["R"], specs[1]["R"]) / min(specs[0]["R"], specs[1]["R"])
        apart = all(abs(math.log(specs[2]["R"] / s["R"])) > 0.25 for s in specs[:2])
        if len(sections) == 3 and ratio >= 1.6 and apart:
            return dict(id=f"{rng.choice('ABCDEFGHJK')}{rng.randint(100, 999)}",
                        pmax=rng.choice([0.25, 0.5, 1.0]), specs=dict(zip(TAGS, specs)))
    raise RuntimeError("no valid batch for " + mat["key"])


def solve(topo, E, r, R1, R2, Rx):
    """Every voltage and current in the chosen circuit (r is the supply's internal resistance)."""
    if topo == "series":
        i = E / (r + R1 + Rx)
        q = dict(I_tot=i, I_R1=i, I_Rx=i, V_R1=i * R1, V_Rx=i * Rx, V_src=E - i * r)
    elif topo == "parallel":
        rp = R1 * Rx / (R1 + Rx)
        i = E / (r + rp)
        v = i * rp
        q = dict(I_tot=i, I_R1=v / R1, I_Rx=v / Rx, V_src=v)
    else:  # R2 in series with (R1 parallel Rx)
        rp = R1 * Rx / (R1 + Rx)
        i = E / (r + R2 + rp)
        v = i * rp
        q = dict(I_tot=i, I_R1=v / R1, I_Rx=v / Rx, V_R2=i * R2, V_par=v, V_src=E - i * r)
    q["P_x"] = q["I_Rx"] ** 2 * Rx
    return q


def read_meter(rng, true, kind, sigma):
    """Auto-ranging 3½-digit meter: gain noise plus resolution."""
    if kind == "V":
        ranges = [(0.2, "mV", 1e3, 1), (2.0, "V", 1, 3), (20.0, "V", 1, 2)]
    else:
        ranges = [(0.002, "mA", 1e3, 3), (0.02, "mA", 1e3, 2), (0.2, "mA", 1e3, 1), (2.0, "A", 1, 3)]
    noisy = true * (1 + rng.gauss(0, sigma))
    for full, unit, mult, dec in ranges:
        if abs(noisy) < full * 0.9995 or full == ranges[-1][0]:
            res = full / 2000
            val = round((noisy + rng.gauss(0, 0.4 * res)) / res) * res
            return dict(si=val, value=val * mult, dec=dec, unit=unit, text=f"{val * mult:.{dec}f} {unit}",
                        frac=abs(val) / full, ticks=("0", f"{full * mult / 2:g}", f"{full * mult:g}"))


def fmt_len(m):
    return f"{m:g} m" if m >= 1 else f"{m * 1000:g} mm"


def score_round(batch, mat, ans_rho_u, guess, ans_pred, n_meas, hint, burned):
    r_c = batch["specs"]["C"]["R"]
    e_rho = abs(ans_rho_u * 1e-6 - mat["rho"]) / mat["rho"]
    e_pred = abs(ans_pred - r_c) / r_c
    pts = dict(
        material=40 if guess == mat["key"] else 0,
        rho=30 if e_rho <= 0.03 else 15 if e_rho <= 0.08 else 0,
        pred=30 if e_pred <= 0.03 else 15 if e_pred <= 0.08 else 0,
        meas=-2 * max(0, n_meas - FREE_MEAS),
        hint=-10 if hint else 0,
        burn=-15 * burned,
    )
    total = max(0, sum(pts.values()))
    stars = 3 if total >= 90 else 2 if total >= 65 else 1 if total >= 40 else 0
    return pts, total, stars, e_rho, e_pred


def verification_code(name, level, total):
    try:
        secret = st.secrets["GAME_SECRET"]
    except Exception:
        secret = "ohm-lab-default"
    raw = f"{name.strip().lower()}|{level}|{int(total)}|{secret}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8].upper()


# --------------------------------------------------------------------------
# Game state
# --------------------------------------------------------------------------
def reset_round():
    s = st.session_state
    s.log, s.hint, s.burned, s.last = [], False, 0, None


def start_game():
    s = st.session_state
    rng = random.Random()
    final = rng.choice(TWINS)
    others = rng.sample([m["key"] for m in MATERIALS if m["key"] != final], N_ROUNDS - 1)
    s.rng = rng
    s.mats = others + [final]
    s.batches = [gen_batch(rng, MAT[k]) for k in s.mats]
    s.round, s.results, s.game_id = 0, [], rng.randint(0, 10 ** 9)
    s.player = (s.get("name_input") or "").strip() or "Anon"
    reset_round()
    s.phase = "play"


def to_start():
    st.session_state.phase = "start"


def next_round():
    s = st.session_state
    if s.round + 1 >= N_ROUNDS:
        s.phase = "end"
    else:
        s.round += 1
        reset_round()
        s.phase = "play"


def take_reading(tag, topo, E, R1, R2, place):
    s = st.session_state
    batch = s.batches[s.round]
    lv = LEVELS[s.level]
    instr = place[0] if place[0] == "V" else "A"
    q = solve(topo, E, lv["r_int"], R1, R2, batch["specs"][tag]["R"])
    entry = dict(tag=tag, topo=topo, E=E, R1=R1, R2=R2 if topo == "mixed" else None, instr=instr,
                 place=place, status="ok", sig=(tag, topo, E, R1, R2, place), n=len(s.log) + 1,
                 flow={k: q[k] for k in ("I_tot", "I_R1", "I_Rx")}, heat=q["P_x"] / batch["pmax"])
    if q["I_tot"] > I_LIMIT:
        entry["status"] = "trip"
    elif q["P_x"] > batch["pmax"]:
        entry["status"] = "burn"
        entry["p"] = q["P_x"]
        s.burned += 1
    else:
        entry["reading"] = read_meter(s.rng, q[place], instr, lv["sigma"])
    s.log.append(entry)
    s.last = entry


def show_hint():
    st.session_state.hint = True


def set_lang(widget_key):
    st.session_state.lang = LANGS[st.session_state[widget_key]]


# --------------------------------------------------------------------------
# Interface pieces
# --------------------------------------------------------------------------
CSS = f"""
<style>
.stApp p, .stApp li, .stApp label, .stApp input, .stApp button p, .stApp [data-testid="stCaptionContainer"] {{
    font-family: Calibri, 'Segoe UI', Roboto, Arial, sans-serif; }}
h1, h2, h3 {{ font-family: Cambria, Georgia, 'Times New Roman', serif !important; color: {NAVY}; letter-spacing: 0; }}
.block-container {{ padding-top: 3.4rem; max-width: 720px; }}
.stButton button, .stDownloadButton button, .stFormSubmitButton button {{ min-height: 3.1rem; }}
.stButton button p, .stFormSubmitButton button p {{ font-weight: 700; font-size: 1.02rem; }}
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {{ box-shadow: 0 3px 0 #1c6f66; }}
.stButton button[kind="primary"]:active {{ transform: translateY(2px); box-shadow: 0 1px 0 #1c6f66; }}
.rl-hud {{ display: flex; align-items: center; gap: .8rem; margin-bottom: .7rem; }}
.rl-line {{ display: flex; align-items: center; flex: 1; }}
.rl-node {{ width: 30px; height: 30px; border-radius: 50%; border: 2.5px solid #C4CEDA; color: #8C97AD;
           display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .9rem;
           background: #fff; flex: none; position: relative; }}
.rl-node.done {{ background: {TEAL}; border-color: {TEAL}; color: #fff; }}
.rl-node.now {{ border-color: {AMBER}; color: {NAVY}; animation: rl-pulse 1.6s ease-out infinite; }}
.rl-node small {{ position: absolute; top: 30px; font-size: .58rem; color: {AMBER}; letter-spacing: -1px; white-space: nowrap; }}
.rl-bar {{ flex: 1; height: 3px; background: #C4CEDA; }}
.rl-bar.done {{ background: {TEAL}; }}
.rl-score {{ font-family: Cambria, Georgia, serif; color: {NAVY}; text-align: right; line-height: 1.05; }}
.rl-score b {{ font-size: 1.55rem; display: block; }}
.rl-score span {{ font-size: .78rem; opacity: .7; }}
@keyframes rl-pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(232,163,61,.65); }} 100% {{ box-shadow: 0 0 0 11px rgba(232,163,61,0); }} }}
.rl-mission {{ border-left: 5px solid {AMBER}; padding: .1rem 0 .1rem .85rem; margin: 1.1rem 0 .9rem 0; }}
.rl-mission h3 {{ margin: 0 0 .15rem 0; padding: 0; font-size: 1.3rem; }}
.rl-mission p {{ margin: 0; }}
.rl-tray {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .45rem; margin: .2rem 0 .5rem 0; }}
.rl-spec {{ border: 2px solid #D5DEE2; border-radius: 12px; padding: .4rem .35rem .45rem; text-align: center;
           background: #fff; color: {NAVY}; transition: transform .2s ease, border-color .2s ease; }}
.rl-spec img {{ width: 100%; max-width: 110px; height: auto; display: block; margin: 0 auto; }}
.rl-spec .rl-tag {{ font-family: Cambria, Georgia, serif; font-size: 1.25rem; font-weight: 700; line-height: 1.1; }}
.rl-spec .rl-form {{ font-size: .8rem; opacity: .75; }}
.rl-spec .rl-dim {{ font-size: .86rem; font-weight: 700; line-height: 1.25; }}
.rl-spec .rl-state {{ font-size: .7rem; margin-top: .25rem; border-radius: 99px; padding: .05rem .4rem; display: inline-block; }}
.rl-spec.sel {{ border-color: {TEAL}; background: #EAF6F4; transform: translateY(-3px); animation: rl-mount .35s ease-out; }}
.rl-spec.sel .rl-state {{ background: {TEAL}; color: #fff; }}
.rl-spec.sealed {{ border-style: dashed; background: repeating-linear-gradient(135deg, #F6F7F9 0 8px, #ECEFF3 8px 16px); }}
.rl-spec.sealed .rl-state {{ background: {NAVY}; color: #fff; }}
@keyframes rl-mount {{ from {{ transform: translateY(6px) scale(.96); }} to {{ transform: translateY(-3px) scale(1); }} }}
.rl-batch {{ font-size: .9rem; color: {NAVY}; opacity: .85; margin-bottom: .15rem; }}
.rl-code {{ font-family: 'Courier New', ui-monospace, monospace; font-size: 1.6rem; font-weight: 700;
           color: {TEAL}; letter-spacing: .12em; }}
@media (prefers-reduced-motion: reduce) {{ .rl-node.now, .rl-spec.sel {{ animation: none; }} }}
</style>
"""


def _wide(fn, *args, **kwargs):
    """Full-width button on any Streamlit version (width="stretch" replaced use_container_width)."""
    try:
        return fn(*args, width="stretch", **kwargs)
    except TypeError:
        return fn(*args, use_container_width=True, **kwargs)


def button(*args, **kwargs):
    return _wide(st.button, *args, **kwargs)


def embed(html, height):
    """Animated scene in an iframe (st.iframe on current Streamlit, components.html on older ones)."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=height)


def bench_labels(place):
    return dict(probe=t("p_" + place), range=t("range"), reading=t("reading"), open=t("open"), heat=t("heat"))


def hud():
    s = st.session_state
    total = sum(r["total"] for r in s.results)
    parts = []
    for i in range(N_ROUNDS):
        if i < len(s.results):
            stars = "★" * s.results[i]["stars"]
            parts.append(f'<div class="rl-node done">{i + 1}<small>{stars}</small></div>')
        elif i == s.round:
            parts.append(f'<div class="rl-node now">{i + 1}</div>')
        else:
            parts.append(f'<div class="rl-node">{i + 1}</div>')
        if i < N_ROUNDS - 1:
            parts.append(f'<div class="rl-bar{" done" if i < len(s.results) else ""}"></div>')
    st.markdown(f'<div class="rl-hud"><div class="rl-line">{"".join(parts)}</div>'
                f'<div class="rl-score"><span>{t("score")}</span><b>{total}</b></div></div>',
                unsafe_allow_html=True)


def dims_lines(spec):
    d = spec["dims"]
    if spec["form"] in ("wire", "rod"):
        return [f"⌀ {d['d']:g} mm", f"L {fmt_len(spec['L'])}"]
    return [f"w {d['w']:g} mm", f"t {d['t']:g} µm", f"L {fmt_len(spec['L'])}"]


def tray(batch, mounted):
    cards = []
    for tag in TAGS:
        sp = batch["specs"][tag]
        sealed = tag == "C"
        cls = "rl-spec" + (" sealed" if sealed else " sel" if tag == mounted else "")
        state = f'🔒 {t("sealed")}' if sealed else t("on_bench") if tag == mounted else "&nbsp;"
        cards.append(
            f'<div class="{cls}"><div class="rl-tag">{tag}</div>'
            f'<img alt="{sp["form"]}" src="{specimen_icon(sp["form"], sp["dims"], sp["L"], sealed)}"/>'
            f'<div class="rl-form">{t("f_" + sp["form"])}</div>'
            f'<div class="rl-dim">{"<br>".join(dims_lines(sp))}</div>'
            f'<div class="rl-state">{state}</div></div>')
    st.markdown(f'<div class="rl-batch">{t("batch")} <b>{batch["id"]}</b>, {t("pmax")} '
                f'<b>{batch["pmax"]:g} W</b></div><div class="rl-tray">{"".join(cards)}</div>',
                unsafe_allow_html=True)


def reference_table():
    lang = st.session_state.lang
    st.dataframe([{
        t("rc_mat"): m[lang], t("rc_rho"): f"{m['rho'] * 1e6:.4g}", t("rc_comp"): m["comp"],
        t("rc_tcr"): m["tcr"], t("rc_use"): m["use_" + lang],
    } for m in MATERIALS], hide_index=True)
    st.caption(t("ref_note"))


def circuit_label(e):
    parts = [t(e["topo"]), f"E={e['E']:g} V", f"R1={fmt_R(e['R1'])}"]
    if e["R2"]:
        parts.append(f"R2={fmt_R(e['R2'])}")
    return ", ".join(parts)


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def page_start():
    s = st.session_state
    names = list(LANGS)
    st.radio(t("language"), names, index=names.index("English" if s.lang == "en" else "Español"),
             horizontal=True, key="lang_start", on_change=set_lang, args=("lang_start",))
    st.title(t("title"))
    st.markdown(f"**{t('tagline')}**")
    demo = dict(text="1.482 V", value=1.482, dec=3, unit="V", frac=0.741, ticks=("0", "1", "2"), n=1)
    embed(bench_html("mixed", 6, 220, 100, "A", "V", "V_par", bench_labels("V_par"), mode="live",
                     flow=dict(I_tot=0.03, I_R1=0.007, I_Rx=0.023), heat=0.35, reading=demo), 384)
    st.markdown(t("intro"))
    st.text_input(t("name"), key="name_input", max_chars=40)
    st.radio(t("level"), list(LEVELS), key="level", format_func=lambda k: t("lv_" + k), horizontal=True)
    st.caption(t("lvd_" + s.level))
    button(t("start"), type="primary", on_click=start_game)
    with st.expander(t("rules_title")):
        st.markdown(t("rules"))
    with st.expander(t("tab_data")):
        reference_table()
    with st.expander(t("instructor")):
        v_name = st.text_input(t("name"), key="v_name")
        v_level = st.selectbox(t("level"), list(LEVELS), key="v_level", format_func=lambda k: t("lv_" + k))
        v_score = st.number_input(t("v_score"), min_value=0, max_value=100 * N_ROUNDS, step=1, key="v_score")
        v_code = st.text_input(t("v_code"), key="v_code")
        if v_name and v_code:
            if verification_code(v_name, v_level, v_score) == v_code.strip().upper():
                st.success(t("v_ok"))
            else:
                st.error(t("v_bad"))


def page_play():
    s = st.session_state
    rd = s.round
    spec = ROUNDS[rd]
    batch = s.batches[rd]
    k = f"{s.game_id}_{rd}"
    hud()
    st.markdown(f'<div class="rl-mission"><h3>{t("station")} {rd + 1}: {t("m_title")[rd]}</h3>'
                f'<p>{t("m_desc")[rd]}</p></div>', unsafe_allow_html=True)
    tab_bench, tab_book, tab_data, tab_report = st.tabs(
        [t("tab_bench"), t("tab_notebook"), t("tab_data"), t("tab_report")])

    # ---- bench -------------------------------------------------------------
    with tab_bench:
        tag = st.segmented_control(t("mount"), ["A", "B"], default="A", key=f"tag_{k}") or "A"
        tray(batch, tag)
        if len(spec["topos"]) > 1:
            topo = st.segmented_control(t("topology"), spec["topos"], default=spec["topos"][0],
                                        key=f"topo_{k}", format_func=t) or spec["topos"][0]
        else:
            topo = spec["topos"][0]
        E = st.slider(t("supply"), 0.5, 12.0, 3.0, 0.5, key=f"E_{k}")
        R1 = st.select_slider(f"{t('r_known')} R1", R_STD, value=100, key=f"R1_{k}", format_func=fmt_R)
        R2 = None
        if topo == "mixed":
            R2 = st.select_slider(f"{t('r_known')} R2", R_STD, value=100, key=f"R2_{k}", format_func=fmt_R)
        places = [p for i in spec["instr"] for p in PLACES[(i, topo)]]
        place = st.pills(t("probe"), places, default=places[0], key=f"place_{k}_{topo}",
                         format_func=lambda p: t("p_" + p)) or places[0]
        instr = "V" if place[0] == "V" else "A"

        last = s.last
        same = last is not None and last["sig"] == (tag, topo, E, R1, R2, place)
        if same and last["status"] == "ok":
            reading = dict(last["reading"], n=last["n"])
            scene = bench_html(topo, E, R1, R2, tag, instr, place, bench_labels(place), mode="live",
                               flow=last["flow"], heat=last["heat"], reading=reading)
        else:
            mode = last["status"] if same else "idle"
            scene = bench_html(topo, E, R1, R2, tag, instr, place, bench_labels(place), mode=mode)
        scene += f"<!-- reading {last['n'] if same else 0} -->"      # new reading -> the needle swings again
        embed(scene, 384)
        button(t("measure"), type="primary", on_click=take_reading, args=(tag, topo, E, R1, R2, place))
        if same and last["status"] == "trip":
            st.error(t("trip"))
        elif same and last["status"] == "burn":
            st.error(t("burn").format(tag=last["tag"], p=last["p"], pm=f"{batch['pmax']:g}"))
        elif LEVELS[s.level]["r_int"] > 0:
            st.caption(t("sag_note"))

    # ---- notebook ----------------------------------------------------------
    with tab_book:
        if s.log:
            rows = []
            for e in s.log:
                reading = e["reading"]["text"] if e["status"] == "ok" else "⚠ " + t("st_" + e["status"])
                rows.append({t("c_n"): e["n"], t("c_spec"): e["tag"], t("c_read"): reading,
                             t("c_meter"): t("p_" + e["place"]), t("c_circ"): circuit_label(e)})
            st.dataframe(rows, hide_index=True)
            st.caption(t("meas_count").format(n=len(s.log), f=FREE_MEAS))
        else:
            st.caption(t("nb_empty"))
        tray(batch, None)
        with st.expander(t("method")):
            if s.hint:
                st.markdown(t("hint")[rd])
                st.markdown(t("hint_common"))
            else:
                button(t("method_btn"), on_click=show_hint)

    with tab_data:
        reference_table()

    # ---- report ------------------------------------------------------------
    with tab_report:
        sp_c = batch["specs"]["C"]
        st.markdown(f"**C**: {t('f_' + sp_c['form'])}, {', '.join(dims_lines(sp_c))}")
        with st.form(f"report_{k}"):
            a_rho = st.number_input(t("a_rho"), min_value=0.0, value=None, format="%.4f", key=f"arho_{k}")
            a_mat = st.selectbox(t("a_mat"), [""] + [m["key"] for m in MATERIALS], key=f"amat_{k}",
                                 format_func=lambda x: mat_name(x) if x else t("choose"))
            a_pred = st.number_input(t("a_pred"), min_value=0.0, value=None, format="%.3f", key=f"apred_{k}")
            sent = _wide(st.form_submit_button, t("check"), type="primary")
        if sent:
            if not a_rho or not a_mat or not a_pred:
                st.warning(t("need_all"))
            else:
                mat = MAT[s.mats[rd]]
                pts, tot, stars, e_rho, e_pred = score_round(batch, mat, a_rho, a_mat, a_pred,
                                                             len(s.log), s.hint, s.burned)
                s.results.append(dict(batch=batch["id"], true=mat["key"], guess=a_mat, rho_ans=a_rho,
                                      pred_ans=a_pred, e_rho=e_rho, e_pred=e_pred, pts=pts, total=tot,
                                      stars=stars, n_meas=len(s.log)))
                s.phase = "result"
                st.rerun()
        st.divider()
        button(t("quit"), on_click=to_start)


def page_result():
    s = st.session_state
    rd = s.round
    res, batch = s.results[rd], s.batches[rd]
    mat = MAT[res["true"]]
    lang = s.lang
    ok = res["guess"] == res["true"]
    hud()
    st.write("")
    embed(stamp_html(ok, t("approved") if ok else t("rejected"), res["stars"], res["total"], t("pts")), 140)
    if ok:
        st.success(t("correct").format(m=mat[lang]))
    else:
        st.error(t("wrong").format(m=mat[lang], g=mat_name(res["guess"])))
    st.markdown(f"**{mat[lang]}** ({mat['comp']}): {mat['use_' + lang]}. TCR {mat['tcr']} ppm/K.")
    r_c = batch["specs"]["C"]["R"]
    st.dataframe([
        {t("quantity"): t("q_rho"), t("yours"): f"{res['rho_ans']:.4g}", t("true"): f"{mat['rho'] * 1e6:.4g}",
         t("err"): f"{res['e_rho'] * 100:.1f} %"},
        {t("quantity"): t("q_pred"), t("yours"): f"{res['pred_ans']:.4g}", t("true"): f"{r_c:.4g}",
         t("err"): f"{res['e_pred'] * 100:.1f} %"},
    ], hide_index=True)
    p = res["pts"]
    rows = [{t("points"): t("pt_" + key), " ": f"{p[key]:+d}"}
            for key in ("material", "rho", "pred", "meas", "hint", "burn")
            if p[key] or key in ("material", "rho", "pred")]
    rows.append({t("points"): t("pt_total"), " ": str(res["total"])})
    st.dataframe(rows, hide_index=True)
    with st.expander(t("solution"), expanded=True):
        st.dataframe([{
            t("s_spec"): tag, t("s_R"): f"{sp['R']:.4g}", t("s_area"): f"{sp['area'] * 1e6:.4g}",
            t("s_geo"): f"{t('f_' + sp['form'])}, {', '.join(dims_lines(sp))}",
        } for tag, sp in batch["specs"].items()], hide_index=True)
        st.caption(t("s_note").format(rho=f"{mat['rho'] * 1e6:.4g}"))
    button(t("finish") if rd + 1 >= N_ROUNDS else t("next"), type="primary", on_click=next_round)


def page_end():
    s = st.session_state
    lang = s.lang
    total = sum(r["total"] for r in s.results)
    stars = sum(r["stars"] for r in s.results)
    frac = total / (100 * N_ROUNDS)
    rank = t("rank")[0 if frac >= 0.9 else 1 if frac >= 0.7 else 2 if frac >= 0.5 else 3]
    code = verification_code(s.player, s.level, total)
    st.title(t("final"))
    embed(final_html(total, 100 * N_ROUNDS, stars, 3 * N_ROUNDS, rank,
                     f"{s.player}, {t('lv_' + s.level).lower()}"), 216)
    st.dataframe([{
        t("h_station"): i + 1, t("h_pts"): r["total"], t("h_stars"): "★" * r["stars"],
        t("h_true"): MAT[r["true"]][lang], t("h_guess"): MAT[r["guess"]][lang], t("h_batch"): r["batch"],
    } for i, r in enumerate(s.results)], hide_index=True)
    st.markdown(f'{t("code")}: <span class="rl-code">{code}</span>', unsafe_allow_html=True)
    st.caption(t("code_note"))

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["player", s.player]); w.writerow(["level", s.level])
    w.writerow(["total", total]); w.writerow(["stars", stars]); w.writerow(["code", code]); w.writerow([])
    w.writerow(["station", "batch", "material_true", "material_reported", "rho_true_uohm_m",
                "rho_reported_uohm_m", "R_C_true_ohm", "R_C_predicted_ohm", "readings", "stars", "points"])
    for i, r in enumerate(s.results):
        w.writerow([i + 1, r["batch"], MAT[r["true"]]["en"], MAT[r["guess"]]["en"],
                    f"{MAT[r['true']]['rho'] * 1e6:.5g}", f"{r['rho_ans']:.5g}",
                    f"{s.batches[i]['specs']['C']['R']:.5g}", f"{r['pred_ans']:.5g}",
                    r["n_meas"], r["stars"], r["total"]])
    _wide(st.download_button, t("download"), buf.getvalue().encode("utf-8-sig"),
                       file_name=f"resistor_lab_{code}.csv", mime="text/csv")
    button(t("again"), type="primary", on_click=to_start)


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Resistor Lab", page_icon="🔌", layout="centered")
    s = st.session_state
    s.setdefault("lang", "en")
    s.setdefault("phase", "start")
    s.setdefault("level", "apprentice")
    s.level = s.level        # keep the choice alive after its widget leaves the page
    st.markdown(CSS, unsafe_allow_html=True)
    if s.phase != "start":
        names = list(LANGS)
        with st.sidebar:
            st.selectbox(t("language"), names, index=names.index("English" if s.lang == "en" else "Español"),
                         key="lang_side", on_change=set_lang, args=("lang_side",))
    {"start": page_start, "play": page_play, "result": page_result, "end": page_end}[s.phase]()


main()
