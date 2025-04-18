import asyncio
import gc
import json
import os
import resource
import sys
import time

import yaml
from camoufox.async_api import AsyncCamoufox
from hcaptcha_challenger.agent import AgentV, AgentConfig
from hcaptcha_challenger.models import CaptchaResponse, ChallengeSignal
from hcaptcha_challenger.utils import SiteKey
from common.logger import get_logger,emoji

logger = get_logger("HCaptcha")

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)
# gemini_key = config.get("apikey").get("gemini_api_key")
# models = config.get("models")
headless_str = config.get("camoufox").get("headless", "true")
headless = headless_str.lower() == "true"
# if gemini_key:
#     os.environ["GEMINI_API_KEY"] = gemini_key
# else:
#     raise RuntimeError("config.yaml 缺少 gemini_api_key")

async def run(task_data, proxy):
    url = task_data["websiteURL"]
    sitekey = task_data["websiteKey"]
    print(task_data)
    gemini_key = task_data["clientKey"]
    action = task_data.get("metadata", {}).get("action", "")
    cdata = task_data.get("metadata", {}).get("cdata", "")

    logger.debug(f"🌐 Preparing hCaptcha page at {url}")
    start_time = time.time()
    async with AsyncCamoufox(
        headless=headless,
        proxy=proxy,
        geoip=True,
        args=["--lang=en-US", "--accept-language=en-US,en;q=0.9"]
    ) as browser:
        try:
            page = await browser.new_page()
            await page.goto(SiteKey.as_site_link(sitekey))

            # 初始化 Agent
            agent_config = AgentConfig(
                GEMINI_API_KEY=gemini_key,
                EXECUTION_TIMEOUT = 300,
                RESPONSE_TIMEOUT = 30,
                RETRY_ON_FAILURE = True,
                # CHALLENGE_CLASSIFIER_MODEL=models['CHALLENGE_CLASSIFIER_MODEL'],
                # IMAGE_CLASSIFIER_MODEL=models['IMAGE_CLASSIFIER_MODEL'],
                # SPATIAL_POINT_REASONER_MODEL=models['SPATIAL_POINT_REASONER_MODEL'],
                # SPATIAL_PATH_REASONER_MODEL=models['SPATIAL_PATH_REASONER_MODEL'],
            )
            agent = AgentV(page=page, agent_config=agent_config)

            await agent.robotic_arm.click_checkbox()

            # 执行挑战并等待结果
            await agent.wait_for_challenge()
            elapsed = round(time.time() - start_time, 2)
            if agent.cr_list:
                cr = agent.cr_list[-1]
                cr_data = cr.model_dump()
                logger.debug(cr_data)
                token = cr_data["generated_pass_UUID"] if cr_data.get("is_pass") else None
                logger.info(emoji("SUCCESS", f"Solved Hcaptcha in {elapsed}s -> {token[:10]}..."))
                return {
                    "token": token,
                    "elapsed": cr_data.get("expiration", 0),
                    "status": "success" if cr_data.get("is_pass") else "failure",
                    "type": "hcaptcha"
                }
            else:
                return {
                    "token": None,
                    "elapsed": 0,
                    "status": "failure",
                    "type": "hcaptcha"
                }

        except Exception as e:
            logger.error(emoji("ERROR", f"Failed to solve Hcaptcha: {str(e)}"))
            return {
                "token": None,
                "elapsed": 0,
                "status": "failure",
                "type": "hcaptcha"
            }
        finally:
            await page.close()
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
# if __name__ == "__main__":
#     task_data = {
#         "websiteURL": "https://faucet.n1stake.com/",
#         "websiteKey": "d0ba98cc-0528-41a0-98fe-dc66945e5416"
#     }
#     proxy = {
#         "server": "http://pr-sg.ip2world.com:6001",
#         "username": "capsolver-zone-resi-region-hk",
#         "password": "123456"
#     }
#
#     token = asyncio.run(run(task_data, proxy))
#     print(token)