workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "-"
errorlog = "-"
bind = ["0.0.0.0:8080"]
user = "app"
group = "app"
