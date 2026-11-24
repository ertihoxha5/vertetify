# Personal walkthrough

Use Python 3.12, Docker Desktop with the Linux engine and PowerShell. Run commands from the project root. The first build needs internet access. For a simulator-only run:

```powershell
python scripts/setup.py
docker compose up -d --build --wait
docker compose ps -a
Invoke-RestMethod http://127.0.0.1:8184/api/health/ready
```

Expected services are a healthy database and web app, a running dispatcher and a successfully exited setup worker. Readiness reports the application database state. For an actual Registry run, follow [the external environment instructions](integrations/compellio.md) instead. Both journeys use the same interface.

1. Open [the local workspace](http://127.0.0.1:8184) and check its source label. Run the following locally to display the registrar password. Keep the output out of screen captures and evidence.

   ```powershell
   docker compose exec -T web python flows.py fixture-registrar
   ```

2. Choose **fixture-registrar**, enter that password and sign in. Review the synthetic graduate, programme, award and date. Choose **Create draft for fixture holder**. Check the new draft, then select **Confirm issuance**. The page refreshes pending records. An issued record shows its reference. Simulator references start with `sim-`. Actual test-chain references begin with `urn:tar:eip155.31337:`.
3. Sign out. Retrieve the holder's password and sign in as **fixture-holder**.

   ```powershell
   docker compose exec -T web python flows.py fixture-holder
   ```

4. In the graduate wallet, select **Share award, programme, date and institution**. A QR and text link appear. Open the link in a private window. Expect a source, check time and those four fields on success. The graduate's name stays private. The link lasts seven days. Loopback URLs work on the same computer. Use browser device emulation for a phone-sized view. A physical phone needs a separately secured reachable deployment.
5. Return to the holder window, choose **Disable this link** and reopen the original link. Expect the unavailable-link message and zero diploma details. Reloading the verifier after its fragment was cleared also requires reopening the original link.
6. The second institution's **fixture-auditor** account can sign in using the same password command with its account name. It sees no Juniper diplomas or issue/share actions.
7. For an automated replay (creates a new synthetic diploma, then disables its share):

   ```powershell
   docker compose exec -T web python journey.py
   ```

If sign-in fails, use the password from the web container for the current mode. A draft is immutable after creation. Create a new draft for corrections. A **registered** record is waiting for independent readback. A **review** record needs operator inspection. Switching modes creates a separate view of credentials. An empty holder wallet can mean the diploma has not reached **issued**.

To stop Vertetify while preserving data, run `docker compose down` (include the registry override if used). Stop the separate provider with `docker compose -p vertetify-registry -f "$env:LOCALAPPDATA/VertetifyRegistry/docker-compose.yml" stop`.

For the narrow-screen regression, start the actual provider and Vertetify on the default port and issue at least one synthetic diploma. In a Python virtual environment with Microsoft Edge installed, run `python -m pip install playwright==1.65.2` followed by `python scripts/check_mobile.py`. The test signs in with the keyboard, opens a new share at 320 pixels wide, disables it and reopens it in the same verifier tab.
