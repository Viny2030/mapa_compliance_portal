# Manual de Uso — Monitor de Compliance Empresarial

**Programa de Integridade · Lei 27.401 (Argentina) · Padrões Internacionais**
Ecosistema Transparencia · Ph.D. Vicente H. Monteverde

---

## 1. Introdução

O **Monitor de Compliance Empresarial** é uma plataforma web para gerenciar, medir e reportar o Programa de Integridade de uma empresa frente à Lei 27.401 (Argentina) e a mais de 20 marcos normativos internacionais (anticorrupção, privacidade, segurança da informação, ambiental, governança e digital).

A plataforma centraliza em um único dashboard:

- O **score de compliance** por eixo e por marco normativo.
- O **canal de denúncias** interno, com acompanhamento de casos.
- A **gestão de riscos**, controles, incidentes e conflitos de interesse.
- O **plano de ação** e os alertas regulatórios.
- A **geração de relatórios** em PDF para a diretoria, auditores e a Oficina Anticorrupción (órgão anticorrupção argentino).

Cada cliente acessa uma instância com URL própria (por exemplo `mapacompliance-production.up.railway.app`) e vê apenas os módulos ativados no seu plano (Starter, Professional ou Enterprise).

### 1.1 Navegação geral

Todo o sistema é organizado em **abas** na barra superior. Existem dois tipos:

- **Abas internas**: trocam o conteúdo sem recarregar a página (Dashboard, Lei 27.401, ISO 27001, etc.). São a maioria.
- **Abas que abrem uma página separada**: Benchmark, Conflitos, Preditor, Incidentes, Controles, Assinaturas e Documentos. Cada uma tem seu próprio botão "← Dashboard" para voltar.

No canto superior direito há um seletor de idioma: **🇦🇷 ES / 🇺🇸 EN / 🇧🇷 PT**. Ele traduz todo o texto da interface (não o conteúdo normativo específico de cada país, que permanece no idioma original quando aplicável).

### 1.2 Modo demonstração

Se a URL incluir `?demo=true`, a plataforma exibe dados fictícios de exemplo para que um cliente em potencial explore todas as abas sem carregar informações reais. Um banner no topo indica "🧪 MODO DEMO — Dados fictícios", com um link para sair do modo demo (`?demo=false`).

### 1.3 Acessos com PIN

Alguns painéis administrativos (Canal de Denúncias — painel de gestão, Portal de Clientes, Painel de Documentos) são protegidos por um **PIN de acesso**. Ao inserir o PIN correto, é gerada uma sessão temporária (por padrão 8 horas) identificada por um token salvo no navegador. Após várias tentativas incorretas seguidas, o sistema bloqueia temporariamente novas tentativas a partir da mesma conexão, como medida de proteção contra ataques de força bruta.

---

## 2. Dashboard

É a tela inicial e dá uma fotografia geral do estado do Programa de Integridade:

- **Score de Compliance**: número de 0 a 100 calculado a partir de seis eixos ponderados (programa, capacitação, due diligence, gestão de risco, comunicação/canal de denúncias, investigações). Inclui uma barra de progresso e o nível alcançado (Inicial / Intermediário / Avançado).
- **Cartões de Programa e Capacitação**: resumo rápido do avanço em cada um.
- **Risco por área**: visão compacta do mapa de risco.
- **Alertas ativos**: notificações regulatórias e de vencimentos, geradas automaticamente pelo sistema (raspagem de fontes oficiais como a Oficina Anticorrupción, a UIF e a OCDE, além de alertas internos de vencimento).
- **Cobertura por Framework**: score de implementação resumido de cada marco normativo ativo, calculado sobre os controles do Cross-Framework Mapping.
- **Próximos vencimentos**: unifica prazos de capacitações, plano de melhoria e normativa em uma única visão.

A partir do Dashboard também se acessa o **Verificador de CUIT** (mesmo componente da aba Due Diligence) e o **Registro RITE**.

---

## 3. Board View — Visão Executiva

Pensada para apresentar à Diretoria ou a um auditor externo. Inclui o botão **🖨️ Imprimir** para gerar uma versão pronta para reunião de diretoria.

Contém:

- **KPIs principais** do programa em uma visão geral.
- **Semáforo por eixo**: status (verde/amarelo/vermelho) de cada um dos seis eixos do score.
- **Evolução do score**: gráfico de linha com o histórico mês a mês.
- **Riscos críticos**: lista dos riscos de maior severidade ainda não mitigados.
- **Alertas para a diretoria**: alertas relevantes filtrados por importância estratégica.
- **Próximas ações prioritárias**: extrato do Plano de Ação.
- **Cobertura Multi-Framework**: resumo do nível de conformidade de todos os marcos internacionais ativos.
- **Bloco de assinatura**: espaço para que o responsável de Compliance e/ou a Diretoria registrem a revisão do relatório.

---

## 4. Marcos normativos e padrões

Cada um desses marcos tem sua própria aba com: introdução normativa, score específico calculado sobre seus elementos, checklist de conformidade, referências a artigos/seções-chave e, em vários casos, comparações com outros marcos relacionados.

### 4.1 Lei 27.401 (Argentina)
Aba central da plataforma. Mede o **nível de maturidade do Programa de Integridade** (Inicial / Médio / Avançado) segundo o Art. 23. Distingue:
- **Elementos obrigatórios** (Art. 23) — exigidos para contratar com o Estado Nacional (Art. 24).
- **Elementos opcionais** — elevam o nível de maturidade e são atenuantes de responsabilidade penal (Art. 9).
- Um resumo de "O que falta para o próximo nível?" com ações concretas sugeridas.

### 4.2 Lei 12.846/2013 — Brasil (Lei Anticorrupção)
Baseada no regime de **responsabilidade objetiva** brasileiro. Cobre elementos obrigatórios do programa de integridade segundo o Decreto 11.129/2022 e a Portaria CGU 909/2015, fatores atenuantes (Art. 7) e o mecanismo de Acordo de Leniência (Art. 16, redução de até 2/3 da multa).

### 4.3 FCPA & UK Bribery Act
Cobre dois regimes anticorrupção com aplicação extraterritorial:
- **FCPA** (EUA, 1977): aplica-se a empresas com vínculo com os EUA (listagem em bolsa americana, pagamentos em USD, filiais ou funcionários em território americano). Books & Records e Internal Controls (§ 78m(b)).
- **UK Bribery Act 2010**: a lei mais rígida do mundo na matéria — *strict liability* corporativa (Seção 7) para empresas com presença ou negócios no Reino Unido.
Inclui uma tabela comparativa entre os dois regimes.

### 4.4 LGPD — Lei Geral de Proteção de Dados (Lei 13.709/2018)
Checklist de adequação por capítulos-chave: bases legais de tratamento (Art. 7), score e nível de adequação, itens cumpridos/pendentes, e detalhe das sanções da ANPD (até 2% do faturamento no Brasil, máx. R$ 50 milhões por infração, mais multa diária).

### 4.5 OCDE — Diretrizes para Empresas Multinacionais (Edição 2023)
Recomendações de conduta empresarial responsável dos 50 países aderentes (Argentina desde 1997). Detalha os **11 capítulos** (Políticas gerais, Divulgação, Direitos humanos, Emprego, Meio ambiente, Anticorrupção, Consumidores, Ciência e tecnologia, Concorrência, Tributação, e o novo Capítulo XI de 2023 sobre cadeia de suprimentos). Inclui informações sobre o Ponto de Contato Nacional (PCN) argentino e os benefícios de adotar o marco (acesso a fundos ESG, licitações de organismos multilaterais, redução de risco reputacional).

### 4.6 ISO 37001 — Sistema de Gestão Antissuborno
Norma internacional certificável, complementar à Lei 27.401, FCPA, UK Bribery Act e Lei 12.846. Inclui cláusulas-chave e uma comparação direta com a Lei 27.401.

### 4.7 ISO 14001 — Sistema de Gestão Ambiental
Cobre as cláusulas 4 a 10 (Contexto, Planejamento, Operação, Melhoria contínua) e sua integração com os KPIs do eixo Ambiental do módulo ESG (emissões de GEE, efluentes, economia circular, biodiversidade).

### 4.8 ISO 45001 — Sistemas de Gestão de SST
Segurança e Saúde no Trabalho. Relevante para setores de alto risco laboral (construção, indústria, energia, mineração). Cobre as cláusulas 4 a 10.

### 4.9 GDPR — Regulamento Geral de Proteção de Dados (UE)
Checklist dos 7 princípios e direitos do titular. Inclui o detalhe das sanções por nível (até €10M/2% do faturamento global, ou até €20M/4% — aplica-se o valor maior) e uma comparação GDPR vs. LGPD.

### 4.10 ESG — Environmental, Social & Governance
Três dimensões com score próprio:
- **Ambiental**: registro de emissões de GEE por escopo (1, 2 e 3 — GRI 305), plano de redução e tipo de relatório (interno/público, GRI/TCFD).
- **Social**: % de mulheres na diretoria e na gerência média, diferença salarial de gênero, política DEI, auditoria salarial.
- **Governança**: checklist de canal de denúncias, código de ética, diretoria independente, auditoria interna, política anticorrupção, relatório ESG anual e taxa de resolução de denúncias.
Referência cruzada a GRI 2021, TCFD, SASB, ODS/SDG e Resolução CVM 896/2021 (equivalente à CNV Argentina).

### 4.11 ISO 27001 — Segurança da Informação
Score global pelos 4 domínios do Anexo A (ISO 27001:2022): Organizacional (37 controles), Pessoas (8), Físico (14) e Tecnológico (34), com contador de controles OK / em andamento / pendentes.

### 4.12 SOC 2 — Service Organization Control 2
Marco do AICPA para provedores cloud/SaaS, avaliado sobre os 5 Trust Service Criteria (Security é obrigatório; Availability, Processing Integrity, Confidentiality e Privacy são opcionais). Distingue relatório Tipo I (desenho) vs. Tipo II (efetividade operacional, ≥6 meses). Comparação SOC 2 vs. ISO 27001.

### 4.13 CCPA / CPRA — California Consumer Privacy Act
Checklist de direitos e obrigações. Sanções: US$7.500 por infração intencional, US$2.500 por infração não intencional, e ações privadas de US$100–750 por consumidor em casos de vazamento de dados. Comparação CCPA vs. GDPR vs. LGPD.

### 4.14 NIS2 — Diretiva de Cibersegurança da UE
Gestão de riscos (Art. 21), governança e responsabilidade da diretoria (Art. 20), cadeia de suprimentos (Art. 21.2.d) e prazos de notificação de incidentes (24h alerta antecipado, 72h avaliação inicial, 1 mês relatório final). Sanções diferenciadas para entidades essenciais (até €10M/2%) e importantes (até €7M/1,4%), com responsabilidade pessoal de diretores.

### 4.15 EU AI Act — Regulamento de Inteligência Artificial da UE
Organizado por **níveis de risco**: proibido (vigente desde fev. 2025), alto risco (prazo ago. 2026), transparência obrigatória (ago. 2025) e risco mínimo. Inclui cronograma de implementação e sanções (até €35M/7% para IA proibida).

### 4.16 ISO 27701 — Gestão de Informações de Privacidade
Extensão da ISO 27001 para privacidade, alinhada com GDPR/LGPD/CCPA. Requer ISO 27001 como base. Cobre controladores e operadores de dados pessoais.

### 4.17 PCI DSS v4.0 — Segurança de dados de cartões de pagamento
12 requisitos organizados em 6 metas (redes seguras, proteção de dados do titular, gestão de vulnerabilidades, controle de acesso, monitoramento, política de segurança). Sanções de US$5.000 a US$100.000 mensais por entidade não conforme.

### 4.18 COBIT 2019 — Governança de TI
Os 5 domínios (EDM, APO, BAI, DSS, MEA) e sua relação com ISO 27001, SOX, DORA e SOC 2. Relevante para o setor financeiro e empresas listadas em bolsa.

### 4.19 SOX — Sarbanes-Oxley Act
Para empresas listadas na NYSE/NASDAQ. Seções 302 (certificação executiva), 404 (ICFR — controles internos sobre relatórios financeiros), 409 e 802 (divulgação e retenção de registros), 906 (responsabilidade penal, até 20 anos de prisão). Mapa de relação SOX–COBIT–ISO 27001.

### 4.20 DORA — Digital Operational Resilience Act (UE)
Vigente desde 17/1/2025 para entidades financeiras e seus fornecedores críticos de TIC. Cinco pilares: Gestão de Riscos de TIC, Gestão e Notificação de Incidentes, Testes de Resiliência Operacional, Risco de Terceiros e Fornecedores, e Compartilhamento de Informações.

---

## 5. Ferramentas transversais

### 5.1 Risco
- **Mapa de calor Probabilidade × Impacto**: matriz de risco inerente por área, com botão "Carregar autoavaliação" para preencher o questionário base.
- **Radar de risco** e **Distribuição** (gráfico de rosca) por nível.
- **Detalhe por área**.

### 5.2 Cross-Framework Mapping
Mostra quais controles satisfazem simultaneamente vários marcos normativos ao mesmo tempo, maximizando o retorno do investimento em compliance. Inclui contador de controles mapeados, cobertura média por controle, cobertura máxima alcançada e uma matriz de cobertura por marco. Organizado por domínio: Segurança da Informação, Privacidade, Terceiros e Cadeia de Suprimentos, Governança e Cultura, Gestão de Incidentes, Inteligência Artificial.

### 5.3 Plano de Ação
Lista os controles pendentes do Cross-Framework Mapping, com responsável sugerido e prazo estimado, filtrável por prioridade (Alta / Média / Baixa) e exportável para CSV pelo botão correspondente.

### 5.4 Capacitação (progresso)
Visão de acompanhamento do avanço da capacitação: progresso por módulo (gráfico de barras), radar de conclusão e lista de módulos. (Para o fluxo de assinatura de conformidade dos funcionários, veja a seção "Assinaturas / Capacitações com assinatura" abaixo.)

### 5.5 Due Diligence
- **Verificador de CUIT contra lista da OCDE**: informe um CUIT e o sistema consulta o status na AFIP (simulado/stub nesta versão), listas da UIF de pessoas expostas politicamente e listas cinza/negra da OCDE, retornando um nível de risco (baixo/médio).
- **Resumo das verificações** e **histórico** de consultas.
- **Radar de mercado**: listagem ao vivo, a partir do **MEACI** (Mapa de Empresas e Atores de Compliance Internacional), de empresas sancionadas em casos da OCDE com presença na Argentina. É informação de contexto para avaliar terceiros — não implica relação comercial.

### 5.6 Internacional
Resume a **exposição internacional** da empresa e o **marco legal aplicável** conforme onde ela opera. Também inclui, integrado nesta mesma aba, o conteúdo completo das Diretrizes da OCDE (ver 4.5).

### 5.7 RITE — Registro de Integridade (Oficina Anticorrupción)
Guia passo a passo para se cadastrar na plataforma oficial do órgão anticorrupção argentino (rite.gob.ar): por que se cadastrar (credencia o programa para licitações do Art. 24, reduz a responsabilidade penal do Art. 9), os três módulos do RITE (Programa de Integridade, Due Diligence, Dados Pessoais) e os 5 passos de inscrição.

### 5.8 Melhorias & Alertas
- **Alertas ativos** (mesmos do Dashboard, com mais detalhe).
- **Evolução do score**.
- **Lacunas vs. padrão da Oficina Anticorrupción**: comparação entre o nível atual, o mínimo exigido pelo órgão anticorrupção e o nível avançado.
- **Plano de melhoria priorizado**.
- **Acessos rápidos** para Incidentes, Controles, Preditor e Benchmark.

### 5.9 Calendário
Calendário regulatório unificado: capacitações, itens do plano de melhoria e vencimentos normativos, filtráveis por tipo de fonte.

### 5.10 Legislação
Catálogo normativo completo, com busca de texto livre ("Buscar norma, artigo ou tema…") que filtra por nome, descrição, categoria ou país.

### 5.11 Relatório
Gera o **Relatório Executivo de Compliance**, apto para apresentar à Oficina Anticorrupción, à diretoria ou a auditores externos. Inclui capa, score global, e nove seções: dados da organização, status do programa (Lei 27.401), score por eixo, elementos pendentes, capacitação, registro RITE, plano de melhoria, cobertura por framework internacional e plano de ação priorizado.

Dois botões de exportação:
- **🖨️ Exportar PDF** — relatório executivo completo.
- **🌐 PDF Frameworks** — relatório focado na cobertura multi-framework internacional.

---

## 6. Canal de Denúncias

Disponível tanto integrado ao Dashboard (aba "🔒 Canal de Denúncias") quanto na página independente `canal_denuncias.html`. Atende à Lei 27.401 (Argentina) e à Lei 2/2023 (Espanha).

**Para qualquer pessoa (sem necessidade de conta):**
- **Registrar Denúncia**: categoria (corrupção/suborno, assédio, fraude, conflito de interesse, violação de dados, descumprimento ambiental, outro), descrição, prioridade sugerida, área relacionada, e opção de anonimato (se não for anônima, são solicitados dados de contato). Ao enviá-la, é gerado um **código de acompanhamento único** — é a única forma de consultar o caso depois, por isso deve ser guardado.
- **Consultar Status**: com o código de acompanhamento é possível ver o status do caso e enviar/ler mensagens de acompanhamento com a equipe de Compliance, sem revelar a identidade do denunciante.

**Painel de gestão (requer PIN — ver seção 11):**
- Estatísticas: total de denúncias, recebidas, em investigação, encerradas e alertas.
- Lista filtrável por status e prioridade, com detalhe completo de cada caso.
- Alertas automáticos do sistema por: prazo de confirmação de recebimento vencido, prazo de resposta próximo do vencimento (10 dias ou menos) e casos críticos (prioridade alta com mais de 30 dias em investigação).
- Atualização de status (recebida → em investigação → encerrada), prioridade e área, com possibilidade de deixar uma mensagem para o denunciante.

Os prazos legais são calculados automaticamente ao criar a denúncia: 7 dias para a confirmação de recebimento e 90 dias para o encerramento do caso.

---

## 7. Ferramentas de gestão operacional

Essas páginas abrem separadamente do Dashboard (cada uma com seu próprio botão "← Dashboard" para voltar) e geralmente exigem o preenchimento de formulários com dados próprios da empresa — não vêm pré-carregadas com informações reais.

### 7.1 Benchmark Setorial
Compara a posição da empresa frente a outras registradas no RITE do mesmo setor (dados OA/RITE 2024-2025): percentil, radar comparativo contra a média setorial, ranking anonimizado de empresas do setor, comparação por eixo e evolução do score próprio vs. a média do setor.

### 7.2 Conflito de Interesses
Declaração juramentada digital com fluxo de aprovação (Art. 23, inciso g, da Lei 27.401):
- O **declarante** preenche seus dados (nome, CUIL/documento, cargo, área), indica se tem ou não um conflito de interesses e, em caso afirmativo, o tipo (participação societária em fornecedor/cliente, vínculo familiar com agente público, cargo em concorrente, benefícios de terceiros, interesse em contrato/licitação, outro), a empresa/pessoa envolvida, descrição e a medida de mitigação proposta. É apresentada como declaração juramentada, com aviso de responsabilidade penal por falsidade (Art. 275 do Código Penal argentino).
- O **responsável de Compliance** ("Visão Aprovador") revisa e resolve as declarações pendentes, filtráveis por Pendentes / Aprovadas / Rejeitadas.

### 7.3 AI Score Predictor
Prevê o score de compliance do próximo trimestre usando regressão linear e análise de fatores, com nível de confiança do modelo. Inclui cenários alternativos, projeção gráfica (histórico real + linha pontilhada de previsão + faixa de confiança de 80%), os fatores de maior impacto na previsão e ações recomendadas para maximizar o score. O histórico de scores usado como base é editável, para recalcular a previsão com dados próprios.

### 7.4 Registro de Incidentes
Log de violações, descumprimentos e "near-misses" (quase-incidentes) (Art. 23 da Lei 27.401). Ao registrar um incidente, preenche-se: título, tipo (corrupção/suborno, conflito de interesses, fraude interna, descumprimento do código de ética, violação de contratações públicas, lavagem de dinheiro, near-miss, retaliação a denunciante, uso indevido de informação, outro), severidade (crítico/alto/médio/baixo), área envolvida, data do fato, quem detectou, descrição detalhada e primeira ação corretiva. Os incidentes são filtráveis por status: Aberto, Investigando, Encerrado, e cada um pode ter seu status avançado ou ser excluído a partir de sua ficha de detalhe.

### 7.5 Gestão de Controles
Controles internos alinhados a ISO 27001, COSO, Lei 27.401, FCPA ou outros marcos internos. Cada controle tem: marco de referência, categoria (ambiente de controle, avaliação de riscos, atividades de controle, informação e comunicação, supervisão, segurança da informação, controles anticorrupção), nome, status (implementado / parcial / pendente / não aplicável), % de implementação, evidência e responsável. Visão geral de implementação por marco e lista filtrável por status.

### 7.6 Assinaturas — Capacitações com Assinatura de Conformidade
Registro de leituras, conformidades e rastreabilidade de funcionários (Art. 23 da Lei 27.401), com duas visões:
- **👔 Visão Administrador**: cria módulos de capacitação (nome, se são obrigatórios ou opcionais, prazo, destinatários e conteúdo/descrição) e acompanha quem assinou.
- **👤 Visão Funcionário (Assinatura)**: o funcionário informa seu nome e assina a conformidade de ter concluído cada módulo atribuído.

### 7.7 Gestão Documental
Repositório de documentos do Programa de Integridade com versionamento, lembretes de vencimento e rastreabilidade de leituras (Art. 23 da Lei 27.401):
- Cadastro de documentos: nome, código/ID, tipo (código, política, procedimento, manual, regulamento, formulário, declaração juramentada, outro), versão, data de vigência e de vencimento, responsável, URL de referência e descrição.
- Filtro por status: Vencidos / Próximos do vencimento / Vigentes.
- Cada documento admite **novas versões** (com nota de alterações) e **registro de leitura/conformidade** por cada funcionário, certificando que leu a versão vigente — rastreabilidade fundamental diante de uma auditoria.

---

## 8. Painel de Documentos do Cliente

Página `upload_clientes.html`, protegida por **PIN** (ver seção 11). Permite carregar e organizar as evidências documentais do programa de integridade (não confundir com a Gestão Documental da seção 7.7, que é para políticas e procedimentos internos com controle de versões):

- **Upload de documentos**: arrastar e soltar (ou clicar) um arquivo — PDF, XLSX, XLS, CSV, DOC ou DOCX, no máximo 20 MB. O tipo de documento é detectado automaticamente pelo seu conteúdo e nome de arquivo (ou pode ser forçado manualmente por um seletor) entre 10 categorias: código de ética, política de presentes, declarações juramentadas de conflito de interesse, procedimento de investigações, manual de compliance, comprovante de registro RITE, lista de pessoal capacitado, lista de fornecedores, mapa de riscos e contratos com o setor público.
- O sistema processa o arquivo no momento do upload: extrai texto e detecta a data do documento (PDF), ou extrai linhas/colunas e CUITs mencionados (Excel/CSV).
- **Checklist documental**: mostra quais elementos do programa de integridade já estão cobertos por pelo menos um documento e quais faltam.
- **Lista de documentos enviados**, com a opção de excluí-los.

**Requer login com PIN** antes de poder enviar ou excluir documentos.

---

## 9. Portal Admin de Clientes

Página `portal.html`, protegida por **PIN** (ver seção 11). É o painel interno da Ecosistema Transparencia para administrar todos os clientes da plataforma (uso da equipe da Ecosistema Transparencia, não do cliente final):

- **KPIs**: clientes ativos, clientes Enterprise, clientes com sugestões de módulos pendentes e clientes sem onboarding concluído.
- **Busca e filtros** por plano (Enterprise/Professional/Starter) ou por "com sugestões".
- **Ficha de cada cliente**, expansível em três abas:
  - **Info**: status do onboarding, CUIT, plano, setor, tamanho, país, responsável, datas de cadastro/vencimento e flags operacionais (Brasil, UE, EUA, listada em bolsa, cartões, setor financeiro regulado, SST).
  - **Módulos**: percentual de módulos ativos agrupados por domínio (Core, Anticorrupção, Privacidade, Segurança, Ambiental, Governança, Digital, Cross).
  - **Sugestor**: recomenda módulos adicionais conforme o perfil de onboarding do cliente (setor, países onde opera, características). Permite ativar um módulo específico ou todos os sugeridos de uma vez.

---

## 10. Cadastro de novos clientes

### 10.1 Assistente de Onboarding interno (`onboarding.html`)
Ferramenta interna (equipe da Ecosistema Transparencia) para configurar um novo cliente em 3 etapas: (1) perfil da empresa e plano, (2) alcance operacional (países onde opera, características como estar listada em bolsa ou processar cartões) — isso determina quais módulos são obrigatórios — e (3) ajuste fino de módulos e geração automática do bloco de configuração (`modulos_activos` e `onboarding`) pronto para colar no `config.js` do cliente e no `data/clientes.json`.

### 10.2 Formulário público de solicitação (`formulario-cliente.html`)
Formulário voltado a um prospect/cliente final para solicitar acesso à sua própria plataforma: dados da empresa, alcance operacional e plano sugerido (Starter / Professional / Enterprise), com cálculo em tempo real dos módulos que seriam ativados. Ao enviá-lo, o sistema:
- Salva um backup da solicitação.
- Envia um e-mail interno à equipe da Ecosistema Transparencia com todos os dados.
- Envia um e-mail de confirmação ao solicitante, com um número de referência e a promessa de contato em 24–48 horas.

---

## 11. Segurança e acessos

- **PIN de Consultor e PIN de Responsável de Compliance**: dois perfis com acesso ao painel de gestão. São configurados como variáveis de ambiente do servidor e têm validade configurável (30 dias por padrão), após a qual devem ser renovados.
- **Sessão**: ao inserir o PIN correto, é gerado um token de sessão válido por um tempo configurável (8 horas por padrão). O mesmo token habilita o acesso ao Canal de Denúncias (painel), ao Portal de Clientes e ao Painel de Documentos — não é necessário logar novamente em cada um se já iniciou sessão em qualquer um deles.
- **Bloqueio por tentativas incorretas**: após várias tentativas de PIN incorreto seguidas a partir da mesma conexão, o sistema bloqueia temporariamente novas tentativas.
- **Endpoints de escrita protegidos**: enviar ou excluir documentos, ver a lista completa de clientes e ver as solicitações de onboarding exigem sessão iniciada — não são acessíveis publicamente.
- **Encerrar sessão**: disponível na barra de sessão em cada painel protegido.

---

## 12. Perguntas frequentes

**Por que o Score de Compliance aparece vazio no início?**
Antes de carregar dados reais do programa (por meio dos formulários de cada aba), o score não tem informação para ser calculado. No modo demo, são exibidos valores de exemplo.

**Os dados do "Verificador de CUIT" e do "Radar de mercado" são em tempo real?**
O verificador de CUIT AFIP/UIF/OCDE é uma funcionalidade de referência; para produção, recomenda-se conectar os webservices oficiais (AFIP WS_SR_PADRON_A5, listas da UIF e da OCDE). O Radar de mercado consulta em tempo real o serviço externo MEACI.

**O que acontece se eu perder o código de acompanhamento de uma denúncia?**
Não há como recuperá-lo — é a única credencial para consultar o caso de forma anônima, por design (para não comprometer o anonimato do denunciante).

**Posso exportar o Plano de Ação para Excel?**
Ele é exportado em CSV, que abre diretamente no Excel ou no Google Sheets.

**O modo demo modifica os dados reais?**
Não. O modo demo apenas altera quais dados são exibidos na tela (fictícios em vez dos carregados pela empresa); não grava nem apaga informações reais.

---

*Manual de Uso — Monitor de Compliance Empresarial · Ecosistema Transparencia · Ph.D. Vicente H. Monteverde*
