import json
import os
import time
from .utils import parse_proxy_line
from common.logger import get_logger,emoji
logger = get_logger("proxy_manager")
USAGE_FILE = os.path.join(os.path.dirname(__file__), "proxy_usage.json")

class Proxy:
    def __init__(self, raw, usage_data=None):
        parsed = parse_proxy_line(raw)
        self.raw = raw
        self.ip = parsed["ip"]
        self.port = parsed["port"]
        self.user = parsed["user"]
        self.password = parsed["pass"]
        self.key = f"{self.ip}:{self.port}"

        usage = usage_data.get(self.key, {}) if usage_data else {}
        self.usage_count = usage.get("usage_count", 0)
        self.last_assigned_time = usage.get("last_assigned_time", 0)

    def is_available(self, now_ts, cooldown=600):
        return (now_ts - self.last_assigned_time) >= cooldown

    def get_proxy_config(self):
        return {
            "server": f"http://{self.ip}:{self.port}",
            "username": self.user,
            "password": self.password
        }

    def to_usage_record(self):
        return {
            "usage_count": self.usage_count,
            "last_assigned_time": self.last_assigned_time
        }
class ProxyManager:
    def __init__(self, path="proxy/proxies.txt"):
        self.proxies = []
        self.usage_data = self._load_usage()
        self.load_proxies(path)

    def _load_usage(self):
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, "r") as f:
                data = json.loads(f.read())
                logger.info(emoji("SUCCESS", f"共加载了{len(data)}条IP"))
                return data
        return {}

    def _save_usage(self):
        data = {p.key: p.to_usage_record() for p in self.proxies}
        with open(USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load_proxies(self, path):
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        self.proxies.append(Proxy(line.strip(), self.usage_data))
                    except ValueError as e:
                        logger.info(emoji("ERROR",f"跳过无效代理:{line.strip()}"))
    def assign_proxy(self):
        now = time.time()
        available = [p for p in self.proxies if p.is_available(now)]
        if not available:
            return None

        available.sort(key=lambda p: (p.usage_count, p.last_assigned_time))
        proxy = available[0]
        proxy.usage_count += 1
        proxy.last_assigned_time = now
        self._save_usage()
        return proxy.get_proxy_config()
# proxy_mgr = ProxyManager()
# proxy_config = proxy_mgr.assign_proxy()
# if proxy_config:
#     print(proxy_config)
# else:
#     print("没有可用代理")