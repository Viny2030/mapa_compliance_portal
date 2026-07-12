# Manual de Uso — Monitor de Compliance Empresarial

**Programa de Integridad · Ley 27.401 · Estándares Internacionales**
Ecosistema Transparencia · Ph.D. Vicente H. Monteverde

---

## 1. Introducción

El **Monitor de Compliance Empresarial** es una plataforma web para gestionar, medir y reportar el Programa de Integridad de una empresa frente a la Ley 27.401 (Argentina) y a más de 20 marcos normativos internacionales (anticorrupción, privacidad, seguridad de la información, ambiental, gobernanza y digital).

La plataforma centraliza en un solo dashboard:

- El **score de compliance** por eje y por marco normativo.
- El **canal de denuncias** interno, con seguimiento de casos.
- La **gestión de riesgos**, controles, incidentes y conflictos de interés.
- El **plan de acción** y las alertas regulatorias.
- La **generación de reportes** en PDF para directorio, auditores y la Oficina Anticorrupción.

Cada cliente accede a una instancia con URL propia (por ejemplo `mapacompliance-production.up.railway.app`) y ve únicamente los módulos activados en su plan (Starter, Professional o Enterprise).

### 1.1 Navegación general

Todo el sistema se organiza en **pestañas** ubicadas en la barra superior. Existen dos tipos:

- **Pestañas internas**: cambian de contenido sin recargar la página (Dashboard, Ley 27.401, ISO 27001, etc.). Son la mayoría.
- **Pestañas que abren una página aparte**: Benchmark, Conflictos, Predictor, Incidentes, Controles, Firmas y Documentos. Cada una tiene su propio botón "← Dashboard" para volver.

En la esquina superior derecha hay un selector de idioma: **🇦🇷 ES / 🇺🇸 EN / 🇧🇷 PT**. Cambia todo el texto de la interfaz (no el contenido normativo específico de cada país, que se mantiene en su idioma original cuando corresponde).

### 1.2 Modo demo

Si la URL incluye `?demo=true`, la plataforma muestra datos ficticios de ejemplo para que un cliente potencial pueda explorar todas las pestañas sin cargar información real. Un banner en la parte superior indica "🧪 MODO DEMO — Datos ficticios" con un link para salir del modo demo (`?demo=false`).

### 1.3 Accesos con PIN

Algunos paneles administrativos (Canal de Denuncias — panel de gestión, Portal de Clientes, Panel de Documentos) están protegidos con un **PIN de acceso**. Al ingresar el PIN correcto se genera una sesión temporal (por defecto 8 horas) identificada por un token que se guarda en el navegador. Después de varios intentos fallidos seguidos, el sistema bloquea temporalmente los reintentos desde esa misma conexión, como medida de protección contra ataques de fuerza bruta.

---

## 2. Dashboard

Es la pantalla de inicio y da una fotografía general del estado del Programa de Integridad:

- **Score de Compliance**: número de 0 a 100 calculado a partir de seis ejes ponderados (programa, capacitación, due diligence, gestión de riesgo, comunicación/canal de denuncias, investigaciones). Incluye una barra de progreso y el nivel alcanzado (Inicial / Intermedio / Avanzado).
- **Tarjetas de Programa y Capacitación**: resumen rápido del avance en cada uno.
- **Riesgo por área**: vista compacta del mapa de riesgo.
- **Alertas activas**: notificaciones regulatorias y de vencimientos, generadas automáticamente por el sistema (scraping de fuentes oficiales como la Oficina Anticorrupción, UIF y OCDE, más alertas internas de vencimiento).
- **Cobertura por Framework**: score de implementación resumido de cada marco normativo activo, calculado sobre los controles del Cross-Framework Mapping.
- **Próximos vencimientos**: unifica plazos de capacitaciones, plan de mejora y normativa en una sola vista.

Desde el Dashboard también se accede al **Verificador de CUIT** (mismo componente que en la pestaña Due Diligence) y al **Registro RITE**.

---

## 3. Board View — Vista Ejecutiva

Pensada para presentar al Directorio o a un auditor externo. Incluye botón **🖨️ Imprimir** para generar una versión lista para reunión de Directorio.

Contiene:

- **KPIs principales** del programa en un vistazo.
- **Semáforo por eje**: estado (verde/amarillo/rojo) de cada uno de los seis ejes del score.
- **Evolución del score**: gráfico de línea con el histórico mes a mes.
- **Riesgos críticos**: listado de los riesgos de mayor severidad sin mitigar.
- **Alertas para el directorio**: alertas relevantes filtradas por importancia estratégica.
- **Próximas acciones prioritarias**: extracto del Plan de Acción.
- **Cobertura Multi-Framework**: resumen del nivel de cumplimiento de todos los marcos internacionales activos.
- **Bloque de firma**: espacio para que el responsable de Compliance y/o el Directorio dejen constancia de haber revisado el reporte.

---

## 4. Marcos normativos y estándares

Cada uno de estos marcos tiene su propia pestaña con: introducción normativa, score específico calculado sobre sus elementos, checklist de cumplimiento, referencias a artículos/secciones clave y, en varios casos, comparativas con otros marcos relacionados.

### 4.1 Ley 27.401 (Argentina)
Pestaña central de la plataforma. Mide el **nivel de madurez del Programa de Integridad** (Inicial / Medio / Avanzado) según el Art. 23. Distingue:
- **Elementos obligatorios** (Art. 23) — requeridos para contratar con el Estado Nacional (Art. 24).
- **Elementos opcionales** — elevan el nivel de madurez y son atenuantes de responsabilidad penal (Art. 9).
- Un resumen de "¿Qué falta para el siguiente nivel?" con acciones concretas sugeridas.

### 4.2 Lei 12.846/2013 — Brasil (Lei Anticorrupção)
Basada en el régimen de **responsabilidad objetiva** brasileño. Cubre elementos obligatorios del programa de integridad según el Decreto 11.129/2022 y la Portaria CGU 909/2015, factores atenuantes (Art. 7) y el mecanismo de Acordo de Leniência (Art. 16, reducción de hasta 2/3 de la multa).

### 4.3 FCPA & UK Bribery Act
Cubre dos regímenes anticorrupción con aplicación extraterritorial:
- **FCPA** (EE.UU., 1977): aplica a empresas con nexo con EE.UU. (cotización en bolsa americana, pagos en USD, filiales o empleados en territorio americano). Books & Records e Internal Controls (§ 78m(b)).
- **UK Bribery Act 2010**: la ley más estricta del mundo en la materia — *strict liability* corporativa (Sección 7) para empresas con presencia o negocios en el Reino Unido.
Incluye una tabla comparativa entre ambos regímenes.

### 4.4 LGPD — Lei Geral de Proteção de Dados (Brasil, Lei 13.709/2018)
Checklist de adecuación por capítulos clave: bases legales de tratamiento (Art. 7), score y nivel de adecuación, ítems cumplidos/pendientes, y detalle de sanciones ANPD (hasta 2% de la facturación en Brasil, máx. R$ 50 millones por infracción, más multa diaria).

### 4.5 OCDE — Lineamientos para Empresas Multinacionales (Edición 2023)
Recomendaciones de conducta empresarial responsable de los 50 países adherentes (Argentina desde 1997). Desglosa los **11 capítulos** (Políticas generales, Divulgación, Derechos humanos, Empleo, Medio ambiente, Anticorrupción, Consumidores, Ciencia y tecnología, Competencia, Fiscalidad, y el nuevo Capítulo XI de 2023 sobre cadena de suministro). Incluye información sobre el Punto de Contacto Nacional (PCN) argentino y los beneficios de adoptar el marco (acceso a fondos ESG, licitaciones de organismos multilaterales, reducción de riesgo reputacional).

### 4.6 ISO 37001 — Sistema de Gestión Antisoborno
Norma internacional certificable, complementaria a la Ley 27.401, FCPA, UK Bribery Act y Lei 12.846. Incluye cláusulas clave y una comparativa directa con la Ley 27.401.

### 4.7 ISO 14001 — Sistema de Gestión Ambiental
Cubre las cláusulas 4 a 10 (Contexto, Planificación, Operación, Mejora continua) y su integración con los KPIs del eje Ambiental del módulo ESG (emisiones GEI, efluentes, economía circular, biodiversidad).

### 4.8 ISO 45001 — Sistemas de Gestión de SST
Seguridad y Salud en el Trabajo. Relevante para sectores de alto riesgo laboral (construcción, industria, energía, minería). Cubre las cláusulas 4 a 10.

### 4.9 GDPR — Reglamento General de Protección de Datos (UE)
Checklist de los 7 principios y derechos del titular. Incluye el detalle de sanciones por nivel (hasta €10M/2% de facturación global, o hasta €20M/4% — se aplica la cifra mayor) y una comparativa GDPR vs. LGPD.

### 4.10 ESG — Environmental, Social & Governance
Tres dimensiones con score propio:
- **Ambiental**: registro de emisiones GEI por alcance (1, 2 y 3 — GRI 305), plan de reducción y tipo de reporte (interno/público, GRI/TCFD).
- **Social**: % de mujeres en directorio y gerencia media, brecha salarial de género, política DEI, auditoría salarial.
- **Gobernanza**: checklist de canal de denuncias, código de ética, directorio independiente, auditoría interna, política anticorrupción, reporte ESG anual y ratio de resolución de denuncias.
Referencia cruzada a GRI 2021, TCFD, SASB, ODS/SDG y CNV Res. 896/2021.

### 4.11 ISO 27001 — Seguridad de la Información
Score global por los 4 dominios del Anexo A (ISO 27001:2022): Organizacional (37 controles), Personas (8), Físico (14) y Tecnológico (34), con contador de controles OK / en proceso / pendientes.

### 4.12 SOC 2 — Service Organization Control 2
Marco del AICPA para proveedores cloud/SaaS, evaluado sobre los 5 Trust Service Criteria (Security es obligatorio; Availability, Processing Integrity, Confidentiality y Privacy son opcionales). Distingue reporte Tipo I (diseño) vs. Tipo II (efectividad operativa, ≥6 meses). Comparativa SOC 2 vs. ISO 27001.

### 4.13 CCPA / CPRA — California Consumer Privacy Act
Checklist de derechos y obligaciones. Sanciones: US$7.500 por infracción intencional, US$2.500 por no intencional, y acciones privadas de US$100–750 por consumidor ante brechas de datos. Comparativa CCPA vs. GDPR vs. LGPD.

### 4.14 NIS2 — Directiva de Ciberseguridad de la UE
Gestión de riesgos (Art. 21), gobernanza y responsabilidad directiva (Art. 20), cadena de suministro (Art. 21.2.d) y plazos de notificación de incidentes (24h alerta temprana, 72h evaluación inicial, 1 mes informe final). Sanciones diferenciadas para entidades esenciales (hasta €10M/2%) e importantes (hasta €7M/1,4%), con responsabilidad personal de directivos.

### 4.15 EU AI Act — Reglamento de Inteligencia Artificial de la UE
Organizado por **niveles de riesgo**: prohibido (vigente desde feb. 2025), alto riesgo (deadline ago. 2026), transparencia obligatoria (ago. 2025) y riesgo mínimo. Incluye cronograma de implementación y sanciones (hasta €35M/7% para IA prohibida).

### 4.16 ISO 27701 — Gestión de Información de Privacidad
Extensión de ISO 27001 para privacidad, alineada con GDPR/LGPD/CCPA. Requiere tener ISO 27001 como base. Cubre controladores y procesadores de datos personales.

### 4.17 PCI DSS v4.0 — Seguridad de datos de tarjetas de pago
12 requisitos organizados en 6 metas (redes seguras, protección de datos del titular, gestión de vulnerabilidades, control de acceso, monitoreo, política de seguridad). Sanciones de US$5.000 a US$100.000 mensuales por entidad incumplidora.

### 4.18 COBIT 2019 — Gobierno de TI
Los 5 dominios (EDM, APO, BAI, DSS, MEA) y su relación con ISO 27001, SOX, DORA y SOC 2. Relevante para el sector financiero y empresas cotizantes.

### 4.19 SOX — Sarbanes-Oxley Act
Para empresas que cotizan en NYSE/NASDAQ. Secciones 302 (certificación ejecutiva), 404 (ICFR — controles internos sobre reporte financiero), 409 y 802 (divulgación y retención de registros), 906 (responsabilidad penal, hasta 20 años de prisión). Mapa de relación SOX–COBIT–ISO 27001.

### 4.20 DORA — Digital Operational Resilience Act (UE)
Vigente desde el 17/1/2025 para entidades financieras y sus proveedores críticos de TIC. Cinco pilares: Gestión de Riesgos TIC, Gestión y Notificación de Incidentes, Pruebas de Resiliencia, Riesgo de Terceros y Proveedores, Intercambio de Información.

---

## 5. Herramientas transversales

### 5.1 Riesgo
- **Mapa de calor Probabilidad × Impacto**: matriz de riesgo inherente por área, con botón "Cargar autoevaluación" para completar el cuestionario base.
- **Radar de riesgo** y **Distribución** (gráfico de dona) por nivel.
- **Detalle por área**.

### 5.2 Cross-Framework Mapping
Muestra qué controles satisfacen simultáneamente varios marcos normativos a la vez, maximizando el retorno de la inversión en compliance. Incluye contador de controles mapeados, cobertura promedio por control, máxima cobertura alcanzada y una matriz de cobertura por marco. Organizado por dominio: Seguridad de la Información, Privacidad, Terceros y Cadena de Suministro, Gobernanza y Cultura, Gestión de Incidentes, Inteligencia Artificial.

### 5.3 Plan de Acción
Lista los controles pendientes del Cross-Framework Mapping, con responsable sugerido y plazo estimado, filtrable por prioridad (Alta / Media / Baja) y exportable a CSV con el botón correspondiente.

### 5.4 Capacitación (progreso)
Vista de seguimiento del avance de capacitación: progreso por módulo (gráfico de barras), radar de completitud y listado de módulos. (Para el flujo de firma de conformidad de los empleados, ver la sección "Firmas / Capacitaciones con firma" más abajo.)

### 5.5 Due Diligence
- **Verificador de CUIT contra lista OCDE**: ingresá un CUIT y el sistema consulta estado AFIP (simulado/stub en esta versión), listas UIF de personas expuestas y listas OCDE/gris/negra, devolviendo un nivel de riesgo (bajo/medio).
- **Resumen de verificaciones** e **historial** de consultas.
- **Radar de mercado**: listado en vivo, desde **MEACI** (Mapa de Empresas y Actores de Compliance Internacional), de empresas sancionadas por casos OCDE con presencia en Argentina. Es información de contexto para evaluar terceros — no implica relación comercial.

### 5.6 Internacional
Resume la **exposición internacional** de la empresa y el **marco legal aplicable** según dónde opera. Incluye también, integrado en esta misma pestaña, el contenido completo de los Lineamientos OCDE (ver 4.5).

### 5.7 RITE — Registro de Integridad (Oficina Anticorrupción)
Guía paso a paso para registrarse en la plataforma oficial de la OA (rite.gob.ar): por qué registrarse (acredita el programa para licitaciones Art. 24, reduce responsabilidad penal Art. 9), los tres módulos del RITE (Programa de Integridad, Debida Diligencia, Datos Personales) y los 5 pasos de inscripción.

### 5.8 Mejoras & Alertas
- **Alertas activas** (mismas que en el Dashboard, con más detalle).
- **Evolución del score**.
- **Brechas vs. estándar OA**: comparación entre el nivel actual, el mínimo exigido por la Oficina Anticorrupción y el nivel avanzado.
- **Plan de mejora priorizado**.
- **Accesos rápidos** a Incidentes, Controles, Predictor y Benchmark.

### 5.9 Calendario
Calendario regulatorio unificado: capacitaciones, ítems del plan de mejora y vencimientos normativos, filtrables por tipo de fuente.

### 5.10 Legislación
Catálogo normativo completo, con buscador de texto libre ("Buscar norma, artículo o tema…") que filtra por nombre, descripción, categoría o país.

### 5.11 Reporte
Genera el **Reporte Ejecutivo de Compliance**, apto para presentar a la Oficina Anticorrupción, al directorio o a auditores externos. Incluye portada, score global, y nueve secciones: datos de la organización, estado del programa (Ley 27.401), score por eje, elementos pendientes, capacitación, registro RITE, plan de mejora, cobertura por framework internacional y plan de acción priorizado.

Dos botones de exportación:
- **🖨️ Exportar PDF** — reporte ejecutivo completo.
- **🌐 PDF Frameworks** — reporte enfocado en la cobertura multi-framework internacional.

---

## 6. Canal de Denuncias

Disponible tanto integrado en el Dashboard (pestaña "🔒 Canal de Denuncias") como en la página independiente `canal_denuncias.html`. Cumple con la Ley 27.401 (Argentina) y la Ley 2/2023 (España).

**Para cualquier persona (sin necesidad de cuenta):**
- **Presentar Denuncia**: categoría (corrupción/soborno, acoso, fraude, conflicto de interés, violación de datos, incumplimiento ambiental, otro), descripción, prioridad sugerida, área relacionada, y opción de anonimato (si no es anónima, se piden datos de contacto). Al enviarla se genera un **código de seguimiento único** — es la única forma de consultar el caso después, por lo que hay que guardarlo.
- **Consultar Estado**: con el código de seguimiento se ve el estado del caso y se puede enviar/leer mensajes de seguimiento con el equipo de Compliance, sin revelar la identidad del denunciante.

**Panel de gestión (requiere PIN — ver sección 11):**
- Estadísticas: total de denuncias, recibidas, en investigación, cerradas y alertas.
- Listado filtrable por estado y prioridad, con detalle completo de cada caso.
- Alertas automáticas del sistema por: plazo de acuse de recibo vencido, plazo de respuesta próximo a vencer (10 días o menos) y casos críticos (prioridad alta con más de 30 días en investigación).
- Actualización de estado (recibida → en investigación → cerrada), prioridad y área, con posibilidad de dejar un mensaje para el denunciante.

Los plazos legales se calculan automáticamente al crear la denuncia: 7 días para el acuse de recibo y 90 días para el cierre del caso.

---

## 7. Herramientas de gestión operativa

Estas páginas se abren aparte del Dashboard (con su propio botón "← Dashboard" para volver) y suelen requerir completar formularios con datos propios de la empresa — no vienen precargadas con información real.

### 7.1 Benchmark Sectorial
Compara la posición de la empresa frente a otras registradas en el RITE del mismo sector (datos OA/RITE 2024-2025): percentil, radar comparativo contra el promedio sectorial, ranking anonimizado de empresas del sector, comparativa por eje y evolución del score propio vs. el promedio del sector.

### 7.2 Conflicto de Intereses
Declaración jurada digital con flujo de aprobación (Art. 23 inc. g) Ley 27.401):
- El **declarante** completa sus datos (nombre, CUIL, cargo, área), indica si tiene o no un conflicto de intereses y, en caso afirmativo, el tipo (participación societaria, vínculo familiar con funcionario público, cargo en competidor, beneficios de terceros, interés en contrato/licitación, otro), la empresa/persona involucrada, descripción y la medida de mitigación propuesta. Se presenta bajo declaración jurada, con la advertencia de responsabilidad penal por falsedad (Art. 275 Código Penal).
- El **responsable de Compliance** ("Vista Aprobador") revisa y resuelve las declaraciones pendientes: puede filtrarlas por Pendientes / Aprobadas / Rechazadas.

### 7.3 AI Score Predictor
Predice el score de compliance del próximo trimestre usando regresión lineal y análisis de factores, con nivel de confianza del modelo. Incluye escenarios alternativos, proyección gráfica (histórico real + línea punteada de predicción + banda de confianza del 80%), los factores de mayor impacto en la predicción y acciones recomendadas para maximizar el score. El historial de scores usado como base es editable, para recalcular la predicción con datos propios.

### 7.4 Registro de Incidentes
Log de violaciones, incumplimientos y "near-misses" (Art. 23 Ley 27.401). Al registrar un incidente se completa: título, tipo (cohecho/soborno, conflicto de intereses, fraude interno, incumplimiento de código de ética, violación de contrataciones públicas, lavado de activos, near-miss, represalia a denunciante, uso indebido de información, otro), severidad (crítico/alto/medio/bajo), área involucrada, fecha del hecho, quién lo detectó, descripción detallada y primera acción correctiva. Los incidentes se filtran por estado: Abierto, Investigando, Cerrado, y cada uno se puede avanzar de estado o eliminar desde su ficha de detalle.

### 7.5 Gestión de Controles
Controles internos alineados a ISO 27001, COSO, Ley 27.401, FCPA u otros marcos internos. Cada control tiene: marco de referencia, categoría (ambiente de control, evaluación de riesgos, actividades de control, información y comunicación, supervisión, seguridad de la información, controles anticorrupción), nombre, estado (implementado / parcial / pendiente / no aplica), % de implementación, evidencia y responsable. Vista general de implementación por marco y listado filtrable por estado.

### 7.6 Firmas — Capacitaciones con Firma de Conformidad
Registro de lecturas, conformidades y trazabilidad de empleados (Art. 23 Ley 27.401), con dos vistas:
- **👔 Vista Administrador**: crea módulos de capacitación (nombre, si son obligatorios u opcionales, fecha límite, destinatarios y contenido/descripción) y hace seguimiento de quién firmó.
- **👤 Vista Empleado (Firma)**: el empleado ingresa su nombre y firma la conformidad de haber completado cada módulo asignado.

### 7.7 Gestión Documental
Repositorio de documentos del Programa de Integridad con versionado, recordatorios de vencimiento y trazabilidad de lecturas (Art. 23 Ley 27.401):
- Alta de documentos: nombre, código/ID, tipo (código, política, procedimiento, manual, reglamento, formulario, declaración jurada, otro), versión, fecha de vigencia y de vencimiento, responsable, URL de referencia y descripción.
- Filtro por estado: Vencidos / Próximos a vencer / Vigentes.
- Cada documento admite **nuevas versiones** (con nota de cambios) y **registro de lectura/conformidad** por parte de cada empleado, que certifica haber leído la versión vigente — trazabilidad clave ante una auditoría.

---

## 8. Panel de Documentos del Cliente

Página `upload_clientes.html`, protegida con **PIN** (ver sección 11). Permite cargar y organizar la evidencia documental del programa de integridad (no confundir con la Gestión Documental de la sección 7.7, que es para políticas y procedimientos internos con control de versiones):

- **Subida de documentos**: arrastrar y soltar (o hacer clic) un archivo — PDF, XLSX, XLS, CSV, DOC o DOCX, máximo 20 MB. El tipo de documento se detecta automáticamente por su contenido y nombre de archivo (o se puede forzar manualmente desde un selector) entre 10 categorías: código de ética, política de regalos, declaraciones juradas de conflicto de interés, procedimiento de investigaciones, manual de compliance, constancia RITE, nómina de personal capacitado, listado de proveedores, mapa de riesgos y contratos con el sector público.
- El sistema procesa el archivo al subirlo: extrae texto y detecta la fecha del documento (PDF), o extrae filas/columnas y CUITs mencionados (Excel/CSV).
- **Checklist documental**: muestra qué elementos del programa de integridad ya están cubiertos con al menos un documento y cuáles faltan.
- **Listado de documentos subidos**, con la opción de eliminarlos.

**Requiere iniciar sesión con PIN** antes de poder subir o eliminar documentos.

---

## 9. Portal Admin de Clientes

Página `portal.html`, protegida con **PIN** (ver sección 11). Es el panel interno de Ecosistema Transparencia para administrar todos los clientes de la plataforma (uso del equipo de Ecosistema Transparencia, no del cliente final):

- **KPIs**: clientes activos, clientes Enterprise, clientes con sugerencias de módulos pendientes y clientes sin onboarding completado.
- **Buscador y filtros** por plan (Enterprise/Professional/Starter) o por "con sugerencias".
- **Ficha de cada cliente**, expandible en tres pestañas:
  - **Info**: estado del onboarding, CUIT, plan, sector, tamaño, país, responsable, fechas de alta/vencimiento y flags operacionales (Brasil, UE, EE.UU., cotiza en bolsa, tarjetas, sector financiero regulado, SST).
  - **Módulos**: porcentaje de módulos activos agrupados por dominio (Core, Anticorrupción, Privacidad, Seguridad, Ambiental, Gobernanza, Digital, Cross).
  - **Sugeridor**: recomienda módulos adicionales según el perfil de onboarding del cliente (sector, países donde opera, características). Permite activar un módulo puntual o todos los sugeridos de una vez.

---

## 10. Alta de nuevos clientes

### 10.1 Wizard de Onboarding interno (`onboarding.html`)
Herramienta interna (equipo de Ecosistema Transparencia) para configurar un cliente nuevo en 3 pasos: (1) perfil de la empresa y plan, (2) alcance operacional (países donde opera, características como cotizar en bolsa o procesar tarjetas) — esto determina qué módulos son obligatorios — y (3) ajuste fino de módulos y generación automática del bloque de configuración (`modulos_activos` y `onboarding`) listo para copiar en el `config.js` del cliente y en `data/clientes.json`.

### 10.2 Formulario público de solicitud (`formulario-cliente.html`)
Formulario orientado a un prospecto/cliente final para solicitar acceso a su propia plataforma: datos de la empresa, alcance operacional y plan sugerido (Starter / Professional / Enterprise), con cálculo en vivo de los módulos que se activarían. Al enviarlo, el sistema:
- Guarda un backup de la solicitud.
- Envía un email interno al equipo de Ecosistema Transparencia con todos los datos.
- Envía un email de confirmación al solicitante, con un número de referencia y la promesa de contacto en 24–48 horas.

---

## 11. Seguridad y accesos

- **PIN de Consultor y PIN de Compliance Officer**: dos roles con acceso al panel de gestión. Se configuran como variables de entorno del servidor y tienen una vigencia configurable (por defecto 30 días), pasada la cual hay que renovarlos.
- **Sesión**: al ingresar el PIN correcto se genera un token de sesión válido por un tiempo configurable (por defecto 8 horas). El mismo token habilita el acceso al Canal de Denuncias (panel), al Portal de Clientes y al Panel de Documentos — no hace falta volver a loguearse en cada uno si ya se inició sesión en cualquiera de ellos.
- **Bloqueo por intentos fallidos**: tras varios PIN incorrectos seguidos desde la misma conexión, el sistema bloquea temporalmente nuevos intentos.
- **Endpoints de escritura protegidos**: subir o eliminar documentos, ver el listado completo de clientes y ver las solicitudes de onboarding requieren sesión iniciada — no son accesibles públicamente.
- **Cierre de sesión**: disponible desde la barra de sesión en cada panel protegido.

---

## 12. Preguntas frecuentes

**¿Por qué el Score de Compliance aparece vacío al principio?**
Antes de cargar datos reales del programa (a través de los formularios de cada pestaña) el score no tiene información para calcularse. En modo demo se muestran valores de ejemplo.

**¿Los datos de "Verificador de CUIT" y "Radar de mercado" son en tiempo real?**
El verificador de CUIT AFIP/UIF/OCDE es una funcionalidad de referencia; para producción se recomienda conectar los webservices oficiales (AFIP WS_SR_PADRON_A5, listas UIF y OCDE). El Radar de mercado sí consulta en vivo el servicio externo MEACI.

**¿Qué pasa si pierdo el código de seguimiento de una denuncia?**
No hay forma de recuperarlo — es la única credencial para consultar el caso de forma anónima, por diseño (para no comprometer el anonimato del denunciante).

**¿Puedo exportar el Plan de Acción a Excel?**
Se exporta a CSV, que se abre directamente en Excel o Google Sheets.

**¿El modo demo modifica los datos reales?**
No. El modo demo solo cambia qué datos se muestran en pantalla (ficticios en vez de los cargados por la empresa); no escribe ni borra información real.

---

*Manual de Uso — Monitor de Compliance Empresarial · Ecosistema Transparencia · Ph.D. Vicente H. Monteverde*
