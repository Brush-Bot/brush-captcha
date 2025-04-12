import asyncio
import gc
import logging
import os
import resource
import sys
import time
from typing import Optional

from camoufox.async_api import AsyncCamoufox
# from patchright.async_api import async_playwright

from dataclasses import dataclass
@dataclass
class TurnstileResult:
    turnstile_value: Optional[str]
    elapsed_time_seconds: float
    status: str
    reason: Optional[str] = None


COLORS = {
    'MAGENTA': '\033[35m',
    'BLUE': '\033[34m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'RED': '\033[31m',
    'RESET': '\033[0m',
}


class CustomLogger(logging.Logger):
    @staticmethod
    def format_message(level, color, message):
        timestamp = time.strftime('%H:%M:%S')
        return f"[{timestamp}] [{COLORS.get(color)}{level}{COLORS.get('RESET')}] -> {message}"

    def debug(self, message, *args, **kwargs):
        super().debug(self.format_message('DEBUG', 'MAGENTA', message), *args, **kwargs)

    def info(self, message, *args, **kwargs):
        super().info(self.format_message('INFO', 'BLUE', message), *args, **kwargs)

    def success(self, message, *args, **kwargs):
        super().info(self.format_message('SUCCESS', 'GREEN', message), *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        super().warning(self.format_message('WARNING', 'YELLOW', message), *args, **kwargs)

    def error(self, message, *args, **kwargs):
        super().error(self.format_message('ERROR', 'RED', message), *args, **kwargs)


logging.setLoggerClass(CustomLogger)
logger = logging.getLogger("TurnstileAPIServer")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class TurnstileSolver:
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Turnstile Solver</title>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async></script>
        <script>
            async function fetchIP() {
                try {
                    const response = await fetch('https://api64.ipify.org?format=json');
                    const data = await response.json();
                    document.getElementById('ip-display').innerText = `Your IP: ${data.ip}`;
                } catch (error) {
                    console.error('Error fetching IP:', error);
                    document.getElementById('ip-display').innerText = 'Failed to fetch IP';
                }
            }
            window.onload = fetchIP;
        </script>
    </head>
    <body>
        <!-- cf turnstile -->
        <p id="ip-display">Fetching your IP...</p>
    </body>
    </html>
    """

    def __init__(self, debug: bool = False, headless: Optional[bool] = False, useragent: Optional[str] = None, browser_type: str = "chromium"):
        self.debug = debug
        self.browser_type = browser_type
        self.headless = headless
        self.useragent = useragent
        self.browser_args = []
        if useragent:
            self.browser_args.append(f"--user-agent={useragent}")

    async def _setup_page(self, browser, url: str, sitekey: str, action: str = None, cdata: str = None):
        if self.browser_type == "chrome":
            page = browser.pages[0]
        else:
            page = await browser.new_page()

        url_with_slash = url + "/" if not url.endswith("/") else url

        if self.debug:
            logger.debug(f"Navigating to URL: {url_with_slash}")

        turnstile_div = f'<div class="cf-turnstile" style="background: white; width: 70px;" data-sitekey="{sitekey}"' + (f' data-action="{action}"' if action else '') + (f' data-cdata="{cdata}"' if cdata else '') + '></div>'
        page_data = self.HTML_TEMPLATE.replace("<!-- cf turnstile -->", turnstile_div)

        await page.route(url_with_slash, lambda route: route.fulfill(body=page_data, status=200))
        await page.goto(url_with_slash)

        return page, url_with_slash, handler

    async def _get_turnstile_response(self, page, max_attempts: int = 10) -> Optional[str]:
        for attempt in range(max_attempts):
            if self.debug:
                logger.debug(f"Attempt {attempt + 1}: No Turnstile response yet.")

            try:
                turnstile_check = await page.input_value("[name=cf-turnstile-response]")
                if turnstile_check == "":
                    await page.click("//div[@class='cf-turnstile']", timeout=3000)
                    await asyncio.sleep(3)
                else:
                    # element = page.query_selector("[name=cf-turnstile-response]")
                    # if element:
                    #     return element.get_attribute("value")
                    return turnstile_check
                    # break
            except Exception as e:
                logger.debug(f"Click error: {str(e)}")
                continue
        return None

    async def solve(self, url: str, sitekey: str, action: str = None, cdata: str = None):
        start_time = time.time()
        if self.browser_type == "camoufox":
            async with AsyncCamoufox(
                    headless=self.headless,
                    geoip=True,
                    proxy={
                        "server": "http://pr-sg.ip2world.com:6001",
                        "username": "capsolver-zone-resi-region-hk",
                        "password": "123456"
                    }
            ) as browser:
                try:
                    page,url_with_slash, handler = await self._setup_page(browser, url, sitekey, action, cdata)
                    token = await self._get_turnstile_response(page)
                    elapsed = round(time.time() - start_time, 2)

                    if not token:
                        logger.error("Failed to retrieve Turnstile value.")
                        return TurnstileResult(None, elapsed, "failure", "No token obtained")

                    logger.success(f"Solved Turnstile in {elapsed}s -> {token[:10]}...")
                    return TurnstileResult(token, elapsed, "success")

                finally:
                    await page.unroute(url_with_slash, handler)
                    await browser.close()
                    # ✅ 强制垃圾回收
                    gc.collect()

                    # ✅ 打印内存使用情况
                    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    rss_mb = rss_kb / 1024 if sys.platform != "darwin" else rss_kb / (1024 * 1024)  # macOS单位不同
                    logger.debug(f"🧠 内存占用: {rss_mb:.2f} MB")
                    logger.debug(f"对象数量追踪: {len(gc.get_objects())}")
                    # ✅ 打印句柄数（文件 + socket 等）
                    try:
                        open_fds = len(os.listdir(f'/proc/{os.getpid()}/fd'))
                        logger.debug(f"📎 打开文件描述符数: {open_fds}")
                    except Exception:
                        pass  # 非 Linux 忽略

async def get_turnstile_token(url: str, sitekey: str, action: str = None, cdata: str = None, debug: bool = False, headless: bool = False, useragent: str = None, browser_type: str = "chromium"):
    """Legacy wrapper function for backward compatibility."""
    browser_types = [
        'chromium',
        'chrome',
        'camoufox',
    ]
    if browser_type not in browser_types:
        logger.error(f"Unknown browser type: {COLORS.get('RED')}{browser_type}{COLORS.get('RESET')} Available browser types: {browser_types}")
    elif headless is True and useragent is None and "camoufox" not in browser_type:
        logger.error(f"You must specify a {COLORS.get('YELLOW')}User-Agent{COLORS.get('RESET')} for Turnstile Solver or use {COLORS.get('GREEN')}camoufox{COLORS.get('RESET')} without useragent")
    else:
        solver = TurnstileSolver(debug=debug, useragent=useragent, headless=headless, browser_type=browser_type)
        result = await solver.solve(url=url, sitekey=sitekey, action=action, cdata=cdata)
        return result.__dict__

async def run(task_data):
    # print(task_data)
    url = task_data["websiteURL"]
    sitekey = task_data["websiteKey"]
    action = task_data.get("metadata", {}).get("action")
    # print(f"url: {url}, sitekey: {sitekey}, action: {action}")
    res = await get_turnstile_token(
        url=url,
        sitekey=sitekey,
        action=None,
        cdata=None,
        debug=False,
        headless=True,
        useragent=None,
        browser_type="camoufox"
    )
    return {
        "token": res["turnstile_value"],
        "elapsed": res["elapsed_time_seconds"],
        "status": "success" if res["turnstile_value"] else "failure",
        "type": "turnstile"
    }
# if __name__ == "__main__":
#     result = await get_turnstile_token(
#         url="https://testnet.megaeth.com/",
#         sitekey="0x4AAAAAABA4JXCaw9E2Py-9",
#         action=None,
#         cdata=None,
#         debug=True,
#         headless=False,
#         useragent=None,
#         browser_type="camoufox"
#     )
#     print(result)