"""Exercise the synthetic university onboarding UI on the local application."""

import subprocess
from uuid import uuid4
from playwright.sync_api import sync_playwright

ORIGIN = "http://127.0.0.1:8184"


def main():
    name = "Synthetic Campus " + uuid4().hex[:8]
    secret = subprocess.check_output(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "web",
            "python",
            "flows.py",
            "fixture-operator",
        ],
        text=True,
    ).strip()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="msedge", headless=True, args=["--no-proxy-server"]
        )
        visitor = browser.new_page(viewport={"width": 390, "height": 844})
        visitor.goto(ORIGIN + "/?access", wait_until="domcontentloaded")
        visitor.get_by_label("Institution name").fill(name)
        visitor.get_by_label("Institution contact").fill("admin@example.test")
        visitor.get_by_role("button", name="Submit access request").click()
        visitor.get_by_text("Request status: pending").wait_for()
        operator = browser.new_page()
        operator.goto(ORIGIN + "/?workspace", wait_until="domcontentloaded")
        operator.get_by_label("Fixture account").select_option("fixture-operator")
        operator.get_by_label("Local password").fill(secret)
        operator.get_by_role("button", name="Sign in").click()
        operator.get_by_role("heading", name="Platform operations").wait_for()
        operator.get_by_text("Chain 31337 reachable", exact=False).wait_for()
        operator.get_by_role("heading", name="Verification outcomes").wait_for()
        operator.locator("article").filter(has_text=name).get_by_role(
            "button", name="Approve and invite"
        ).click()
        invitation = operator.get_by_label("Invitation link").input_value()
        visitor.get_by_role("button", name="Refresh status").click()
        visitor.get_by_text("Request status: approved").wait_for()
        visitor.goto(invitation)
        visitor.get_by_role("button", name="Activate invitation").click()
        visitor.get_by_text("Account ID", exact=True).wait_for()
        member, secret = visitor.locator("dd").all_text_contents()
        visitor.get_by_role("link", name="Sign in with your account").click()
        visitor.get_by_label("Account ID").fill(member)
        visitor.get_by_label("Local password").fill(secret)
        visitor.get_by_role("button", name="Sign in").click()
        visitor.get_by_role("heading", name="University administration").wait_for()
        visitor.get_by_role("button", name="Create invitation").click()
        visitor.get_by_label("Invitation link").wait_for()
        assert visitor.evaluate("document.documentElement.scrollWidth <= innerWidth")
        browser.close()
    print(
        "Pending, approval, activation, admin sign-in, team invitation and platform health passed."
    )


if __name__ == "__main__":
    main()
