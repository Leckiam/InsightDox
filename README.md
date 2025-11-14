# InsightDox

**InsightDox** es una plataforma web de gestión de información empresarial que centraliza datos financieros, de ventas, remuneraciones y logística en un único lugar seguro y accesible. Incorpora inteligencia artificial para búsqueda, análisis de tendencias y predicciones, apoyando la toma de decisiones estratégicas.  

## Tecnologías utilizadas

- **Backend:** Django 5.2.6  
- **Base de datos:** MariaDB/MySQL con **mysqlclient**  
- **Almacenamiento y servicios en la nube:** Google Cloud Storage (**django-storages**, **google-cloud-storage**), manejo de credenciales con **google-auth** y **python-decouple**  
- **Manejo de archivos estáticos y media:** Whitenoise para archivos estáticos y `MEDIA` para Avatares e Informes de Costos, soporte de **ImageField** con **Pillow**  
- **API y análisis de datos:** Django REST Framework, **pandas**, **numpy**, **scikit-learn**, **sentence-transformers**  
- **Procesamiento de archivos Excel:** **openpyxl**  
- **Seguridad y autenticación:** Django Auth, manejo de roles y permisos, integración con APIs de Google para autenticación y acceso seguro  
- **Soporte de conexiones externas:** **requests** para integración con APIs externas  
- **Frontend y estilos:** Bootstrap 5, modales y previsualización de imágenes con JavaScript  

## Tecnologías utilizadas

- **Phi3:mini (Ollama local):** Genera respuestas naturales y legibles en español a las consultas de los usuarios sobre movimientos financieros.
- **RandomForestRegressor (scikit-learn):** Predice valores futuros de gastos y otros indicadores financieros mediante regresión basada en árboles de decisión.
- **LogisticRegression (scikit-learn):** Clasifica la intención del usuario para determinar qué tipo de análisis o consulta se debe ejecutar.

## Objetivo

Optimizar procesos, reducir costos y mejorar la eficiencia en la comunicación y análisis de información dentro de las organizaciones, incorporando control de usuarios, gestión de archivos y análisis avanzado de datos mediante técnicas de inteligencia artificial y machine learning.  
