# Challenge 1 discovery · 23 November 2026

The implementation plan (pp. 4–5, 10–11, 28 and 58–60) is the working source. The repository started at `158ff97` with a project README and no application, test suite or AGENTS.md. The organizer materials below were linked by the plan. Direct verification of the brief and template remains pending.

| Working requirement from the plan | Evidence or decision |
| --- | --- |
| Three scored artifacts | PDF report using the official template (up to four pages), accessible code repository, and a demo video up to two minutes. |
| Registry gate | Demonstrate a real registration and verification through the Compellio Registry API. Local receipts support engineering tests only. |
| Rubric | Scope and functionality 70%, adoption plan 30%. |
| Deadline | 13 December 2026, 23:59 CET, subject to organizer confirmation. |
| Participation | Plan lists Kosovo residency, one challenge per team, one team per person, individuals or teams (ideally 2–5). Listed categories include BlockJump graduates/students, University of Prishtina students, startups, companies and public-sector teams. |
| Applicant and delivery channel | Project owner to confirm eligibility for the actual applicant category, including UBT if applicable, and obtain final artifact delivery instructions separately from the application form. Review 25 November CET. |

[Competition page](https://kutia.net/block-jump-kosovo/open-innovation-challenges/) · [Organizer brief v1.2](https://kutia.net/wp-content/uploads/2026/11/BlockJump_Challenge_1_-_Certifications_v1.2.pdf) · [Report template v1.2](https://kutia.net/wp-content/uploads/2026/11/BlockJump_PoC_Report_Template_v1.2.docx)

## Proposed architecture decisions

1. **Modular monolith.** Serve the built React app and its read-only API from FastAPI. A one-shot worker shares database code and migrations. PostgreSQL stays on the internal Compose network.
2. **Versioned diploma commitments.** For the issuance milestone, propose a private random nonce per credential and a versioned canonical representation before hashing. The local rehearsal uses a fixed synthetic test digest. The precise provider payload needs approval.
3. **Mode isolation.** This build accepts only the local environment and simulator mode. Simulator receipts have their own table and reference prefix. A future live build needs approved authentication, tenant authorization, isolated storage and secure origin.

## Milestone board

| Gate | State | Owner and next action |
| --- | --- | --- |
| M0 discovery | Local scope recorded. Organizer decisions open. | Project owner reviews access and competition questions on 25 November. |
| M1 foundation | Local application, migrations, synthetic fixture roles and repeatable rehearsal. | Engineering owner maintains [baseline evidence](evidence/index.md). |
| Live proof | Blocked on scope, access and documented write/read semantics. | Integration owner uses the [onboarding matrix](integrations/compellio.md) before implementing a provider adapter. |
