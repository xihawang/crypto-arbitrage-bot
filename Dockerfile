# 使用Python 3.10官方镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=web/app_optimized.py \
    FLASK_ENV=production \
    PORT=5000 \
    PIP_NO_PROGRESS_BAR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖 - 简化版本，逐个安装核心包
RUN pip install --no-cache-dir Flask==2.3.0 && \
    pip install --no-cache-dir requests==2.31.0 && \
    pip install --no-cache-dir ccxt && \
    pip install --no-cache-dir python-dotenv==1.0.0

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/data

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# 启动命令
CMD ["python", "web/app_optimized.py"]
