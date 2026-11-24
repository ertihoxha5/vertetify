# Compellio local Registry

Organizer confirmation on 24 November supersedes the earlier sandbox-access wait. Challenge 1 uses DCAP.Web and its local pre-funded chain. The Registry process holds the disposable signing key. Vertetify needs no external API credential. BCBCTI, STIX and TAXII belong to Challenge 3.

## Start the official environment on Windows

Use Docker Desktop in Linux container mode, PowerShell, Python 3.12 and an internet connection for the initial image pulls. From the Vertetify root run these commands in order.

```powershell
python scripts/setup.py
powershell -ExecutionPolicy Bypass -File scripts/start_registry.ps1
docker compose -p vertetify-registry -f "$env:LOCALAPPDATA/VertetifyRegistry/docker-compose.yml" ps
docker compose -f compose.yaml -f compose.registry.yaml up -d --build --wait
```

The first script preserves existing app settings. The PowerShell script fetches only the pinned upstream deployment definition into LocalAppData. The official Registry and Ethereum services run in their own project, with separate storage and loopback bindings. The optional explorer is omitted. The provider images use upstream tags. Record their resolved digests when freezing a release. The registry override connects the app and dispatcher to the provider network. Keep one Vertetify writer deployment per provider instance. Use plain `docker compose up -d --build --wait` to return to simulator mode. The evidence mode travels with the diploma, session and share.

Visit [Vertetify](http://127.0.0.1:8184) and [Registry Swagger](http://127.0.0.1:18660/swagger). The guide illustrates host port 8080. The pinned Compose publishes 6060 by default. This installation maps 18660 to Registry port 8080 and 18545 to chain port 8545. Provider calls from the container use service DNS on the external project network.

## Independently check a synthetic diploma

1. Follow [the three-role walkthrough](../manual-testing.md). The header must show **Compellio · local test blockchain**. Confirm issuance once and wait for **issued**. Save the displayed TAR reference.
2. In PowerShell inspect both the latest and first TAR representations. Paste the actual public TAR reference in place of the placeholder.

```powershell
$id = 'PASTE_THE_TAR_REFERENCE'
$api = 'http://127.0.0.1:18660/api/v1/TAR'
Invoke-RestMethod "$api/$id" | Select-Object id,version,checksum,data
Invoke-RestMethod "${api}/version/${id}:1" | Select-Object id,version,checksum,data
```

3. Inspect the envelope. Its two application fields are a versioned type and a salted diploma commitment. Names, programmes, dates and nonce stay in PostgreSQL.
4. Open the holder's share in a separate private browser window. The verifier recomputes the diploma commitment, reads both TAR representations, hashes the RFC 8785 envelope and invokes the deployed contract's `getChecksum(uint256)` at slot 0 for REST version 1 using read-only Ethereum JSON-RPC. It requires chain ID 31337 and equality of all three checksums. Compare the displayed time and source. This checks integrity against a local chain controlled by its operator. Institutional accreditation and legal recognition need separate evidence.
5. An automated run with fresh synthetic data is available below. It prints sanitized identifiers and a checksum only after completing the workflow.

```powershell
docker compose exec -T web python journey.py
```

## Operational boundaries

The dispatcher durably marks dispatch before its single POST and stores the returned TAR ID before attempting readback. A PostgreSQL advisory lock serializes dispatch across this application's workers. A lost response or interrupted write goes to **review**. Investigate in the Registry's own records before further action. Use `docker compose exec -T web python reconcile.py CREDENTIAL_UUID KNOWN_TAR_ID` to reconcile a known candidate. It performs read-only verification and refuses a mismatch. An operation without a known matching TAR stays in review. A saved ID allows bounded read-only retries with backoff. Eight failed reads or a mismatching record move the operation to review. Missing, altered or unavailable proof suppresses all public fields. An unavailable registry never triggers simulator fallback.

If Docker hangs on `docker ps`, check Docker Desktop's Linux engine before debugging routes. A deployment failure can indicate a disconnected chain or unfunded signing wallet. If Compose reports a missing external network, start the external registry project first. Anvil and the registry have separate volumes. Keep both for reproducible historical reads. A local chain reset breaks previous evidence. External testnets, mainnet and hosted authentication are outside this local build.

## Sources

- Guide v1.1 pp. 1 and 3 establish the Challenge 1 workflow. Page 2 describes the separate Challenge 3 workflow. [Organizer guide](https://kutia.net/wp-content/uploads/2026/11/BlockJump_Getting_Started_Guide_Registry_API_BCBCTI_v1.1.pdf)
- The pinned deployment and controller describe ports, mounts, registration and version reads. The deployed binding specifies `getChecksum(uint256) → bytes32`. The standalone token project's current interface differs. This adapter targets the Registry deployment binding. [Deployment](https://github.com/compellio/DCAP.Web/tree/bd265515804cd969479959b7bb3e0f170e332454) · [Contract binding](https://github.com/compellio/DCAP.Web/blob/bd265515804cd969479959b7bb3e0f170e332454/Contracts/ContractDefinition/DCAPv2Definition.cs)
- The separately requested `compellio/DCAP` URL returned HTTP 404 from GitHub's official API. DCAP.Web provides the usable deployment reference. The public asset explorer is optional. [BCBCTI architecture](https://github.com/compellio/bcbcti/blob/main/docs/architecture.md) · [Asset explorer](https://github.com/compellio/dcap-asset-explorer)
