import asyncio
import sys
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Navigating to http://localhost:8082")
        await page.goto("http://localhost:8082")
        await page.wait_for_timeout(3000)

        print("Clicking Log In...")
        try:
            await page.click("text=Log In", timeout=2000)
            await page.wait_for_timeout(2000)
        except:
            pass
            
        print("Typing credentials...")
        await page.click('input[type="email"]')
        await page.keyboard.type('test@example.com', delay=10)
        
        await page.click('input[type="password"]')
        await page.keyboard.type('Password123!', delay=10)
        
        print("Clicking Sign In...")
        await page.click("text=Sign In")
        
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path="after_signin.png")
        print("Screenshot saved to after_signin.png")

        await browser.close()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
