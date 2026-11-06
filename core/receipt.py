from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from .orders import totals

def receipt(cart, service, promo=False):
    if not cart or service not in ("recoger","domicilio"): raise ValueError("Pedido incompleto")
    buf=BytesIO();doc=SimpleDocTemplate(buf)
    styles=getSampleStyleSheet()
    story=[Paragraph("PizzaBot | Comprobante de demostración",styles["Title"]),Paragraph("Pedido ficticio. No es factura ni implica compra real.",styles["Normal"]),Spacer(1,12)]
    for x in cart:
        detail=f"{x['cantidad']} x {x['nombre']} ({x['tamano'] or 'estándar'})"
        if x['extras']:detail+=" + "+", ".join(x['extras'])
        story.append(Paragraph(f"{detail}: ${x['cantidad']*x['unitario']} MXN",styles["Normal"]))
    t=totals(cart,service,promo)
    for k,v in t.items():story.append(Paragraph(f"{k.capitalize()}: ${v} MXN",styles["Normal"]))
    story.append(Paragraph(f"Servicio simulado: {service}. No se recopilan direcciones ni datos bancarios.",styles["Normal"]))
    doc.build(story);return buf.getvalue()
