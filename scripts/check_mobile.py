"""Exercise the local wallet and same-tab verifier using an existing issued fixture."""
import subprocess

from playwright.sync_api import sync_playwright


def main():
    origin = "http://127.0.0.1:8184"
    password = subprocess.check_output(
        ["docker", "compose", "exec", "-T", "web", "python", "flows.py", "fixture-holder"],
        text=True,
    ).strip()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        holder = browser.new_page(viewport={"width": 390, "height": 844})
        holder.goto(origin)
        holder.keyboard.press("Tab")
        assert holder.locator("select").evaluate("e => e === document.activeElement")
        holder.get_by_label("Fixture account").select_option("fixture-holder")
        holder.keyboard.press("Tab")
        field = holder.get_by_label("Local password")
        assert field.evaluate("e => e === document.activeElement")
        field.fill(password)
        holder.keyboard.press("Enter")
        holder.get_by_role("button", name="Share award", exact=False).first.click()
        link = holder.get_by_role("link", name="Open verification link").get_attribute("href")
        verifier = browser.new_page(viewport={"width": 320, "height": 640})
        try:
            verifier.goto(link)
            verifier.get_by_role("heading", name="Registry and local blockchain evidence match").wait_for()
            assert verifier.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            assert "#t=" not in verifier.url
            assert "Drita Demo" not in verifier.locator("body").inner_text()
        finally:
            holder.get_by_role("button", name="Disable this link").click()
            holder.get_by_text("Share disabled.").wait_for()
        verifier.goto(link)
        verifier.get_by_role("heading", name="Link expired, disabled or unavailable").wait_for()
        assert verifier.locator("dl").count() == 0
        browser.close()
    print("Keyboard login, mobile layout and same-tab recheck passed.")


if __name__ == "__main__":
    main()
