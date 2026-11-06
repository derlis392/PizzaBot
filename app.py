import streamlit as st
import pandas as pd
from pathlib import Path
from core.dialogue import initial, process
from core.nlp import analyze
from core.knowledge import catalog, load
from core.orders import totals, summary
from core.receipt import receipt

st.set_page_config(page_title="PizzaBot | Laboratorio PLN",page_icon="🍕",layout="wide")
if "bot" not in st.session_state:
    st.session_state.bot=initial()
    st.session_state.messages=[{"role":"assistant","content":"¡Bienvenido a PizzaBot! 🍕 Soy un chatbot académico. Escribe 'menú' para comenzar. Los pedidos y precios son ficticios."}]
if "trace" not in st.session_state:st.session_state.trace=[]

def send(msg):
    if not msg.strip():return
    st.session_state.messages.append({"role":"user","content":msg})
    reply=process(st.session_state.bot,msg)
    st.session_state.messages.append({"role":"assistant","content":reply})
    st.session_state.trace.append({"entrada":msg,"analisis":st.session_state.bot["last_analysis"].copy(),"regla":st.session_state.bot["rule"],"pendiente":str(st.session_state.bot["pending"])})

st.image(str(Path(__file__).parent/"assets/logo.svg"),width=210)
st.caption("Laboratorio de procesamiento de lenguaje natural · Datos y pedidos 100 % ficticios · Sin pagos reales")
tab1,tab2,tab3=st.tabs(["💬 Chatbot y pedidos","🍕 Catálogo","🧠 ¿Cómo funciona el chatbot?"])
with tab1:
    left,right=st.columns([2,1],gap="large")
    with left:
        st.subheader("Conversación")
        actions={"🍕 Menú":"menú","🎁 Promociones":"promociones","🛒 Mi pedido":"ver carrito","❔ Ayuda":"ayuda"}
        cols=st.columns(4)
        for col,(label,cmd) in zip(cols,actions.items()):
            if col.button(label,use_container_width=True):send(cmd);st.rerun()
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):st.markdown(m["content"])
        user=st.chat_input("Ej.: Quiero una hawaiana grande y luego dos refrescos")
        if user:send(user);st.rerun()
    with right:
        st.subheader("Carrito")
        b=st.session_state.bot
        st.caption("Estado: "+("Confirmado" if b["confirmed"] else "En preparación"))
        if b["cart"]:
            for i,x in enumerate(b["cart"]):
                st.write(f"**{i+1}. {x['nombre']}** · {x['tamano'] or 'Estándar'} · {x['cantidad']} × ${x['unitario']}")
                if x["extras"]:st.caption("Extras: "+", ".join(x["extras"]))
            t=totals(b["cart"],b["service"],b["promo"])
            st.metric("Total MXN",f"${t['total']:,}")
            st.caption(f"Subtotal ${t['subtotal']} · Descuento ${t['descuento']} · Entrega ${t['entrega']}")
            if not b["confirmed"]:
                if st.button("Confirmar pedido",use_container_width=True):send("confirmar pedido");st.rerun()
                if st.button("Aplicar FAMILIAR10",use_container_width=True):send("aplicar FAMILIAR10");st.rerun()
            else:
                st.download_button("📄 Descargar comprobante PDF",receipt(b["cart"],b["service"],b["promo"]),file_name="PizzaBot_comprobante_demo.pdf",mime="application/pdf",use_container_width=True)
        else:st.info("Todavía no hay productos.")
        st.divider()
        if st.button("🔄 Reiniciar conversación",use_container_width=True):
            st.session_state.bot=initial();st.session_state.messages=[{"role":"assistant","content":"Conversación reiniciada. ¿Qué deseas ordenar?"}];st.session_state.trace=[];st.rerun()
with tab2:
    m=catalog();st.info(m["aviso"])
    st.subheader("Pizzas")
    cols=st.columns(3)
    for i,x in enumerate(m["productos"]):
        with cols[i%3]:
            with st.container(border=True):
                st.markdown("### 🍕 "+x["nombre"])
                st.write(", ".join(x["ingredientes"]))
                st.write(f"**Desde ${x['precio']} MXN (mediana)**")
                if x.get("infantil"):st.caption("Menú infantil")
                if st.button("Pedir "+x["nombre"],key="p_"+x["id"]):send("quiero una "+x["id"]);st.rerun()
    st.subheader("Bebidas y complementos")
    for group in ("bebidas","complementos"):
        st.dataframe(pd.DataFrame(m[group]).rename(columns={"nombre":"Producto","precio":"Precio MXN"})[["Producto","Precio MXN"]],hide_index=True,use_container_width=True)
    st.subheader("Extras y tamaños")
    st.write(" · ".join(f"{x['id']} +${x['precio']}" for x in m["extras"]))
    st.write("Chica: 75 % del precio base · Mediana: 100 % · Grande: 135 %")
    st.warning("No hay certificación de alérgenos ni garantía de ausencia de contaminación cruzada.")
with tab3:
    st.subheader("Arquitectura del chatbot")
    st.code("Cliente → Streamlit (frontend) → Normalización → Detector de intenciones + Entidades → Gestor de diálogo → Reglas + JSON → Respuesta / Carrito / PDF",language="text")
    st.markdown("**Frontend:** captura mensajes, presenta respuestas y carrito. **Backend:** interpreta texto, mantiene el contexto, valida pedidos y calcula importes.")
    st.markdown("**Modo demostración:** inspecciona la última interacción y prueba frases sin alterar el carrito.")
    sample=st.text_input("Texto para analizar (no se envía al chatbot)","Quiero dos pizzas hawaianas grandes")
    if sample:
        a=analyze(sample)
        st.json(a)
    b=st.session_state.bot
    st.markdown("#### Estado del diálogo")
    st.json({"intencion_actual":b["intent"],"entidades":b["last_analysis"].get("entidades",{}),"pendiente":b["pending"],"servicio":b["service"],"confirmado":b["confirmed"],"preferencias":b["preferences"],"carrito":b["cart"],"regla_fuente":b["rule"]})
    st.markdown("#### Traza de interacciones")
    if st.session_state.trace:st.json(st.session_state.trace[-10:])
    else:st.info("Envía un mensaje para observar su procesamiento.")
    st.markdown("**Ejemplo contextual:** 'Quiero una hawaiana' → solicita tamaño → 'grande' → agrega pizza → 'dos refrescos' → agrega bebidas.")
    st.markdown("**Límites:** reglas y coincidencia aproximada; no hay modelo generativo, comprensión semántica general ni verificación sanitaria.")
