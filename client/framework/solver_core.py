import yaml

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

def get_proxy_url():
    proxy_cfg = config.get("proxy")
    if proxy_cfg:
        proxy = {
            "server": proxy_cfg["server"],
            "username": proxy_cfg["username"],
            "password": proxy_cfg["password"],
        }
        return proxy
    return None

def get_solver_config():
    return config.get("camoufox", {})
