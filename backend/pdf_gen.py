from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


COLOR_VERDE = colors.HexColor("#10b981")
COLOR_NARANJA = colors.HexColor("#f97316")
COLOR_ROJA = colors.HexColor("#ef4444")
COLOR_PRIMARY = colors.HexColor("#0f172a")
COLOR_MUTED = colors.HexColor("#475569")
COLOR_LIGHT = colors.HexColor("#94a3b8")
COLOR_BORDER = colors.HexColor("#e2e8f0")


def _alerta_color(alerta: str):
    return {
        "Verde": COLOR_VERDE,
        "Naranja": COLOR_NARANJA,
        "Roja": COLOR_ROJA,
    }.get(alerta, COLOR_MUTED)


def render_evaluation_pdf(student, evaluation, evaluador_nombre=None) -> bytes:
    buffer = __import__("io").BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Reporte NutriIA - {student.nombres} {student.apellidos}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=COLOR_PRIMARY,
        spaceAfter=2,
    )
    sub_style = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=COLOR_MUTED,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=COLOR_PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=COLOR_PRIMARY,
        leading=13,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=COLOR_MUTED,
    )

    story = []
    story.append(Paragraph("NutriIA — Reporte de Evaluación Nutricional", title_style))
    story.append(
        Paragraph(
            "Sistema de Apoyo a la Decisión Clínica • Programa de Alimentación Escolar (PAE) Colombia",
            sub_style,
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    header_data = [
        [Paragraph("<b>Estudiante</b>", body_style), f"{student.nombres} {student.apellidos}"],
        [Paragraph("<b>Documento</b>", body_style), student.documento or "—"],
        [Paragraph("<b>Fecha de nacimiento</b>", body_style), str(student.fecha_nacimiento)],
        [Paragraph("<b>Sexo</b>", body_style), student.sexo],
        [Paragraph("<b>Grado</b>", body_style), student.grado],
        [Paragraph("<b>Colegio</b>", body_style), student.colegio or "—"],
    ]
    header_tbl = Table(header_data, colWidths=[4.5 * cm, 12 * cm])
    header_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, COLOR_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(header_tbl)
    story.append(Spacer(1, 0.4 * cm))

    color_alerta = _alerta_color(evaluation.alerta)
    result_data = [
        [
            Paragraph("<b>Resultado</b>", body_style),
            Paragraph(
                f"<font color='{color_alerta.hexval()}'><b>{evaluation.prediccion}</b></font>",
                body_style,
            ),
            Paragraph("<b>Alerta</b>", body_style),
            Paragraph(
                f"<font color='{color_alerta.hexval()}'><b>{evaluation.alerta}</b></font>",
                body_style,
            ),
        ],
        [
            Paragraph("<b>IMC</b>", body_style),
            f"{evaluation.imc:.2f}",
            Paragraph("<b>Z-score IMC/edad</b>", body_style),
            (
                f"{evaluation.zscore_imc:.2f}"
                if evaluation.zscore_imc is not None
                else "Sin referencia"
            ),
        ],
        [
            Paragraph("<b>Acción recomendada</b>", body_style),
            Paragraph(evaluation.accion or "—", body_style),
            "",
            "",
        ],
    ]
    result_tbl = Table(result_data, colWidths=[3.5 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm])
    result_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, COLOR_BORDER),
                ("SPAN", (1, 2), (3, 2)),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(result_tbl)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Mediciones antropométricas", section_style))
    medidas_data = [
        ["Variable", "Valor", "Unidad"],
        ["Peso", f"{evaluation.peso_kg:.2f}", "kg"],
        ["Estatura", f"{evaluation.estatura_cm:.2f}", "cm"],
        ["MUAC (perímetro braquial)", f"{evaluation.muac_cm:.2f}", "cm"],
        ["IMC", f"{evaluation.imc:.2f}", "kg/m²"],
        ["Edad", f"{evaluation.edad_meses:.1f}", "meses"],
    ]
    medidas_tbl = Table(medidas_data, colWidths=[7 * cm, 5 * cm, 4.5 * cm])
    medidas_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, COLOR_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(medidas_tbl)
    story.append(Spacer(1, 0.4 * cm))

    from backend.model_service import ALERT_MAP

    codigo = next((k for k, v in ALERT_MAP.items() if v["prediccion"] == evaluation.prediccion), 1)
    plan = ALERT_MAP[codigo]["plan_seguimiento"]

    story.append(Paragraph("Plan de seguimiento", section_style))

    story.append(Paragraph("<b>Alimentación</b>", body_style))
    story.append(Paragraph(plan["alimentacion"]["descripcion"], body_style))
    story.append(Paragraph("<b>Recomendados:</b>", body_style))
    for a in plan["alimentacion"]["alimentos_recomendados"]:
        story.append(Paragraph(f"• {a}", body_style))
    story.append(Paragraph("<b>A evitar/limitar:</b>", body_style))
    for a in plan["alimentacion"]["alimentos_evitar"]:
        story.append(Paragraph(f"• {a}", body_style))
    story.append(Paragraph(f"<b>Frecuencia:</b> {plan['alimentacion']['frecuencia']}", body_style))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("<b>Sueño</b>", body_style))
    story.append(Paragraph(plan["sueno"]["descripcion"], body_style))
    story.append(Paragraph(f"<b>Horas recomendadas:</b> {plan['sueno']['horas_recomendadas']}", body_style))
    for h in plan["sueno"]["habitos"]:
        story.append(Paragraph(f"• {h}", body_style))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("<b>Estilo de vida</b>", body_style))
    story.append(Paragraph(plan["estilo_vida"]["descripcion"], body_style))
    story.append(Paragraph(f"<b>Actividad física:</b> {plan['estilo_vida']['actividad_fisica']}", body_style))
    for r in plan["estilo_vida"]["recomendaciones"]:
        story.append(Paragraph(f"• {r}", body_style))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Notas clínicas", section_style))
    story.append(Paragraph(evaluation.notas or "—", body_style))
    story.append(Spacer(1, 0.8 * cm))

    firma_data = [
        ["", ""],
        ["______________________________", "______________________________"],
        ["Firma del nutricionista", "Fecha"],
    ]
    firma_tbl = Table(firma_data, colWidths=[8.5 * cm, 8 * cm])
    firma_tbl.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_MUTED),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    story.append(firma_tbl)

    story.append(Spacer(1, 0.4 * cm))
    story.append(
        Paragraph(
            "<b>Disclaimer ético:</b> NutriIA es un sistema de apoyo a la decisión clínica (CDSS). "
            "Los resultados deben ser validados por un profesional de salud calificado. "
            "El procesamiento de datos cumple con la Ley 1581 de 2012 (Colombia).",
            small_style,
        )
    )
    story.append(
        Paragraph(
            f"Generado el {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} por NutriIA. "
            + (f"Evaluado por: {evaluador_nombre}." if evaluador_nombre else "Sin evaluador asociado."),
            small_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()
