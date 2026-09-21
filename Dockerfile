# ============================================
# 会场精灵 - 后端镜像（FastAPI + Uvicorn）
# ============================================
FROM python:3.11-slim

# 运行时环境
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# 国内 pip 源；海外构建可用 --build-arg PIP_INDEX_URL=https://pypi.org/simple/ 覆盖
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# 先装依赖（利用层缓存：requirements 不变时不重复安装）
COPY requirements.txt .
RUN pip install --no-cache-dir -i ${PIP_INDEX_URL} -r requirements.txt

# 再复制业务代码
COPY main.py ./
COPY app/ ./app/
COPY database/ ./database/
COPY static/ ./static/

RUN mkdir -p static/uploads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health').status == 200 else 1)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
