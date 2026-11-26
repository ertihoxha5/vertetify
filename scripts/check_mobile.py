"""Exercise the local wallet and same-tab verifier using an existing issued fixture."""

from io import BytesIO
import os
from pathlib import Path
import subprocess

from PIL import Image
from playwright.sync_api import sync_playwright
import zxingcpp


def main():
    origin = "http://127.0.0.1:8184"
    password = subprocess.check_output(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "web",
            "python",
            "flows.py",
            "fixture-holder",
        ],
        text=True,
    ).strip()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="msedge", headless=True, args=["--no-proxy-server"]
        )
        holder = browser.new_page(viewport={"width": 390, "height": 844})
        evidence = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "evidence"
            / os.getenv("VERTETIFY_EVIDENCE_FOLDER", "frontend-redesign")
        )
        evidence.mkdir(exist_ok=True)
        for width in (360, 390, 768, 1440):
            holder.set_viewport_size({"width": width, "height": 900})
            holder.emulate_media(reduced_motion="reduce")
            holder.goto(origin, wait_until="domcontentloaded", timeout=60000)
            holder.get_by_role("link", name="Vertetify home").wait_for()
            holder.wait_for_function(
                "document.querySelector('.wordmark img')?.naturalWidth > 0"
            )
            assert holder.locator(".wordmark img").evaluate(
                "e => e.complete && e.naturalWidth > 0"
            )
            assert holder.locator(".hero h1 span").evaluate(
                "e => getComputedStyle(e).animationName === 'none'"
            )
            assert holder.evaluate("document.documentElement.scrollWidth <= innerWidth")
            if width == 1440:
                holder.screenshot(path=evidence / "home-desktop.png", full_page=True)
        for width in (390, 1440):
            holder.set_viewport_size({"width": width, "height": 900})
            holder.goto(origin)
            if width == 390:
                holder.locator(".wordmark img").evaluate("img => img.decode()")
                holder.screenshot(path=evidence / "home-mobile.png", animations="disabled")
                holder.get_by_role("button", name="Menu", exact=True).click()
            nav = holder.get_by_role("navigation", name="Main navigation")
            nav.get_by_role("link", name="Platform", exact=True).click()
            for label in ("University dashboard", "Diploma issuance", "Graduate wallet", "Public result"):
                holder.get_by_role("button", name=label).click()
                holder.wait_for_function("document.querySelector('.showcase img')?.naturalWidth === 960")
            for route in ("universities", "graduates", "privacy"):
                holder.goto(origin + "/?page=" + route)
                assert holder.locator("h1").is_visible()
                assert holder.evaluate("document.documentElement.scrollWidth <= innerWidth")
            holder.goto(origin + "/?how")
            for label in ("University", "Registry", "Graduate", "Verifier"):
                button = holder.get_by_role("button", name=label, exact=True)
                button.focus()
                holder.keyboard.press("Enter")
                assert button.get_attribute("aria-pressed") == "true"
        holder.goto(origin)
        holder.set_viewport_size({"width": 390, "height": 844})
        holder.get_by_role("link", name="Staff and graduate sign-in").click()
        holder.get_by_label("Fixture account").focus()
        assert holder.locator("select").evaluate("e => e === document.activeElement")
        holder.get_by_label("Fixture account").select_option("fixture-holder")
        holder.keyboard.press("Tab")
        field = holder.get_by_label("Local password")
        assert field.evaluate("e => e === document.activeElement")
        field.fill(password)
        holder.keyboard.press("Enter")
        award = holder.get_by_role("button", name="Share award", exact=False).first
        if key := os.getenv("VERTETIFY_CHECK_CREDENTIAL"):
            award = (
                holder.locator("article")
                .filter(has=holder.locator(f'[data-credential="{key}"]'))
                .get_by_role("button", name="Share award", exact=False)
            )
        if key:
            article = holder.locator("article").filter(
                has=holder.locator(f'[data-credential="{key}"]')
            )
            article.get_by_role("link", name="Open credential details").click()
            holder.get_by_role("link", name="Back to wallet").wait_for()
            assert holder.locator("[data-credential]").count() == 1
        award.click()
        link = holder.get_by_role("link", name="Open verification link").get_attribute(
            "href"
        )
        verifier = browser.new_page(viewport={"width": 320, "height": 640})
        try:
            qr_image = Image.open(
                BytesIO(holder.locator(".share-panel svg").screenshot())
            )
            decoded = zxingcpp.read_barcode(qr_image)
            if decoded is None or decoded.text != link:
                raise RuntimeError(
                    "The rendered QR did not decode to the current share URL."
                )
            verifier.goto(origin + "/verify")
            verifier.get_by_label("Verification link").fill(
                "https://example.invalid/verify#t=test"
            )
            verifier.get_by_role("button", name="Verify", exact=True).click()
            verifier.get_by_text(
                "Enter a verification link from this Vertetify site."
            ).wait_for()
            assert verifier.locator("dl").count() == 0
            verifier.get_by_label("Verification link").fill(link)
            verifier.get_by_role("button", name="Verify", exact=True).click()
            verifier.get_by_role(
                "heading", name="Registry and local blockchain evidence match"
            ).wait_for()
            assert verifier.evaluate(
                "document.documentElement.scrollWidth <= window.innerWidth"
            )
            verifier.screenshot(path=evidence / "verifier-mobile.png", full_page=True)
            assert "#t=" not in verifier.url
            assert "Drita Demo" not in verifier.locator("body").inner_text()
        finally:
            holder.get_by_role("button", name="Disable this link").click()
            holder.get_by_text("Share disabled.").wait_for()
        verifier.goto(link)
        verifier.get_by_role(
            "heading", name="Link expired, disabled or unavailable"
        ).wait_for()
        assert verifier.locator("dl").count() == 0
        for account in ("fixture-registrar", "fixture-auditor"):
            page = browser.new_page(viewport={"width": 768, "height": 900})
            page.goto(origin + "/?workspace")
            page.get_by_label("Fixture account").select_option(account)
            secret = subprocess.check_output(
                [
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "web",
                    "python",
                    "flows.py",
                    account,
                ],
                text=True,
            ).strip()
            page.get_by_label("Local password").fill(secret)
            page.get_by_role("button", name="Sign in").click()
            if account == "fixture-registrar":
                page.get_by_role("heading", name="Registry evidence").wait_for()
                page.get_by_label("Search credentials").fill("no-matching-synthetic-record")
                page.get_by_text("No credentials match this view.").wait_for()
                page.get_by_label("Search credentials").fill(key or "")
                if key:
                    page.get_by_label("Issuance state").select_option("issued")
                row = page.locator(".record-link")
                (row.filter(has_text=key) if key else row.first).click()
                page.get_by_role("dialog").wait_for()
                if key:
                    assert page.get_by_role("button", name="Copy checksum").is_visible()
                page.screenshot(path=evidence / "registrar-receipt.png", animations="disabled")
                page.keyboard.press("Escape")
                assert page.get_by_role("dialog").count() == 0
            else:
                page.get_by_text("No diplomas available for this account.").wait_for()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.get_by_role("button", name="Sign out").click()
            page.get_by_label("Fixture account").wait_for()
        browser.close()
    print(
        "Keyboard login, owner detail, QR decode, public verification and same-tab recheck passed."
    )


if __name__ == "__main__":
    main()
