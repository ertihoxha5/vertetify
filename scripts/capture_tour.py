"""Render public tour images from the production UI with synthetic records only."""
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "frontend/dist"
OUTPUT = ROOT / "frontend/public/previews"
ORIGIN = "http://127.0.0.1:8184"


def capture():
    OUTPUT.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", args=["--no-proxy-server"])
        for view in ("dashboard", "issue", "wallet", "result"):
            page = browser.new_page(viewport={"width": 1280, "height": 800}, reduced_motion="reduce")
            fields = dict(issuer_id="juniper", award_name="BSc", program_name="Computer Science",
                          subject_display_name="Drita Demo", award_date="2026-06-30")
            states = ["issued"] if view == "wallet" else ["issued", "draft", "queued", "issued"]
            items = [dict(id=f"example-diploma-{i+1}", state=state, snapshot=fields,
                          reference=None, version=None, last_matched=None) for i, state in enumerate(states)]

            def serve(route):
                path = urlsplit(route.request.url).path
                if path == "/api/v1/diplomas":
                    return route.fulfill(json=dict(role="holder" if view == "wallet" else "registrar",
                        institution="Juniper Valley University", items=items, holders=["fixture-holder"]))
                if path == "/api/workspace":
                    return route.fulfill(json={"mode": "simulator"})
                if path == "/api/v1/shares":
                    return route.fulfill(json=[])
                if path == "/api/v1/public/verify":
                    return route.fulfill(json=dict(status="matched_simulator", source="simulator",
                        checked_at="2026-11-26T10:00:00Z", diploma={k:v for k,v in fields.items() if k!="subject_display_name"}))
                file = DIST / ("index.html" if path in ("/", "/verify") else path.lstrip("/"))
                if urlsplit(route.request.url).netloc != "127.0.0.1:8184" or not file.is_file():
                    return route.abort()
                route.fulfill(path=file)

            page.route("**/*", serve)
            page.goto(ORIGIN + ("/verify#t=" + "x"*43 if view=="result" else "/?workspace"))
            if view == "issue":
                page.locator("#issue summary").click()
                page.locator("#issue").evaluate("el => el.scrollIntoView({block:'start'})")
            elif view == "result":
                page.get_by_text("Local simulator records match").wait_for()
            else:
                page.locator(".overview").wait_for()
            image = Image.open(BytesIO(page.screenshot())).convert("RGB")
            image.resize((960,600),Image.Resampling.LANCZOS).save(OUTPUT / (view+".webp"),quality=90)
            page.close()
        browser.close()


if __name__ == "__main__":
    capture()
