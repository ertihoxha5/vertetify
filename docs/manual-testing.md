# Personal walkthrough

Use Python 3.12, Docker Desktop with the Linux engine and PowerShell. Run commands from the project root. The first build needs internet access. For a simulator-only run:

```powershell
python scripts/setup.py
docker compose up -d --build --wait
docker compose ps -a
Invoke-RestMethod http://127.0.0.1:8184/api/health/ready
```

Expected services are a healthy database and web app, a running dispatcher and a successfully exited setup worker. Readiness reports the application database state. For an actual Registry run, follow [the external environment instructions](integrations/compellio.md) instead. Both journeys use the same interface.

1. Open [the local workspace](http://127.0.0.1:8184) and check the environment in the footer. Select **Staff and graduate sign-in**. Run the following locally to display the registrar password. Keep the output out of screen captures and evidence.

   ```powershell
   docker compose exec -T web python flows.py fixture-registrar
   ```

2. Choose **Registrar · Juniper Valley**, enter that password and sign in. Select **Issue a diploma**. Review the synthetic graduate, programme, award and date. Choose **Create draft for fixture holder**. Select the draft row in **Institution credentials**, then select **Confirm issuance**. The page refreshes pending records. Select the issued row and read **Registry reference** in **Evidence details**. Escape closes the panel. Simulator references start with `sim-`. Actual test-chain references begin with `urn:tar:eip155.31337:`.
3. Sign out. Retrieve the holder's password and choose **Graduate · Juniper Valley** and sign in.

   ```powershell
   docker compose exec -T web python flows.py fixture-holder
   ```

4. In the graduate wallet, select **Share award, programme, date and institution**. A QR and text link appear. Open the link in a private window. Expect a source, check time and those four fields on success. The graduate's name stays private. The link lasts seven days. Loopback URLs work on the same computer. Use browser device emulation for a phone-sized view. A physical phone needs a separately secured reachable deployment.
5. Return to the holder window, choose **Disable this link** and reopen the original link. Expect the unavailable-link message and zero diploma details. Reloading the verifier after its fragment was cleared also requires reopening the original link.
   To test management after sign-out, create two shares for the same diploma and copy each link. Sign out, sign back in as the graduate, and open **Active verification links**. Disable one row using its link identifier and expiry. Reopen both original links. Only the disabled share should withhold the diploma.
6. The second institution's **Auditor · Alder Ridge** account can sign in using the same password command with its account name. It sees no Juniper diplomas or issue/share actions.
7. For an automated replay (creates a new synthetic diploma, then disables its share):

   ```powershell
   docker compose exec -T web python journey.py
   ```

If sign-in fails, use the password from the web container for the current mode. A draft is immutable after creation. Create a new draft for corrections. A **registered** record is waiting for independent readback. A **review** record needs operator inspection. Switching modes creates a separate view of credentials. An empty holder wallet can mean the diploma has not reached **issued**.

To stop Vertetify while preserving data, run `docker compose down` (include the registry override if used). Stop the separate provider with `docker compose -p vertetify-registry -f "$env:LOCALAPPDATA/VertetifyRegistry/docker-compose.yml" stop`.

For the narrow-screen regression, start the actual provider and Vertetify on the default port and issue at least one synthetic diploma. In a Python virtual environment with Microsoft Edge installed, run `python -m pip install playwright==1.65.2` followed by `python scripts/check_mobile.py`. The test uses Microsoft Edge, checks four homepage widths and reduced motion, signs in with the keyboard, pastes a fresh share at 320 pixels, disables it and reopens it in the same verifier tab. It also opens and dismisses a registrar receipt and checks the second institution's empty account. To bind browser evidence to the exact real-chain HTTP journey, run the following once the actual stack is ready:

```powershell
$proof = docker compose exec -T web python journey.py
if ($LASTEXITCODE -ne 0) { throw "Inspect the operation before another issuance." }
$env:VERTETIFY_CHECK_CREDENTIAL = ($proof | ConvertFrom-Json).credential_id
python scripts/check_mobile.py
```

Open the three PNGs in `docs/evidence` to review the resulting home, registrar receipt and public verifier. The script disables the link used for browser evidence.

## Physical phone acceptance (Erti, pending)

The shipped web server accepts loopback hostnames. A phone on the same Wi-Fi cannot use the desktop's loopback address directly. If a trusted SSH service is already available on the development PC, use a phone SSH client with local port forwarding on the trusted LAN. On a phone with OpenSSH, substitute the workstation account and its private LAN hostname:

```sh
ssh -N -L 127.0.0.1:8184:127.0.0.1:8184 workstation-user@workstation-lan-host
```

Keep this connection open and open **http://127.0.0.1:8184** in the phone browser. This forwards only the app. Leave Registry, RPC and database bindings alone. If no authorized tunnel exists, record the network constraint and skip physical acceptance. On an Android device with authorized USB debugging, an alternative is `adb reverse tcp:8184 tcp:8184` from the workstation.

1. Open the homepage, use **Verify a diploma** then return with **Vertetify home**. Check that navigation and text fit the real screen.
2. From the desktop wallet at the identical origin, share a synthetic diploma. Scan the screen QR with the phone or paste the link in the phone verifier. Expect four fields, a current check time and the real-chain result. Record whether scan and paste each worked.
3. Disable the link on the desktop, return home on the phone and reopen the original link. Expect the unavailable state and no award fields. To check natural expiry, retain a separate seven-day synthetic share privately and revisit after its displayed expiry. The isolated expiry test is available immediately.
4. Record date/time, phone model, OS, browser, tunnel method, readability, back navigation, QR/paste and actual expiry outcome here. Device, network and outcomes are pending. Do not attach QR screenshots or bearer URLs.

## Independent reviewer (pending)

Use a fresh checkout on a separate workstation with Git, Python 3.12 and Docker Desktop running Linux containers. Record reviewer, date, `git rev-parse HEAD`, OS and image digests. Start at the repository root, follow [Registry startup](integrations/compellio.md), then run:

```powershell
python scripts/smoke.py
docker compose exec -T web python journey.py
```

Check that all isolated tests pass and that the real journey prints `verified_local_chain` with three identical checksum values. Reproduce steps 1-6 above using registrar, graduate, anonymous verifier and the second institution. Compare the TAR with the version-specific Swagger read. Attach sanitized results, check screenshots at normal zoom, and record discrepancies. A different local chain will generate different IDs and checksums. Verify access to the repository from the reviewer's own account. No independent reviewer has signed off.
