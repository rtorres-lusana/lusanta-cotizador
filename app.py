import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import io
import os

# =============================
# CONFIGURACIÓN
# =============================

st.set_page_config(page_title="LUSANTA Cotizador", layout="wide")

st.title("☀️ LUSANTA | Cotizador Inteligente Premium")

st.divider()

# =============================
# INPUTS
# =============================

col1, col2, col3 = st.columns(3)

with col1:
    precio_m2_lusanta = st.number_input("Precio m² Lusanta Hoy", value=32000)

with col2:
    precio_m2_torre3 = st.number_input("Precio m² Torre 3 (Estimado)", value=48000)

with col3:
    metros = st.number_input("Metros del Departamento", value=102)

renta_mensual = st.number_input("Renta mensual estimada", value=23000)

# =============================
# CÁLCULOS
# =============================

precio_lusanta = precio_m2_lusanta * metros
precio_torre3 = precio_m2_torre3 * metros
diferencia_precio = precio_torre3 - precio_lusanta

# =============================
# SIMULADOR HIPOTECARIO
# =============================

st.subheader("🏦 Simulador Hipotecario")

enganche_pct = st.slider("Enganche (%)", 10, 50, 20)
tasa_anual = st.number_input("Tasa anual (%)", value=10.5)
plazo_años = st.selectbox("Plazo (años)", [10, 15, 20, 25, 30], index=2)

enganche = precio_lusanta * (enganche_pct / 100)
monto_credito = precio_lusanta - enganche

tasa_mensual = (tasa_anual / 100) / 12
num_pagos = plazo_años * 12

mensualidad = monto_credito * (
    tasa_mensual * (1 + tasa_mensual) ** num_pagos
) / ((1 + tasa_mensual) ** num_pagos - 1)

total_pagado = mensualidad * num_pagos
intereses_totales = total_pagado - monto_credito

flujo_mensual = renta_mensual - mensualidad

# =============================
# MOSTRAR RESULTADOS
# =============================

st.divider()
st.subheader("📊 Resultados")

colA, colB, colC = st.columns(3)

colA.metric("Precio Lusanta", f"${precio_lusanta:,.0f}")
colB.metric("Valor Torre 3", f"${precio_torre3:,.0f}")
colC.metric("Ganancia Potencial", f"${diferencia_precio:,.0f}")

# =============================
# GENERADOR PDF
# =============================

st.divider()
st.subheader("📄 Generar Propuesta Personalizada")

nombre_cliente = st.text_input("Nombre del Cliente")

if st.button("Generar PDF Personalizado"):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    centered_style = ParagraphStyle(
        name='Centered',
        parent=styles['Normal'],
        alignment=TA_CENTER
    )

    fecha = datetime.now().strftime("%d/%m/%Y")

    # LOGO
    logo_path = "logo_lusanta.png"

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.8*inch, height=1.2*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph("<b>Propuesta de Inversión</b>", centered_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Cliente: {nombre_cliente}", normal))
    elements.append(Paragraph(f"Fecha: {fecha}", normal))
    elements.append(Spacer(1, 0.5 * inch))

    data = [
        ["Concepto", "Monto"],
        ["Precio Lusanta Hoy", f"${precio_lusanta:,.0f}"],
        ["Valor Proyectado Torre 3", f"${precio_torre3:,.0f}"],
        ["Ganancia Potencial", f"${diferencia_precio:,.0f}"],
        ["Enganche", f"${enganche:,.0f}"],
        ["Mensualidad Estimada", f"${mensualidad:,.0f}"],
        ["Intereses Totales", f"${intereses_totales:,.0f}"],
        ["Flujo Mensual Estimado", f"${flujo_mensual:,.0f}"],
    ]

    table = Table(data, colWidths=[3.2 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4F4F4")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.6 * inch))

    doc.build(elements)
    buffer.seek(0)

    st.download_button(
        label="Descargar Propuesta PDF",
        data=buffer,
        file_name=f"Propuesta_Lusanta_{nombre_cliente}.pdf",
        mime="application/pdf"
    )
