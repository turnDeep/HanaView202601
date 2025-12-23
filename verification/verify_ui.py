from playwright.sync_api import sync_playwright, expect
import time

def verify_algo_tab():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emulate mobile
        context = browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        )
        page = context.new_page()

        # 1. Login
        page.goto("http://localhost:8000/")

        # Enter PIN 555777
        pin_inputs = page.locator("#pin-inputs input")
        pin_code = "555777"
        for i, digit in enumerate(pin_code):
            pin_inputs.nth(i).fill(digit)

        page.get_by_role("button", name="認証").click()

        # Wait for dashboard
        expect(page.locator(".container")).to_be_visible(timeout=10000)

        # 2. Go to Algo tab
        page.get_by_role("button", name="Algo").click()

        # Wait for Algo content
        algo_content = page.locator("#algo-content-area")
        expect(algo_content).not_to_be_empty(timeout=10000)

        # 3. Verify Elements
        # Check if 1-column list exists
        expect(page.locator(".algo-symbol-list-one-col")).to_be_visible()

        # Check if counts are removed (no summary-card elements in main area, or check text)
        # Note: Summary cards were removed from code.
        count_elements = page.locator(".summary-count")
        if count_elements.count() > 0:
            print("Warning: Summary counts found, might not be removed correctly.")
        else:
            print("Verified: Summary counts removed.")

        # Check card structure
        first_card = page.locator(".algo-symbol-item-card").first
        expect(first_card).to_be_visible()

        # Check Header (Ticker + Dot)
        header = first_card.locator(".algo-card-header")
        expect(header).to_be_visible()
        expect(header.locator(".algo-card-ticker")).to_be_visible()
        expect(header.locator(".status-dot")).to_be_visible()

        # Check AI Text footer
        footer = first_card.locator(".algo-card-footer")
        expect(footer).to_be_visible()
        expect(footer.locator(".algo-ai-text")).to_be_visible()

        # 4. Take Screenshot
        page.screenshot(path="verification/algo_tab_verified.png", full_page=True)
        print("Screenshot saved to verification/algo_tab_verified.png")

        browser.close()

if __name__ == "__main__":
    verify_algo_tab()
