import multiprocessing
import os

# KVM 1: 1 vCPU, 1GB RAM
# Workers = (2 x CPU cores) + 1
workers = 3
threads = 2
worker_class = "gthread"

bind = "127.0.0.1:8000"
backlog = 2048

timeout = 120
graceful_timeout = 30
keepalive = 5

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app for faster worker startup
preload_app = True

# Worker memory limits (MB) - kill workers using more than this
worker_tmp_dir = "/dev/shm"

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "warning"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "thedecoredits"

def on_starting(server):
    os.makedirs("/var/log/gunicorn", exist_ok=True)
