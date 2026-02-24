import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================

st.set_page_config(page_title="Cotizador Lusanta 2026", layout="wide")

st.title("🏢 Cotizador Oficial Lusanta 2026")

# ======================================
# CARGAR EXCEL
# ======================================

@st.cache_data
def cargar_datos():
    df = pd.read_excel("LISTA_DE_PRECIOS_2026.xlsx")
    return df

df = cargar_datos()

# ======================================
# SELECCIÓN DE DEPARTAMENTO
# ======================================

st.subheader("Selección de Departamento")

torre = st.selectbox("Selecciona Torre", sorted(df["Torre"].unique()))
df_torre = df[df["Torre"] == torre]

nivel = st.selectbox("Selecciona Nivel", sorted(df_torre["Nivel"].unique()))
df_nivel = df_torre[df_torre["Nivel"] == nivel]

modelo = st.selectbox("Selecciona Modelo", sorted(df_nivel["Modelo"].unique()))
df_modelo = df_nivel[df_nivel["Modelo"] == modelo]

unidad = st.selectbox("Selecciona Unidad", df_modelo["Unidad"])
fila = df_modelo[df_modelo["Unidad"] == unidad].iloc[0]

# Datos automáticos
metros = fila["Totales M2"]
precio_lusanta = fila["Precio"]
precio_m2_lusanta = fila["Precio x m2"]
recamaras = fila["Rec"]
banos = fila["Baños"]
vista = fila["Vista"]
interior = fila["Interior m2"]
terraza = fila["Teraza m2"]

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Metros Totales", f"{metros} m²")
col2.metric("Precio Total", f"${precio_lusanta:,.0f}")
col3.metric("Precio por m²", f"${precio_m2_lusanta:,.0f}")

col4, col5, col6 = st.columns(3)
col4.metric("Recámaras", recamaras)
col5.metric("Baños", banos)
col6.metric("Vista", vista)

col7, col8 = st.columns(2)
col7.metric("Interior m²", interior)
col8.metric("Terraza m²", terraza)

# ======================================
# COMPARATIVO VS TORRE 3
# ======================================

st.divider()
st.subheader("Comparativo de Plusvalía vs Torre 3")

precio_m2_torre3 = 48000
precio_torre3 = metros * precio_m2_torre3
diferencia_precio = precio_torre3 - precio_lusanta

colA, colB, colC = st.columns(3)
colA.metric("Precio Lusanta Hoy", f"${precio_lusanta:,.0f}")
colB.metric("Valor Proyectado Torre 3", f"${precio_torre3:,.0f}")
colC.metric("Plusvalía Proyectada", f"${diferencia_precio:,.0f}")

# ======================================
# SIMULADOR HIPOTECARIO
# ======================================

st.divider()
st.subheader("Simulador Hipotecario")

enganche_pct = st.slider("Porcentaje de Enganche", 10, 50, 20)
tasa = st.slider("Tasa de interés anual (%)", 5.0, 15.0, 10.5)
plazo = st.selectbox("Plazo (años)", [10, 15, 20, 25])

enganche = precio_lusanta * (enganche_pct / 100)
credito = precio_lusanta - enganche

tasa_mensual = tasa / 100 / 12
num_pagos = plazo * 12

mensualidad = credito * (
    tasa_mensual * (1 + tasa_mensual) ** num_pagos
) / ((1 + tasa_mensual) ** num_pagos - 1)

colX, colY, colZ = st.columns(3)
colX.metric("Enganche", f"${enganche:,.0f}")
colY.metric("Monto de Crédito", f"${credito:,.0f}")
colZ.metric("Mensualidad Aproximada", f"${mensualidad:,.0f}")

# ======================================
# GENERADOR DE PDF PERSONALIZADO
# ======================================

st.divider()
st.subheader("Generar Propuesta en PDF")

nombre_cliente = st.text_input("Nombre del Cliente")

def generar_pdf():
    doc = SimpleDocTemplate("Propuesta_Lusanta.pdf", pagesize=letter)
    elementos = []

    estilos = getSampleStyleSheet()
    estilo_titulo = estilos["Heading1"]
    estilo_normal = estilos["Normal"]

    # Logo
    logo = Image("logo_lusanta.png", width=4*inch, height=2.5*inch)
    elementos.append(logo)
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph(f"Propuesta Personalizada para {nombre_cliente}", estilo_titulo))
    elementos.append(Spacer(1, 20))

    datos = [
        ["Torre", torre],
        ["Nivel", nivel],
        ["Unidad", unidad],
        ["Modelo", modelo],
        ["Metros Totales", f"{metros} m²"],
        ["Interior", f"{interior} m²"],
        ["Terraza", f"{terraza} m²"],
        ["Recámaras", recamaras],
        ["Baños", banos],
        ["Vista", vista],
        ["Precio Total", f"${precio_lusanta:,.0f}"],
        ["Plusvalía Proyectada", f"${diferencia_precio:,.0f}"],
        ["Enganche", f"${enganche:,.0f}"],
        ["Mensualidad Estimada", f"${mensualidad:,.0f}"],
    ]

    tabla = Table(datos, colWidths=[2.5*inch, 3*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

if st.button("Generar PDF"):
    if nombre_cliente:
        generar_pdf()
        with open("Propuesta_Lusanta.pdf", "rb") as file:
            st.download_button(
                label="Descargar PDF",
                data=file,
                file_name=f"Propuesta_Lusanta_{nombre_cliente}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Por favor escribe el nombre del cliente.")




