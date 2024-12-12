from pathlib import Path

raw_env = (Path(__file__).parent / ".env").read_text().strip().splitlines()
worker_class = "uvicorn.workers.UvicornWorker"
reload = True
accesslog = "-"
errorlog = "-"
bind = ["0.0.0.0:8080"]
user = "app"
group = "app"
