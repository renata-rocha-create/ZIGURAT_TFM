"""
♿ Auditor de Acessibilidade BIM — NBR 9050:2020
Streamlit App — Verificação Automatizada de Conformidade
Master Internacional em IA para Arquitetura e Construção — Zigurat Institute of Technology
"""

import streamlit as st
import json
import os
import re
import time
import tempfile
import io
from pathlib import Path
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Auditor NBR 9050 — BIM",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>

:root {
    /* ── Zigurat brand palette ── */
    --zk-slate:   rgb(77,83,99);       /* #4D5363 — texto principal, sidebar */
    --zk-green:   rgb(68,205,148);     /* #44CD94 — accent primário */
    --zk-blue:    rgb(28,96,241);      /* #1C60F1 — accent secundário / links */

    --bg:         #ffffff;
    --surface:    #f4f6f9;
    --surface2:   #eaecf1;
    --border:     #d1d5de;
    --text:       rgb(77,83,99);
    --muted:      #8e95a6;
    --success:    #1ab87a;
    --danger:     #e03c3c;
    --warn:       #e8920a;

    --font: 'Trebuchet MS', Trebuchet, Arial, sans-serif;
    --mono: 'Courier New', Courier, monospace;
}

/* ── Global reset to white + Trebuchet ── */
html, body, [class*="css"], .stApp {
    font-family: var(--font) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background-color: var(--bg) !important; }

/* ── Sidebar — slate escuro ── */
[data-testid="stSidebar"] {
    background: var(--zk-slate) !important;
    border-right: 1px solid #3a3f4f !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; font-family: var(--font) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSlider label { color: #c8ccd6 !important; font-size: 0.78rem !important; }

/* ── Hero banner ── */
.hero-block {
    background: linear-gradient(120deg, rgb(77,83,99) 0%, rgb(50,56,72) 100%);
    border-radius: 10px;
    padding: 1.75rem 2rem 1.75rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.hero-block::after {
    content: '';
    position: absolute;
    bottom: -30px; left: -30px;
    width: 180px; height: 180px;
    background: rgba(68,205,148,0.08);
    border-radius: 50%;
}
.hero-left {}
.hero-title {
    font-family: var(--font);
    font-size: 1.75rem;
    font-weight: 700;
    color: rgb(68,205,148);
    margin: 0 0 0.2rem 0;
}
.hero-sub {
    font-family: var(--font);
    font-size: 0.72rem;
    color: rgba(255,255,255,0.55);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.hero-logo {
    height: 36px;
    opacity: 0.92;
    flex-shrink: 0;
    filter: brightness(0) invert(1);
}

/* ── Section titles ── */
.section-title {
    font-family: var(--font);
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--zk-blue);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: var(--font);
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-conforme { background: rgba(26,184,122,0.12); color: #0e8a58;  border: 1px solid rgba(26,184,122,0.35); }
.badge-nao      { background: rgba(224,60,60,0.10);  color: #b52929;  border: 1px solid rgba(224,60,60,0.35); }
.badge-indet    { background: rgba(232,146,10,0.12); color: #a05e00;  border: 1px solid rgba(232,146,10,0.35); }
.badge-na       { background: rgba(77,83,99,0.08);   color: var(--muted); border: 1px solid rgba(77,83,99,0.2); }

/* ── Result table ── */
.result-table { width: 100%; border-collapse: collapse; font-size: 0.81rem; }
.result-table th {
    font-family: var(--font);
    font-size: 0.67rem;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 2px solid var(--zk-blue);
    padding: 9px 12px;
    text-align: left;
    background: var(--zk-slate);
}
.result-table td {
    padding: 9px 12px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
    color: var(--text);
}
.result-table tr:hover td { background: rgba(68,205,148,0.05); }

/* ── GlobalId chip ── */
.globalid {
    font-family: var(--mono);
    font-size: 0.67rem;
    background: #eef1f8;
    border: 1px solid #c5cad8;
    border-radius: 4px;
    padding: 2px 6px;
    color: var(--zk-blue);
    display: inline-block;
}

/* ── Metric cards ── */
.metric-row { display: flex; gap: 0.85rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    flex: 1;
    min-width: 110px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--zk-green);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.metric-num {
    font-family: var(--font);
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.metric-label {
    font-family: var(--font);
    font-size: 0.62rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.c-green { color: var(--success); }
.c-red   { color: var(--danger);  }
.c-amber { color: var(--warn);    }
.c-blue  { color: var(--zk-blue); }
.c-muted { color: var(--muted);   }

/* ── Terminal / log ── */
.terminal {
    background: rgb(77,83,99);
    border: 1px solid #3a3f4f;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-family: var(--mono);
    font-size: 0.74rem;
    color: rgb(68,205,148);
    max-height: 280px;
    overflow-y: auto;
    line-height: 1.7;
}

/* ── Form inputs ── */
.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--zk-green) !important;
    box-shadow: 0 0 0 2px rgba(68,205,148,0.2) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--zk-green) !important; }

/* ── Buttons ── */
.stButton button {
    background: var(--zk-green) !important;
    color: rgb(77,83,99) !important;
    font-family: var(--font) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    background: rgb(28,96,241) !important;
    color: #fff !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(28,96,241,0.25) !important;
}
.stButton button:disabled {
    background: var(--border) !important;
    color: var(--muted) !important;
    transform: none !important;
}

/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {
    background: var(--surface) !important;
    color: var(--zk-blue) !important;
    border: 1.5px solid var(--zk-blue) !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--zk-blue) !important;
    color: #fff !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    color: var(--text) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    color: var(--muted) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--zk-blue) !important;
    border-bottom-color: var(--zk-blue) !important;
}

/* ── Info / warning boxes ── */
.info-box {
    background: rgba(28,96,241,0.06);
    border-left: 3px solid var(--zk-blue);
    border-radius: 0 6px 6px 0;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #1a47a8;
    margin: 0.75rem 0;
}
.warn-box {
    background: rgba(232,146,10,0.08);
    border-left: 3px solid var(--warn);
    border-radius: 0 6px 6px 0;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #7a4500;
    margin: 0.75rem 0;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Pulse animation ── */
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(68,205,148,0.4); } 50% { box-shadow: 0 0 0 8px rgba(68,205,148,0); } }

/* ── Slider track ── */
.stSlider [data-baseweb="slider"] { background: var(--border) !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def extract_ifc_elements(ifc_path: str) -> dict:
    """Extract relevant IFC elements for NBR 9050 check. Returns dict."""
    try:
        import ifcopenshell
        import ifcopenshell.util.element as ifc_util
    except ImportError:
        return {"error": "ifcopenshell não instalado. Execute: pip install ifcopenshell"}

    ifc = ifcopenshell.open(ifc_path)
    schema = ifc.schema

    PROPS_RELEVANTES = {
        "overallwidth", "overallheight", "overallrise", "overallrun",
        "mountingheight", "sillheight", "riserheight", "treadlength",
        "numberofrisers", "numberoftreads", "width", "height", "area"
    }

    def psets_de(el):
        psets = {}
        try:
            for rel in getattr(el, "IsDefinedBy", []):
                if rel.is_a("IfcRelDefinesByProperties"):
                    pdef = rel.RelatingPropertyDefinition
                    if pdef.is_a("IfcPropertySet"):
                        props = {}
                        for p in pdef.HasProperties:
                            if p.Name.lower() in PROPS_RELEVANTES:
                                val = None
                                if hasattr(p, "NominalValue") and p.NominalValue:
                                    val = p.NominalValue.wrappedValue
                                props[p.Name] = val
                        if props:
                            psets[pdef.Name] = props
        except Exception:
            pass
        return psets

    def info_basica(el):
        return {
            "GlobalId":    el.GlobalId,
            "Name":        getattr(el, "Name", None),
            "ObjectType":  getattr(el, "ObjectType", None),
            "Tag":         getattr(el, "Tag", None),
            "Description": getattr(el, "Description", None),
        }

    def limpar_nulos(obj):
        if isinstance(obj, dict):
            return {k: limpar_nulos(v) for k, v in obj.items() if v is not None}
        if isinstance(obj, list):
            return [limpar_nulos(i) for i in obj]
        return obj

    ENTIDADES_SANITARIO = ["IfcFlowTerminal", "IfcFurnishingElement"] if schema == "IFC2X3" \
                          else ["IfcSanitaryTerminal", "IfcFlowTerminal"]

    resultado = {"schema": schema, "arquivo": Path(ifc_path).name, "elementos": {}}

    # Portas
    portas = []
    for el in ifc.by_type("IfcDoor"):
        d = info_basica(el)
        d["OverallWidth"]  = getattr(el, "OverallWidth", None)
        d["OverallHeight"] = getattr(el, "OverallHeight", None)
        d["Psets"] = psets_de(el)
        portas.append(d)
    resultado["elementos"]["IfcDoor"] = portas[:50]

    # Rampas
    rampas = []
    for tipo in ["IfcRamp", "IfcRampFlight"]:
        for el in ifc.by_type(tipo):
            d = info_basica(el)
            d["tipo_ifc"] = tipo
            d["OverallRise"] = getattr(el, "OverallRise", None)
            d["OverallRun"]  = getattr(el, "OverallRun", None)
            d["Psets"] = psets_de(el)
            rampas.append(d)
    for el in ifc.by_type("IfcSlab"):
        nome  = (getattr(el, "Name", "") or "").lower()
        otype = (getattr(el, "ObjectType", "") or "").lower()
        if any(t in nome + otype for t in ["rampa", "ramp", "rmp"]):
            d = info_basica(el)
            d["tipo_ifc"] = "IfcSlab(rampa-fallback)"
            d["Psets"] = psets_de(el)
            rampas.append(d)
    resultado["elementos"]["Rampas"] = rampas

    # Escadas
    escadas = []
    for tipo in ["IfcStair", "IfcStairFlight"]:
        for el in ifc.by_type(tipo):
            d = info_basica(el)
            d["tipo_ifc"] = tipo
            d["NumberOfRisers"] = getattr(el, "NumberOfRisers", None)
            d["RiserHeight"]    = getattr(el, "RiserHeight", None)
            d["TreadLength"]    = getattr(el, "TreadLength", None)
            d["Psets"] = psets_de(el)
            escadas.append(d)
    resultado["elementos"]["Escadas"] = escadas

    # Espaços
    espacos = []
    for el in ifc.by_type("IfcSpace"):
        d = info_basica(el)
        d["LongName"] = getattr(el, "LongName", None)
        psets = psets_de(el)
        d["Psets"] = psets
        espacos.append(d)
    resultado["elementos"]["IfcSpace"] = espacos[:30]

    # Sanitários
    sanitarios = []
    termos_san = ["bacia","vaso","wc","lavatório","lavatorio","chuveiro","ducha","mictório","mictorio","sanit","toilet","sink","basin","shower"]
    for tipo in ENTIDADES_SANITARIO:
        for el in ifc.by_type(tipo):
            nome  = (getattr(el, "Name", "") or "").lower()
            otype = (getattr(el, "ObjectType", "") or "").lower()
            desc  = (getattr(el, "Description", "") or "").lower()
            incluir = (tipo == "IfcFlowTerminal" and schema == "IFC2X3") or \
                      any(t in nome + otype + desc for t in termos_san)
            if incluir:
                d = info_basica(el)
                d["tipo_ifc"] = tipo
                psets = psets_de(el)
                d["Psets"] = psets
                altura = None
                for ps in psets.values():
                    for k, v in ps.items():
                        if "height" in k.lower() or "altura" in k.lower():
                            altura = v
                d["MountingHeight"] = altura
                sanitarios.append(d)
    resultado["elementos"]["Sanitarios"] = sanitarios

    # Janelas
    janelas = []
    for el in ifc.by_type("IfcWindow"):
        d = info_basica(el)
        d["OverallWidth"]  = getattr(el, "OverallWidth", None)
        d["OverallHeight"] = getattr(el, "OverallHeight", None)
        d["Psets"] = psets_de(el)
        janelas.append(d)
    resultado["elementos"]["IfcWindow"] = janelas[:30]

    # Corrimões
    corrimaos = []
    for tipo in ["IfcRailing", "IfcBuildingElementProxy"]:
        for el in ifc.by_type(tipo):
            nome  = (getattr(el, "Name", "") or "").lower()
            otype = (getattr(el, "ObjectType", "") or "").lower()
            if tipo == "IfcRailing" or any(t in nome + otype for t in ["corrimao","handrail","guard"]):
                d = info_basica(el)
                d["tipo_ifc"] = tipo
                d["Psets"] = psets_de(el)
                corrimaos.append(d)
    resultado["elementos"]["Corrimaos"] = corrimaos

    # Pisos
    pisos = []
    for el in ifc.by_type("IfcSlab"):
        d = info_basica(el)
        d["Psets"] = psets_de(el)
        pisos.append(d)
    resultado["elementos"]["IfcSlab"] = pisos[:20]

    # Barras de apoio
    barras = []
    for tipo in ["IfcFurnishingElement", "IfcBuildingElementProxy"]:
        for el in ifc.by_type(tipo):
            nome  = (getattr(el, "Name", "") or "").lower()
            desc  = (getattr(el, "Description", "") or "").lower()
            otype = (getattr(el, "ObjectType", "") or "").lower()
            if any(t in nome + desc + otype for t in ["barra","apoio","grab bar"]):
                d = info_basica(el)
                d["tipo_ifc"] = tipo
                d["Psets"] = psets_de(el)
                barras.append(d)
    resultado["elementos"]["BarrasApoio"] = barras

    return limpar_nulos(resultado)


def read_xlsx_items(xlsx_bytes: bytes) -> list[dict]:
    """Read NBR items from uploaded Excel file."""
    try:
        import pandas as pd
        df = pd.read_excel(io.BytesIO(xlsx_bytes))
        return df.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]


def build_audit_prompt(elementos: dict, norma_items: list, modelo_nome: str) -> str:
    """Build the LLM prompt for NBR 9050 audit."""
    elementos_json = json.dumps(elementos, ensure_ascii=False, default=str)[:60000]
    norma_json = json.dumps(norma_items, ensure_ascii=False)[:8000] if norma_items else "Usar os 12 itens padrão da NBR 9050:2020"

    return f"""Você é um especialista em acessibilidade arquitetônica e norma ABNT NBR 9050:2020.

Analise os elementos BIM extraídos do modelo IFC "{modelo_nome}" e verifique a conformidade com a NBR 9050:2020.

## ITENS NORMATIVOS A VERIFICAR
{norma_json}

## ELEMENTOS EXTRAÍDOS DO MODELO IFC
{elementos_json}

## INSTRUÇÕES
Para cada item normativo, gere um resultado com:
1. **item_nbr**: código do item (ex: "6.11.2")
2. **categoria**: Rampas | Portas | Corredores | Sanitários | Escadas | Pisos | Janelas | Circulação
3. **elemento**: descrição do elemento analisado
4. **globalid**: GlobalId do elemento no IFC (OBRIGATÓRIO quando encontrado — usado para filtro no Revit/BIM)
5. **tipo_ifc**: entidade IFC (ex: IfcDoor, IfcRamp)
6. **valor_encontrado**: dimensão/condição encontrada no modelo
7. **valor_exigido**: requisito da norma
8. **status**: "Conforme" | "Não Conforme" | "Indeterminado" | "N/A"
9. **recomendacao**: ação corretiva se não conforme, ou motivo se indeterminado

## FORMATO DE RESPOSTA
Responda SOMENTE com JSON válido, sem markdown, sem texto extra:

{{
  "modelo": "{modelo_nome}",
  "schema_ifc": "IFC2X3 ou IFC4",
  "data_auditoria": "dd/mm/aaaa",
  "resultados": [
    {{
      "item_nbr": "6.11.2",
      "categoria": "Portas",
      "subcategoria": "Vão livre mínimo",
      "elemento": "Porta P01 — Pavimento Térreo",
      "globalid": "0yScVqI2LFdAHBnJsma8Hp",
      "tipo_ifc": "IfcDoor",
      "valor_encontrado": "0,78m × 2,10m",
      "valor_exigido": "≥ 0,80m × 2,10m",
      "status": "Não Conforme",
      "recomendacao": "Ampliar vão livre para mínimo de 0,80m conforme NBR 9050 item 6.11.2."
    }}
  ],
  "resumo": {{
    "total": 12,
    "conformes": 5,
    "nao_conformes": 3,
    "indeterminados": 3,
    "na": 1,
    "percentual_conformidade": "62%"
  }},
  "observacoes_gerais": "Texto com análise geral do modelo..."
}}
"""


def call_anthropic(api_key: str, model: str, prompt: str, temperature: float) -> dict:
    """Call Anthropic API and return parsed JSON result."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text
    raw_clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw_clean)


def call_gemini(api_key: str, model: str, prompt: str, temperature: float) -> dict:
    """Call Google Gemini API and return parsed JSON result."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)
    resp = m.generate_content(
        prompt,
        generation_config={"temperature": temperature, "max_output_tokens": 4096}
    )
    raw = resp.text
    raw_clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw_clean)


def status_badge(status: str) -> str:
    s = status.lower()
    if "conforme" in s and "não" not in s and "nao" not in s:
        return '<span class="badge badge-conforme">✅ Conforme</span>'
    elif "não" in s or "nao" in s:
        return '<span class="badge badge-nao">❌ Não Conforme</span>'
    elif "indet" in s:
        return '<span class="badge badge-indet">⚠️ Indeterminado</span>'
    else:
        return '<span class="badge badge-na">— N/A</span>'


def gerar_relatorio_html(resultado: dict, modelo_nome: str) -> str:
    """Generate a self-contained HTML report."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    resumo = resultado.get("resumo", {})
    itens = resultado.get("resultados", [])

    rows = ""
    for it in itens:
        gid = it.get("globalid", "—")
        st  = it.get("status", "N/A")
        badge_color = {"conforme": "#10b981", "não conforme": "#ef4444", "indeterminado": "#f59e0b"}.get(st.lower(), "#64748b")
        rows += f"""
        <tr>
          <td><code>{it.get('item_nbr','—')}</code></td>
          <td>{it.get('categoria','—')}</td>
          <td>{it.get('elemento','—')}</td>
          <td style="color:{badge_color};font-weight:600">{st}</td>
          <td>{it.get('valor_encontrado','—')}</td>
          <td>{it.get('valor_exigido','—')}</td>
          <td><code style="color:#3b82f6;font-size:0.75em">{gid}</code></td>
          <td style="color:#94a3b8;font-size:0.85em">{it.get('tipo_ifc','—')}</td>
          <td style="color:#f87171;font-size:0.85em">{it.get('recomendacao','—')}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório NBR 9050 — {modelo_nome}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background: #0a0e1a; color: #e2e8f0; margin: 0; padding: 2rem; }}
  h1 {{ color: #00d4aa; font-size: 1.6rem; border-bottom: 1px solid #1f2d45; padding-bottom: 1rem; }}
  h2 {{ color: #3b82f6; font-size: 1rem; margin-top: 2rem; }}
  .meta {{ color: #64748b; font-size: 0.8rem; margin-bottom: 2rem; font-family: monospace; }}
  .resumo {{ display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap; }}
  .card {{ background: #111827; border: 1px solid #1f2d45; border-radius: 8px; padding: 1rem 1.5rem; text-align: center; min-width: 110px; }}
  .card .num {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
  .card .lbl {{ font-size: 0.65rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 1rem; }}
  th {{ background: #111827; color: #64748b; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; padding: 10px 12px; text-align: left; border-bottom: 1px solid #1f2d45; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #1f2d451a; vertical-align: top; }}
  tr:hover td {{ background: rgba(0,212,170,0.03); }}
  code {{ background: #111827; padding: 2px 6px; border-radius: 4px; font-size: 0.78em; }}
  .obs {{ background: #111827; border-left: 3px solid #00d4aa; padding: 1rem; border-radius: 0 6px 6px 0; margin: 1.5rem 0; font-size: 0.9rem; color: #94a3b8; }}
  .info {{ font-size: 0.78rem; color: #475569; margin-top: 3rem; border-top: 1px solid #1f2d45; padding-top: 1rem; }}
</style>
</head>
<body>
<h1>♿ Relatório de Verificação de Acessibilidade BIM</h1>
<p class="meta">
  Norma: ABNT NBR 9050:2020 &nbsp;|&nbsp;
  Modelo: <strong>{modelo_nome}</strong> &nbsp;|&nbsp;
  Schema IFC: {resultado.get('schema_ifc','—')} &nbsp;|&nbsp;
  Emitido em: {now}
</p>

<h2>Resumo Executivo</h2>
<div class="resumo">
  <div class="card"><div class="num" style="color:#e2e8f0">{resumo.get('total',0)}</div><div class="lbl">Total</div></div>
  <div class="card"><div class="num" style="color:#10b981">{resumo.get('conformes',0)}</div><div class="lbl">Conformes</div></div>
  <div class="card"><div class="num" style="color:#ef4444">{resumo.get('nao_conformes',0)}</div><div class="lbl">Não Conformes</div></div>
  <div class="card"><div class="num" style="color:#f59e0b">{resumo.get('indeterminados',0)}</div><div class="lbl">Indeterminados</div></div>
  <div class="card"><div class="num" style="color:#64748b">{resumo.get('na',0)}</div><div class="lbl">N/A</div></div>
  <div class="card"><div class="num" style="color:#00d4aa">{resumo.get('percentual_conformidade','—')}</div><div class="lbl">Conformidade</div></div>
</div>

<div class="obs">{resultado.get('observacoes_gerais','Sem observações gerais.')}</div>

<h2>Resultados Detalhados por Elemento</h2>
<p style="font-size:0.78rem;color:#64748b">
  💡 A coluna <strong>GlobalId</strong> corresponde ao identificador único do elemento no IFC.
  Use-o no Revit (filtro por GlobalId) ou no BIMcollab/Solibri para localizar o elemento diretamente.
</p>
<table>
  <thead>
    <tr>
      <th>Item NBR</th><th>Categoria</th><th>Elemento</th><th>Status</th>
      <th>Valor Encontrado</th><th>Valor Exigido</th>
      <th>GlobalId (IFC/Revit)</th><th>Tipo IFC</th><th>Recomendação</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>

<div class="info">
  Gerado automaticamente por sistema de IA — uso exclusivamente técnico e acadêmico.<br>
  Verificação manual complementar é necessária para itens qualitativos e indeterminados.
</div>
</body>
</html>"""


def gerar_excel(resultado: dict, modelo_nome: str) -> bytes:
    """Generate XLSX report with openpyxl."""
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    except ImportError:
        return b""

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Checklist NBR 9050"

    # Colors
    H_FILL  = PatternFill("solid", fgColor="0A1628")
    SUB_FILL = PatternFill("solid", fgColor="111827")
    CONF_F  = PatternFill("solid", fgColor="064E3B")
    NAO_F   = PatternFill("solid", fgColor="4C0519")
    INDET_F = PatternFill("solid", fgColor="4B2B06")
    NA_F    = PatternFill("solid", fgColor="1E293B")

    thin = Side(style="thin", color="1F2D45")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # Header
    ws.merge_cells("A1:I1")
    ws["A1"] = f"♿ RELATÓRIO DE ACESSIBILIDADE NBR 9050:2020 — {modelo_nome}"
    ws["A1"].font = Font(bold=True, color="00D4AA", size=12, name="Calibri")
    ws["A1"].fill = H_FILL
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:I2")
    ws["A2"] = f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Schema IFC: {resultado.get('schema_ifc','—')}"
    ws["A2"].font = Font(color="64748B", size=9, italic=True, name="Calibri")
    ws["A2"].fill = SUB_FILL
    ws["A2"].alignment = Alignment(horizontal="center")

    # Column headers
    headers = ["Item NBR", "Categoria", "Elemento", "Status", "Valor Encontrado",
               "Valor Exigido", "GlobalId (Revit/IFC)", "Tipo IFC", "Recomendação"]
    widths   = [12, 16, 32, 16, 20, 20, 32, 18, 45]

    for i, (h, w) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(row=3, column=i, value=h)
        cell.font = Font(bold=True, color="94A3B8", size=9, name="Calibri")
        cell.fill = SUB_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
        ws.column_dimensions[chr(64+i)].width = w
    ws.row_dimensions[3].height = 20

    # Data rows
    status_fills = {
        "conforme": CONF_F, "não conforme": NAO_F, "nao conforme": NAO_F,
        "indeterminado": INDET_F, "n/a": NA_F
    }
    status_colors = {
        "conforme": "10B981", "não conforme": "F87171", "nao conforme": "F87171",
        "indeterminado": "FCD34D", "n/a": "64748B"
    }

    for r, it in enumerate(resultado.get("resultados", []), start=4):
        st_key = it.get("status","").lower()
        fill = status_fills.get(st_key, NA_F)

        values = [
            it.get("item_nbr",""),
            it.get("categoria",""),
            it.get("elemento",""),
            it.get("status",""),
            it.get("valor_encontrado",""),
            it.get("valor_exigido",""),
            it.get("globalid","—"),
            it.get("tipo_ifc",""),
            it.get("recomendacao",""),
        ]
        for c, val in enumerate(values, start=1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.fill = fill
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.font = Font(color="E2E8F0", size=9, name="Calibri")
            if c == 4:
                color = status_colors.get(st_key, "E2E8F0")
                cell.font = Font(color=color, bold=True, size=9, name="Calibri")
            if c == 7:
                cell.font = Font(color="60A5FA", size=9, name="Calibri Mono")
        ws.row_dimensions[r].height = 36

    # Summary sheet
    ws2 = wb.create_sheet("Resumo")
    resumo = resultado.get("resumo", {})
    ws2.column_dimensions["A"].width = 30
    ws2.column_dimensions["B"].width = 20
    ws2.append(["Métrica", "Valor"])
    ws2.append(["Modelo", resultado.get("modelo","—")])
    ws2.append(["Schema IFC", resultado.get("schema_ifc","—")])
    ws2.append(["Data Auditoria", resultado.get("data_auditoria", datetime.now().strftime("%d/%m/%Y"))])
    ws2.append(["Total de Itens", resumo.get("total", 0)])
    ws2.append(["✅ Conformes", resumo.get("conformes", 0)])
    ws2.append(["❌ Não Conformes", resumo.get("nao_conformes", 0)])
    ws2.append(["⚠️ Indeterminados", resumo.get("indeterminados", 0)])
    ws2.append(["— N/A", resumo.get("na", 0)])
    ws2.append(["% Conformidade", resumo.get("percentual_conformidade","—")])
    for row in ws2.iter_rows(min_row=1, max_row=ws2.max_row):
        for cell in row:
            cell.font = Font(name="Calibri", size=10)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "resultado": None,
    "elementos": None,
    "logs": [],
    "running": False,
    "ifc_nome": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid rgba(255,255,255,0.12);margin-bottom:1rem">
      <img src="https://www.e-zigurat.com/images/logo.svg"
           style="height:28px;filter:brightness(0) invert(1);margin-bottom:0.75rem;display:block" />
      <div style="font-family:'Trebuchet MS',Trebuchet,sans-serif;font-size:1rem;font-weight:700;color:rgb(68,205,148)">
        &#9851; NBR 9050 Auditor
      </div>
      <div style="font-family:'Trebuchet MS',Trebuchet,sans-serif;font-size:0.65rem;color:rgba(255,255,255,0.45);text-transform:uppercase;letter-spacing:0.1em">
        BIM Accessibility Checker
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🔑 Provedor de IA**")
    provider = st.selectbox("Provedor", ["Anthropic (Claude)", "Google (Gemini)"], label_visibility="collapsed")

    api_key = st.text_input(
        "Chave API",
        type="password",
        placeholder="sk-ant-..." if "Anthropic" in provider else "AIza...",
        help="Sua chave de API. Não é armazenada."
    )

    st.markdown("**🤖 Modelo**")
    if "Anthropic" in provider:
        model_options = [
            "claude-haiku-4-5",
            "claude-sonnet-4-5",
            "claude-opus-4-5",
        ]
        model_labels = {
            "claude-haiku-4-5":  "Claude Haiku 4.5 (rápido, econômico)",
            "claude-sonnet-4-5": "Claude Sonnet 4.5 (balanceado)",
            "claude-opus-4-5":   "Claude Opus 4.5 (máxima qualidade)",
        }
    else:
        model_options = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        model_labels = {
            "gemini-1.5-flash": "Gemini 1.5 Flash (rápido)",
            "gemini-1.5-pro": "Gemini 1.5 Pro (balanceado)",
            "gemini-2.0-flash": "Gemini 2.0 Flash (novo)",
        }

    selected_model = st.selectbox(
        "Modelo",
        model_options,
        format_func=lambda x: model_labels.get(x, x),
        label_visibility="collapsed"
    )

    temperature = st.slider("🌡 Temperature", 0.0, 1.0, 0.1, 0.05,
                            help="0.0 = determinístico | 1.0 = mais criativo. Para auditoria normativa, use 0.0–0.2")

    st.markdown("---")
    st.markdown("""
    <div class="info-box">
    <strong>Sobre o GlobalId</strong><br>
    O relatório inclui o <code>GlobalId</code> de cada elemento IFC verificado.
    Use esse ID no Revit (<em>Manage → Select by ID</em>) para selecionar o elemento diretamente.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Trebuchet MS',Trebuchet,sans-serif;font-size:0.65rem;color:rgba(255,255,255,0.35);text-align:center;padding-top:0.5rem">
    Zigurat Institute of Technology<br>
    Master IA para AEC &middot; 2025
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-block">
  <div class="hero-left">
    <div class="hero-title">&#9851; Auditor de Acessibilidade BIM</div>
    <div class="hero-sub">Verificação Automatizada de Conformidade &nbsp;·&nbsp; ABNT NBR 9050:2020 &nbsp;·&nbsp; Powered by IA</div>
  </div>
  <img src="https://www.e-zigurat.com/images/logo.svg" class="hero-logo" alt="Zigurat Institute of Technology" />
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_upload, tab_resultado, tab_ajuda = st.tabs(["📁 Arquivos & Execução", "📊 Resultados", "❓ Ajuda"])

# ─────────────────────────────────────────────
with tab_upload:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-title">📐 Modelo BIM</div>', unsafe_allow_html=True)
        ifc_file = st.file_uploader(
            "Arquivo IFC",
            type=["ifc"],
            help="Formato IFC2X3 ou IFC4. Exportado via Revit, ArchiCAD, Vectorworks etc.",
            label_visibility="collapsed"
        )
        if ifc_file:
            st.markdown(f"""
            <div class="info-box">
            ✅ <strong>{ifc_file.name}</strong><br>
            <span style="font-family:'Courier New',monospace;font-size:0.72rem">
            Tamanho: {ifc_file.size / 1024 / 1024:.1f} MB
            </span>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">📋 Norma / Checklist</div>', unsafe_allow_html=True)
        xlsx_file = st.file_uploader(
            "Planilha NBR 9050 (opcional)",
            type=["xlsx", "xls"],
            help="Planilha com os itens verificáveis. Se não enviada, usa os 12 itens padrão da NBR 9050:2020.",
            label_visibility="collapsed"
        )
        if xlsx_file:
            st.markdown(f"""
            <div class="info-box">
            ✅ <strong>{xlsx_file.name}</strong> carregada.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warn-box">
            📋 Nenhuma planilha carregada — serão usados os <strong>12 itens padrão</strong> da NBR 9050:2020.
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Run button
    can_run = bool(ifc_file and api_key)
    if not api_key:
        st.markdown('<div class="warn-box">⚠️ Insira sua chave API na barra lateral para prosseguir.</div>', unsafe_allow_html=True)
    if not ifc_file:
        st.markdown('<div class="warn-box">⚠️ Carregue um arquivo IFC para prosseguir.</div>', unsafe_allow_html=True)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run = st.button("▶ Executar Auditoria", disabled=not can_run, use_container_width=True)

    # ── Execution ──────────────────────────────────────────────────────────────
    if run and can_run:
        st.session_state.logs = []
        st.session_state.resultado = None

        log_box = st.empty()
        step_box = st.empty()
        progress_bar = st.progress(0)

        def log(msg: str):
            ts = datetime.now().strftime("%H:%M:%S")
            st.session_state.logs.append(f"[{ts}] {msg}")
            log_content = "\n".join(st.session_state.logs[-20:])
            log_box.markdown(f'<div class="terminal">{log_content}</div>', unsafe_allow_html=True)

        try:
            # Step 1 — Save IFC
            log("🔄 Salvando arquivo IFC temporariamente...")
            progress_bar.progress(10)
            with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
                tmp.write(ifc_file.read())
                tmp_path = tmp.name
            st.session_state.ifc_nome = ifc_file.name
            log(f"✅ IFC salvo: {ifc_file.name} ({ifc_file.size/1024/1024:.1f} MB)")

            # Step 2 — Extract IFC elements
            log("🔍 Extraindo elementos do modelo IFC (IfcOpenShell)...")
            progress_bar.progress(25)
            elementos = extract_ifc_elements(tmp_path)
            if "error" in elementos:
                st.error(elementos["error"])
                st.stop()
            resumo_ext = {k: len(v) for k, v in elementos.get("elementos", {}).items()}
            log(f"✅ Elementos extraídos: {resumo_ext}")
            log(f"   Schema IFC detectado: {elementos.get('schema','?')}")
            st.session_state.elementos = elementos
            progress_bar.progress(45)

            # Step 3 — Read XLSX
            norma_items = []
            if xlsx_file:
                log("📋 Lendo planilha da norma...")
                norma_items = read_xlsx_items(xlsx_file.read())
                log(f"✅ {len(norma_items)} itens carregados da planilha.")
            else:
                log("📋 Usando 12 itens padrão NBR 9050:2020.")
            progress_bar.progress(55)

            # Step 4 — Build prompt
            log("📝 Construindo prompt de auditoria...")
            prompt = build_audit_prompt(elementos, norma_items, ifc_file.name)
            log(f"   Prompt: ~{len(prompt)//4:,} tokens estimados")
            progress_bar.progress(65)

            # Step 5 — Call LLM
            log(f"🤖 Chamando {selected_model} ({provider})...")
            log("   Aguarde — isso pode levar 30–90 segundos...")
            progress_bar.progress(70)

            if "Anthropic" in provider:
                resultado = call_anthropic(api_key, selected_model, prompt, temperature)
            else:
                resultado = call_gemini(api_key, selected_model, prompt, temperature)

            progress_bar.progress(90)
            log(f"✅ Auditoria concluída!")

            resumo = resultado.get("resumo", {})
            log(f"   Total: {resumo.get('total',0)} | ✅ {resumo.get('conformes',0)} | ❌ {resumo.get('nao_conformes',0)} | ⚠️ {resumo.get('indeterminados',0)}")

            st.session_state.resultado = resultado
            progress_bar.progress(100)
            log("🎉 Relatório pronto! Acesse a aba 'Resultados'.")

            # Cleanup
            os.unlink(tmp_path)

        except json.JSONDecodeError as e:
            log(f"❌ Erro ao parsear resposta JSON do modelo: {e}")
            st.error("O modelo não retornou JSON válido. Tente novamente ou ajuste o modelo/temperatura.")
        except Exception as e:
            log(f"❌ Erro: {e}")
            st.error(f"Erro durante a execução: {e}")


# ─────────────────────────────────────────────
with tab_resultado:
    if st.session_state.resultado is None:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#334155">
          <div style="font-size:3rem;margin-bottom:1rem">📊</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#475569">
            Nenhuma auditoria executada ainda.
          </div>
          <div style="font-size:0.82rem;color:#334155;margin-top:0.5rem">
            Vá para a aba <strong>Arquivos & Execução</strong> e clique em <strong>Executar Auditoria</strong>.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        resultado = st.session_state.resultado
        resumo = resultado.get("resumo", {})
        itens = resultado.get("resultados", [])

        # Metrics
        total   = resumo.get("total", len(itens))
        conf    = resumo.get("conformes", 0)
        nconf   = resumo.get("nao_conformes", 0)
        indet   = resumo.get("indeterminados", 0)
        na      = resumo.get("na", 0)
        pct     = resumo.get("percentual_conformidade", "—")

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card"><div class="metric-num c-blue">{total}</div><div class="metric-label">Total</div></div>
          <div class="metric-card"><div class="metric-num c-green">{conf}</div><div class="metric-label">Conformes</div></div>
          <div class="metric-card"><div class="metric-num c-red">{nconf}</div><div class="metric-label">Não Conformes</div></div>
          <div class="metric-card"><div class="metric-num c-amber">{indet}</div><div class="metric-label">Indeterminados</div></div>
          <div class="metric-card"><div class="metric-num c-muted">{na}</div><div class="metric-label">N/A</div></div>
          <div class="metric-card"><div class="metric-num c-green">{pct}</div><div class="metric-label">Conformidade</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Observações
        obs = resultado.get("observacoes_gerais", "")
        if obs:
            st.markdown(f'<div class="info-box">💬 <strong>Análise Geral:</strong> {obs}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_status = st.multiselect(
                "Filtrar por Status",
                ["Conforme", "Não Conforme", "Indeterminado", "N/A"],
                default=["Conforme", "Não Conforme", "Indeterminado", "N/A"]
            )
        with col_f2:
            cats = sorted(set(it.get("categoria","") for it in itens if it.get("categoria")))
            filter_cat = st.multiselect("Filtrar por Categoria", cats, default=cats)
        with col_f3:
            search_gid = st.text_input("Buscar GlobalId", placeholder="0yScV...", help="Filtra pelo GlobalId do elemento IFC")

        # Table
        itens_filtrados = [
            it for it in itens
            if it.get("status","") in filter_status
            and it.get("categoria","") in filter_cat
            and (not search_gid or search_gid.lower() in it.get("globalid","").lower())
        ]

        st.markdown(f"""
        <div class="section-title">
          📋 Itens Verificados
          <span style="font-weight:400;color:#475569;font-size:0.75rem">— {len(itens_filtrados)} de {len(itens)} itens</span>
        </div>
        """, unsafe_allow_html=True)

        # Build table HTML
        rows_html = ""
        for it in itens_filtrados:
            gid = it.get("globalid", "—")
            gid_chip = f'<span class="globalid" title="GlobalId para filtro no Revit">{gid}</span>' if gid != "—" else "—"
            rows_html += f"""
            <tr>
              <td style="font-family:var(--mono);color:#94a3b8;white-space:nowrap">{it.get('item_nbr','—')}</td>
              <td style="color:#cbd5e1">{it.get('categoria','—')}</td>
              <td style="color:#e2e8f0">{it.get('elemento','—')}</td>
              <td>{status_badge(it.get('status','N/A'))}</td>
              <td style="font-family:var(--mono);font-size:0.78rem;color:#94a3b8">{it.get('valor_encontrado','—')}</td>
              <td style="font-family:var(--mono);font-size:0.78rem;color:#94a3b8">{it.get('valor_exigido','—')}</td>
              <td>{gid_chip}</td>
              <td style="font-family:var(--mono);font-size:0.72rem;color:#475569">{it.get('tipo_ifc','—')}</td>
              <td style="font-size:0.8rem;color:#f87171">{it.get('recomendacao','—') if 'nao' in it.get('status','').lower() or 'não' in it.get('status','').lower() else '<span style="color:#64748b">—</span>'}</td>
            </tr>"""

        st.markdown(f"""
        <div style="overflow-x:auto">
        <table class="result-table">
          <thead>
            <tr>
              <th>Item NBR</th><th>Categoria</th><th>Elemento</th><th>Status</th>
              <th>Valor Encontrado</th><th>Valor Exigido</th>
              <th>GlobalId 🔍</th><th>Tipo IFC</th><th>Recomendação</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-title">⬇️ Exportar Relatório</div>', unsafe_allow_html=True)

        col_dl1, col_dl2, col_dl3 = st.columns(3)
        modelo_nome = st.session_state.ifc_nome or "modelo"
        ts = datetime.now().strftime("%Y%m%d_%H%M")

        with col_dl1:
            html_bytes = gerar_relatorio_html(resultado, modelo_nome).encode("utf-8")
            st.download_button(
                "📄 Baixar Relatório HTML",
                data=html_bytes,
                file_name=f"relatorio_nbr9050_{ts}.html",
                mime="text/html",
                use_container_width=True,
            )

        with col_dl2:
            xlsx_bytes = gerar_excel(resultado, modelo_nome)
            if xlsx_bytes:
                st.download_button(
                    "📊 Baixar Checklist XLSX",
                    data=xlsx_bytes,
                    file_name=f"checklist_nbr9050_{ts}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        with col_dl3:
            json_bytes = json.dumps(resultado, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button(
                "🗂 Baixar JSON Completo",
                data=json_bytes,
                file_name=f"auditoria_nbr9050_{ts}.json",
                mime="application/json",
                use_container_width=True,
            )

        # JSON expandable
        with st.expander("🔍 Ver JSON bruto da auditoria"):
            st.json(resultado)


# ─────────────────────────────────────────────
with tab_ajuda:
    st.markdown("""
    <div class="section-title">📖 Como usar o Auditor NBR 9050</div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **1. Configure a IA (barra lateral)**
        - Escolha o provedor: **Anthropic** (Claude) ou **Google** (Gemini)
        - Cole sua chave API
        - Selecione o modelo desejado
        - Ajuste a temperature (0.0–0.2 recomendado para auditoria)

        **2. Carregue os arquivos**
        - **IFC** (obrigatório): arquivo exportado do Revit, ArchiCAD etc.
          - Formatos suportados: IFC2X3, IFC4
          - O sistema detecta o schema automaticamente
        - **XLSX** (opcional): planilha com itens NBR 9050
          - Se não carregado, usa os 12 itens padrão

        **3. Execute a auditoria**
        - Clique em **Executar Auditoria**
        - Acompanhe o log em tempo real
        - Aguarde 30–90 segundos (depende do modelo e tamanho do IFC)
        """)

    with col_b:
        st.markdown("""
        **4. Analise os resultados**
        - Filtre por status, categoria ou GlobalId
        - O **GlobalId** identifica cada elemento no IFC

        **5. Como usar o GlobalId no Revit**
        - No Revit: `Manage → Select by ID` → cole o GlobalId
        - No Navisworks: filtro por GUID
        - No Solibri / BIMcollab: filtro por GlobalId no modelo IFC
        - No IfcOpenShell: `ifc.by_guid("0yScV...")`

        **6. Exporte os relatórios**
        - **HTML**: relatório visual completo com todos os dados
        - **XLSX**: checklist com formatação por status (conforme/não conforme)
        - **JSON**: dados brutos para integração com outros sistemas
        """)

    st.markdown("---")
    st.markdown("""
    <div class="section-title">♿ Itens NBR 9050:2020 verificados (padrão)</div>
    """, unsafe_allow_html=True)

    itens_padrao = [
        ("6.6", "Geométrica", "Rampas", "Inclinação máxima por faixa de desnível", "IfcRamp / IfcRampFlight"),
        ("6.11.1", "Geométrica", "Corredores", "Largura mínima de circulação", "IfcSpace"),
        ("6.11.2", "Geométrica", "Portas", "Vão livre mínimo 0,80m × 2,10m", "IfcDoor"),
        ("6.11.3", "Condicional", "Janelas", "Peitoril mínimo 1,20m", "IfcWindow"),
        ("5.4.3", "Condicional", "Corrimões", "Altura e presença em ambos os lados", "IfcRailing"),
        ("6.3.4", "Condicional", "Pisos", "Desníveis com chanfro ou rampa", "IfcSlab"),
        ("7.5", "Relacional", "Circulação", "Espaço de giro Ø 1,50m", "IfcSpace"),
        ("7.7.2.1", "Relacional", "Sanitários", "Bacia sanitária altura 0,43–0,45m", "IfcFlowTerminal"),
        ("7.7.1", "Relacional", "Sanitários", "Vaso sanitário espaço lateral livre 0,80m", "IfcFlowTerminal"),
        ("4.6.6", "Qualitativa", "Portas", "Maçaneta tipo alavanca", "IfcDoor"),
        ("7.6–7.8", "Qualitativa", "Sanitários", "Box de acessibilidade com barras de apoio", "IfcFurnishingElement"),
        ("7.8", "Qualitativa", "Sanitários", "Lavatório suspenso ou sem coluna", "IfcFlowTerminal"),
    ]

    cat_colors = {"Geométrica": "#3b82f6", "Condicional": "#f59e0b", "Relacional": "#10b981", "Qualitativa": "#8b5cf6"}
    rows_help = ""
    for item_nbr, classificacao, cat, desc, entidade in itens_padrao:
        color = cat_colors.get(classificacao, "#64748b")
        rows_help += f"""
        <tr>
          <td style="font-family:var(--mono);color:#94a3b8">{item_nbr}</td>
          <td><span style="color:{color};font-size:0.78rem;font-weight:600">{classificacao}</span></td>
          <td style="color:#cbd5e1">{cat}</td>
          <td style="color:#e2e8f0">{desc}</td>
          <td style="font-family:var(--mono);font-size:0.72rem;color:#475569">{entidade}</td>
        </tr>"""

    st.markdown(f"""
    <table class="result-table">
      <thead>
        <tr><th>Item NBR</th><th>Tipo</th><th>Categoria</th><th>Verificação</th><th>Entidade IFC</th></tr>
      </thead>
      <tbody>{rows_help}</tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warn-box" style="margin-top:1.5rem">
    ⚠️ <strong>Limitações conhecidas:</strong>
    Itens qualitativos (maçaneta alavanca, lavatório suspenso) dependem de atributos textuais raramente preenchidos no IFC.
    Itens como espaço de giro (IfcSpace) ficam Indeterminados se o modelo não exportar espaços.
    Verificação manual complementar é sempre recomendada.
    </div>
    """, unsafe_allow_html=True)

