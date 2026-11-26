# Challenge 1 · Certifications

Reviewed the official competition page, brief v1.2, report template v1.2 and attached Getting Started Guide v1.1 on 24 November 2026. The owner's organizer confirmation establishes individual participation and eligibility for master's students who are registered Kosovo residents. One team per person and one challenge per team apply.

| Mandatory requirement | Acceptance evidence | Status |
| --- | --- | --- |
| Working PoC with issuer, Registry registration and third-party verification | Issuer, wallet and anonymous verifier journey against the actual local chain | Passed, including independent chain readback and restart. [Actual TAR evidence](evidence/compellio-local.md) |
| Code repository | Working link, reviewer setup, Compellio access for a private repository | GitHub reports the repository is public. Its report link returned HTTP 200 without credentials. Independent reviewer sign-off is pending. |
| PDF of at most four pages using official template | Reviewed PDF with repository, video and owner-approved contact | One page, two embedded links. Both resolved anonymously; the public PDF matched the local file byte for byte. Final content review is pending. [Report](submission/report.pdf) |
| Demo video up to two minutes | Timed recording of actual issuance, registration and verification | 42.5 seconds, H.264, recorded against the official local chain. [Demo](submission/demo.mp4) |
| Scope and functionality (70%) | Demonstrate working integration consistent with report | [Traceability](requirements.md) |
| Adoption plan (30%) | Buyer, first users, pilot and measured or explicitly proposed impact | [Pilot hypothesis](adoption.md) |
| Deadline | 13 December 2026, 23:59 CET | Owner to verify final delivery channel and retain acknowledgement. |

The template asks for scope/features, market potential, innovation/impact, contact and artifact links. Evaluation is scheduled for 14–16 December, online Selection Day on 17 December and awards on 18 December. The application form does not establish a final artifact receipt.

[Competition page](https://kutia.net/block-jump-kosovo/open-innovation-challenges/) · [Official brief](https://kutia.net/wp-content/uploads/2026/11/BlockJump_Challenge_1_-_Certifications_v1.2.pdf) · [Official report template](https://kutia.net/wp-content/uploads/2026/11/BlockJump_PoC_Report_Template_v1.2.docx)

## Organizer recheck on 25 November 2026

The official downloads page still links the same brief v1.2, report template v1.2 and guide v1.1. All three freshly downloaded files were byte-identical to the previously reviewed copies. No changed submission instructions were found in those documents. The exact final delivery channel and recipient access still need confirmation.

| Official source and section | Requirement | Implementation or artifact | Evidence and status |
| --- | --- | --- | --- |
| Brief p1, The challenge; guide p1 steps 3-5 | Registrar issues and registers, third party checks authenticity | Registry adapter, dispatcher, graduate wallet, public verifier | [Real local-chain regression](evidence/compellio-local.md) |
| Brief p1, What you submit; template, Before you submit | Reproducible repository and Compellio access if private | README, Compose, smoke suite | Remote clean-clone rehearsal passed. Anonymous repository access verified. Independent human review pending. |
| Brief p1, What you submit; template, How to use | Official template, PDF of at most 4 pages; working demo of at most 2 minutes | Existing one-page PDF and 42.5-second recording | Public PDF and MP4 matched the local artifacts. Final content alignment with the dashboard release is deferred to the end. |
| Brief p1, How it is judged; template sections 1-3 | Functionality 70%; adoption 30% | Real journey and pilot hypothesis | Technical evidence recorded; adoption remains a proposal. |
| Brief p1, Key dates; template, Before you submit | Deadline 13 December 2026 at 23:59 CET; working artifact links | M7 owner handoff | Submission and acknowledgment pending. The brief specifies the time; the template refers to the deadline. |
| Guide pp1-3 | Local Docker Registry, serial writes, independent version checksum | External DCAP.Web stack, registry.py | Page 2 BCBCTI is Challenge 3 only. No sandbox API credentials required. |

Remaining delivery work includes final artifact review, rechecking published links after any replacement, and timely submission. Physical-device and independent QA are project release gates. Additional animation and optional explorer integration are polish.
