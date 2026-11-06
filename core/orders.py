from decimal import Decimal, ROUND_HALF_UP
from .knowledge import catalog, product_by_id, load

def money(v):
    return int(Decimal(str(v)).quantize(Decimal("1"),rounding=ROUND_HALF_UP))
def item(pid, size=None, qty=1, extras=None):
    p=product_by_id(pid)
    if not p or not isinstance(qty,int) or qty<1 or qty>20: raise ValueError("Producto o cantidad inválida")
    m=catalog(); pizza=pid in [x["id"] for x in m["productos"]]
    if pizza and not size: raise ValueError("Se requiere tamaño")
    if pizza and size not in m["tamanos"]: raise ValueError("Tamaño inválido")
    if not pizza and extras: raise ValueError("Extras solo en pizzas")
    allowed={x["id"]:x["precio"] for x in m["extras"]}
    if any(e not in allowed for e in (extras or [])): raise ValueError("Extra inválido")
    price=money(Decimal(str(p["precio"]))*Decimal(str(m["tamanos"][size]))) if pizza else p["precio"]
    price+=sum(allowed[e] for e in (extras or []))
    return {"id":pid,"nombre":p["nombre"],"tamano":size,"cantidad":qty,"extras":extras or [],"unitario":price}

def totals(cart,service=None, promo=False):
    subtotal=sum(x["unitario"]*x["cantidad"] for x in cart)
    discount=0
    if promo:
        rule=load("promociones.json")[0]
        pizzas=[x for x in cart if x["tamano"]=="grande"]
        if sum(x["cantidad"] for x in pizzas)>=rule["min_pizzas"]:
            base=sum(x["cantidad"]*(x["unitario"]-sum(e["precio"] for e in catalog()["extras"] if e["id"] in x["extras"])) for x in pizzas)
            discount=money(Decimal(base)*Decimal(str(rule["descuento"])))
    delivery=catalog()["entrega"]["costo"] if service=="domicilio" and cart else 0
    return {"subtotal":subtotal,"descuento":discount,"entrega":delivery,"total":subtotal-discount+delivery}

def summary(cart,service=None,promo=False):
    if not cart:return "Tu carrito está vacío."
    lines=[f"{i+1}. {x['cantidad']} × {x['nombre']}"+(f" ({x['tamano']})" if x['tamano'] else "")+(f" + {', '.join(x['extras'])}" if x['extras'] else "")+f" — ${x['unitario']*x['cantidad']}" for i,x in enumerate(cart)]
    t=totals(cart,service,promo)
    lines += [f"Subtotal: ${t['subtotal']}",f"Descuento: -${t['descuento']}",f"Entrega: ${t['entrega']}",f"TOTAL: ${t['total']}",f"Servicio: {service or 'pendiente'}"]
    return "\\n".join(lines).replace("\\n","\n")
