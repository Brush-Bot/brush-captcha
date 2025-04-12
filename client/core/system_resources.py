import os
import psutil

def auto_concurrency():
    logical_cpu = psutil.cpu_count(logical=True)
    physical_cpu = psutil.cpu_count(logical=False) or 1
    mem_gb = psutil.virtual_memory().available / (1024 ** 3)

    # 每 1 GB 支持一个并发
    mem_based = int(mem_gb)

    # 限制最大并发：不超过物理核心数的 2 倍
    max_concurrency = physical_cpu * 2

    # min(逻辑核, 内存估算, 最大限制)，最少为 1
    return max(1, min(logical_cpu, mem_based, max_concurrency))