import re
import unicodedata
from difflib import get_close_matches
from .knowledge import load, catalog, products

def normalize(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()

PRIORITY = ["cancelar_pedido", "eliminar_producto", "modificar_pedido", "consultar_menu_infantil", "confirmar_pedido", "consultar_carrito", "consultar_ingredientes", "consultar_precios", "consultar_promociones", "consultar_horario", "consultar_pago", "consultar_domicilio", "recomendar", "agregar_producto", "iniciar_pedido", "consultar_menu", "ayuda", "agradecer", "despedirse", "saludar"]
NUM = {"un":1,"una":1,"uno":1,"dos":2,"tres":3,"cuatro":4,"cinco":5,"seis":6,"siete":7,"ocho":8,"nueve":9,"diez":10}

def entities(message):
    t=normalize(message)
    result={}
    m=catalog()
    found=[]
    for x in products():
        if re.search(r"(?<!\w)"+re.escape(normalize(x["id"]))+r"(?!\w)",t) or normalize(x["nombre"]) in t:
            found.append(x["id"])
    if not found:
        words=t.split()
        for w in words:
            if len(w)>=5:
                candidates=[x["id"] for x in products()]
                close=get_close_matches(w,candidates,n=1,cutoff=.84)
                if close: found.append(close[0])
    if found: result["productos"]=list(dict.fromkeys(found))
    for size in m["tamanos"]:
        if re.search(r"\b"+size+r"s?\b",t): result["tamano"]=size
    q=re.search(r"\b(\d{1,2}|"+"|".join(NUM)+r")\s+(?:pizzas?|refrescos?|aguas?|jugos?|papas|alitas)\b",t)
    if q: result["cantidad"]=int(q.group(1)) if q.group(1).isdigit() else NUM[q.group(1)]
    elif re.search(r"\b(?:una|un)\s+(?:pizza|refresco|agua|jugo)\b",t): result["cantidad"]=1
    elif t.isdigit() and 0<int(t)<=20: result["cantidad"]=int(t)
    for s in ("domicilio","recoger"):
        if s in t: result["servicio"]=s
    if "para llevar" in t or "recojo" in t: result["servicio"]="recoger"
    for restriction in ("vegetariano","vegetariana","vegano","vegana","sin gluten","sin lactosa","alergia","alergico","celiaco"):
        if restriction in t: result["restriccion"]=restriction
    budget=re.search(r"(?:presupuesto|menos de|hasta)\s*\$?\s*(\d+)",t)
    if budget: result["presupuesto"]=int(budget.group(1))
    people=re.search(r"(?:para|somos)\s*(\d+)\s*personas?",t)
    if people: result["personas"]=int(people.group(1))
    extras=[e["id"] for e in m["extras"] if normalize(e["id"]) in t]
    if extras: result["extras"]=extras
    return result

def intent(message):
    t=normalize(message)
    pats=load("intenciones.json")
    for name in PRIORITY:
        for phrase in pats[name]:
            pat=normalize(phrase)
            if re.search(r"(?<!\w)"+re.escape(pat)+r"(?!\w)",t): return name
    if entities(message).get("productos"): return "agregar_producto" if re.search(r"\b(quiero|pedido|pedir|dame|ponme|agrega|anade|dos|una|un)\b",t) else "consultar_precios"
    return "desconocida"

def analyze(message):
    return {"normalizado":normalize(message),"intencion":intent(message),"entidades":entities(message)}
