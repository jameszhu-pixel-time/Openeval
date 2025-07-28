# log_setup.py
import logging, sys
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")        # 20250707_101530
log_file = LOG_DIR / f"pipeline_{ts}.log"            # logs/pipeline_20250707_101530.log

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),            # 控制台
        logging.FileHandler(log_file, encoding="utf-8")
    ],
    datefmt="%Y-%m-%d %H:%M:%S",
)