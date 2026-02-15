"""
Genera datos sinteticos de expedientes medicos mexicanos para entrenamiento.

Tipos de documentos:
    1. Recetas medicas — medicamento, dosis, frecuencia, duracion
    2. Resultados de laboratorio — glucosa, colesterol, biometria hematica
    3. Notas medicas — diagnostico, exploracion fisica, plan de tratamiento
    4. Referencias/Contrarreferencias — motivo, dx, tratamiento previo

Genera:
    - 500+ ejemplos por tipo de documento (2000+ total)
    - Anotaciones NER en formato SpaCy (entidades con offsets)
    - Variaciones realistas (abreviaturas medicas, errores OCR)
    - Datos demograficos mexicanos realistas
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── Catalogos de datos realistas ────────────────────────────────

NOMBRES_MASCULINOS = [
    "Juan Carlos", "Jose Luis", "Miguel Angel", "Francisco Javier",
    "Carlos Alberto", "Roberto", "Pedro", "Eduardo", "Fernando",
    "Ricardo", "Alejandro", "Luis", "Jorge", "Manuel", "Rafael",
    "Daniel", "Mario", "Sergio", "Arturo", "Enrique",
]

NOMBRES_FEMENINOS = [
    "Maria Guadalupe", "Maria del Carmen", "Ana Patricia", "Rosa Elena",
    "Patricia", "Claudia", "Adriana", "Gabriela", "Leticia",
    "Sandra", "Veronica", "Martha", "Laura", "Teresa", "Silvia",
    "Lucia", "Diana", "Monica", "Beatriz", "Carmen",
]

APELLIDOS = [
    "Garcia", "Martinez", "Lopez", "Hernandez", "Gonzalez",
    "Rodriguez", "Perez", "Sanchez", "Ramirez", "Torres",
    "Flores", "Rivera", "Gomez", "Diaz", "Cruz",
    "Morales", "Reyes", "Gutierrez", "Ortiz", "Ramos",
    "Mendoza", "Jimenez", "Aguilar", "Castillo", "Ruiz",
]

NOMBRES_DOCTOR = [
    "Dr. Roberto Mendez Castillo", "Dra. Ana Maria Flores Rivera",
    "Dr. Carlos Eduardo Sanchez Perez", "Dra. Patricia Gomez Torres",
    "Dr. Jorge Luis Ramirez Diaz", "Dra. Laura Elena Gutierrez Morales",
    "Dr. Fernando Aguilar Reyes", "Dra. Monica Hernandez Cruz",
    "Dr. Alejandro Ruiz Ortiz", "Dra. Gabriela Martinez Lopez",
]

ESPECIALIDADES = [
    "Medicina General", "Medicina Interna", "Endocrinologia",
    "Cardiologia", "Nefrologia", "Neumologia",
]

CEDULAS = [f"{random.randint(1000000, 9999999)}" for _ in range(10)]

INSTITUCIONES = [
    "Clinica Rural San Luis", "Centro de Salud Soledad",
    "Hospital General de Zona No. 1", "Unidad Medica Familiar No. 47",
    "Centro de Salud Villa de Reyes", "Clinica Comunitaria Matehuala",
    "Hospital Basico Comunitario Tamazunchale",
]

MEDICAMENTOS = [
    {"nombre": "Metformina", "presentacion": "850mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 12 horas", "duracion": "30 dias", "indicacion": "Diabetes Mellitus tipo 2"},
    {"nombre": "Glibenclamida", "presentacion": "5mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 24 horas", "duracion": "30 dias", "indicacion": "Diabetes Mellitus tipo 2"},
    {"nombre": "Losartan", "presentacion": "50mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 24 horas", "duracion": "30 dias", "indicacion": "Hipertension arterial"},
    {"nombre": "Enalapril", "presentacion": "10mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 12 horas", "duracion": "30 dias", "indicacion": "Hipertension arterial"},
    {"nombre": "Amlodipino", "presentacion": "5mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 24 horas", "duracion": "30 dias", "indicacion": "Hipertension arterial"},
    {"nombre": "Atorvastatina", "presentacion": "20mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 24 horas", "duracion": "30 dias", "indicacion": "Dislipidemia"},
    {"nombre": "Omeprazol", "presentacion": "20mg capsulas", "dosis": "1 capsula", "frecuencia": "cada 24 horas", "duracion": "14 dias", "indicacion": "ERGE"},
    {"nombre": "Amoxicilina", "presentacion": "500mg capsulas", "dosis": "1 capsula", "frecuencia": "cada 8 horas", "duracion": "7 dias", "indicacion": "Infeccion bacteriana"},
    {"nombre": "Ciprofloxacino", "presentacion": "500mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 12 horas", "duracion": "7 dias", "indicacion": "Infeccion urinaria"},
    {"nombre": "Paracetamol", "presentacion": "500mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 6 horas", "duracion": "5 dias", "indicacion": "Dolor y fiebre"},
    {"nombre": "Ibuprofeno", "presentacion": "400mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 8 horas", "duracion": "5 dias", "indicacion": "Dolor e inflamacion"},
    {"nombre": "Naproxeno", "presentacion": "250mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 12 horas", "duracion": "7 dias", "indicacion": "Dolor musculoesqueletico"},
    {"nombre": "Salbutamol", "presentacion": "100mcg/dosis inhalador", "dosis": "2 disparos", "frecuencia": "cada 6 horas", "duracion": "según necesidad", "indicacion": "Broncoespasmo"},
    {"nombre": "Insulina NPH", "presentacion": "100 UI/ml", "dosis": "20 UI", "frecuencia": "cada 12 horas", "duracion": "30 dias", "indicacion": "Diabetes Mellitus"},
    {"nombre": "Hidroclorotiazida", "presentacion": "25mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 24 horas", "duracion": "30 dias", "indicacion": "Hipertension arterial"},
    {"nombre": "Diclofenaco", "presentacion": "100mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 12 horas", "duracion": "5 dias", "indicacion": "Dolor e inflamacion"},
    {"nombre": "Fluoxetina", "presentacion": "20mg capsulas", "dosis": "1 capsula", "frecuencia": "cada 24 horas", "duracion": "30 dias", "indicacion": "Depresion"},
    {"nombre": "Prednisona", "presentacion": "5mg tabletas", "dosis": "2 tabletas", "frecuencia": "cada 24 horas", "duracion": "5 dias", "indicacion": "Proceso inflamatorio"},
    {"nombre": "Ranitidina", "presentacion": "150mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 12 horas", "duracion": "14 dias", "indicacion": "Gastritis"},
    {"nombre": "TMP/SMX", "presentacion": "160/800mg tabletas", "dosis": "1 tableta", "frecuencia": "cada 12 horas", "duracion": "5 dias", "indicacion": "Infeccion urinaria"},
]

DIAGNOSTICOS = [
    {"nombre": "Diabetes Mellitus tipo 2", "cie10": "E11.9"},
    {"nombre": "Hipertension arterial esencial", "cie10": "I10"},
    {"nombre": "Dislipidemia mixta", "cie10": "E78.5"},
    {"nombre": "Infeccion de vias urinarias", "cie10": "N39.0"},
    {"nombre": "Infeccion aguda de vias respiratorias superiores", "cie10": "J06.9"},
    {"nombre": "Gastritis no especificada", "cie10": "K29.7"},
    {"nombre": "Lumbalgia", "cie10": "M54.5"},
    {"nombre": "Obesidad", "cie10": "E66.9"},
    {"nombre": "Episodio depresivo no especificado", "cie10": "F32.9"},
    {"nombre": "Neumonia no especificada", "cie10": "J18.9"},
    {"nombre": "Enfermedad por reflujo gastroesofagico", "cie10": "K21.0"},
    {"nombre": "Diabetes Mellitus tipo 2 con complicaciones renales", "cie10": "E11.2"},
    {"nombre": "Enfermedad cardiaca hipertensiva", "cie10": "I11"},
    {"nombre": "Migrana", "cie10": "G43.9"},
    {"nombre": "Candidiasis vulvovaginal", "cie10": "B37.3"},
]

ANALISIS_LAB = [
    {"nombre": "Glucosa en ayunas", "unidad": "mg/dL", "min_normal": 70, "max_normal": 100, "min_val": 45, "max_val": 450},
    {"nombre": "Hemoglobina glucosilada (HbA1c)", "unidad": "%", "min_normal": 4.0, "max_normal": 5.6, "min_val": 4.0, "max_val": 14.0},
    {"nombre": "Colesterol total", "unidad": "mg/dL", "min_normal": 0, "max_normal": 200, "min_val": 100, "max_val": 380},
    {"nombre": "Trigliceridos", "unidad": "mg/dL", "min_normal": 0, "max_normal": 150, "min_val": 50, "max_val": 500},
    {"nombre": "Creatinina", "unidad": "mg/dL", "min_normal": 0.7, "max_normal": 1.3, "min_val": 0.5, "max_val": 8.0},
    {"nombre": "Urea", "unidad": "mg/dL", "min_normal": 10, "max_normal": 50, "min_val": 8, "max_val": 180},
    {"nombre": "Acido urico", "unidad": "mg/dL", "min_normal": 3.5, "max_normal": 7.2, "min_val": 2.0, "max_val": 12.0},
    {"nombre": "Hemoglobina", "unidad": "g/dL", "min_normal": 12.0, "max_normal": 17.5, "min_val": 6.0, "max_val": 20.0},
    {"nombre": "Leucocitos", "unidad": "cel/uL", "min_normal": 4500, "max_normal": 11000, "min_val": 2000, "max_val": 25000},
    {"nombre": "Plaquetas", "unidad": "cel/uL", "min_normal": 150000, "max_normal": 400000, "min_val": 80000, "max_val": 600000},
    {"nombre": "TGO (AST)", "unidad": "U/L", "min_normal": 0, "max_normal": 40, "min_val": 10, "max_val": 300},
    {"nombre": "TGP (ALT)", "unidad": "U/L", "min_normal": 0, "max_normal": 41, "min_val": 10, "max_val": 300},
]

SIGNOS_VITALES = [
    {"nombre": "TA", "formato": "{sys}/{dia} mmHg", "sys_range": (90, 180), "dia_range": (60, 120)},
    {"nombre": "FC", "formato": "{val} lpm", "range": (55, 110)},
    {"nombre": "FR", "formato": "{val} rpm", "range": (14, 24)},
    {"nombre": "Temp", "formato": "{val} C", "range": (36.0, 39.5)},
    {"nombre": "Peso", "formato": "{val} kg", "range": (45.0, 120.0)},
    {"nombre": "Talla", "formato": "{val} m", "range": (1.45, 1.90)},
]


# ── Funciones de generacion ─────────────────────────────────────

def _random_date(year_range: tuple[int, int] = (2024, 2026)) -> str:
    year = random.randint(*year_range)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"


def _random_patient() -> dict:
    sexo = random.choice(["M", "F"])
    if sexo == "M":
        nombre = random.choice(NOMBRES_MASCULINOS)
    else:
        nombre = random.choice(NOMBRES_FEMENINOS)
    apellido1 = random.choice(APELLIDOS)
    apellido2 = random.choice(APELLIDOS)
    edad = random.randint(18, 85)
    return {
        "nombre": f"{nombre} {apellido1} {apellido2}",
        "edad": edad,
        "sexo": sexo,
    }


def _find_entity(text: str, substring: str) -> tuple[int, int] | None:
    """Encuentra la posicion de un substring en el texto."""
    start = text.find(substring)
    if start == -1:
        return None
    return (start, start + len(substring))


# ── Generadores por tipo de documento ───────────────────────────

def generate_receta() -> tuple[str, dict, list[tuple[int, int, str]]]:
    """Genera una receta medica con anotaciones NER."""
    doctor = random.choice(NOMBRES_DOCTOR)
    cedula = random.choice(CEDULAS)
    especialidad = random.choice(ESPECIALIDADES)
    institucion = random.choice(INSTITUCIONES)
    paciente = _random_patient()
    fecha = _random_date()

    num_meds = random.randint(1, 3)
    meds = random.sample(MEDICAMENTOS, num_meds)
    num_dx = random.randint(1, 2)
    dxs = random.sample(DIAGNOSTICOS, num_dx)

    # Construir texto
    lines: list[str] = []
    lines.append(f"{institucion}")
    lines.append(f"{doctor}")
    lines.append(f"Cedula Profesional: {cedula}")
    lines.append(f"{especialidad}")
    lines.append("")
    lines.append(f"Paciente: {paciente['nombre']}")
    lines.append(f"Edad: {paciente['edad']} anos    Sexo: {paciente['sexo']}")
    lines.append(f"Fecha: {fecha}")
    lines.append("")
    lines.append("Rx:")

    for i, med in enumerate(meds, 1):
        lines.append(f"{i}. {med['nombre']} {med['presentacion']}")
        lines.append(f"   {med['dosis']} {med['frecuencia']} por {med['duracion']}")

    lines.append("")
    dx_texts = []
    for dx in dxs:
        dx_texts.append(f"{dx['nombre']} ({dx['cie10']})")
    lines.append(f"Dx: {', '.join(dx_texts)}")
    lines.append("")
    lines.append(f"Proxima cita: {_random_date()}")

    text = "\n".join(lines)

    # Generar anotaciones NER
    entities: list[tuple[int, int, str]] = []

    span = _find_entity(text, institucion)
    if span:
        entities.append((*span, "INSTITUCION"))

    span = _find_entity(text, doctor)
    if span:
        entities.append((*span, "NOMBRE_MEDICO"))

    span = _find_entity(text, paciente["nombre"])
    if span:
        entities.append((*span, "NOMBRE_PACIENTE"))

    span = _find_entity(text, fecha)
    if span:
        entities.append((*span, "FECHA"))

    for med in meds:
        span = _find_entity(text, med["nombre"])
        if span:
            entities.append((*span, "MEDICAMENTO"))
        span = _find_entity(text, med["presentacion"])
        if span:
            entities.append((*span, "DOSIS"))
        span = _find_entity(text, med["dosis"])
        if span:
            entities.append((*span, "FRECUENCIA_DOSIS"))
        span = _find_entity(text, med["frecuencia"])
        if span:
            entities.append((*span, "FRECUENCIA_TIEMPO"))
        span = _find_entity(text, med["duracion"])
        if span:
            entities.append((*span, "DURACION"))

    for dx in dxs:
        span = _find_entity(text, dx["nombre"])
        if span:
            entities.append((*span, "DIAGNOSTICO"))
        span = _find_entity(text, dx["cie10"])
        if span:
            entities.append((*span, "CODIGO_CIE10"))

    metadata = {"doc_type": "receta", "patient": paciente, "medications": len(meds)}
    return text, metadata, entities


def generate_laboratorio() -> tuple[str, dict, list[tuple[int, int, str]]]:
    """Genera resultado de laboratorio con anotaciones NER."""
    institucion = random.choice(INSTITUCIONES)
    paciente = _random_patient()
    fecha = _random_date()

    num_tests = random.randint(4, 8)
    tests = random.sample(ANALISIS_LAB, num_tests)

    lines: list[str] = []
    lines.append(f"{institucion}")
    lines.append("LABORATORIO CLINICO")
    lines.append(f"Fecha: {fecha}")
    lines.append("")
    lines.append(f"Paciente: {paciente['nombre']}")
    lines.append(f"Edad: {paciente['edad']} anos    Sexo: {paciente['sexo']}")
    lines.append("")
    lines.append("RESULTADOS:")
    lines.append("-" * 50)

    results_data = []
    for test in tests:
        if isinstance(test["min_val"], float):
            valor = round(random.uniform(test["min_val"], test["max_val"]), 1)
        else:
            valor = random.randint(test["min_val"], test["max_val"])

        rango = f"{test['min_normal']}-{test['max_normal']}"
        es_anormal = valor < test["min_normal"] or valor > test["max_normal"]
        flag = " *" if es_anormal else ""

        line = f"{test['nombre']}: {valor} {test['unidad']}  (Ref: {rango} {test['unidad']}){flag}"
        lines.append(line)
        results_data.append({
            "nombre": test["nombre"],
            "valor": valor,
            "unidad": test["unidad"],
            "rango": rango,
            "anormal": es_anormal,
        })

    lines.append("-" * 50)
    lines.append("Quimico responsable: QFB Maria Elena Rodriguez")

    text = "\n".join(lines)

    # Anotaciones NER
    entities: list[tuple[int, int, str]] = []

    span = _find_entity(text, institucion)
    if span:
        entities.append((*span, "INSTITUCION"))

    span = _find_entity(text, paciente["nombre"])
    if span:
        entities.append((*span, "NOMBRE_PACIENTE"))

    span = _find_entity(text, fecha)
    if span:
        entities.append((*span, "FECHA"))

    for r in results_data:
        span = _find_entity(text, r["nombre"])
        if span:
            entities.append((*span, "SIGNO_VITAL"))
        valor_str = str(r["valor"])
        span = _find_entity(text, f"{valor_str} {r['unidad']}")
        if span:
            entities.append((*span, "VALOR_MEDICION"))
        rango_str = f"{r['rango']} {r['unidad']}"
        span = _find_entity(text, rango_str)
        if span:
            entities.append((*span, "RANGO_REFERENCIA"))

    metadata = {"doc_type": "laboratorio", "patient": paciente, "tests": len(tests)}
    return text, metadata, entities


def generate_nota_medica() -> tuple[str, dict, list[tuple[int, int, str]]]:
    """Genera nota medica con anotaciones NER."""
    doctor = random.choice(NOMBRES_DOCTOR)
    institucion = random.choice(INSTITUCIONES)
    paciente = _random_patient()
    fecha = _random_date()
    dx = random.choice(DIAGNOSTICOS)
    meds = random.sample(MEDICAMENTOS, random.randint(1, 2))

    # Signos vitales
    ta_sys = random.randint(90, 180)
    ta_dia = random.randint(60, 120)
    fc = random.randint(55, 110)
    fr = random.randint(14, 24)
    temp = round(random.uniform(36.0, 39.0), 1)
    peso = round(random.uniform(50.0, 110.0), 1)

    motivos = [
        "Control de enfermedad cronica",
        "Dolor abdominal de 3 dias de evolucion",
        "Cefalea intensa y mareo",
        "Revision de resultados de laboratorio",
        "Tos productiva y fiebre de 2 dias",
        "Dolor lumbar de inicio subito",
        "Consulta de primera vez por malestar general",
    ]
    motivo = random.choice(motivos)

    exploraciones = [
        "Paciente consciente, orientado, hidratado, cooperador.",
        "Paciente alerta, con facies de dolor, mucosas hidratadas.",
        "Paciente en buen estado general, sin datos de dificultad respiratoria.",
    ]
    exploracion = random.choice(exploraciones)

    planes = [
        "Se ajusta tratamiento farmacologico. Cita en 1 mes.",
        "Se solicitan estudios de laboratorio de control. Cita en 2 semanas.",
        "Se inicia tratamiento antibiotico. Revalorar en 72 horas.",
        "Se mantiene tratamiento actual. Control en 3 meses.",
    ]
    plan = random.choice(planes)

    lines: list[str] = []
    lines.append(f"{institucion}")
    lines.append("NOTA MEDICA")
    lines.append(f"Fecha: {fecha}")
    lines.append(f"Medico: {doctor}")
    lines.append("")
    lines.append(f"Paciente: {paciente['nombre']}")
    lines.append(f"Edad: {paciente['edad']} anos    Sexo: {paciente['sexo']}")
    lines.append("")
    lines.append(f"Motivo de consulta: {motivo}")
    lines.append("")
    lines.append("Exploracion fisica:")
    lines.append(exploracion)
    lines.append(f"TA: {ta_sys}/{ta_dia} mmHg  FC: {fc} lpm  FR: {fr} rpm  Temp: {temp} C  Peso: {peso} kg")
    lines.append("")
    lines.append(f"Diagnostico: {dx['nombre']} ({dx['cie10']})")
    lines.append("")
    lines.append("Plan de tratamiento:")
    for med in meds:
        lines.append(f"- {med['nombre']} {med['presentacion']}, {med['dosis']} {med['frecuencia']}")
    lines.append(plan)

    text = "\n".join(lines)

    # Anotaciones NER
    entities: list[tuple[int, int, str]] = []

    span = _find_entity(text, institucion)
    if span:
        entities.append((*span, "INSTITUCION"))
    span = _find_entity(text, doctor)
    if span:
        entities.append((*span, "NOMBRE_MEDICO"))
    span = _find_entity(text, paciente["nombre"])
    if span:
        entities.append((*span, "NOMBRE_PACIENTE"))
    span = _find_entity(text, fecha)
    if span:
        entities.append((*span, "FECHA"))
    span = _find_entity(text, dx["nombre"])
    if span:
        entities.append((*span, "DIAGNOSTICO"))
    span = _find_entity(text, dx["cie10"])
    if span:
        entities.append((*span, "CODIGO_CIE10"))

    ta_str = f"{ta_sys}/{ta_dia} mmHg"
    span = _find_entity(text, ta_str)
    if span:
        entities.append((*span, "VALOR_MEDICION"))

    for med in meds:
        span = _find_entity(text, med["nombre"])
        if span:
            entities.append((*span, "MEDICAMENTO"))

    metadata = {"doc_type": "nota_medica", "patient": paciente}
    return text, metadata, entities


def generate_referencia() -> tuple[str, dict, list[tuple[int, int, str]]]:
    """Genera referencia/contrarreferencia con anotaciones NER."""
    doctor_origen = random.choice(NOMBRES_DOCTOR)
    inst_origen = random.choice(INSTITUCIONES[:4])
    inst_destino = random.choice(INSTITUCIONES[4:])
    paciente = _random_patient()
    fecha = _random_date()
    dx = random.choice(DIAGNOSTICOS)
    meds = random.sample(MEDICAMENTOS, random.randint(1, 2))

    motivos_ref = [
        "Valoracion por especialista por descontrol metabolico",
        "Estudio complementario no disponible en esta unidad",
        "Segunda opinion diagnostica",
        "Manejo de complicaciones de enfermedad cronica",
        "Valoracion prequirurgica",
    ]
    motivo = random.choice(motivos_ref)

    resumen = (
        f"Paciente de {paciente['edad']} anos con diagnostico de {dx['nombre']} "
        f"desde hace {random.randint(1, 10)} anos. Actualmente en tratamiento con "
        f"{meds[0]['nombre']} {meds[0]['presentacion']}. "
        f"Se refiere por {motivo.lower()}."
    )

    lines: list[str] = []
    lines.append("FORMATO DE REFERENCIA Y CONTRARREFERENCIA")
    lines.append(f"Fecha: {fecha}")
    lines.append("")
    lines.append(f"Unidad de origen: {inst_origen}")
    lines.append(f"Medico que refiere: {doctor_origen}")
    lines.append(f"Unidad de destino: {inst_destino}")
    lines.append("")
    lines.append(f"Paciente: {paciente['nombre']}")
    lines.append(f"Edad: {paciente['edad']} anos    Sexo: {paciente['sexo']}")
    lines.append("")
    lines.append(f"Diagnostico: {dx['nombre']} ({dx['cie10']})")
    lines.append(f"Motivo de referencia: {motivo}")
    lines.append("")
    lines.append("Resumen clinico:")
    lines.append(resumen)
    lines.append("")
    lines.append("Tratamiento actual:")
    for med in meds:
        lines.append(f"- {med['nombre']} {med['presentacion']}, {med['dosis']} {med['frecuencia']}")

    text = "\n".join(lines)

    entities: list[tuple[int, int, str]] = []

    span = _find_entity(text, inst_origen)
    if span:
        entities.append((*span, "INSTITUCION"))
    span = _find_entity(text, doctor_origen)
    if span:
        entities.append((*span, "NOMBRE_MEDICO"))
    span = _find_entity(text, paciente["nombre"])
    if span:
        entities.append((*span, "NOMBRE_PACIENTE"))
    span = _find_entity(text, fecha)
    if span:
        entities.append((*span, "FECHA"))
    span = _find_entity(text, dx["nombre"])
    if span:
        entities.append((*span, "DIAGNOSTICO"))
    span = _find_entity(text, dx["cie10"])
    if span:
        entities.append((*span, "CODIGO_CIE10"))
    for med in meds:
        span = _find_entity(text, med["nombre"])
        if span:
            entities.append((*span, "MEDICAMENTO"))

    metadata = {"doc_type": "referencia", "patient": paciente}
    return text, metadata, entities


# ── Generacion masiva ────────────────────────────────────────────

GENERATORS = {
    "receta": generate_receta,
    "laboratorio": generate_laboratorio,
    "nota_medica": generate_nota_medica,
    "referencia": generate_referencia,
}


def generate_dataset(
    samples_per_type: int = 550,
    output_dir: str | None = None,
) -> dict:
    """Genera dataset completo con anotaciones NER.

    Args:
        samples_per_type: Numero de muestras por tipo de documento.
        output_dir: Directorio de salida. Si None, usa data/synthetic.

    Returns:
        Diccionario con estadisticas de generacion.
    """
    if output_dir is None:
        output_dir = str(Path(__file__).resolve().parent.parent / "data" / "synthetic")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_samples: list[dict] = []
    ner_training_data: list[tuple[str, dict]] = []
    classifier_data: list[dict] = []
    stats: dict[str, int] = {}

    for doc_type, generator in GENERATORS.items():
        count = 0
        for i in range(samples_per_type):
            text, metadata, entities = generator()

            # Formato para almacenamiento general
            sample = {
                "id": f"{doc_type}_{i:04d}",
                "text": text,
                "doc_type": doc_type,
                "metadata": metadata,
                "entities": [
                    {"start": s, "end": e, "label": l} for s, e, l in entities
                ],
            }
            all_samples.append(sample)

            # Formato SpaCy NER training
            ner_training_data.append((
                text,
                {"entities": [(s, e, l) for s, e, l in entities]},
            ))

            # Formato clasificador
            classifier_data.append({
                "text": text,
                "label": doc_type,
            })

            count += 1

        stats[doc_type] = count

    # Guardar archivos
    with open(output_path / "all_samples.json", "w", encoding="utf-8") as f:
        json.dump(all_samples, f, ensure_ascii=False, indent=2)

    with open(output_path / "ner_training_data.json", "w", encoding="utf-8") as f:
        json.dump(
            [{"text": t, "entities": e["entities"]} for t, e in ner_training_data],
            f, ensure_ascii=False, indent=2,
        )

    with open(output_path / "classifier_data.json", "w", encoding="utf-8") as f:
        json.dump(classifier_data, f, ensure_ascii=False, indent=2)

    total = sum(stats.values())
    stats["total"] = total

    # Guardar estadisticas
    with open(output_path / "generation_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    return stats


if __name__ == "__main__":
    random.seed(42)
    print("Generando datos sinteticos de expedientes medicos...")
    print("=" * 50)

    stats = generate_dataset(samples_per_type=550)

    print(f"Total generado: {stats['total']} documentos")
    for doc_type, count in stats.items():
        if doc_type != "total":
            print(f"  {doc_type}: {count}")
    print("=" * 50)
    print("Archivos generados en backend/data/synthetic/")
    print("  - all_samples.json")
    print("  - ner_training_data.json")
    print("  - classifier_data.json")
    print("  - generation_stats.json")
