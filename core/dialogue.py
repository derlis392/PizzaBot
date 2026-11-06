from .nlp import analyze, normalize
from .knowledge import catalog, load, product_by_id
from .orders import item, totals, summary

def initial():
    return {"cart":[],"pending":None,"service":None,"confirmed":False,"promo":False,"preferences":{},"intent":"","last_analysis":{},"rule":"inicio"}

def process(state,message):
    a=analyze(message); e=a["entidades"]; intent=a["intencion"]; t=normalize(message)
    state["intent"]=intent;state["last_analysis"]=a
    def say(reply,rule):
        state["rule"]=rule
        return reply
    if state["confirmed"]:
        if intent=="consultar_carrito":return say(summary(state["cart"],state["service"],state["promo"]),"resumen_confirmado")
        if intent in ("saludar","agradecer","despedirse","ayuda"):return say("Pedido de demostración confirmado. Reinicia la conversación para crear otro.","pedido_cerrado")
        return say("Este pedido ya está confirmado. Reinicia la conversación para crear uno nuevo.","pedido_cerrado")
    if intent=="cancelar_pedido":
        state.update(initial());return say("Pedido cancelado y carrito vaciado.","cancelacion")
    if state["pending"]:
        pending=state["pending"]
        if pending["kind"]=="size":
            if e.get("tamano"):
                state["pending"]=None
                p=pending["product"]
                state["cart"].append(item(p,e["tamano"],pending["qty"],pending.get("extras",[])))
                return say(f"Agregué {pending['qty']} {product_by_id(p)['nombre']} tamaño {e['tamano']}. ¿Deseas agregar alguna bebida o revisar tu pedido?","resolver_tamano")
            if intent in ("consultar_menu","consultar_menu_infantil","ayuda"):state["pending"]=None
            else:return say("¿Qué tamaño prefieres: chica, mediana o grande? Puedes escribir 'cancelar pedido'.","aclarar_tamano")
        elif pending["kind"]=="service":
            if e.get("servicio"):
                state["service"]=e["servicio"];state["pending"]=None
                return say(summary(state["cart"],state["service"],state["promo"])+"\nEscribe 'confirmar pedido' para finalizar.","resolver_servicio")
            if intent not in ("consultar_menu","ayuda","consultar_carrito"):
                return say("¿Será para recoger o para entrega a domicilio? No necesito tu dirección.","aclarar_servicio")
        elif pending["kind"]=="product":
            if e.get("productos"):
                state["pending"]=None;intent="agregar_producto"
            elif intent not in ("ayuda","consultar_menu"):
                return say("¿Qué producto deseas? Por ejemplo: 'una hawaiana'.","aclarar_producto")
    m=catalog()
    if e.get("restriccion"):
        state["preferences"]["restriccion"]=e["restriccion"]
    if e.get("presupuesto") is not None:state["preferences"]["presupuesto"]=e["presupuesto"]
    if e.get("personas"):state["preferences"]["personas"]=e["personas"]
    if intent in ("agregar_producto","iniciar_pedido"):
        ids=e.get("productos",[])
        if not ids:
            state["pending"]={"kind":"product"};return say("¿Qué pizza, bebida o complemento deseas agregar?","solicitar_producto")
        if len(ids)>1:return say("Detecté varios productos. Para evitar errores, agrégalos uno por uno, indicando cantidad y tamaño.","aclarar_multiples")
        pid=ids[0];pizza=pid in [x["id"] for x in m["productos"]]
        if pizza and not e.get("tamano"):
            state["pending"]={"kind":"size","product":pid,"qty":e.get("cantidad",1),"extras":e.get("extras",[])}
            return say(f"¿Qué tamaño prefieres para {product_by_id(pid)['nombre']}: chica, mediana o grande?","solicitar_tamano")
        state["cart"].append(item(pid,e.get("tamano"),e.get("cantidad",1),e.get("extras",[])))
        return say(f"Agregué {e.get('cantidad',1)} × {product_by_id(pid)['nombre']}. ¿Deseas algo más?","agregar_carrito")
    if intent=="consultar_menu" or intent=="consultar_menu_infantil":
        ps=[x for x in m["productos"] if intent=="consultar_menu" or x.get("infantil")]
        return say("Menú (precios base medianos, MXN):\n"+"\n".join(f"• {x['nombre']}: ${x['precio']} — {', '.join(x['ingredientes'])}" for x in ps)+"\nTamaños: chica ×0.75, mediana ×1, grande ×1.35. Precios ficticios.","catalogo_json")
    if intent=="consultar_precios":
        ids=e.get("productos",[])
        if not ids:return say("¿De qué producto quieres consultar el precio? También puedes escribir 'menú'.","aclarar_precio")
        x=product_by_id(ids[0]);return say(f"{x['nombre']}: desde ${x['precio']} MXN (precio base para mediana en pizzas).","precio_catalogo")
    if intent=="consultar_ingredientes":
        ids=e.get("productos",[])
        if not ids:return say("¿De qué pizza quieres conocer los ingredientes?","aclarar_ingredientes")
        x=product_by_id(ids[0]);return say(f"{x['nombre']}: "+(", ".join(x["ingredientes"]) if "ingredientes" in x else "No aplica; producto sin ficha de ingredientes")+". No se garantiza ausencia de alérgenos ni contaminación cruzada.","ingredientes_catalogo")
    if intent=="recomendar":
        r=state["preferences"].get("restriccion","")
        if any(v in r for v in ("vegano","gluten","lactosa","alerg","celiac")):
            return say("No puedo garantizar opciones seguras para esa restricción: faltan fichas de alérgenos y contaminación cruzada. No recomiendo consumir un producto sin verificarlo con el establecimiento.","seguridad_alimentaria")
        candidates=[x for x in m["productos"] if not r or not "vegetarian" in r or x["vegetariana"]]
        budget=state["preferences"].get("presupuesto")
        if budget is not None:candidates=[x for x in candidates if x["precio"]<=budget]
        if not candidates:return say("No encuentro una pizza mediana dentro de ese presupuesto y preferencias.","sin_coincidencias")
        x=candidates[0]
        return say(f"Te recomiendo {x['nombre']} (mediana ${x['precio']} MXN). Ingredientes: {', '.join(x['ingredientes'])}. Si tienes alergias, no podemos garantizar seguridad alimentaria.","recomendacion_reglas")
    if intent=="consultar_promociones":
        pr=load("promociones.json");return say("Promociones de demostración:\n"+"\n".join(f"• {x['nombre']}: {x['descripcion']} (código {x['codigo']})" for x in pr if x["vigente"])+"\nPara aplicar el descuento, escribe 'aplicar FAMILIAR10'.","promociones_json")
    if "familiar10" in t and "aplicar" in t:
        state["promo"]=True;return say("Código FAMILIAR10 activado. Se aplicará únicamente si el carrito cumple la condición de dos pizzas grandes.","activar_promocion")
    if intent=="consultar_carrito":return say(summary(state["cart"],state["service"],state["promo"]),"resumen_carrito")
    if intent=="modificar_pedido":
        if not state["cart"]:return say("El carrito está vacío.","carrito_vacio")
        ids=e.get("productos",[])
        if not ids:return say("Para cambiar el tamaño, escribe 'cambia hawaiana a grande'. Para cambiar cantidad: 'cambia hawaiana a 2'.","aclarar_modificacion")
        idx=next((i for i,x in enumerate(state["cart"]) if x["id"]==ids[0]),None)
        if idx is None:return say("No encontré ese producto en el carrito.","producto_no_encontrado")
        old=state["cart"][idx];newsize=e.get("tamano",old["tamano"])
        qtymatch=__import__("re").search(r"\ba\s+(\d{1,2})\b",t)
        qty=int(qtymatch.group(1)) if qtymatch else e.get("cantidad",old["cantidad"])
        if not e.get("tamano") and not qtymatch:return say("Indica el tamaño o la cantidad nueva. Por ejemplo: 'cambia hawaiana a grande'.","aclarar_modificacion")
        try:state["cart"][idx]=item(old["id"],newsize,qty,old["extras"])
        except ValueError:return say("No pude realizar ese cambio. Revisa cantidad y tamaño.","validacion_modificacion")
        return say("Producto actualizado.\n"+summary(state["cart"],state["service"],state["promo"]),"modificar_carrito")
    if intent=="eliminar_producto":
        ids=e.get("productos",[])
        if not ids:return say("Indica qué producto quieres quitar; por ejemplo: 'quita hawaiana'.","aclarar_eliminacion")
        idx=next((i for i,x in enumerate(state["cart"]) if x["id"]==ids[0]),None)
        if idx is None:return say("Ese producto no está en el carrito.","producto_no_encontrado")
        state["cart"].pop(idx);return say("Producto eliminado.\n"+summary(state["cart"],state["service"],state["promo"]),"eliminar_carrito")
    if intent=="confirmar_pedido":
        if not state["cart"]:return say("No puedes confirmar un carrito vacío.","validar_carrito")
        if not state["service"]:
            state["pending"]={"kind":"service"};return say("¿Tu pedido será para recoger o para entrega a domicilio?","solicitar_servicio")
        state["confirmed"]=True
        return say("Pedido de demostración confirmado. Puedes descargar el comprobante PDF. No se enviará a ninguna pizzería.\n"+summary(state["cart"],state["service"],state["promo"]),"confirmacion")
    if e.get("servicio") and intent in ("desconocida","consultar_domicilio") and state["cart"]:
        state["service"]=e["servicio"];return say("Servicio establecido: "+e["servicio"]+". Puedes confirmar el pedido.","seleccionar_servicio")
    replies={"saludar":"¡Hola! Soy PizzaBot. Puedo mostrar el menú, recomendar pizzas y preparar pedidos ficticios.","despedirse":"¡Hasta pronto!","agradecer":"¡Con gusto!","consultar_horario":m["horario"],"consultar_domicilio":load("faq.json")["domicilio"],"consultar_pago":load("faq.json")["pago"],"ayuda":"Prueba: 'menú', 'menú infantil', 'ingredientes hawaiana', 'recomiéndame una vegetariana', 'quiero una pepperoni', 'dos refrescos', 'ver carrito', 'confirmar pedido' o 'cancelar pedido'."}
    if intent in replies:return say(replies[intent],"faq_o_respuesta_predefinida")
    return say("No comprendí tu mensaje. ¿Puedes reformularlo? Puedes escribir 'ayuda' para ver ejemplos.","fallback_sin_inventar")
