# Evaluación ejecutada

Fecha: 2026-11-05.

Comando: `python -m pytest -q`

Resultado: **40 passed**.

- 30 pruebas parametrizadas de intenciones: 30/30 correctas. Exactitud observada = 30/30 = 100 % en este conjunto de frases diseñado para la demostración.
- 10 pruebas adicionales: extracción de entidades, seguimiento de tamaño, adición de bebida, recuperación ante ambigüedad, cálculo y promoción, modificación/eliminación/cancelación, confirmación/PDF, fuera de dominio, restricciones alimentarias y validación de errores.
- Compilación sintáctica de los módulos: correcta mediante `python -m compileall -q .`.
- Ejecución de una conversación de extremo a extremo en el motor Python: correcta.

**Pendiente:** validación visual de la aplicación con Streamlit en navegador, despliegue en Community Cloud, pruebas móviles, pruebas de concurrencia, accesibilidad y evaluación con usuarios independientes. Streamlit no estaba instalado en el entorno de validación. No se ha creado un repositorio ni publicado la aplicación.

**Advertencia metodológica:** el conjunto de frases incluye ejemplos cercanos a los patrones del sistema; por tanto, la exactitud de 100 % no mide generalización fuera del conjunto. Para una evaluación externa, recopilar y etiquetar expresiones de estudiantes no usadas al diseñar patrones y reportar precisión, recall, F1 y matriz de confusión.
