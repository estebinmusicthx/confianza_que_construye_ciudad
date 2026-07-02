# -*- coding: utf-8 -*-
"""
Confianza que Construye Ciudad
Bogotá DataJam Edición 2 — análisis reproducible.

Este script descarga/lee datos públicos, documenta fuentes, calcula indicadores
territoriales y genera un dashboard HTML con reseñas por gráfico.

Nota metodológica:
- No se afirma causalidad entre confianza y aporte voluntario.
- El aporte voluntario predial se analiza a nivel distrital/estrato/año porque la fuente no tiene llave territorial pública.
- El componente territorial se construye con cumplimiento predial, condiciones de Encuesta Multipropósito y presupuestos participativos.
"""
from __future__ import annotations

import io
import os
import re
import json
import math
import textwrap
import warnings
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
BASE_DIR = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd()
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "outputs"
CLEAN_DIR = OUT_DIR / "clean"
DOCS_DIR = BASE_DIR / "docs"
for p in [DATA_DIR, OUT_DIR, CLEAN_DIR, DOCS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Cambiar a True si se quiere intentar incorporar variables de percepción/participación
# desde la base completa EM2021. Puede tardar por tamaño del archivo (~1,25 GB).
USAR_EM_COMPLETA = os.getenv("USAR_EM_COMPLETA", "false").lower() == "true"

SOURCES = {
    "aporte_predial": {
        "nombre": "Recaudo Aporte Voluntario Impuesto Predial 2006-2023",
        "entidad": "Secretaría Distrital de Hacienda",
        "portal": "Portal de Datos Abiertos Bogotá",
        "url_dataset": "https://datosabiertos.bogota.gov.co/dataset/recaudo-aporte-voluntario-impuesto-predial",
        "url_recurso": "https://datosabiertos.bogota.gov.co/dataset/recaudo-aporte-voluntario-impuesto-predial/resource/10a5f103-ac7c-42f9-9096-05561839fa3e",
        "url_descarga": "https://datosabiertos.bogota.gov.co/dataset/e03353e3-8c8f-4b9f-a342-999af007e9a8/resource/10a5f103-ac7c-42f9-9096-05561839fa3e/download/18.-recaudo-aporte-voluntario-impuesto-predial_2006_2023.csv",
        "resource_id": "10a5f103-ac7c-42f9-9096-05561839fa3e",
        "formato": "CSV",
        "granularidad": "año - impuesto - estrato",
        "uso": "Contexto del aporte voluntario predial: evolución, aportantes y estrato.",
        "limitacion": "No incluye localidad ni llave pública para asociar directamente cada aporte a proyectos territoriales."
    },
    "cumplimiento_predial": {
        "nombre": "Cumplimiento Impuesto Predial 2007-2023. Bogotá D.C.",
        "entidad": "Secretaría Distrital de Hacienda",
        "portal": "Portal de Datos Abiertos Bogotá",
        "url_dataset": "https://datosabiertos.bogota.gov.co/dataset/cumplimiento-impuesto-predial-2007-2017",
        "url_recurso": "https://datosabiertos.bogota.gov.co/dataset/cumplimiento-impuesto-predial-2007-2017/resource/2dada77d-7355-4cbf-b944-89b8d87bb65b",
        "url_descarga": "https://datosabiertos.bogota.gov.co/dataset/092ad69a-7d04-4195-b203-0fd70af52412/resource/2dada77d-7355-4cbf-b944-89b8d87bb65b/download/15.-cumplimiento-impuesto-predial_2007_2023.csv",
        "resource_id": "2dada77d-7355-4cbf-b944-89b8d87bb65b",
        "formato": "CSV",
        "granularidad": "año gravable - localidad - UPZ - barrio - estrato - destino",
        "uso": "Indicadores territoriales de cumplimiento, oportunidad, morosidad y pago predial.",
        "limitacion": "Es registro administrativo agregado; no mide confianza, motivación ni comportamiento individual."
    },
    "em2021_completa": {
        "nombre": "Encuesta Multipropósito 2021",
        "entidad": "Secretaría Distrital de Planeación",
        "portal": "Portal de Datos Abiertos Bogotá",
        "url_dataset": "https://datosabiertos.bogota.gov.co/dataset/encuesta-multiproposito-2021-sdp",
        "url_recurso": "https://datosabiertos.bogota.gov.co/dataset/encuesta-multiproposito-2021-sdp/resource/b3fd892e-b9f9-4f34-ac22-6cc50612eac9",
        "url_descarga": "https://datosabiertos.bogota.gov.co/dataset/8ac12a95-1415-4812-b343-f07f90608014/resource/b3fd892e-b9f9-4f34-ac22-6cc50612eac9/download/em2021.csv",
        "resource_id": "b3fd892e-b9f9-4f34-ac22-6cc50612eac9",
        "formato": "CSV",
        "granularidad": "hogar/persona; agregable territorialmente si las columnas de localidad están disponibles",
        "uso": "Variables de percepción, participación, satisfacción y entorno para robustecer el ITCC.",
        "limitacion": "Archivo grande; se incorpora de forma opcional para evitar bloqueos por tiempo o memoria."
    },
    "em2021_adicionales": {
        "nombre": "Variables Adicionales Encuesta Multipropósito 2021",
        "entidad": "Secretaría Distrital de Planeación",
        "portal": "Portal de Datos Abiertos Bogotá",
        "url_dataset": "https://datosabiertos.bogota.gov.co/dataset/encuesta-multiproposito-2021-sdp",
        "url_recurso": "https://datosabiertos.bogota.gov.co/dataset/encuesta-multiproposito-2021-sdp/resource/ba44798f-5257-4c5c-8a57-0966da1bb4fa",
        "url_descarga": "https://datosabiertos.bogota.gov.co/dataset/8ac12a95-1415-4812-b343-f07f90608014/resource/ba44798f-5257-4c5c-8a57-0966da1bb4fa/download/20240430_variables_adicionales_2021.csv",
        "resource_id": "ba44798f-5257-4c5c-8a57-0966da1bb4fa",
        "formato": "CSV",
        "granularidad": "hogar/persona con variables adicionales e indicadores compuestos",
        "uso": "Proxies de condiciones sociales, vivienda, pobreza, ingreso y acceso a servicios para ITCC de respaldo.",
        "limitacion": "No contiene por sí sola todas las variables subjetivas de confianza; sirve como respaldo o componente social."
    },
    "pp_avance": {
        "nombre": "Estado de avance propuestas priorizadas Bogotá D.C.",
        "entidad": "Secretaría Distrital de Planeación",
        "portal": "Portal de Datos Abiertos Bogotá",
        "url_dataset": "https://datosabiertos.bogota.gov.co/dataset/presupuestos-participativos-bogota-dc",
        "url_recurso": "https://datosabiertos.bogota.gov.co/dataset/presupuestos-participativos-bogota-dc/resource/99d01780-ee33-40ff-9f09-2ecd62d9b1d9",
        "url_descarga": "https://datosabiertos.bogota.gov.co/dataset/3ded79df-ec9e-4f92-a949-ca8b1ae12d7d/resource/99d01780-ee33-40ff-9f09-2ecd62d9b1d9/download/datos_abiertos_avance_propuestas_priorizadas_pp_31-03-2026.ods",
        "resource_id": "99d01780-ee33-40ff-9f09-2ecd62d9b1d9",
        "formato": "ODS",
        "granularidad": "vigencia - localidad - sector - proyecto - propuesta",
        "uso": "Proyectos priorizados por ciudadanía y estado de avance; evidencia de participación/proyectos visibles.",
        "limitacion": "No prueba que los proyectos hayan sido financiados por aporte voluntario. Sirve para trazabilidad pública de proyectos territoriales."
    },
    "pp_presupuesto": {
        "nombre": "Presupuesto comprometido por meta proyecto y propuestas financiadas Bogotá D.C.",
        "entidad": "Secretaría Distrital de Planeación",
        "portal": "Portal de Datos Abiertos Bogotá",
        "url_dataset": "https://datosabiertos.bogota.gov.co/dataset/presupuestos-participativos-bogota-dc",
        "url_recurso": "https://datosabiertos.bogota.gov.co/dataset/presupuestos-participativos-bogota-dc/resource/7c5d5813-3621-47d7-92bc-fb46957988cb",
        "url_descarga": "https://datosabiertos.bogota.gov.co/dataset/3ded79df-ec9e-4f92-a949-ca8b1ae12d7d/resource/7c5d5813-3621-47d7-92bc-fb46957988cb/download/datos_abiertos_presupuesto_comprometido_xmeta_pp_31-03-2026.ods",
        "resource_id": "7c5d5813-3621-47d7-92bc-fb46957988cb",
        "formato": "ODS",
        "granularidad": "vigencia - localidad - sector - proyecto - compromiso presupuestal",
        "uso": "Presupuesto asociado a propuestas financiadas de presupuestos participativos.",
        "limitacion": "Se interpreta como proyecto territorial visible, no como destinación directa del aporte voluntario."
    },
    "tarjeta_metro": {
        "nombre": "Reconocimiento a contribuyentes con aporte voluntario: tarjeta conmemorativa Metro",
        "entidad": "Portal Bogotá / Secretaría Distrital de Hacienda",
        "portal": "Bogotá.gov.co",
        "url_dataset": "https://bogota.gov.co/mi-ciudad/hacienda/bogota-reconoce-quienes-hicieron-aporte-voluntario-en-impuestos",
        "url_recurso": "https://bogota.gov.co/mi-ciudad/hacienda/bogota-reconoce-quienes-hicieron-aporte-voluntario-en-impuestos",
        "url_descarga": "No aplica; fuente documental oficial de contexto",
        "resource_id": "No aplica",
        "formato": "Nota web oficial",
        "granularidad": "distrital - contribuyentes por impuesto con corte informado",
        "uso": "Antecedente institucional de reconocimiento ciudadano asociado al aporte voluntario.",
        "limitacion": "No se usa para inferencia estadística; contextualiza la recomendación de reconocimiento inteligente."
    },
}

LOCALIDADES = {
    1: "USAQUÉN", 2: "CHAPINERO", 3: "SANTA FE", 4: "SAN CRISTÓBAL", 5: "USME",
    6: "TUNJUELITO", 7: "BOSA", 8: "KENNEDY", 9: "FONTIBÓN", 10: "ENGATIVÁ",
    11: "SUBA", 12: "BARRIOS UNIDOS", 13: "TEUSAQUILLO", 14: "LOS MÁRTIRES",
    15: "ANTONIO NARIÑO", 16: "PUENTE ARANDA", 17: "LA CANDELARIA", 18: "RAFAEL URIBE URIBE",
    19: "CIUDAD BOLÍVAR", 20: "SUMAPAZ"
}

# =============================================================================
# UTILIDADES
# =============================================================================
def norm_col(c: str) -> str:
    c = str(c).strip()
    c = c.replace("\ufeff", "")
    c = c.upper()
    c = (c.replace("Á", "A").replace("É", "E").replace("Í", "I")
           .replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N"))
    c = re.sub(r"[^A-Z0-9]+", "_", c).strip("_")
    return c

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [norm_col(c) for c in df.columns]
    return df

def read_csv_robust(path_or_url: str, nrows=None, usecols=None) -> pd.DataFrame:
    attempts = [
        {"sep": ";", "encoding": "latin1"},
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ",", "encoding": "latin1"},
    ]
    last = None
    for kwargs in attempts:
        try:
            df = pd.read_csv(path_or_url, nrows=nrows, usecols=usecols, low_memory=False, **kwargs)
            if df.shape[1] > 1:
                return normalize_columns(df)
            last = df
        except Exception as e:
            last = e
    raise RuntimeError(f"No se pudo leer CSV: {path_or_url}. Último error: {last}")

def to_num(s: pd.Series) -> pd.Series:
    if s is None:
        return pd.Series(dtype=float)
    return pd.to_numeric(s.astype(str).str.replace("$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")

def minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    if x.notna().sum() == 0:
        return pd.Series(np.nan, index=series.index)
    lo, hi = x.min(), x.max()
    if math.isclose(lo, hi):
        res = pd.Series(50.0, index=series.index)
    else:
        res = (x - lo) / (hi - lo) * 100
    if invert:
        res = 100 - res
    return res.clip(0, 100)

def safe_div(a, b):
    return np.where(pd.to_numeric(b, errors="coerce").fillna(0) == 0, np.nan, pd.to_numeric(a, errors="coerce") / pd.to_numeric(b, errors="coerce"))

def save_df(df: pd.DataFrame, name: str) -> Path:
    path = CLEAN_DIR / name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path

def source_manifest() -> pd.DataFrame:
    df = pd.DataFrame(SOURCES).T.reset_index().rename(columns={"index": "id_fuente"})
    return df

# =============================================================================
# CARGA Y TRANSFORMACIÓN
# =============================================================================
def load_aporte_predial() -> pd.DataFrame:
    local = DATA_DIR / "18.-recaudo-aporte-voluntario-impuesto-predial_2006_2023.csv"
    src = str(local) if local.exists() else SOURCES["aporte_predial"]["url_descarga"]
    df = read_csv_robust(src)
    df["ANO_PRESENTACION"] = to_num(df.get("ANO_PRESENTACION")).astype("Int64")
    df["ESTRATO"] = to_num(df.get("ESTRATO")).astype("Int64")
    df["NO_CONTRIBUYENTES"] = to_num(df.get("NO_CONTRIBUYENTES"))
    df["VALOR_APORTE_VOLUNTARIO"] = to_num(df.get("VALOR_APORTE_VOLUNTARIO"))
    return df

def transform_aporte(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    anual = (df.groupby("ANO_PRESENTACION", dropna=False)
               .agg(contribuyentes=("NO_CONTRIBUYENTES", "sum"),
                    valor_aporte=("VALOR_APORTE_VOLUNTARIO", "sum"))
               .reset_index().sort_values("ANO_PRESENTACION"))
    anual["aporte_promedio_por_contribuyente"] = safe_div(anual["valor_aporte"], anual["contribuyentes"])
    anual["variacion_valor_pct"] = anual["valor_aporte"].pct_change() * 100

    estrato = (df.groupby(["ANO_PRESENTACION", "ESTRATO"], dropna=False)
                 .agg(contribuyentes=("NO_CONTRIBUYENTES", "sum"),
                      valor_aporte=("VALOR_APORTE_VOLUNTARIO", "sum"))
                 .reset_index().sort_values(["ANO_PRESENTACION", "ESTRATO"]))
    estrato["aporte_promedio_por_contribuyente"] = safe_div(estrato["valor_aporte"], estrato["contribuyentes"])
    return {"aporte_anual": anual, "aporte_estrato": estrato}

def load_cumplimiento() -> pd.DataFrame:
    local = DATA_DIR / "15.-cumplimiento-impuesto-predial_2007_2023.csv"
    src = str(local) if local.exists() else SOURCES["cumplimiento_predial"]["url_descarga"]
    df = read_csv_robust(src)
    num_cols = [c for c in df.columns if c.startswith("TOTAL_") or c in ["ANIO_GRAVABLE", "CODIGO_LOCALIDAD", "ESTRATO"]]
    for c in num_cols:
        df[c] = to_num(df[c])
    if "NOMBRE_LOCALIDAD" in df.columns:
        df["NOMBRE_LOCALIDAD"] = df["NOMBRE_LOCALIDAD"].astype(str).str.upper().str.strip()
    return df

def transform_cumplimiento(df: pd.DataFrame) -> pd.DataFrame:
    # Usar la última vigencia disponible para el diagnóstico territorial principal
    last_year = int(pd.to_numeric(df["ANIO_GRAVABLE"], errors="coerce").max())
    d = df[df["ANIO_GRAVABLE"] == last_year].copy()
    agg = (d.groupby(["CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD"], dropna=False)
             .agg(total_predios=("TOTAL_PREDIOS", "sum"),
                  predios_obligados=("TOTAL_PREDIOS_OBLIGADOS", "sum"),
                  oportunos=("TOTAL_PREDIOS_OPORTUNOS", "sum"),
                  extemporaneos=("TOTAL_PREDIOS_EXTEMPORANEOS", "sum"),
                  morosos=("TOTAL_PREDIOS_MOROSOS", "sum"),
                  no_declaran=("TOTAL_PREDIOS_NO_DECLARAN", "sum") if "TOTAL_PREDIOS_NO_DECLARAN" in d.columns else ("TOTAL_PREDIOS_NO_DECLARAN", "sum"),
                  total_pagado=("TOTAL_PAGADO", "sum"))
             .reset_index())
    agg["anio_gravable"] = last_year
    agg["tasa_pago_oportuno"] = safe_div(agg["oportunos"], agg["predios_obligados"]) * 100
    agg["tasa_morosidad"] = safe_div(agg["morosos"], agg["predios_obligados"]) * 100
    agg["tasa_extemporaneidad"] = safe_div(agg["extemporaneos"], agg["predios_obligados"]) * 100
    agg["pago_promedio_por_predio_obligado"] = safe_div(agg["total_pagado"], agg["predios_obligados"])
    agg = agg[agg["CODIGO_LOCALIDAD"].notna()].copy()
    agg["CODIGO_LOCALIDAD"] = agg["CODIGO_LOCALIDAD"].astype(int)
    return agg.sort_values("CODIGO_LOCALIDAD")

def load_em_adicionales(sample: bool = False) -> pd.DataFrame:
    local = DATA_DIR / "20240430_variables_adicionales_2021.csv"
    src = str(local) if local.exists() else SOURCES["em2021_adicionales"]["url_descarga"]
    nrows = 50000 if sample else None
    return read_csv_robust(src, nrows=nrows)

def try_load_em_percepcion() -> Optional[pd.DataFrame]:
    """Intenta leer columnas de percepción/participación de la EM completa.
    Si no se activa USAR_EM_COMPLETA o falla por tamaño/memoria, retorna None.
    """
    if not USAR_EM_COMPLETA:
        return None
    url = SOURCES["em2021_completa"]["url_descarga"]
    try:
        header = read_csv_robust(url, nrows=0)
        cols = list(header.columns)
        # Palabras clave: localidad + confianza/participación/satisfacción/seguridad/barrio
        keep_patterns = [
            "LOCAL", "UPZ", "BARRIO", "LOC", "FACTOR", "DIRECTORIO",
            "CONFI", "PARTICI", "SATIS", "SEGUR", "BARRIO", "ENTORNO", "CALIDAD", "VIDA",
            "PERTEN", "GOBIER", "INSTIT", "ALCAL", "ESPACIO", "PUBLIC", "COMUN"
        ]
        usecols = [c for c in cols if any(p in c for p in keep_patterns)]
        if len(usecols) < 3:
            return None
        df = read_csv_robust(url, usecols=usecols)
        return df
    except Exception as e:
        print("No se pudo incorporar EM completa:", e)
        return None

def build_itcc_from_em_adicionales(em_add: pd.DataFrame, cumplimiento_loc: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Construye un ITCC reproducible de respaldo con variables adicionales.
    Debido a que esta fuente no trae directamente todas las variables subjetivas, el índice se presenta
    como condiciones territoriales/proxy y se documenta su limitación.
    """
    df = em_add.copy()
    # Si no existe localidad residencial, usamos el cumplimiento predial para completar un índice territorial robusto.
    # Las variables adicionales se agregan por localidad de trabajo si está disponible, como respaldo no central.
    possible_loc = [c for c in df.columns if "LOCALIDAD" in c]
    components = []

    if possible_loc:
        loc_col = possible_loc[0]
        df[loc_col] = to_num(df[loc_col])
        df = df[df[loc_col].between(1, 20, inclusive="both")].copy()
        # Variables negativas: pobreza, déficit, desempleo, informalidad, sin capacidad de pago
        neg_candidates = [c for c in df.columns if any(k in c for k in ["POBRE", "DEFICIT", "HACIN", "DESEMPLEO", "INFORMAL", "ANALFAB", "INASISTENCIA", "SIN_CP"])]
        pos_candidates = [c for c in df.columns if any(k in c for k in ["INGPC", "INGTOT", "OCUPADOS", "ACCESO", "SALUD"])]
        agg_dict = {c: "mean" for c in list(set(neg_candidates + pos_candidates))}
        if agg_dict:
            g = df.groupby(loc_col).agg(agg_dict).reset_index().rename(columns={loc_col: "CODIGO_LOCALIDAD"})
            for c in neg_candidates:
                if c in g.columns:
                    g[f"score_{c}"] = minmax(g[c], invert=True)
                    components.append(f"score_{c}")
            for c in pos_candidates:
                if c in g.columns:
                    g[f"score_{c}"] = minmax(g[c], invert=False)
                    components.append(f"score_{c}")
            if components:
                g["itcc_em_adicionales"] = g[components].mean(axis=1)
            else:
                g = pd.DataFrame({"CODIGO_LOCALIDAD": list(LOCALIDADES.keys()), "itcc_em_adicionales": np.nan})
        else:
            g = pd.DataFrame({"CODIGO_LOCALIDAD": list(LOCALIDADES.keys()), "itcc_em_adicionales": np.nan})
    else:
        g = pd.DataFrame({"CODIGO_LOCALIDAD": list(LOCALIDADES.keys()), "itcc_em_adicionales": np.nan})

    base = cumplimiento_loc[["CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD", "predios_obligados", "total_pagado", "tasa_pago_oportuno", "tasa_morosidad", "tasa_extemporaneidad", "pago_promedio_por_predio_obligado"]].copy()
    base["score_cumplimiento"] = minmax(base["tasa_pago_oportuno"])
    base["score_morosidad_inversa"] = minmax(base["tasa_morosidad"], invert=True)
    base["score_pago_promedio"] = minmax(base["pago_promedio_por_predio_obligado"])
    merged = base.merge(g[["CODIGO_LOCALIDAD", "itcc_em_adicionales"]], on="CODIGO_LOCALIDAD", how="left")

    # ITCC comparable: TODAS las localidades deben promediar exactamente los mismos
    # componentes. El componente social EM2021 solo se incorpora si cubre (casi) todas
    # las localidades; si su cobertura es parcial se excluye y se documenta, para no
    # mezclar índices calculados con distinto número de componentes.
    comp_base = ["score_cumplimiento", "score_morosidad_inversa"]
    cobertura_em = merged["itcc_em_adicionales"].notna().mean()
    if cobertura_em >= 0.9:
        comp_itcc = comp_base + ["itcc_em_adicionales"]
        version = ("ITCC experimental: cumplimiento territorial + morosidad inversa + "
                   "componente social EM2021 (cobertura completa, componentes homogéneos)")
    else:
        comp_itcc = comp_base
        version = ("ITCC experimental: cumplimiento territorial + morosidad inversa "
                   "(componente social EM2021 excluido por cobertura parcial; componentes homogéneos)")
    merged["componentes_itcc"] = ", ".join(comp_itcc)
    merged["ITCC"] = merged[comp_itcc].mean(axis=1)
    merged["version_itcc"] = version
    merged["limitacion_itcc"] = "No mide confianza individual; resume condiciones territoriales observables para orientar pedagogía y trazabilidad."
    componentes_out = pd.DataFrame({"componente_usado": comp_itcc, "cobertura_em2021": round(float(cobertura_em), 3)})
    return merged.sort_values("ITCC", ascending=False), componentes_out

def load_pp(url: str, resource_id: str) -> Optional[pd.DataFrame]:
    # Intentar por URL ODS; si falla, intentar API datastore.
    try:
        df = pd.read_excel(url, engine="odf")
        return normalize_columns(df)
    except Exception as e1:
        try:
            # CKAN datastore_search por páginas
            import requests
            rows = []
            offset = 0
            limit = 5000
            while True:
                api = f"https://datosabiertos.bogota.gov.co/api/3/action/datastore_search?resource_id={resource_id}&limit={limit}&offset={offset}"
                js = requests.get(api, timeout=60).json()
                recs = js.get("result", {}).get("records", [])
                if not recs:
                    break
                rows.extend(recs)
                if len(recs) < limit:
                    break
                offset += limit
            return normalize_columns(pd.DataFrame(rows)) if rows else None
        except Exception as e2:
            print("No se pudo cargar PP:", e1, e2)
            return None

def transform_pp() -> Tuple[pd.DataFrame, pd.DataFrame]:
    avance = load_pp(SOURCES["pp_avance"]["url_descarga"], SOURCES["pp_avance"]["resource_id"])
    presupuesto = load_pp(SOURCES["pp_presupuesto"]["url_descarga"], SOURCES["pp_presupuesto"]["resource_id"])

    if avance is not None and not avance.empty:
        loc_col = "NOMBRE_LOCALIDAD" if "NOMBRE_LOCALIDAD" in avance.columns else None
        sector_col = "SECTOR" if "SECTOR" in avance.columns else None
        estado_col = "ESTADO_PROPUESTA" if "ESTADO_PROPUESTA" in avance.columns else None
        benef_col = "TOTAL_POBLACION_BENEFICIADA_EN_LA_EJECUCION" if "TOTAL_POBLACION_BENEFICIADA_EN_LA_EJECUCION" in avance.columns else None
        if benef_col:
            avance[benef_col] = to_num(avance[benef_col])
        if loc_col:
            avance[loc_col] = avance[loc_col].astype(str).str.upper().str.strip()
            pp_av = avance.groupby(loc_col).agg(
                propuestas=(loc_col, "size"),
                poblacion_beneficiada=(benef_col, "sum") if benef_col else (loc_col, "size")
            ).reset_index().rename(columns={loc_col: "NOMBRE_LOCALIDAD"})
        else:
            pp_av = pd.DataFrame()
    else:
        pp_av = pd.DataFrame()

    if presupuesto is not None and not presupuesto.empty:
        loc_col = "NOMBRE_LOCALIDAD" if "NOMBRE_LOCALIDAD" in presupuesto.columns else None
        sector_col = "SECTOR" if "SECTOR" in presupuesto.columns else None
        val_col = "VALOR_CRP_ASIGNADO_PRESUPUESTOS_PARTICIPATIVOS" if "VALOR_CRP_ASIGNADO_PRESUPUESTOS_PARTICIPATIVOS" in presupuesto.columns else None
        if val_col:
            presupuesto[val_col] = to_num(presupuesto[val_col])
        if loc_col:
            presupuesto[loc_col] = presupuesto[loc_col].astype(str).str.upper().str.strip()
            group_cols = [loc_col] + ([sector_col] if sector_col else [])
            pp_pr = presupuesto.groupby(group_cols).agg(
                presupuesto_comprometido=(val_col, "sum") if val_col else (loc_col, "size"),
                registros=(loc_col, "size")
            ).reset_index().rename(columns={loc_col: "NOMBRE_LOCALIDAD"})
        else:
            pp_pr = pd.DataFrame()
    else:
        pp_pr = pd.DataFrame()
    return pp_av, pp_pr

# =============================================================================
# ANÁLISIS Y SALIDAS
# =============================================================================
def classify_quadrants(itcc: pd.DataFrame) -> pd.DataFrame:
    df = itcc.copy()
    x = df["ITCC"]
    y = df["tasa_pago_oportuno"]
    x_med, y_med = x.median(), y.median()
    def quad(row):
        alta_conf = row["ITCC"] >= x_med
        alto_cump = row["tasa_pago_oportuno"] >= y_med
        if alta_conf and alto_cump:
            return "Embajadores: alta confianza territorial + alto cumplimiento"
        if alta_conf and not alto_cump:
            return "Comunicar beneficios: buenas condiciones + menor cumplimiento"
        if not alta_conf and alto_cump:
            return "Reconocimiento: cumplimiento alto + confianza territorial por fortalecer"
        return "Transparencia prioritaria: menor confianza territorial + menor cumplimiento"
    df["cuadrante"] = df.apply(quad, axis=1)
    df["accion_recomendada"] = df["cuadrante"].map({
        "Embajadores: alta confianza territorial + alto cumplimiento": "Activar vocerías ciudadanas, reconocimiento público y casos de uso por localidad.",
        "Comunicar beneficios: buenas condiciones + menor cumplimiento": "Mostrar proyectos concretos, explicar destinación y reducir fricciones de pago.",
        "Reconocimiento: cumplimiento alto + confianza territorial por fortalecer": "Agradecer, reconocer y reforzar transparencia sobre inversión y resultados.",
        "Transparencia prioritaria: menor confianza territorial + menor cumplimiento": "Priorizar pedagogía tributaria, trazabilidad visible y presencia territorial institucional."
    })
    return df

def brechas_trazabilidad() -> pd.DataFrame:
    return pd.DataFrame([
        {"brecha": "Aporte voluntario sin localidad pública", "riesgo": "No permite atribución territorial directa del aporte", "respuesta_metodologica": "Analizar aporte por año/estrato e integrar territorialmente cumplimiento, EM y proyectos sin afirmar causalidad."},
        {"brecha": "Proyectos no tienen llave directa con aporte voluntario", "riesgo": "Riesgo de sugerir destinación no verificable", "respuesta_metodologica": "Usar proyectos como evidencia de visualización pública territorial, no como destino causal de recursos."},
        {"brecha": "Encuesta mide percepciones/condiciones, no decisión individual de aportar", "riesgo": "Confundir condiciones territoriales con comportamiento individual", "respuesta_metodologica": "Construir un índice de condiciones territoriales y declarar explícitamente sus límites."},
        {"brecha": "Diferentes ventanas temporales", "riesgo": "Comparaciones temporales no homogéneas", "respuesta_metodologica": "Separar análisis temporal de aporte/cumplimiento y usar EM2021 como corte estructural de condiciones territoriales."},
    ])

def make_dashboard(aporte_anual, aporte_estrato, cumplimiento_loc, itcc, cuadrantes, pp_av, pp_pr):
    template = "plotly_white"
    accent = "#2563eb"
    secondary = "#10b981"
    danger = "#ef4444"
    purple = "#7c3aed"

    figs_html = []
    def add_section(title, fig, review, source):
        figs_html.append(f"""
        <section class='card'>
          <h2>{title}</h2>
          {fig.to_html(include_plotlyjs=False, full_html=False, config={'displayModeBar': False})}
          <div class='review'><b>Reseña estratégica:</b> {review}</div>
          <div class='source'><b>Fuente:</b> {source}</div>
        </section>
        """)

    # 1 ITCC
    fig1 = px.bar(itcc.sort_values("ITCC"), x="ITCC", y="NOMBRE_LOCALIDAD", orientation="h",
                  title="Índice Territorial de Confianza para la Corresponsabilidad (ITCC)",
                  labels={"ITCC": "ITCC (0-100)", "NOMBRE_LOCALIDAD": "Localidad"}, template=template)
    fig1.update_traces(marker_color=accent)
    add_section(
        "1. Mapa de condiciones: ITCC por localidad",
        fig1,
        "Este gráfico no clasifica localidades como buenas o malas. Muestra dónde existen condiciones territoriales más favorables —o más frágiles— para hablar de corresponsabilidad, transparencia y pedagogía tributaria.",
        "Construcción propia con Cumplimiento Impuesto Predial 2007-2023 y Encuesta Multipropósito 2021 / Variables Adicionales EM2021."
    )

    # 2 Quadrants
    fig2 = px.scatter(cuadrantes, x="ITCC", y="tasa_pago_oportuno", color="cuadrante", size="predios_obligados",
                      hover_name="NOMBRE_LOCALIDAD", title="Cuadrantes de decisión: confianza territorial vs cumplimiento predial",
                      labels={"ITCC": "ITCC (0-100)", "tasa_pago_oportuno": "Tasa de pago oportuno (%)"}, template=template)
    fig2.add_vline(x=cuadrantes["ITCC"].median(), line_dash="dash", line_color="gray")
    fig2.add_hline(y=cuadrantes["tasa_pago_oportuno"].median(), line_dash="dash", line_color="gray")
    add_section(
        "2. Modelo de decisión pública: cuatro estrategias, no una campaña genérica",
        fig2,
        "La innovación no es solo graficar. Es convertir datos abiertos en una matriz de decisión: reconocer donde hay cumplimiento, explicar donde hay distancia y priorizar transparencia donde más se necesita.",
        "Construcción propia con ITCC y Cumplimiento Impuesto Predial 2007-2023."
    )

    # 3 Aporte annual
    fig3 = px.line(aporte_anual, x="ANO_PRESENTACION", y="valor_aporte", markers=True,
                   title="Evolución del aporte voluntario predial", labels={"ANO_PRESENTACION": "Año", "valor_aporte": "Valor aportado"}, template=template)
    fig3.update_traces(line_color=secondary)
    add_section(
        "3. Aporte voluntario: una señal de confianza que ya existe",
        fig3,
        "Detrás de cada punto no hay solamente recaudo; hay una decisión voluntaria. El reto público es que esa decisión tenga una historia visible, verificable y comprensible para la ciudadanía.",
        "Recaudo Aporte Voluntario Impuesto Predial 2006-2023, Secretaría Distrital de Hacienda."
    )

    # 4 Aporte estrato últimos años
    last = int(aporte_estrato["ANO_PRESENTACION"].max()) if not aporte_estrato.empty else None
    e = aporte_estrato[aporte_estrato["ANO_PRESENTACION"] == last].copy() if last else aporte_estrato
    fig4 = px.bar(e, x="ESTRATO", y="valor_aporte", color="ESTRATO",
                  title=f"Aporte voluntario por estrato ({last})", labels={"ESTRATO": "Estrato", "valor_aporte": "Valor aportado"}, template=template)
    add_section(
        "4. Pedagogía diferenciada: no todos los territorios ni estratos necesitan el mismo mensaje",
        fig4,
        "El aporte por estrato permite diseñar comunicación tributaria con enfoque diferencial. No se trata de presionar más: se trata de explicar mejor según la realidad social y económica.",
        "Recaudo Aporte Voluntario Impuesto Predial 2006-2023, Secretaría Distrital de Hacienda."
    )

    # 5 Morosidad
    fig5 = px.bar(cumplimiento_loc.sort_values("tasa_morosidad", ascending=True), x="tasa_morosidad", y="NOMBRE_LOCALIDAD", orientation="h",
                  title="Morosidad predial por localidad", labels={"tasa_morosidad": "Tasa de morosidad (%)", "NOMBRE_LOCALIDAD": "Localidad"}, template=template)
    fig5.update_traces(marker_color=danger)
    add_section(
        "5. Donde hay fricción, debe haber más explicación",
        fig5,
        "La morosidad no debe leerse como juicio moral. Es una señal de fricción territorial que puede orientar pedagogía, servicio, transparencia y acompañamiento institucional.",
        "Cumplimiento Impuesto Predial 2007-2023, Secretaría Distrital de Hacienda."
    )

    # 6 Pago promedio
    fig6 = px.scatter(cumplimiento_loc, x="predios_obligados", y="total_pagado", size="tasa_pago_oportuno", color="tasa_morosidad",
                      hover_name="NOMBRE_LOCALIDAD", title="Escala tributaria territorial: predios obligados vs total pagado",
                      labels={"predios_obligados": "Predios obligados", "total_pagado": "Total pagado", "tasa_morosidad": "Morosidad (%)"}, template=template)
    add_section(
        "6. La ciudad tributaria también tiene territorio",
        fig6,
        "El cumplimiento predial no ocurre en abstracto. Tiene escala, concentración y diferencias territoriales. Por eso una estrategia de cultura tributaria debe ser territorial, no genérica.",
        "Cumplimiento Impuesto Predial 2007-2023, Secretaría Distrital de Hacienda."
    )

    # 7 PP projects if available
    if pp_av is not None and not pp_av.empty and "NOMBRE_LOCALIDAD" in pp_av.columns:
        fig7 = px.bar(pp_av.sort_values("propuestas", ascending=True), x="propuestas", y="NOMBRE_LOCALIDAD", orientation="h",
                      title="Propuestas priorizadas por ciudadanía", labels={"propuestas": "Número de propuestas", "NOMBRE_LOCALIDAD": "Localidad"}, template=template)
        fig7.update_traces(marker_color=purple)
        add_section(
            "7. De la contribución al proyecto visible",
            fig7,
            "Presupuestos participativos permite mostrar que la ciudadanía no solo paga: también prioriza, decide y propone. Es una fuente clave para conectar datos con sentido público.",
            "Presupuestos Participativos Bogotá D.C., Secretaría Distrital de Planeación."
        )
    else:
        fig7 = go.Figure()
        fig7.add_annotation(text="Presupuestos participativos: fuente documentada para carga en Colab/entorno con acceso a ODS o API CKAN", x=0.5, y=0.5, showarrow=False, font_size=18)
        add_section(
            "7. Proyectos visibles: fuente preparada",
            fig7,
            "La estructura del análisis deja lista la integración de propuestas y presupuesto participativo como evidencia territorial de proyectos visibles. Si la descarga ODS no está disponible, la limitación queda documentada.",
            "Presupuestos Participativos Bogotá D.C., Secretaría Distrital de Planeación."
        )

    # 8 Brechas
    b = brechas_trazabilidad()
    fig8 = go.Figure(data=[go.Table(
        header=dict(values=["Brecha", "Riesgo", "Respuesta metodológica"], fill_color="#111827", font=dict(color="white"), align="left"),
        cells=dict(values=[b["brecha"], b["riesgo"], b["respuesta_metodologica"]], fill_color="#f9fafb", align="left")
    )])
    fig8.update_layout(title="Brechas de trazabilidad: límites convertidos en propuesta pública")
    add_section(
        "8. Rigor: lo que no podemos afirmar también importa",
        fig8,
        "Una propuesta ganadora no oculta sus límites. Los convierte en agenda de mejora: mejores metadatos, llaves de integración y visualización pública para rendición de cuentas.",
        "Síntesis metodológica del equipo a partir de las fuentes integradas."
    )

    kpis = {
        "aporte_total": float(aporte_anual["valor_aporte"].sum()),
        "contribuyentes_total": float(aporte_anual["contribuyentes"].sum()),
        "anio_inicio": int(aporte_anual["ANO_PRESENTACION"].min()),
        "anio_fin": int(aporte_anual["ANO_PRESENTACION"].max()),
        "localidades": int(cumplimiento_loc["CODIGO_LOCALIDAD"].nunique()),
        "mejor_itcc": str(itcc.iloc[0]["NOMBRE_LOCALIDAD"]) if not itcc.empty else "N/D",
    }
    with open(OUT_DIR / "kpis.json", "w", encoding="utf-8") as f:
        json.dump(kpis, f, ensure_ascii=False, indent=2)

    html = f"""
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <title>Confianza que Construye Ciudad</title>
      <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
      <style>
        body {{font-family: Inter, Arial, sans-serif; margin: 0; color: #111827; background: #f3f4f6;}}
        header {{background: linear-gradient(120deg, #0f172a, #1e3a8a); color: white; padding: 44px 64px;}}
        header h1 {{font-size: 44px; margin: 0 0 10px;}}
        header p {{font-size: 20px; max-width: 1000px; line-height: 1.45;}}
        .kpis {{display:grid; grid-template-columns: repeat(4, 1fr); gap: 16px; padding: 26px 64px;}}
        .kpi {{background:white; border-radius:18px; padding:22px; box-shadow:0 10px 30px rgba(0,0,0,.07);}}
        .kpi b {{display:block; font-size:24px; color:#1e3a8a;}}
        .kpi span {{font-size:13px; color:#4b5563;}}
        .card {{background:white; margin: 22px 64px; padding: 28px; border-radius: 22px; box-shadow:0 10px 35px rgba(0,0,0,.08);}}
        .card h2 {{margin-top:0; font-size:26px;}}
        .review {{background:#eff6ff; border-left:6px solid #2563eb; padding:16px 18px; border-radius:10px; margin-top:12px; font-size:16px; line-height:1.5;}}
        .source {{font-size:12px; color:#4b5563; margin-top:10px;}}
        .closing {{background:#111827; color:white; margin:32px 0 0; padding: 42px 64px; font-size:22px; line-height:1.5;}}
        .credits {{background:#0b1220; color:#e5e7eb; padding: 34px 64px;}}
        .credits h3 {{margin:0; font-size:18px;}}
        .credits h3 span {{display:block; font-weight:400; color:#9ca3af; font-size:14px; margin-top:4px;}}
        .credits ul {{list-style:none; margin:16px 0 0; padding:0; line-height:1.7; font-size:15px;}}
        .credits li b {{color:#fff;}}
        .credits li .role {{color:#9ca3af;}}
        .credits .meta {{margin-top:16px; color:#9ca3af; font-size:13px;}}
        @media (max-width: 900px) {{.kpis{{grid-template-columns:1fr; padding: 20px;}} .card{{margin:20px;}} header{{padding:30px 24px;}} .closing,.credits{{padding:26px 24px;}}}}
      </style>
    </head>
    <body>
      <header>
        <h1>Confianza que Construye Ciudad</h1>
        <p><b>¿Qué tanto puede explicar la ciudad?</b><br>
        Cómo los datos abiertos pueden fortalecer la cultura tributaria mediante transparencia, reconocimiento ciudadano y evidencia territorial.</p>
      </header>
      <div class="kpis">
        <div class="kpi"><b>${kpis['aporte_total']:,.0f}</b><span>Aporte voluntario predial acumulado {kpis['anio_inicio']}-{kpis['anio_fin']}</span></div>
        <div class="kpi"><b>{kpis['contribuyentes_total']:,.0f}</b><span>Registros de contribuyentes aportantes acumulados</span></div>
        <div class="kpi"><b>{kpis['localidades']}</b><span>Localidades con diagnóstico territorial</span></div>
        <div class="kpi"><b>{kpis['mejor_itcc']}</b><span>Mayor condición territorial ITCC en esta ejecución</span></div>
      </div>
      {''.join(figs_html)}
      <div class="closing">
        <p><b>No presentamos un tablero. Presentamos una forma de reconstruir confianza.</b></p>
        <p>Durante años hemos intentado convencer a la ciudadanía de aportar más. Tal vez la pregunta correcta era cuánto más puede explicar la ciudad. Porque la confianza no se decreta: se demuestra.</p>
      </div>
      <footer class="credits">
        <h3>Equipo: SOLUTIONSCITY <span>en representación de Caja de Vivienda Popular — CVP</span></h3>
        <ul>
          <li><span class="role">Perfil técnico en análisis y visualización de datos —</span> <b>Julio Esteban Fuentes Herrera</b></li>
          <li><span class="role">Perfil de análisis sectorial o de política pública —</span> <b>Juan Carlos Sanabria Medina</b></li>
          <li><span class="role">Perfil complementario (temático, metodológico o técnico) —</span> <b>Diego Gonzalez Quiroga</b></li>
        </ul>
        <p class="meta">DATAJAM 2 — Dirección de Innovación Pública y Estado Abierto · Fuentes: Secretaría Distrital de Hacienda · Secretaría Distrital de Planeación (EM2021)</p>
      </footer>
    </body></html>
    """
    path = OUT_DIR / "dashboard_confianza_que_construye_ciudad.html"
    path.write_text(html, encoding="utf-8")
    return path

def write_markdown_outputs(aporte_anual, itcc, cuadrantes):
    top = itcc.head(3)[["NOMBRE_LOCALIDAD", "ITCC", "tasa_pago_oportuno", "tasa_morosidad"]].copy()
    txt = f"""# Resumen ejecutivo de hallazgos

## Tesis del proyecto
Bogotá no necesita pedir confianza a ciegas: puede demostrarla con datos abiertos. El análisis integra aporte voluntario, cumplimiento predial, condiciones territoriales y proyectos visibles para orientar estrategias diferenciadas de cultura tributaria.

## Hallazgos principales
1. El aporte voluntario predial tiene trazabilidad temporal y por estrato, pero no una llave territorial pública; por eso no se atribuye el aporte a localidades ni a proyectos específicos.
2. El cumplimiento predial sí permite lectura territorial por localidad, UPZ, barrio y estrato, lo que habilita estrategias diferenciadas de pedagogía, transparencia y reconocimiento.
3. El ITCC experimental clasifica condiciones territoriales para la corresponsabilidad sin afirmar causalidad individual.
4. Los cuadrantes de decisión permiten pasar de una campaña genérica a cuatro estrategias públicas: embajadores, comunicación de beneficios, reconocimiento y transparencia prioritaria.

## Top 3 ITCC en esta ejecución
{top.to_markdown(index=False)}

## Límite más importante
Este análisis no prueba que una persona aporte voluntariamente por ver proyectos. Identifica condiciones territoriales y brechas de trazabilidad que pueden orientar mejor la política pública.
"""
    (OUT_DIR / "resumen_hallazgos.md").write_text(txt, encoding="utf-8")

    speech = """# Pitch de 3 minutos — Confianza que Construye Ciudad

Buenos días.

Quiero empezar con una pregunta que cualquier persona podría hacerse frente a un recibo de impuesto:

**Si yo hago un aporte voluntario, ¿la ciudad me puede mostrar dónde se ve?**

No es una pregunta menor. Detrás de esa pregunta no hay solo dinero. Hay confianza. Hay una persona que decide hacer algo adicional sin estar obligada.

Nuestra propuesta se llama **Confianza que Construye Ciudad**.

No venimos a decir que si la gente ve un proyecto automáticamente va a pagar más. Eso sería una afirmación causal que los datos disponibles no permiten demostrar.

Lo que sí demostramos es algo más útil para la gestión pública: Bogotá tiene datos sobre aporte voluntario, cumplimiento predial, condiciones territoriales y proyectos priorizados por ciudadanía, pero esa información está fragmentada. Para una persona común, el dato existe, pero no siempre se entiende ni se conecta.

Por eso construimos el **Índice Territorial de Confianza para la Corresponsabilidad — ITCC**. Es un índice experimental, transparente y reproducible que no mide comportamientos individuales, sino condiciones territoriales para orientar estrategias públicas.

Luego cruzamos ese índice con cumplimiento predial y morosidad, y construimos cuatro cuadrantes de decisión:

- Donde hay mejores condiciones y alto cumplimiento: activar embajadores ciudadanos.
- Donde hay buenas condiciones pero menor cumplimiento: comunicar mejor beneficios.
- Donde hay alto cumplimiento pero condiciones de confianza más frágiles: reconocer y agradecer.
- Donde ambas dimensiones son más bajas: priorizar transparencia, pedagogía y presencia institucional.

La innovación no es el dashboard. La innovación es que la ciudad deja de hablarle igual a territorios distintos.

Nuestra recomendación es crear un programa permanente: **Confianza que Construye Ciudad**, con cinco líneas: trazabilidad ciudadana, reconocimiento inteligente, pedagogía diferenciada, actualización periódica del ITCC y gobierno abierto basado en evidencia.

Durante años hemos intentado convencer a la ciudadanía de aportar más.

Tal vez la pregunta correcta nunca fue cuánto más puede aportar la gente.

Tal vez la pregunta era cuánto más puede explicar la ciudad.

Porque la confianza no se decreta.

La confianza se demuestra.

Y cuando una ciudad demuestra con datos abiertos cómo escucha, cómo invierte y cómo rinde cuentas, el aporte deja de ser un pago adicional y se convierte en un acto de pertenencia.

**No presentamos un tablero. Presentamos una forma de reconstruir la confianza entre Bogotá y su ciudadanía.**
"""
    (DOCS_DIR / "pitch_3_minutos.md").write_text(speech, encoding="utf-8")

    fuentes_md = "# Fuentes y rutas de extracción\n\n" + source_manifest().to_markdown(index=False)
    (DOCS_DIR / "fuentes_y_rutas.md").write_text(fuentes_md, encoding="utf-8")

    nota = """# Nota técnica sobre integración de datos públicos

**Proyecto:** Confianza que Construye Ciudad  
**Propósito:** integrar fuentes públicas para orientar estrategias territoriales de cultura tributaria, transparencia y reconocimiento ciudadano.

## Fuentes integradas
Se utilizaron fuentes del Portal de Datos Abiertos Bogotá sobre aporte voluntario predial, cumplimiento predial, Encuesta Multipropósito 2021 / variables adicionales y presupuestos participativos. También se incluye una fuente documental oficial de contexto sobre la tarjeta conmemorativa del Metro para contribuyentes con aporte voluntario.

## Integración técnica
La integración se realiza por tres niveles:
1. Temporal: evolución del aporte voluntario por año.
2. Socioeconómico/estrato: aporte voluntario y condiciones de contribución por estrato.
3. Territorial: cumplimiento predial, condiciones EM y proyectos por localidad.

## Limitaciones
- El dataset de aporte voluntario predial no incluye localidad; por tanto, no se cruza territorialmente ni se atribuye a proyectos.
- Los proyectos de presupuestos participativos no son presentados como destino directo del aporte voluntario.
- El ITCC no mide causalidad ni comportamiento individual; resume condiciones territoriales observables.
- Las fuentes tienen diferentes cortes temporales.

## Recomendaciones
1. Publicar una llave territorial o agregación local del aporte voluntario preservando privacidad.
2. Crear metadatos que indiquen claramente destinación, programa o sector asociado al aporte.
3. Mantener un índice público de condiciones territoriales para corresponsabilidad.
4. Desarrollar un visor ciudadano que explique aporte, proyectos, límites y avances con lenguaje sencillo.
"""
    (DOCS_DIR / "nota_tecnica_integracion.md").write_text(nota, encoding="utf-8")

def main():
    print("1/7 Cargando aporte voluntario...")
    aporte_raw = load_aporte_predial()
    aporte = transform_aporte(aporte_raw)

    print("2/7 Cargando cumplimiento predial...")
    cumplimiento_raw = load_cumplimiento()
    cumplimiento_loc = transform_cumplimiento(cumplimiento_raw)

    print("3/7 Cargando Encuesta Multipropósito / variables adicionales...")
    # Versión rápida (por defecto): NO se descarga la EM2021 (archivo grande) y el ITCC
    # queda con componentes territoriales homogéneos para las 20 localidades. Para intentar
    # incorporar el componente social, exportar USAR_EM_COMPLETA=true antes de ejecutar.
    if USAR_EM_COMPLETA:
        try:
            em_add = load_em_adicionales(sample=False)
        except Exception as e:
            print("No se pudo cargar variables adicionales completas; usando muestra vacía:", e)
            em_add = pd.DataFrame()
    else:
        print("   (versión rápida: EM2021 omitida; ITCC territorial homogéneo)")
        em_add = pd.DataFrame()

    print("4/7 Construyendo ITCC experimental...")
    if not em_add.empty:
        itcc, componentes_itcc = build_itcc_from_em_adicionales(em_add, cumplimiento_loc)
    else:
        itcc = cumplimiento_loc.copy()
        itcc["score_cumplimiento"] = minmax(itcc["tasa_pago_oportuno"])
        itcc["score_morosidad_inversa"] = minmax(itcc["tasa_morosidad"], invert=True)
        comp_itcc = ["score_cumplimiento", "score_morosidad_inversa"]
        itcc["componentes_itcc"] = ", ".join(comp_itcc)
        itcc["ITCC"] = itcc[comp_itcc].mean(axis=1)
        itcc["version_itcc"] = "ITCC territorial homogéneo: cumplimiento (pago oportuno) + morosidad inversa, iguales para las 20 localidades"
        itcc["limitacion_itcc"] = "No mide confianza individual; resume condiciones territoriales observables. Componente social EM2021 no incorporado en esta ejecución."
        itcc = itcc.sort_values("ITCC", ascending=False)
        componentes_itcc = pd.DataFrame({"componente_usado": comp_itcc})

    print("5/7 Cargando presupuestos participativos...")
    pp_av, pp_pr = transform_pp()

    print("6/7 Generando indicadores y dashboard...")
    cuadrantes = classify_quadrants(itcc)
    dashboard_path = make_dashboard(aporte["aporte_anual"], aporte["aporte_estrato"], cumplimiento_loc, itcc, cuadrantes, pp_av, pp_pr)

    print("7/7 Guardando salidas...")
    save_df(aporte_raw, "aporte_voluntario_predial_limpio.csv")
    save_df(aporte["aporte_anual"], "aporte_voluntario_anual.csv")
    save_df(aporte["aporte_estrato"], "aporte_voluntario_estrato.csv")
    save_df(cumplimiento_loc, "cumplimiento_predial_localidad.csv")
    save_df(itcc, "itcc_localidad.csv")
    save_df(cuadrantes, "cuadrantes_decision_publica.csv")
    save_df(componentes_itcc, "componentes_itcc.csv")
    save_df(brechas_trazabilidad(), "brechas_trazabilidad.csv")
    if pp_av is not None and not pp_av.empty:
        save_df(pp_av, "presupuestos_participativos_avance_localidad.csv")
    if pp_pr is not None and not pp_pr.empty:
        save_df(pp_pr, "presupuestos_participativos_presupuesto_localidad_sector.csv")
    save_df(source_manifest(), "fuentes_datos_manifest.csv")
    write_markdown_outputs(aporte["aporte_anual"], itcc, cuadrantes)
    print("\nListo. Dashboard:", dashboard_path)
    print("Salidas en:", OUT_DIR)

if __name__ == "__main__":
    main()
