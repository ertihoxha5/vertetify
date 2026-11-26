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
## Release candidate bc47642 / 25 November 2026

All command paths below are relative to the repository root. Docker Desktop ran the original provider in its separate project with retained volumes. The application used the same database as the baseline.

| Check | Exact command or action | Observed result |
| --- | --- | --- |
| Candidate and mode | `git rev-parse --short HEAD`; `Invoke-RestMethod http://127.0.0.1:8184/api/workspace` | `bc47642`; `compellio-local`. Web and DB healthy, dispatcher running, setup worker exited 0. |
| External services | `docker inspect --format "{{.Config.Image}} {{.Image}}" vertetify-registry-registry-api-1 vertetify-registry-ethereum-1` | DCAP.Web latest, Foundry stable; full image IDs identical to the two digests in the 24 November table above. |
| Interface and chain | `(Invoke-RestMethod http://127.0.0.1:18660/swagger/v1/swagger.json).paths.PSObject.Properties.Name`; `docker compose exec -T web python -c "import registry; print(registry.endpoints(),registry.rpc('eth_chainId',[]))"` | TAR and version routes present; registry-api:8080 and ethereum:8545 internally. Host loopback 18660 and 18545; chain 0x7a69 (31337). |
| Issue | `docker compose exec -T web python journey.py` | Juniper registrar draft and queued issuance, repeat issue HTTP 202, one TAR. Adapter accepted Registry POST 201. Application credential/operation key `b98a6ed2-1a44-4452-9877-7be82692d710`. Queue uses the diploma as the operation. |
| Persistence | `docker compose exec -T db psql -U vertetify -c "select tenant,state,reference from diplomas where id='b98a6ed2-1a44-4452-9877-7be82692d710'"` | juniper, issued, `urn:tar:eip155.31337:0x8a791620dd6260079bf849dc5567adc3f2fdc318`. Audit sequence included drafted, queued, receipt_saved, evidence_matched. |
| Retrieval | Set `$api='http://127.0.0.1:18660/api/v1/TAR'` and `$id` to the full TAR above. Run `Invoke-RestMethod "$api/$id"` and `Invoke-RestMethod "${api}/version/${id}:1"`. | Both GETs HTTP 200, identical ID, data, checksum and version 1. Receipt `8c951e00-375a-47ee-8e9f-342447d3e976`; GET /receipt/{receiptID} also returned 200. These responses expose a receipt UUID and contract address; no transaction hash field. |
| Application commitment | `journey.py` recomputed the sealed diploma commitment from snapshot and private nonce. | `c7c8b6c23a956441d6cc30fb5d87f3ded209a646f98093125088d517ccabf67c` |
| Independent digest | `journey.py` applies SHA-256 to RFC 8785 bytes of the retrieved TAR **data** object with fields `type=VertetifyDiplomaCommitmentV1` and `commitment`. | `ee1e42c9fae9129806ef69f6836220c7ea071bb0462b4e95b6af0b847e16a085` |
| Registry checksum | Same version read, normalize to lowercase hex without 0x. | `ee1e42c9fae9129806ef69f6836220c7ea071bb0462b4e95b6af0b847e16a085` |
| On-chain checksum | `journey.py` uses the documented contract binding and local RPC. Check totalVersions and getChecksum(0) at the same sampled block. | `ee1e42c9fae9129806ef69f6836220c7ea071bb0462b4e95b6af0b847e16a085`. REST v1 maps to contract slot 0. |
| Third party | Holder creates share; anonymous client POSTs through the public verifier. Browser regression uses the same credential ID. | `verified_local_chain` at 2026-11-25T14:41:02.777054Z (HTTP journey). Four fields: issuer ID, award, programme and award date. [Rendered verifier](verifier-mobile.png). |
| Failure states | `python scripts/smoke.py`; `python scripts/check_mobile.py` | Disposable PostgreSQL plus controlled proof stubs cover pending, expired, evidence mismatch and unavailable, membership/tenant and holder rules. Disabled link withholds details. Simulator journey returns matched_simulator. |
| Interface | See [manual testing](../manual-testing.md) | [Homepage](home-desktop.png), [registrar receipt](registrar-receipt.png). Physical phone and independent reviewer pending. |

The comparison proves integrity of the sealed synthetic record on this local chain. Institutional authority comes from Vertetify's fixture membership. The two-field TAR uses the guide's arbitrary-JSON interface. It has no registered profile TAR or @context. No credential revocation or update was performed. Disabling a share ends access through that link.

During the baseline, the eight-second client deadline elapsed while the provider completed registration. A documented POST to /find with the synthetic commitment returned one matching record. The existing reconciliation command independently verified and attached it. Only a fresh diploma was used for each later acceptance journey. The candidate allows 35 seconds for the single write; uncertain outcomes still require review.
## Institution-access candidate · 69cb3be

On 25 November 2026 the existing PostgreSQL and Compellio volumes were retained. A fresh Juniper registrar-to-graduate-to-anonymous-verifier journey ran with `docker compose exec -T web python journey.py`.

| Observation | Value |
| --- | --- |
| Mode and chain | `compellio-local`, 31337 |
| Synthetic diploma | `3ba04dca-350b-4bbb-858d-980d23ca96d1`, issuer `juniper` |
| TAR | `urn:tar:eip155.31337:0xa51c1fc2f0d1a1b8494ed1fe312d7c3a78ed91c0` |
| Receipt | `dce152a5-d6ba-4ab4-9378-aec7c03637cf` |
| Version and contract slot | REST 1, contract 0 |
| Application commitment | `000a3b9a391a3fb2217a56ea3b51c000b879aa177cefcca8a60d9fadb7166235` |
| Canonical TAR payload SHA-256 | `f6c48ae87c0fde8cc219accb9ad0c26acf778ee4b8ed36e30f5bd488deee5f0e` |
| Registry checksum, v1 | `f6c48ae87c0fde8cc219accb9ad0c26acf778ee4b8ed36e30f5bd488deee5f0e` |
| Independent local contract read | `f6c48ae87c0fde8cc219accb9ad0c26acf778ee4b8ed36e30f5bd488deee5f0e` |
| Signed-out HTTP verification | `verified_local_chain`, 2026-11-25T16:42:24.936365Z. Only issuer ID, award, programme and award date were disclosed. |
## M5 remote checkout · d066123

| Check on an isolated fresh chain | Observed value |
| --- | --- |
| Mode, chain and successful verification | `compellio-local`, chain 31337, `verified_local_chain` at 2026-11-25T17:08:06.853822Z |
| Issued synthetic diploma / issuer | `9eeda7d0-0dd2-497c-ad04-8ee31daa46b7` / juniper |
| TAR, REST version and contract slot | `urn:tar:eip155.31337:0x5fbdb2315678afecb367f032d93f642f64180aa3`, version 1, slot 0 |
| Registry receipt | `37ae01b8-9166-4479-af02-778905249967` |
| Private diploma commitment embedded in TAR data | `c64506d5af06add6f6aa0151ac7b01137592917d4639dc82caf51b43f81f2af2` |
| RFC 8785 TAR data SHA-256, Registry checksum and on-chain checksum | All three individually returned `2eec2bc1b2f767a301fa74deb91e3126af46bb47d3060d430e272d5f413b43fe` |

The clean-clone application used the standard registrar/holder/anonymous HTTP journey. It checked the allowed public fields, disabled a link and confirmed that the sibling link still verified. The temporary provider, chain and application had their own volumes. Their TAR belongs to this rehearsal chain; a read against the regular demo chain does not reproduce this evidence.

## M5 candidate · 26 November 2026

Application and test revision `b3b2071`, on the existing local demo volumes. From the repository root, `docker compose exec -T web python journey.py` issued the record, read its version-specific TAR, compared the evidence and opened a holder-created share in an anonymous session.

| Observation | Actual result |
| --- | --- |
| Mode, chain, anonymous result | `compellio-local`, EIP-155 chain 31337, `verified_local_chain` at 2026-11-26T11:23:00.162646Z |
| Credential and institution | `6337ebcb-63a6-4a93-8200-d1b948b5cb36`, `juniper` |
| TAR, version | `urn:tar:eip155.31337:0x9a676e781a523b5d0c0e43731313a708cb607508`, version 1 |
| Registry receipt | `7b4f1b91-f778-42ef-8347-4aa5cdd9dd68` |
| Application commitment embedded in TAR | `4daf97bc5dc823d9d07ec1fd93a0c0eb6db04acf5641c020a8d7f0a8e0f6b109` |
| SHA-256 of RFC 8785 canonical TAR data | `36f8fbcc94337101e377a9f85271d5a74a6f36dfc050fb8ca7e7095157a33f2c` |
| Registry checksum, version 1 | `36f8fbcc94337101e377a9f85271d5a74a6f36dfc050fb8ca7e7095157a33f2c` |
| Local contract checksum, corresponding version | `36f8fbcc94337101e377a9f85271d5a74a6f36dfc050fb8ca7e7095157a33f2c` |
| Anonymous disclosure | Issuer ID, award, award date and programme. After disable the result was `link_unavailable` and contained no diploma. |

The comparison establishes integrity against this local chain. Academic accreditation and the accuracy of the original institutional assertion require separate evidence. The Edge wallet test decoded the displayed QR and verified this credential through the public page. See the [M5 tracker](../progress.md) for the bounded performance run, privacy regression and outstanding reviewer observation.
