from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import io
import os

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

    # ==========================
    # LOGO LUSANTA
    # ==========================
    
    logo_path = "logotipo lusanta_Mesa de trabajo 1.png"

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.8*inch, height=1.2*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.4 * inch))

    # ==========================
    # ENCABEZADO
    # ==========================

    elements.append(Paragraph("<b>Propuesta de Inversión</b>", centered_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Cliente: {nombre_cliente}", normal))
    elements.append(Paragraph(f"Fecha: {fecha}", normal))
    elements.append(Spacer(1, 0.5 * inch))

    # ==========================
    # TABLA FINANCIERA
    # ==========================

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
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.6 * inch))

    # ==========================
    # CONCLUSIÓN
    # ==========================

    conclusion = f"""
Comprar hoy permite capturar aproximadamente ${diferencia_precio:,.0f} de plusvalía proyectada.
Esperar podría representar un impacto financiero relevante considerando el incremento de precio y renta no generada.

Torre 3 no es la oportunidad.
Es la confirmación del valor que puede capturar hoy en Lusanta.
"""

    elements.append(Paragraph(conclusion, normal))

    doc.build(elements)
    buffer.seek(0)

    st.download_button(
        label="Descargar Propuesta PDF",
        data=buffer,
        file_name=f"Propuesta_Lusanta_{nombre_cliente}.pdf",
        mime="application/pdf"
    )
