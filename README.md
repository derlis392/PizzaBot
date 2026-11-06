# 🍕 PizzaBot — Chatbot académico con Streamlit

Aplicación **funcional de demostración**, con productos y precios ficticios. No es una pizzería real, no procesa pagos, no solicita domicilios y no envía pedidos.

## Arquitectura y funciones
- Frontend Streamlit: conversación, accesos rápidos, catálogo y carrito.
- PLN: normalización, expresiones regulares, patrones JSON y coincidencia aproximada (`difflib`).
- Gestor de diálogo: estado de sesión, aclaraciones de tamaño y servicio, carrito y confirmación.
- Reglas: precios por tamaño, extras, promoción familiar, envío simulado y PDF.
- Didáctica: intención, entidades, traza, contexto, regla usada y análisis independiente.
- Pruebas: 30 frases etiquetadas para clasificación y pruebas adicionales de integración.

**Limitaciones conocidas:** el detector es por patrones, no comprende lenguaje abierto; se admiten pedidos de un tipo de producto por turno; no hay persistencia entre sesiones, stock, facturación ni pagos. Las promociones se activan por código. El descuento familiar aplica a dos o más pizzas grandes. La disponibilidad y seguridad alimentaria no están verificadas.

## Estructura
```
app.py
core/{nlp,dialogue,orders,knowledge,receipt}.py
data/{menu,intenciones,promociones,faq}.json
assets/logo.svg
tests/test_bot.py
docs/{arquitectura,conversaciones}.md
requirements.txt
requirements-dev.txt
.streamlit/config.toml
```

## Ejecutar localmente
1. Instala Python 3.10 o superior.
2. Descomprime el ZIP y abre una terminal en la carpeta `PizzaBot`.
3. Crea un entorno virtual: `python -m venv .venv`.
4. Actívalo: Windows `.venv\Scripts\activate`; macOS/Linux `source .venv/bin/activate`.
5. Instala: `pip install -r requirements-dev.txt`.
6. Prueba: `python -m pytest -q`.
7. Ejecuta: `streamlit run app.py`.

## Publicar en GitHub
1. Crea un repositorio público vacío llamado `PizzaBot` en github.com.
2. Desde la carpeta del proyecto: `git init`, `git add .`, `git commit -m "PizzaBot v1"`.
3. Conecta el repositorio: `git branch -M main`; `git remote add origin https://github.com/TU_USUARIO/PizzaBot.git`.
4. Publica: `git push -u origin main`. Autentícate según las opciones de GitHub (por ejemplo, GitHub CLI).
5. Verifica que `app.py`, `requirements.txt`, `core/` y `data/` estén en la raíz.

## Desplegar en Streamlit Community Cloud
1. Accede a https://share.streamlit.io/ e inicia sesión.
2. Selecciona **Create app** / **Deploy an app** y el repositorio GitHub.
3. Rama `main`, archivo principal `app.py`.
4. Publica y espera la instalación automática de `requirements.txt`.
5. Comprueba las conversaciones y descarga PDF desde el sitio desplegado.

La disponibilidad y cuotas del servicio gratuito pueden cambiar. El repositorio no necesita secretos ni tarjetas.

## Evaluación reproducible
`python -m pytest -q` ejecuta pruebas unitarias y de integración. La precisión de clasificación se calcula sobre **30 frases de prueba definidas en `tests/test_bot.py`**, no sobre una muestra independiente ni usuarios reales. No se afirma capacidad de generalización fuera de ese conjunto.

## Editar el catálogo
Edita `data/menu.json` para productos, precios, ingredientes, extras, horarios y servicios; `data/promociones.json` para promociones; `data/faq.json` para respuestas y `data/intenciones.json` para patrones. Reinicia la aplicación tras modificar archivos.

## Privacidad
Los datos de carrito y conversación se mantienen en memoria de sesión. No se escriben pedidos en archivos. Streamlit Community Cloud puede aplicar sus propias políticas de registros operativos; no introduzcas información sensible. El comprobante se genera en memoria y se descarga voluntariamente.

## Fundamento didáctico
Basado conceptualmente en la presentación *Fundamentos y Aplicaciones de Inteligencia Artificial — Sesión 9*, en especial páginas 11–16 (PLN, intenciones, entidades, diálogo, frontend/backend y arquitectura de chatbot). No utiliza IBM Watson ni servicios de nube comerciales obligatorios.
