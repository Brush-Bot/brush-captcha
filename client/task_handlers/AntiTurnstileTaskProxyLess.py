import asyncio
import gc
import json
import logging
import os
import resource
import sys
import time
from typing import Optional

import yaml
from camoufox.async_api import AsyncCamoufox
# from patchright.async_api import async_playwright
from common.logger import get_logger,emoji
from dataclasses import dataclass
logger = get_logger("Anti")
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)
@dataclass
class TurnstileResult:
    turnstile_value: Optional[str]
    elapsed_time_seconds: float
    status: str
    reason: Optional[str] = None

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

        return page, url_with_slash

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
                    return turnstile_check
            except Exception as e:
                logger.debug(f"Click error: {str(e)}")
                continue
        return None

    async def solve(self, proxy:json,url: str, sitekey: str, action: str = None, cdata: str = None):
        start_time = time.time()
        logger.debug(f"Attempting to solve URL: {url}")
        proxy_config = config.get("proxy") or {}
        # proxy = {
        #     "server": proxy_config.get("server"),
        #     "username": proxy_config.get("username"),
        #     "password": proxy_config.get("password"),
        # }
        logger.debug(f"Proxy: {proxy},type:{type(proxy)}")
        async with AsyncCamoufox(
                headless=self.headless,
                geoip=True,
                proxy=proxy,
        ) as browser:
            try:
                page,url_with_slash = await self._setup_page(browser, url, sitekey, action, cdata)
                token = await self._get_turnstile_response(page)
                elapsed = round(time.time() - start_time, 2)

                if not token:
                    logger.error("Failed to retrieve Turnstile value.")
                    return TurnstileResult(None, elapsed, "failure", "No token obtained")

                logger.info(emoji("SUCCESS", f"Solved Turnstile in {elapsed}s -> {token[:10]}..."))
                return TurnstileResult(token, elapsed, "success")
            except Exception as e:
                logger.error(emoji("ERROR", f"Failed to solve Turnstile: {str(e)}"))
                return TurnstileResult(None, elapsed, "failure", str(e))
            finally:
                await browser.close()
                # 强制垃圾回收
                gc.collect()
                # 打印内存使用情况
                rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                rss_mb = rss_kb / 1024 if sys.platform != "darwin" else rss_kb / (1024 * 1024)  # macOS单位不同
                logger.debug(f"🧠 内存占用: {rss_mb:.2f} MB")
                logger.debug(f"对象数量追踪: {len(gc.get_objects())}")
                try:
                    open_fds = len(os.listdir(f'/proc/{os.getpid()}/fd'))
                    logger.debug(f"📎 打开文件描述符数: {open_fds}")
                except Exception:
                    pass

async def get_turnstile_token(proxy:json,url: str, sitekey: str, action: str = None, cdata: str = None, debug: bool = False, headless: bool = False, useragent: str = None):
    solver = TurnstileSolver(debug=debug, useragent=useragent, headless=headless)
    logger.debug(f"solver: {solver}")
    result = await solver.solve(proxy=proxy,url=url, sitekey=sitekey, action=action, cdata=cdata)
    return result.__dict__

async def run(task_data,proxy):
    logger.debug(f"task_data: {task_data}")
    url = task_data["websiteURL"]
    sitekey = task_data["websiteKey"]
    action = task_data.get("metadata", {}).get("action")
    logger.debug(f"action: {sitekey}")
    headless_str = config.get("camoufox").get("headless", "true")
    headless = headless_str.lower() == "true"
    logger.debug(f"headless: {headless}")
    res = await get_turnstile_token(
        proxy=proxy,
        url=url,
        sitekey=sitekey,
        action=None,
        cdata=None,
        debug=False,
        headless=headless,
        useragent=None,
    )
    return {
        "token": res["turnstile_value"],
        "elapsed": res["elapsed_time_seconds"],
        "status": "success" if res["turnstile_value"] else "failure",
        "type": "turnstile"
    }