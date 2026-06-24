# Gunicorn config — production
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 60
accesslog = "/var/log/inventory/access.log"
errorlog = "/var/log/inventory/error.log"
loglevel = "info"
