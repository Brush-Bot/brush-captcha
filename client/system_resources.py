import os
import psutil

def auto_concurrency():
    # 获取逻辑和物理核心
    logical_cpu = psutil.cpu_count(logical=True)
    physical_cpu = psutil.cpu_count(logical=False) or 1

    # 获取可用内存（单位 GB）
    mem_gb = psutil.virtual_memory().available / (1024 ** 3)

    # 每 1 GB 支持一个并发
    mem_based = int(mem_gb)

    # 限制最大并发：不超过物理核心数的 2 倍
    max_concurrency = physical_cpu * 2

    # 最终并发：min(逻辑核, 内存估算, 最大限制)，最少为 1
    return max(1, min(logical_cpu, mem_based, max_concurrency))