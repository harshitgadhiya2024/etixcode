import time
import json
import random
import asyncio
from playwright.async_api import async_playwright


proxy_config = {
    "server": "http://geo.iproyal.com:12321",
    "username": "plural2356",
    "password": "dorbu7r62t9k"
}

start_time = time.time()  # Capture start time
all_responses = {}  # Dictionary to store all responses
url_template = "https://etix.com/ticket/?search=cat+cradle"
value_min = 52
loop_value = int(value_min / 12) + 1
value_min = 12*loop_value

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/605.1"
]



async def capture_network_requests(url):
    async with async_playwright() as p:
        random_user_agent = random.choice(user_agents)
        print(f"Using User-Agent: {random_user_agent}")
        browser = await p.chromium.launch(headless=True, proxy=proxy_config)
        context = await browser.new_context(user_agent=random_user_agent)
        page = await context.new_page()
        all_requests = []
        async def log_response(response):
            if "https://etix.com/ticket/api/online/search" == response.url:
                try:
                    json_response = await response.json()
                    # get_data = json.dumps(json_response, indent=2)
                    a = json_response.get("events")
                    all_requests.extend(a)
                    print(f"Captured response for {response.url}: {json.dumps(json_response, indent=2)}")
                except Exception as e:
                    print(f"Failed to decode JSON response for {response.url}: {e}")

        page.on("response", log_response)

        # Open the website
        await page.goto(url, wait_until="networkidle", timeout=9000000)
        print("load site")
        time.sleep(50)

        for var in range(1, loop_value):
            await page.get_by_role("button", name="Show More").click()
            time.sleep(15)

        # Wait for some time to let all requests complete (adjust as needed)
        await asyncio.sleep(10)

        seen = set()
        unique_data = []

        for event in all_requests:
            if event["eventId"] not in seen:
                unique_data.append(event)
                seen.add(event["eventId"])

        with open("requests_log2.json", "w") as f:
            json.dump(unique_data[:value_min], f, indent=4)

        await browser.close()

asyncio.run(capture_network_requests(url_template))
