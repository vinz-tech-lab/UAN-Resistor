# -*- coding: utf-8 -*-
"""All on-screen text for Resistor Lab, in English and Spanish."""

FREE_MEAS = 6

T = {
    "en": {
        "title": "Resistor Lab",
        "tagline": "One alloy, three shapes. Measure two, name the material, predict the third.",
        "intro": (
            "Five batches of unlabelled resistance material arrive at your bench. Each batch is cut "
            "into **three specimens of the same material with different geometry**. Mount A or B in "
            "a series, parallel or series-parallel circuit, read the meters, and find the "
            "resistivity **ρ = R·A / L**. Then name the material and predict the resistance of "
            "specimen C, which stays sealed."
        ),
        "rules_title": "How scoring works",
        "rules": (
            "- Right material: **40** points\n"
            "- Resistivity within 3 %: **30** (within 8 %: 15)\n"
            "- Predicted resistance of C within 3 %: **30** (within 8 %: 15)\n"
            f"- The first {FREE_MEAS} readings at a station are free, then **−2** each\n"
            "- Showing the method: **−10**\n"
            "- Overheating a specimen: **−15**\n\n"
            "Three stars need 90 points. Meters have limited digits and some noise: a known "
            "resistor close to the specimen's own resistance gives the best readings, and "
            "measuring both A and B lets you average ρ."
        ),
        "name": "Your name",
        "level": "Level",
        "lv_apprentice": "Apprentice", "lv_technician": "Technician", "lv_engineer": "Engineer",
        "lvd_apprentice": "Meters ±0.15 %, ideal power supply.",
        "lvd_technician": "Meters ±0.3 %. The supply sags under load, so the dial is only nominal.",
        "lvd_engineer": "Meters ±0.6 %. The supply sags noticeably. Repeat and average.",
        "start": "Start the shift",
        "language": "Language",
        "station": "Station", "score": "Score",
        "m_title": ["Ohm's law bench", "Voltage divider", "Current divider",
                    "Series-parallel network", "Final inspection"],
        "m_desc": [
            "The specimen Rx is in series with a known resistor R1. You have a voltmeter and an ammeter.",
            "Series circuit, voltmeter only. The ammeter is away for calibration.",
            "Parallel circuit, ammeter only. Compare the branch currents.",
            "Rx is in parallel with R1, and that pair is in series with R2. Voltmeter only.",
            "Two alloys on this line differ in resistivity by about 10 %. Any circuit, both meters. "
            "Choose the method and the known resistors with care.",
        ],
        "hint": [
            "Same current through everything in series: **Rx = V(Rx) / I**.",
            "The current is common, so voltages split in proportion to resistance: "
            "**Rx = R1 · V(Rx) / V(R1)**.",
            "The voltage is common, so currents split inversely to resistance: "
            "**Rx = R1 · I(R1) / I(Rx)**.",
            "First the pair: **Rp = R2 · V(pair) / V(R2)**. Then undo the parallel: "
            "**Rx = Rp · R1 / (R1 − Rp)**. Keep R1 well above Rp or the subtraction amplifies the error.",
            "Use a ratio method (stations 2 or 3) with R1 close to Rx so both readings fall in the "
            "same meter range, repeat the readings, and use both specimens.",
        ],
        "hint_common": (
            "Then **ρ = R · A / L**, with A = π·d²/4 for a wire or rod and A = w·t for a strip. "
            "With A in mm² and L in m, ρ comes out in Ω·mm²/m, the same number as µΩ·m.\n\n"
            "A and B have different resistances but must give the **same ρ**: average the two. "
            "For the sealed specimen, **R(C) = ρ · L(C) / A(C)**."
        ),
        "batch": "Batch", "pmax": "max. power per specimen",
        "sealed": "sealed", "on_bench": "on the bench",
        "mount": "Specimen on the bench",
        "topology": "Circuit",
        "series": "Series", "parallel": "Parallel", "mixed": "Series-parallel",
        "supply": "Supply dial E (V)", "r_known": "Known resistor",
        "sag_note": "The supply has internal resistance: its terminal voltage drops under load.",
        "probe": "Meter and where it goes",
        "p_V_Rx": "V on Rx", "p_V_R1": "V on R1", "p_V_R2": "V on R2", "p_V_par": "V on R1∥Rx",
        "p_V_src": "V on supply", "p_I_tot": "A total", "p_I_R1": "A in R1", "p_I_Rx": "A in Rx",
        "measure": "Close the switch and read",
        "open": "switch open", "range": "range", "heat": "Specimen heat", "reading": "reading",
        "trip": "Supply tripped: the circuit draws more than 1 A. Lower E or raise the known resistors.",
        "burn": "Specimen {tag} overheated: it would dissipate {p:.2f} W, above the {pm} W limit. "
                "A fresh piece is mounted (−15). Lower E or add resistance in series.",
        "tab_bench": "Bench", "tab_notebook": "Notebook", "tab_data": "Data sheet", "tab_report": "Report",
        "nb_empty": "Your readings will be listed here. Take the first one on the Bench tab.",
        "c_n": "#", "c_spec": "Specimen", "c_circ": "Circuit", "c_meter": "Meter", "c_read": "Reading",
        "st_trip": "tripped", "st_burn": "overheated",
        "meas_count": "Readings taken: {n} ({f} free)",
        "method": "Stuck? Show the method",
        "method_btn": "Show the method (−10 points)",
        "ref_note": "Resistivity at 20 °C. 1 µΩ·m = 1 Ω·mm²/m = 10⁻⁶ Ω·m. TCR values are typical.",
        "rc_mat": "Material", "rc_comp": "Composition", "rc_rho": "ρ (µΩ·m)",
        "rc_tcr": "TCR (ppm/K)", "rc_use": "Typical use",
        "a_rho": "Resistivity ρ of the batch (µΩ·m)",
        "a_mat": "Material",
        "a_pred": "Predicted resistance of sealed specimen C (Ω)",
        "choose": "Choose…",
        "check": "Check my report",
        "need_all": "Enter ρ, a material and your prediction for C before checking.",
        "approved": "APPROVED", "rejected": "REJECTED", "pts": "points",
        "correct": "Correct: the batch is {m}.",
        "wrong": "Not this time. The batch is {m}; you reported {g}.",
        "yours": "Yours", "true": "Actual", "err": "Error", "quantity": "Quantity",
        "q_rho": "ρ (µΩ·m)", "q_pred": "R of specimen C (Ω)",
        "points": "Points", "pt_material": "Material", "pt_rho": "Resistivity",
        "pt_pred": "Prediction for C", "pt_meas": "Extra readings", "pt_hint": "Method shown",
        "pt_burn": "Overheated specimens", "pt_total": "Station total",
        "solution": "Same material, three geometries: the worked numbers",
        "s_spec": "Specimen", "s_geo": "Geometry", "s_area": "A (mm²)", "s_R": "R (Ω)",
        "s_note": "Every specimen gives ρ = R·A/L = {rho} µΩ·m. Resistance belongs to the piece; "
                  "resistivity belongs to the material.",
        "next": "Go to the next station", "finish": "See the final result",
        "final": "Shift complete",
        "rank": ["Chief metrologist", "Senior QC engineer", "Lab technician", "Trainee"],
        "code": "Verification code",
        "code_note": "Send your name, level, score and this code to your instructor.",
        "download": "Download my lab report (CSV)",
        "again": "Play again", "quit": "Restart the game",
        "instructor": "For the instructor: verify a code",
        "v_score": "Score", "v_code": "Code", "v_ok": "Valid code.", "v_bad": "This code does not match.",
        "h_station": "Station", "h_batch": "Batch", "h_true": "Material", "h_guess": "Reported",
        "h_pts": "Points", "h_stars": "Stars",
        "f_wire": "wire", "f_rod": "rod", "f_strip": "strip",
    },
    "es": {
        "title": "Laboratorio de Resistencias",
        "tagline": "Una aleación, tres formas. Mide dos, identifica el material y predice la tercera.",
        "intro": (
            "Llegan a tu banco cinco lotes de material resistivo sin etiqueta. Cada lote viene cortado en "
            "**tres probetas del mismo material con geometría distinta**. Monta A o B en un circuito en "
            "serie, paralelo o mixto, lee los medidores y halla la resistividad **ρ = R·A / L**. Después "
            "identifica el material y predice la resistencia de la probeta C, que permanece sellada."
        ),
        "rules_title": "Cómo se puntúa",
        "rules": (
            "- Material correcto: **40** puntos\n"
            "- Resistividad dentro del 3 %: **30** (dentro del 8 %: 15)\n"
            "- Resistencia predicha de C dentro del 3 %: **30** (dentro del 8 %: 15)\n"
            f"- Las primeras {FREE_MEAS} lecturas de cada estación son gratis; después **−2** cada una\n"
            "- Mostrar el método: **−10**\n"
            "- Sobrecalentar una probeta: **−15**\n\n"
            "Tres estrellas exigen 90 puntos. Los medidores tienen dígitos limitados y algo de ruido: "
            "una resistencia conocida cercana a la de la probeta da las mejores lecturas, y medir A y B "
            "permite promediar ρ."
        ),
        "name": "Tu nombre",
        "level": "Nivel",
        "lv_apprentice": "Aprendiz", "lv_technician": "Técnico", "lv_engineer": "Ingeniero",
        "lvd_apprentice": "Medidores ±0,15 %, fuente ideal.",
        "lvd_technician": "Medidores ±0,3 %. La fuente cae bajo carga: el dial es solo nominal.",
        "lvd_engineer": "Medidores ±0,6 %. La fuente cae notablemente. Repite y promedia.",
        "start": "Iniciar el turno",
        "language": "Idioma",
        "station": "Estación", "score": "Puntaje",
        "m_title": ["Banco de la ley de Ohm", "Divisor de voltaje", "Divisor de corriente",
                    "Red serie-paralelo", "Inspección final"],
        "m_desc": [
            "La probeta Rx está en serie con una resistencia conocida R1. Tienes voltímetro y amperímetro.",
            "Circuito en serie, solo voltímetro. El amperímetro está en calibración.",
            "Circuito en paralelo, solo amperímetro. Compara las corrientes de rama.",
            "Rx está en paralelo con R1, y ese par está en serie con R2. Solo voltímetro.",
            "Dos aleaciones de esta línea difieren en resistividad cerca de un 10 %. Cualquier circuito, "
            "ambos medidores. Elige con cuidado el método y las resistencias conocidas.",
        ],
        "hint": [
            "La misma corriente circula por todo el circuito en serie: **Rx = V(Rx) / I**.",
            "La corriente es común, así que los voltajes se reparten en proporción a la resistencia: "
            "**Rx = R1 · V(Rx) / V(R1)**.",
            "El voltaje es común, así que las corrientes se reparten en proporción inversa: "
            "**Rx = R1 · I(R1) / I(Rx)**.",
            "Primero el par: **Rp = R2 · V(par) / V(R2)**. Luego deshaz el paralelo: "
            "**Rx = Rp · R1 / (R1 − Rp)**. Mantén R1 bien por encima de Rp o la resta amplifica el error.",
            "Usa un método de razón (estaciones 2 o 3) con R1 cercana a Rx para que ambas lecturas caigan "
            "en la misma escala, repite las lecturas y usa las dos probetas.",
        ],
        "hint_common": (
            "Después **ρ = R · A / L**, con A = π·d²/4 para alambre o barra y A = w·t para una cinta. "
            "Con A en mm² y L en m, ρ sale en Ω·mm²/m, el mismo número que en µΩ·m.\n\n"
            "A y B tienen resistencias distintas pero deben dar la **misma ρ**: promedia las dos. "
            "Para la probeta sellada, **R(C) = ρ · L(C) / A(C)**."
        ),
        "batch": "Lote", "pmax": "potencia máx. por probeta",
        "sealed": "sellada", "on_bench": "en el banco",
        "mount": "Probeta en el banco",
        "topology": "Circuito",
        "series": "Serie", "parallel": "Paralelo", "mixed": "Serie-paralelo",
        "supply": "Dial de la fuente E (V)", "r_known": "Resistencia conocida",
        "sag_note": "La fuente tiene resistencia interna: su voltaje en bornes cae bajo carga.",
        "probe": "Medidor y dónde se conecta",
        "p_V_Rx": "V en Rx", "p_V_R1": "V en R1", "p_V_R2": "V en R2", "p_V_par": "V en R1∥Rx",
        "p_V_src": "V en la fuente", "p_I_tot": "A total", "p_I_R1": "A en R1", "p_I_Rx": "A en Rx",
        "measure": "Cerrar el interruptor y leer",
        "open": "interruptor abierto", "range": "escala", "heat": "Calor de la probeta", "reading": "lectura",
        "trip": "La fuente se disparó: el circuito pide más de 1 A. Baja E o sube las resistencias conocidas.",
        "burn": "La probeta {tag} se sobrecalentó: disiparía {p:.2f} W, por encima del límite de {pm} W. "
                "Se montó una pieza nueva (−15). Baja E o agrega resistencia en serie.",
        "tab_bench": "Banco", "tab_notebook": "Cuaderno", "tab_data": "Ficha", "tab_report": "Informe",
        "nb_empty": "Aquí aparecerán tus lecturas. Toma la primera en la pestaña Banco.",
        "c_n": "#", "c_spec": "Probeta", "c_circ": "Circuito", "c_meter": "Medidor", "c_read": "Lectura",
        "st_trip": "disparo", "st_burn": "sobrecalentada",
        "meas_count": "Lecturas tomadas: {n} ({f} gratis)",
        "method": "¿Atascado? Muestra el método",
        "method_btn": "Mostrar el método (−10 puntos)",
        "ref_note": "Resistividad a 20 °C. 1 µΩ·m = 1 Ω·mm²/m = 10⁻⁶ Ω·m. Los TCR son valores típicos.",
        "rc_mat": "Material", "rc_comp": "Composición", "rc_rho": "ρ (µΩ·m)",
        "rc_tcr": "TCR (ppm/K)", "rc_use": "Uso típico",
        "a_rho": "Resistividad ρ del lote (µΩ·m)",
        "a_mat": "Material",
        "a_pred": "Resistencia predicha de la probeta sellada C (Ω)",
        "choose": "Elige…",
        "check": "Revisar mi informe",
        "need_all": "Ingresa ρ, un material y tu predicción para C antes de revisar.",
        "approved": "APROBADO", "rejected": "RECHAZADO", "pts": "puntos",
        "correct": "Correcto: el lote es {m}.",
        "wrong": "Esta vez no. El lote es {m}; reportaste {g}.",
        "yours": "Tuyo", "true": "Real", "err": "Error", "quantity": "Magnitud",
        "q_rho": "ρ (µΩ·m)", "q_pred": "R de la probeta C (Ω)",
        "points": "Puntos", "pt_material": "Material", "pt_rho": "Resistividad",
        "pt_pred": "Predicción para C", "pt_meas": "Lecturas extra", "pt_hint": "Método mostrado",
        "pt_burn": "Probetas sobrecalentadas", "pt_total": "Total de la estación",
        "solution": "Mismo material, tres geometrías: los números resueltos",
        "s_spec": "Probeta", "s_geo": "Geometría", "s_area": "A (mm²)", "s_R": "R (Ω)",
        "s_note": "Todas las probetas dan ρ = R·A/L = {rho} µΩ·m. La resistencia es de la pieza; "
                  "la resistividad es del material.",
        "next": "Ir a la siguiente estación", "finish": "Ver el resultado final",
        "final": "Turno terminado",
        "rank": ["Metrólogo jefe", "Ingeniero sénior de calidad", "Técnico de laboratorio", "Practicante"],
        "code": "Código de verificación",
        "code_note": "Envía tu nombre, nivel, puntaje y este código a tu docente.",
        "download": "Descargar mi informe (CSV)",
        "again": "Jugar de nuevo", "quit": "Reiniciar el juego",
        "instructor": "Para el docente: verificar un código",
        "v_score": "Puntaje", "v_code": "Código", "v_ok": "Código válido.", "v_bad": "El código no coincide.",
        "h_station": "Estación", "h_batch": "Lote", "h_true": "Material", "h_guess": "Reportado",
        "h_pts": "Puntos", "h_stars": "Estrellas",
        "f_wire": "alambre", "f_rod": "barra", "f_strip": "cinta",
    },
}
