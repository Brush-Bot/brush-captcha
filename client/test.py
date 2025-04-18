import asyncio
from task_handlers.HcaptchaCracker import run

async def main():
    proxy = {
        "server": "http://capsolver-zone-resi-region-hk:123456@pr-sg.ip2world.com:6001"

    }
    task = {
        "websiteURL": "https://accounts.hcaptcha.com/demo",
        "websiteKey": "00000000-0000-0000-0000-000000000000",  # 替换为真实 sitekey
        "metadata": {
            "label": "bus"
        }
    }
    result = await run(task, proxy)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())