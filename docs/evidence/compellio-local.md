# Actual local-chain verification · 24 November 2026

The application working tree was based on `2fb2debc5c9a6f210f2640be56c22637a9af3ef6`. The following results came from the official images running in the separate `vertetify-registry` Docker project.

| Observed field | Value |
| --- | --- |
| Registry image digest | `sha256:2ee35cf70ae2cfcec7a6b9350a32689fd66bcdacd194795902160be63cb78417` |
| Foundry image digest | `sha256:043752653d5be351c71709091b3db97c4421c907eb40ea294195e7f532aadf46` |
| Official Compose revision | `bd265515804cd969479959b7bb3e0f170e332454` |
| Network | Local Anvil, chain ID 31337 |
| Synthetic credential ID | `9cf9574d-71f7-4c8a-8467-60c53bc3e223` |
| Issuance TAR | `urn:tar:eip155.31337:0xe7f1725e7734ce288f8367e1bb143e90bb3f0512` |
| REST version / contract slot | 1 / 0 |
| Independent verification | `verified_local_chain` at 2026-11-24T20:54:32.655690Z |
| SHA-256 of the registry envelope | `43634637adf6b4e1a3d805997942ac83e9d82b5c4fcf767255e9b7bc5743a0cc` |

`docker compose exec -T web python journey.py` exercised a registrar, holder, second-institution auditor and anonymous verifier. Repeat issue requests resulted in one issued record. Latest and version-specific TAR IDs, data and checksums matched. The deployed contract returned the same checksum. Disabling the share then suppressed all diploma details.

The API returned a contract address with a leading `0x`. During the initial spike the version-1 REST read succeeded, while `getChecksum(1)` reverted with a missing-version error. `totalVersions()` returned one and `getChecksum(0)` returned the expected digest. Vertetify now checks the version count and checksum at the same block. After stopping and restarting **both** official services with their retained volumes, a fresh read of the existing issuance TAR returned the same envelope checksum. No new transaction was required.

These observations establish synthetic record integrity on this local chain. The [walkthrough](../manual-testing.md) and [Registry setup](../integrations/compellio.md) reproduce the flow. A fresh independent chain will generate its own evidence.

An isolated PostgreSQL dump and restore retained the original issued state and TAR reference. Ten sequential verification calls on this workstation took 0.695 s median and 1.109 s nearest-rank p95. An intentional local Registry outage produced an unavailable result with no academic fields; the same share verified again after service recovery.

The final rebuilt application repeated the full HTTP journey at 2026-11-24T21:07:46.733250Z. It returned `verified_local_chain` for `urn:tar:eip155.31337:0xcf7ed3acca5a467e9e704c703e8d87f634fb0fc9`, REST version 1, envelope SHA-256 `9ad304b6091ff75422b216d70d0db79fc6a186b1b301ee0b60928d3411b149e8`.
