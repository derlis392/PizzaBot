# Arquitectura PizzaBot

```mermaid
flowchart TD
 A[Cliente] --> B[Frontend Streamlit]
 B --> C[Normalización de texto]
 C --> D[Detección de intenciones]
 C --> E[Extracción de entidades]
 D --> F[Gestor de diálogo]
 E --> F
 F <--> G[Contexto de sesión]
 F --> H[Reglas comerciales y pedidos]
 H <--> I[Catálogo JSON y promociones]
 F --> J[Generador de respuestas]
 H --> K[Comprobante PDF]
 J --> B
 K --> B
```

El motor es determinista y no realiza inferencia con modelos generativos. Los datos se cargan de JSON en modo lectura. El estado de sesión reside en `st.session_state`. La generación del PDF se realiza en memoria. Las decisiones son auditables en la pestaña didáctica.
