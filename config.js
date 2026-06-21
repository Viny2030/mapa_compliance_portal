/**
 * config.js — Monitor de Compliance Empresarial
 * ================================================
 * ÚNICO ARCHIVO A EDITAR PARA PERSONALIZAR CADA CLIENTE.
 *
 * IDIOMAS: el dashboard soporta ES / EN / PT. Todo campo de texto que se
 * muestra en pantalla debe cargarse como objeto { es: "...", en: "...", pt: "..." }.
 * Si solo completás "es", el sitio mostrará ese texto en los 3 idiomas (fallback).
 * Campos que NO se traducen (números, fechas, ids, códigos, URLs, emails,
 * nombres propios de empresa/persona) van como string plano, igual que antes.
 */

const CONFIG = {

  empresa: {
    nombre:       "Empresa Demo S.A.",            // nombre propio — no se traduce
    cuit:         "30-00000000-0",
    sector:       { es: "Construcción y obra pública", en: "Construction and public works", pt: "Construção e obras públicas" },
    tamanio:      { es: "grande", en: "large", pt: "grande" },
    pais:         "Argentina",                    // nombre propio — no se traduce
    provincias:   ["CABA", "Buenos Aires", "Córdoba"], // nombres propios — no se traducen
    internacional: true,
    logo:         "",
    color_primario: "#1a3a5c",
    responsable_compliance: "Dra. María González", // nombre propio — no se traduce
    contacto:     "compliance@empresademo.com.ar",
  },

  programa_integridad: {
    nivel_madurez:   "medio",   // valores fijos: "inicial" | "medio" | "avanzado" — los traduce el dashboard
    fecha_inicio:    "2024-03-01",
    ultima_revision: "2025-06-01",
    registrado_rite: true,
    url_rite:        "https://www.rite.gob.ar/empresas",

    elementos_obligatorios: [
      { id: "codigo_etica",      label: { es: "Código de ética / conducta", en: "Code of ethics / conduct", pt: "Código de ética / conduta" },
        estado: "completo",
        evidencia: { es: "Aprobado por Directorio 03/2024", en: "Approved by the Board 03/2024", pt: "Aprovado pela Diretoria 03/2024" } },
      { id: "reglas_licitacion", label: { es: "Reglas para contrataciones públicas y licitaciones", en: "Rules for public procurement and tenders", pt: "Regras para contratações públicas e licitações" },
        estado: "completo",
        evidencia: { es: "Procedimiento LP-001 vigente", en: "Procedure LP-001 in effect", pt: "Procedimento LP-001 vigente" } },
      { id: "capacitacion",      label: { es: "Capacitaciones periódicas a directores y empleados", en: "Periodic training for directors and employees", pt: "Treinamentos periódicos para diretores e funcionários" },
        estado: "en_progreso",
        evidencia: { es: "2 de 4 módulos completados", en: "2 of 4 modules completed", pt: "2 de 4 módulos concluídos" } },
    ],

    elementos_opcionales: [
      { id: "analisis_riesgos",  label: { es: "Análisis periódico de riesgos", en: "Periodic risk analysis", pt: "Análise periódica de riscos" },
        estado: "completo",
        evidencia: { es: "Matriz actualizada 06/2025", en: "Matrix updated 06/2025", pt: "Matriz atualizada 06/2025" } },
      { id: "canal_denuncias",   label: { es: "Canal de denuncias confidencial", en: "Confidential whistleblowing channel", pt: "Canal de denúncias confidencial" },
        estado: "completo",
        evidencia: { es: "Canal activo en compliance@empresademo.com.ar", en: "Channel active at compliance@empresademo.com.ar", pt: "Canal ativo em compliance@empresademo.com.ar" } },
      { id: "due_diligence",     label: { es: "Due diligence de terceros", en: "Third-party due diligence", pt: "Due diligence de terceiros" },
        estado: "en_progreso",
        evidencia: { es: "Protocolo DD-003 en implementación", en: "Protocol DD-003 being implemented", pt: "Protocolo DD-003 em implementação" } },
      { id: "politica_regalos",  label: { es: "Política de regalos e invitaciones", en: "Gifts and invitations policy", pt: "Política de presentes e convites" },
        estado: "completo",
        evidencia: { es: "Política GR-002 distribuida", en: "Policy GR-002 distributed", pt: "Política GR-002 distribuída" } },
      { id: "responsable",       label: { es: "Responsable interno de Compliance designado", en: "Internal Compliance Officer appointed", pt: "Responsável interno de Compliance designado" },
        estado: "completo",
        evidencia: { es: "Dra. M. González — Res. Directorio 01/2024", en: "Dr. M. González — Board Resolution 01/2024", pt: "Dra. M. González — Res. Diretoria 01/2024" } },
      { id: "politica_ddjj",     label: { es: "Política de declaraciones juradas de conflictos", en: "Conflict of interest disclosure policy", pt: "Política de declarações de conflitos de interesse" },
        estado: "pendiente",
        evidencia: { es: "", en: "", pt: "" } },
      { id: "investigaciones",   label: { es: "Procedimiento de investigaciones internas", en: "Internal investigations procedure", pt: "Procedimento de investigações internas" },
        estado: "en_progreso",
        evidencia: { es: "Borrador aprobado, pendiente implementación", en: "Draft approved, implementation pending", pt: "Rascunho aprovado, implementação pendente" } },
      { id: "plan_comunicacion", label: { es: "Plan de comunicación interna del Programa", en: "Program internal communication plan", pt: "Plano de comunicação interna do Programa" },
        estado: "pendiente",
        evidencia: { es: "", en: "", pt: "" } },
    ],
  },

  // probabilidad e impacto: escala 1-5, usados por el Mapa de Calor (matriz 5x5) en la pestaña Riesgo.
  mapa_riesgo: [
    { area: { es: "Comercial / Ventas", en: "Sales / Commercial", pt: "Comercial / Vendas" },
      riesgo: "alto", probabilidad: 4, impacto: 5,
      descripcion: { es: "Interacción frecuente con sector público. Riesgo de cohecho en licitaciones.", en: "Frequent interaction with the public sector. Risk of bribery in tenders.", pt: "Interação frequente com o setor público. Risco de suborno em licitações." } },
    { area: { es: "Compras y Abastecimiento", en: "Procurement and Supply", pt: "Compras e Abastecimento" },
      riesgo: "alto", probabilidad: 4, impacto: 4,
      descripcion: { es: "Terceros no evaluados. Riesgo de lavado por cadena de proveedores.", en: "Unvetted third parties. Money laundering risk through the supply chain.", pt: "Terceiros não avaliados. Risco de lavagem por meio da cadeia de fornecedores." } },
    { area: { es: "Finanzas y Contabilidad", en: "Finance and Accounting", pt: "Finanças e Contabilidade" },
      riesgo: "medio", probabilidad: 3, impacto: 4,
      descripcion: { es: "Registros contables. Riesgo de balances falsos (art. 300 bis CP).", en: "Accounting records. Risk of falsified financial statements.", pt: "Registros contábeis. Risco de balanços falsos." } },
    { area: { es: "Recursos Humanos", en: "Human Resources", pt: "Recursos Humanos" },
      riesgo: "medio", probabilidad: 3, impacto: 3,
      descripcion: { es: "Contratación de funcionarios públicos. Conflictos de interés.", en: "Hiring of public officials. Conflicts of interest.", pt: "Contratação de funcionários públicos. Conflitos de interesse." } },
    { area: { es: "Gobierno Corporativo", en: "Corporate Governance", pt: "Governança Corporativa" },
      riesgo: "medio", probabilidad: 2, impacto: 5,
      descripcion: { es: "Toma de decisiones. Riesgo de negociaciones incompatibles.", en: "Decision making. Risk of incompatible negotiations.", pt: "Tomada de decisões. Risco de negociações incompatíveis." } },
    { area: { es: "Operaciones / Producción", en: "Operations / Production", pt: "Operações / Produção" },
      riesgo: "bajo", probabilidad: 2, impacto: 2,
      descripcion: { es: "Bajo nivel de interacción con funcionarios públicos.", en: "Low level of interaction with public officials.", pt: "Baixo nível de interação com funcionários públicos." } },
    { area: { es: "Tecnología e Información", en: "Technology and Information", pt: "Tecnologia e Informação" },
      riesgo: "bajo", probabilidad: 2, impacto: 3,
      descripcion: { es: "Acceso a datos sensibles. Riesgo de uso indebido de información.", en: "Access to sensitive data. Risk of misuse of information.", pt: "Acesso a dados sensíveis. Risco de uso indevido de informações." } },
    { area: { es: "Relaciones Institucionales", en: "Institutional Relations", pt: "Relações Institucionais" },
      riesgo: "alto", probabilidad: 3, impacto: 5,
      descripcion: { es: "Lobby, donaciones, patrocinios. Tráfico de influencias.", en: "Lobbying, donations, sponsorships. Influence peddling.", pt: "Lobby, doações, patrocínios. Tráfico de influência." } },
  ],

  capacitaciones: [
    { modulo: { es: "Introducción a la Ley 27.401", en: "Introduction to Law 27.401", pt: "Introdução à Lei 27.401" },
      obligatorio: true, completado: 95, fecha_limite: "2026-03-31",
      destinatarios: { es: "Todos", en: "All", pt: "Todos" } },
    { modulo: { es: "Código de Ética y Conducta", en: "Code of Ethics and Conduct", pt: "Código de Ética e Conduta" },
      obligatorio: true, completado: 88, fecha_limite: "2026-03-31",
      destinatarios: { es: "Todos", en: "All", pt: "Todos" } },
    { modulo: { es: "Procedimientos en Contrataciones Públicas", en: "Public Procurement Procedures", pt: "Procedimentos em Contratações Públicas" },
      obligatorio: true, completado: 72, fecha_limite: "2026-06-30",
      destinatarios: { es: "Comercial, Compras", en: "Sales, Procurement", pt: "Comercial, Compras" } },
    { modulo: { es: "Due Diligence de Terceros", en: "Third-Party Due Diligence", pt: "Due Diligence de Terceiros" },
      obligatorio: false, completado: 45, fecha_limite: "2026-09-30",
      destinatarios: { es: "Compras, Finanzas", en: "Procurement, Finance", pt: "Compras, Finanças" } },
    { modulo: { es: "Prevención de Lavado de Activos (UIF)", en: "Anti-Money Laundering (AML)", pt: "Prevenção à Lavagem de Dinheiro (UIF)" },
      obligatorio: true, completado: 60, fecha_limite: "2026-06-30",
      destinatarios: { es: "Finanzas, Directores", en: "Finance, Directors", pt: "Finanças, Diretores" } },
    { modulo: { es: "FCPA y Normativa Internacional", en: "FCPA and International Regulations", pt: "FCPA e Normativa Internacional" },
      obligatorio: false, completado: 30, fecha_limite: "2026-12-31",
      destinatarios: { es: "Directores, Comercial", en: "Directors, Sales", pt: "Diretores, Comercial" } },
  ],

  // area_vinculada: nombre del área en mapa_riesgo (en español, clave estable) que se ve afectada
  // por este proveedor. Si resultado==="alerta_ocde", el Mapa de Calor sube el riesgo de esa área.
  cuits_verificados: [
    { razon_social: "Proveedor Ejemplo 1 S.R.L.", cuit: "30-11111111-1", fecha: "2025-05-10", resultado: "sin_antecedentes", area_vinculada: "Compras y Abastecimiento" },
    { razon_social: "Proveedor Ejemplo 2 S.A.",   cuit: "30-22222222-2", fecha: "2025-04-20", resultado: "sin_antecedentes", area_vinculada: "Comercial / Ventas" },
    { razon_social: "Siemens S.A.",               cuit: "30-54667581-3", fecha: "2025-03-15", resultado: "alerta_ocde",     area_vinculada: "Compras y Abastecimiento" },
  ],

  historial_score: [
    { mes: "Ene 2026", score: 42 },
    { mes: "Feb 2026", score: 48 },
    { mes: "Mar 2026", score: 53 },
    { mes: "Abr 2026", score: 58 },
    { mes: "May 2026", score: 63 },
    { mes: "Jun 2026", score: 67 },
  ],

  plan_mejora: [
    { accion: { es: "Completar módulo UIF/Lavado de Activos", en: "Complete the AML module", pt: "Concluir o módulo de Lavagem de Dinheiro" },
      prioridad: "alta",
      responsable: { es: "RRHH", en: "HR", pt: "RH" },
      vence: "2026-06-30", estado: "en_progreso" },
    { accion: { es: "Implementar política de DDJJ conflictos interés", en: "Implement conflict of interest disclosure policy", pt: "Implementar política de declarações de conflito de interesse" },
      prioridad: "alta",
      responsable: { es: "Compliance", en: "Compliance", pt: "Compliance" },
      vence: "2026-07-31", estado: "pendiente" },
    { accion: { es: "Finalizar procedimiento investigaciones internas", en: "Finalize internal investigations procedure", pt: "Finalizar procedimento de investigações internas" },
      prioridad: "media",
      responsable: { es: "Legal", en: "Legal", pt: "Jurídico" },
      vence: "2026-08-31", estado: "en_progreso" },
    { accion: { es: "Desarrollar plan de comunicación interna", en: "Develop internal communication plan", pt: "Desenvolver plano de comunicação interna" },
      prioridad: "media",
      responsable: { es: "Compliance", en: "Compliance", pt: "Compliance" },
      vence: "2026-09-30", estado: "pendiente" },
    { accion: { es: "Ampliar due diligence a 10 proveedores clave", en: "Extend due diligence to 10 key vendors", pt: "Ampliar due diligence para 10 fornecedores-chave" },
      prioridad: "baja",
      responsable: { es: "Compras", en: "Procurement", pt: "Compras" },
      vence: "2026-12-31", estado: "en_progreso" },
  ],

  exposicion_internacional: {
    opera_en_usa:    false,
    opera_en_uk:     false,
    opera_en_brasil: true,
    opera_en_ue:     false,
    // Nombres oficiales de leyes — no se traducen, son nombres propios
    leyes_aplicables: ["Convención OCDE (Ley 25.319)", "UNCAC (Ley 26.097)", "Lei Anticorrupção Brasil 12.846/2013"],
  },

  meaci_url: "https://meaci-production.up.railway.app",
  meaci_api: "https://meaci-production.up.railway.app/api/cruce-compr",
};