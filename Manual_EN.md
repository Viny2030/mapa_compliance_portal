# User Manual — Corporate Compliance Monitor

**Integrity Program · Argentine Law 27.401 · International Standards**
Ecosistema Transparencia · Ph.D. Vicente H. Monteverde

---

## 1. Introduction

The **Corporate Compliance Monitor** is a web platform to manage, measure, and report a company's Integrity Program against Argentina's Law 27.401 and more than 20 international frameworks (anti-corruption, privacy, information security, environmental, governance, and digital).

The platform centralizes in a single dashboard:

- The **compliance score**, broken down by axis and by regulatory framework.
- An internal **whistleblowing channel**, with case tracking.
- **Risk management**, controls, incidents, and conflicts of interest.
- The **action plan** and regulatory alerts.
- **PDF report generation** for the board, auditors, and the Anti-Corruption Office.

Each client accesses an instance with its own URL (for example `mapacompliance-production.up.railway.app`) and only sees the modules enabled in their plan (Starter, Professional, or Enterprise).

### 1.1 General navigation

The whole system is organized into **tabs** in the top bar. There are two kinds:

- **In-page tabs**: switch content without reloading the page (Dashboard, Law 27.401, ISO 27001, etc.). These are the majority.
- **Tabs that open a separate page**: Benchmark, Conflicts, Predictor, Incidents, Controls, Signatures, and Documents. Each has its own "← Dashboard" button to go back.

The top-right corner has a language switcher: **🇦🇷 ES / 🇺🇸 EN / 🇧🇷 PT**. It translates the interface text (not the country-specific regulatory content, which stays in its original language where applicable).

### 1.2 Demo mode

If the URL includes `?demo=true`, the platform shows sample fictitious data so a prospective client can explore every tab without loading real information. A banner at the top reads "🧪 DEMO MODE — Sample data" with a link to exit demo mode (`?demo=false`).

### 1.3 PIN-protected access

Some admin panels (Whistleblowing Channel — management panel, Client Portal, Document Panel) are protected with an **access PIN**. Entering the correct PIN creates a temporary session (8 hours by default) identified by a token stored in the browser. After several consecutive failed attempts, the system temporarily blocks further attempts from that same connection, as a brute-force protection measure.

---

## 2. Dashboard

The home screen, giving an overall snapshot of the Integrity Program:

- **Compliance Score**: a number from 0 to 100 calculated from six weighted axes (program, training, due diligence, risk management, communication/whistleblowing channel, investigations). Includes a progress bar and the maturity level reached (Initial / Intermediate / Advanced).
- **Program and Training cards**: quick summary of progress on each.
- **Risk by area**: compact view of the risk map.
- **Active alerts**: regulatory and deadline notifications, generated automatically by the system (scraping official sources such as the Anti-Corruption Office, the Financial Information Unit — UIF, and the OECD, plus internal deadline alerts).
- **Coverage by Framework**: summarized implementation score for each active regulatory framework, calculated over the Cross-Framework Mapping controls.
- **Upcoming deadlines**: unifies training, improvement-plan, and regulatory deadlines in one view.

The Dashboard also gives access to the **Tax ID (CUIT) Verifier** (the same component as in the Due Diligence tab) and to the **RITE Registry**.

---

## 3. Board View — Executive View

Designed to present to the Board of Directors or an external auditor. Includes a **🖨️ Print** button to generate a board-meeting-ready version.

Contains:

- **Main KPIs** of the program at a glance.
- **Traffic-light status by axis**: status (green/yellow/red) for each of the six score axes.
- **Score evolution**: line chart with the month-by-month history.
- **Critical risks**: list of the highest-severity unmitigated risks.
- **Alerts for the board**: relevant alerts filtered by strategic importance.
- **Top priority next actions**: excerpt from the Action Plan.
- **Multi-Framework Coverage**: summary of the compliance level across all active international frameworks.
- **Sign-off block**: space for the Compliance Officer and/or the Board to record having reviewed the report.

---

## 4. Regulatory frameworks and standards

Each of these frameworks has its own tab with: a regulatory introduction, a specific score calculated over its elements, a compliance checklist, references to key articles/sections and, in several cases, comparisons with related frameworks.

### 4.1 Law 27.401 (Argentina)
The platform's central tab. Measures the **maturity level of the Integrity Program** (Initial / Medium / Advanced) under Art. 23. It distinguishes:
- **Mandatory elements** (Art. 23) — required to contract with the National State (Art. 24).
- **Optional elements** — raise the maturity level and mitigate criminal liability (Art. 9).
- A "What's missing for the next level?" summary with concrete suggested actions.

### 4.2 Lei 12.846/2013 — Brazil (Anti-Corruption Law)
Based on Brazil's **strict/objective liability** regime. Covers mandatory integrity-program elements under Decree 11.129/2022 and CGU Ordinance 909/2015, mitigating factors (Art. 7), and the Leniency Agreement mechanism (Art. 16, up to a 2/3 fine reduction).

### 4.3 FCPA & UK Bribery Act
Covers two anti-corruption regimes with extraterritorial reach:
- **FCPA** (US, 1977): applies to companies with a US nexus (listed on a US exchange, USD payments, US subsidiaries or employees). Books & Records and Internal Controls (§ 78m(b)).
- **UK Bribery Act 2010**: the strictest law of its kind worldwide — corporate *strict liability* (Section 7) for companies with a presence or doing business in the UK.
Includes a side-by-side comparison table.

### 4.4 LGPD — General Data Protection Law (Brazil, Law 13.709/2018)
Adequacy checklist by key chapters: legal bases for processing (Art. 7), adequacy score and level, completed/pending items, and ANPD sanctions detail (up to 2% of Brazil revenue, capped at R$50 million per infraction, plus a daily fine).

### 4.5 OECD — Guidelines for Multinational Enterprises (2023 Edition)
Responsible business conduct recommendations from the 50 adhering countries (Argentina since 1997). Breaks down the **11 chapters** (General Policies, Disclosure, Human Rights, Employment, Environment, Anti-Corruption, Consumer Interests, Science and Technology, Competition, Taxation, and the new 2023 Chapter XI on supply chains). Includes information on Argentina's National Contact Point (NCP) and the benefits of adopting the framework (access to ESG funds, multilateral-organization tenders, reduced reputational risk).

### 4.6 ISO 37001 — Anti-Bribery Management System
Certifiable international standard, complementary to Law 27.401, FCPA, the UK Bribery Act, and Lei 12.846. Includes key clauses and a direct comparison with Law 27.401.

### 4.7 ISO 14001 — Environmental Management System
Covers clauses 4 to 10 (Context, Planning, Operation, Continuous Improvement) and its integration with the Environmental-axis KPIs of the ESG module (GHG emissions, effluents, circular economy, biodiversity).

### 4.8 ISO 45001 — Occupational Health & Safety Management
Relevant for high-labor-risk sectors (construction, industry, energy, mining). Covers clauses 4 to 10.

### 4.9 GDPR — General Data Protection Regulation (EU)
Checklist of the 7 principles and data-subject rights. Includes tiered sanctions (up to €10M/2% of global turnover, or up to €20M/4% — whichever is higher) and a GDPR vs. LGPD comparison.

### 4.10 ESG — Environmental, Social & Governance
Three dimensions, each with its own score:
- **Environmental**: GHG emissions log by scope (1, 2, and 3 — GRI 305), reduction plan, and reporting type (internal/public, GRI/TCFD).
- **Social**: % women on the board and in middle management, gender pay gap, DEI policy, pay-equity audit.
- **Governance**: checklist for whistleblowing channel, code of ethics, board independence, internal audit, anti-corruption policy, annual ESG report, and complaint-resolution ratio.
Cross-references GRI 2021, TCFD, SASB, UN SDGs, and CNV Resolution 896/2021.

### 4.11 ISO 27001 — Information Security
Overall score across the 4 Annex A domains (ISO 27001:2022): Organizational (37 controls), People (8), Physical (14), and Technological (34), with OK / in-progress / pending control counters.

### 4.12 SOC 2 — Service Organization Control 2
AICPA framework for cloud/SaaS providers, assessed against the 5 Trust Service Criteria (Security is mandatory; Availability, Processing Integrity, Confidentiality, and Privacy are optional). Distinguishes Type I (design) vs. Type II (operating effectiveness, ≥6 months) reports. SOC 2 vs. ISO 27001 comparison.

### 4.13 CCPA / CPRA — California Consumer Privacy Act
Checklist of rights and obligations. Penalties: US$7,500 per intentional violation, US$2,500 per unintentional violation, and private actions of US$100–750 per consumer for data breaches. CCPA vs. GDPR vs. LGPD comparison.

### 4.14 NIS2 — EU Cybersecurity Directive
Risk management (Art. 21), governance and board accountability (Art. 20), supply chain (Art. 21.2.d), and incident-notification timelines (24h early warning, 72h initial assessment, 1 month final report). Tiered sanctions for essential entities (up to €10M/2%) and important entities (up to €7M/1.4%), with personal liability for executives.

### 4.15 EU AI Act — EU Artificial Intelligence Regulation
Organized by **risk levels**: prohibited (in effect since Feb. 2025), high risk (deadline Aug. 2026), mandatory transparency (Aug. 2025), and minimal risk. Includes an implementation timeline and penalties (up to €35M/7% for prohibited AI).

### 4.16 ISO 27701 — Privacy Information Management
An ISO 27001 extension for privacy, aligned with GDPR/LGPD/CCPA. Requires ISO 27001 as a baseline. Covers personal data controllers and processors.

### 4.17 PCI DSS v4.0 — Payment Card Data Security
12 requirements organized into 6 goals (secure networks, cardholder data protection, vulnerability management, access control, monitoring, security policy). Penalties of US$5,000 to US$100,000 per month for non-compliant entities.

### 4.18 COBIT 2019 — IT Governance
The 5 domains (EDM, APO, BAI, DSS, MEA) and their relationship to ISO 27001, SOX, DORA, and SOC 2. Relevant for the financial sector and listed companies.

### 4.19 SOX — Sarbanes-Oxley Act
For companies listed on the NYSE/NASDAQ. Sections 302 (executive certification), 404 (ICFR — internal control over financial reporting), 409 and 802 (disclosure and records retention), 906 (criminal liability, up to 20 years imprisonment). SOX–COBIT–ISO 27001 relationship map.

### 4.20 DORA — Digital Operational Resilience Act (EU)
In effect since 1/17/2025 for financial entities and their critical ICT providers. Five pillars: ICT Risk Management, Incident Management and Reporting, Digital Operational Resilience Testing, Third-Party Risk, and Information Sharing.

---

## 5. Cross-cutting tools

### 5.1 Risk
- **Probability × Impact heat map**: inherent risk matrix by area, with a "Load self-assessment" button to fill in the baseline questionnaire.
- **Risk radar** and **Distribution** (donut chart) by level.
- **Detail by area**.

### 5.2 Cross-Framework Mapping
Shows which controls simultaneously satisfy several regulatory frameworks at once, maximizing return on compliance investment. Includes a count of mapped controls, average coverage per control, maximum coverage reached, and a coverage matrix by framework. Organized by domain: Information Security, Privacy, Third Parties and Supply Chain, Governance and Culture, Incident Management, Artificial Intelligence.

### 5.3 Action Plan
Lists pending controls from the Cross-Framework Mapping, with a suggested owner and estimated deadline, filterable by priority (High / Medium / Low) and exportable to CSV via the corresponding button.

### 5.4 Training (progress)
Progress-tracking view for training: progress by module (bar chart), completion radar, and module list. (For the employee sign-off workflow, see "Signatures / Sign-off Training" below.)

### 5.5 Due Diligence
- **Tax ID (CUIT) verifier against OECD lists**: enter a CUIT and the system checks AFIP status (simulated/stub in this version), UIF politically-exposed-person lists, and OECD grey/black lists, returning a risk level (low/medium).
- **Verification summary** and query **history**.
- **Market radar**: a live listing, sourced from **MEACI** (Map of International Compliance Companies and Actors), of companies sanctioned in OECD cases with a presence in Argentina. This is context information for evaluating third parties — it does not imply a business relationship.

### 5.6 International
Summarizes the company's **international exposure** and the **applicable legal framework** based on where it operates. Also embeds, within this same tab, the full content of the OECD Guidelines (see 4.5).

### 5.7 RITE — Integrity Registry (Anti-Corruption Office)
Step-by-step guide to registering on the Anti-Corruption Office's official platform (rite.gob.ar): why register (it credits the program for Art. 24 public tenders, reduces criminal liability under Art. 9), the RITE's three modules (Integrity Program, Due Diligence, Personal Data), and the 5 registration steps.

### 5.8 Improvements & Alerts
- **Active alerts** (same as the Dashboard, with more detail).
- **Score evolution**.
- **Gaps vs. Anti-Corruption Office standard**: comparison between the current level, the minimum required by the Anti-Corruption Office, and the advanced level.
- **Prioritized improvement plan**.
- **Quick links** to Incidents, Controls, Predictor, and Benchmark.

### 5.9 Calendar
Unified regulatory calendar: training, improvement-plan items, and regulatory deadlines, filterable by source type.

### 5.10 Legislation
Full regulatory catalog with a free-text search bar ("Search regulation, article, or topic…") that filters by name, description, category, or country.

### 5.11 Report
Generates the **Executive Compliance Report**, suitable for the Anti-Corruption Office, the board, or external auditors. Includes a cover page, the overall score, and nine sections: organization data, Law 27.401 program status, score by axis, pending elements, training, RITE registration, improvement plan, coverage by international framework, and prioritized action plan.

Two export buttons:
- **🖨️ Export PDF** — full executive report.
- **🌐 PDF Frameworks** — report focused on international multi-framework coverage.

---

## 6. Whistleblowing Channel

Available both embedded in the Dashboard (the "🔒 Whistleblowing Channel" tab) and as a standalone page (`canal_denuncias.html`). Complies with Argentina's Law 27.401 and Spain's Law 2/2023.

**For anyone (no account required):**
- **File a Report**: category (corruption/bribery, harassment, fraud, conflict of interest, data breach, environmental non-compliance, other), description, suggested priority, related area, and an anonymity option (if not anonymous, contact details are requested). Submitting it generates a **unique tracking code** — this is the only way to check the case afterward, so it must be saved.
- **Check Status**: with the tracking code you can see the case status and send/read follow-up messages with the Compliance team, without revealing the reporter's identity.

**Management panel (PIN required — see Section 11):**
- Statistics: total reports, received, under investigation, closed, and alerts.
- Filterable list by status and priority, with full detail per case.
- Automatic system alerts for: overdue acknowledgment deadline, response deadline approaching (10 days or fewer), and critical cases (high priority, more than 30 days under investigation).
- Status updates (received → under investigation → closed), priority, and area, with the option to leave a message for the reporter.

Legal deadlines are calculated automatically when a report is created: 7 days for acknowledgment and 90 days for case closure.

---

## 7. Operational management tools

These pages open separately from the Dashboard (each has its own "← Dashboard" button to go back) and generally require filling in forms with the company's own data — they don't come preloaded with real information.

### 7.1 Sector Benchmark
Compares the company's position against other RITE-registered companies in the same sector (OA/RITE 2024-2025 data): percentile, radar comparison against the sector average, anonymized sector ranking, comparison by axis, and the company's score evolution vs. the sector average.

### 7.2 Conflict of Interest
Digital sworn declaration with an approval workflow (Art. 23(g) of Law 27.401):
- The **declarant** fills in their details (name, national tax ID, position, area), states whether or not they have a conflict of interest and, if so, the type (equity stake in a supplier/client, family ties to a public official, position at a competitor, benefits from third parties, interest in a contract/tender, other), the company/person involved, a description, and the proposed mitigation measure. It is submitted as a sworn declaration, with a warning of criminal liability for false statements (Art. 275, Criminal Code).
- The **Compliance Officer** ("Approver View") reviews and resolves pending declarations, filterable by Pending / Approved / Rejected.

### 7.3 AI Score Predictor
Predicts next quarter's compliance score using linear regression and factor analysis, with a model confidence level. Includes alternative scenarios, a graphical projection (real history + dotted prediction line + 80% confidence band), the highest-impact factors on the prediction, and recommended actions to maximize the score. The underlying score history is editable, to recalculate the prediction with your own data.

### 7.4 Incident Log
Log of violations, non-compliances, and near-misses (Art. 23 of Law 27.401). Registering an incident captures: title, type (bribery, conflict of interest, internal fraud, code-of-ethics breach, public procurement violation, money laundering, near-miss, whistleblower retaliation, misuse of information, other), severity (critical/high/medium/low), area involved, date of the event, who detected it, a detailed description, and the first corrective action. Incidents are filterable by status: Open, Under Investigation, Closed, and each can be advanced to the next status or deleted from its detail card.

### 7.5 Controls Management
Internal controls mapped to ISO 27001, COSO, Law 27.401, FCPA, or other internal frameworks. Each control has: reference framework, category (control environment, risk assessment, control activities, information and communication, monitoring, information security, anti-corruption controls), name, status (implemented / partial / pending / not applicable), % implementation, evidence, and owner. Overview of implementation by framework and a status-filterable list.

### 7.6 Signatures — Sign-off Training
Log of readings, sign-offs, and employee traceability (Art. 23 of Law 27.401), with two views:
- **👔 Administrator View**: creates training modules (name, mandatory or optional, deadline, audience, and content/description) and tracks who has signed off.
- **👤 Employee View (Sign-off)**: the employee enters their name and signs off confirming completion of each assigned module.

### 7.7 Document Management
Repository for Integrity Program documents with versioning, expiration reminders, and read traceability (Art. 23 of Law 27.401):
- Creating a document: name, code/ID, type (code, policy, procedure, manual, regulation, form, sworn declaration, other), version, effective date and expiration date, owner, reference URL, and description.
- Filter by status: Expired / Expiring soon / Current.
- Each document supports **new versions** (with a change note) and **read/acknowledgment logging** for each employee, certifying they read the current version — key traceability for an audit.

---

## 8. Client Document Panel

The `upload_clientes.html` page, protected by a **PIN** (see Section 11). Lets you upload and organize documentary evidence for the integrity program (not to be confused with the Document Management module in Section 7.7, which is for internal policies and procedures with version control):

- **Document upload**: drag-and-drop (or click) a file — PDF, XLSX, XLS, CSV, DOC, or DOCX, up to 20 MB. The document type is auto-detected from its content and file name (or can be forced manually via a dropdown) across 10 categories: code of ethics, gifts policy, conflict-of-interest sworn declarations, investigation procedure, compliance manual, RITE proof of registration, trained-staff roster, supplier list, risk map, and public-sector contracts.
- The system processes the file on upload: extracting text and detecting the document date (PDF), or extracting rows/columns and mentioned tax IDs (Excel/CSV).
- **Document checklist**: shows which integrity-program elements are already covered by at least one document, and which are missing.
- **List of uploaded documents**, with the option to delete them.

**Requires a PIN login** before you can upload or delete documents.

---

## 9. Client Admin Portal

The `portal.html` page, protected by a **PIN** (see Section 11). This is Ecosistema Transparencia's internal panel for administering all platform clients (used by the Ecosistema Transparencia team, not by the end client):

- **KPIs**: active clients, Enterprise clients, clients with pending module suggestions, and clients without completed onboarding.
- **Search and filters** by plan (Enterprise/Professional/Starter) or "with suggestions."
- **Per-client card**, expandable into three tabs:
  - **Info**: onboarding status, tax ID, plan, sector, size, country, owner, sign-up/expiration dates, and operational flags (Brazil, EU, US, publicly listed, cards, regulated financial sector, occupational health & safety).
  - **Modules**: percentage of active modules grouped by domain (Core, Anti-Corruption, Privacy, Security, Environmental, Governance, Digital, Cross).
  - **Suggester**: recommends additional modules based on the client's onboarding profile (sector, countries of operation, characteristics). Lets you activate a single suggested module or all of them at once.

---

## 10. Onboarding new clients

### 10.1 Internal Onboarding Wizard (`onboarding.html`)
Internal tool (Ecosistema Transparencia team) to configure a new client in 3 steps: (1) company profile and plan, (2) operational scope (countries of operation, characteristics such as being publicly listed or processing cards) — this determines which modules are mandatory — and (3) fine-tuning modules and auto-generating the configuration block (`modulos_activos` and `onboarding`) ready to paste into the client's `config.js` and into `data/clientes.json`.

### 10.2 Public Request Form (`formulario-cliente.html`)
A form aimed at a prospect/end client requesting access to their own platform: company data, operational scope, and a suggested plan (Starter / Professional / Enterprise), with a live calculation of the modules that would be enabled. On submission, the system:
- Saves a backup of the request.
- Sends an internal email to the Ecosistema Transparencia team with all the data.
- Sends a confirmation email to the requester, with a reference number and a promise of contact within 24–48 hours.

---

## 11. Security and access

- **Consultant PIN and Compliance Officer PIN**: two roles with access to the management panel. Configured as server environment variables, with a configurable validity period (30 days by default), after which they must be renewed.
- **Session**: entering the correct PIN creates a session token valid for a configurable time (8 hours by default). The same token grants access to the Whistleblowing Channel (panel), the Client Portal, and the Document Panel — you don't need to log in again in each one if you already logged in through any of them.
- **Lockout on failed attempts**: after several consecutive incorrect PINs from the same connection, the system temporarily blocks further attempts.
- **Protected write endpoints**: uploading or deleting documents, viewing the full client list, and viewing onboarding requests all require an active session — they are not publicly accessible.
- **Logout**: available from the session bar in each protected panel.

---

## 12. Frequently asked questions

**Why is the Compliance Score empty at first?**
Before real program data is loaded (through each tab's forms) there's nothing for the score to be calculated from. Demo mode shows sample values instead.

**Is the "Tax ID Verifier" and "Market Radar" data real-time?**
The AFIP/UIF/OECD tax ID verifier is a reference feature; for production use, it's recommended to connect the official web services (AFIP WS_SR_PADRON_A5, UIF and OECD lists). The Market Radar does query the external MEACI service live.

**What happens if I lose a report's tracking code?**
There is no way to recover it — it's the only credential to check the case anonymously, by design (so as not to compromise the reporter's anonymity).

**Can I export the Action Plan to Excel?**
It exports to CSV, which opens directly in Excel or Google Sheets.

**Does demo mode modify real data?**
No. Demo mode only changes what data is shown on screen (sample data instead of what the company has entered); it does not write or delete real information.

---

*User Manual — Corporate Compliance Monitor · Ecosistema Transparencia · Ph.D. Vicente H. Monteverde*
