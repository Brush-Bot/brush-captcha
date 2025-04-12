FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

WORKDIR /app
COPY . .

# 安装 Python 依赖和 Camoufox
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir camoufox \
    && pip install --no-cache-dir 'camoufox[GeoIP]'

# 触发 GeoIP 下载（模拟一次带 geoip=True 的 Camoufox 启动）
RUN python -c "from camoufox import Camoufox; Camoufox(geoip=True, headless=True).start().close()"
# 启动任务
ENTRYPOINT ["python", "run_client.py"]
