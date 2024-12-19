from pathlib import Path

raw_env = (Path(__file__).parent / ".env").read_text().strip().splitlines()
worker_class = "uvicorn.workers.UvicornWorker"
reload = True
accesslog = "-"
errorlog = "-"
