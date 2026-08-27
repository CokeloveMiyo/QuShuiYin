import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

log_path = Path('logs/qingying.log')
log_path.parent.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        RotatingFileHandler(
            str(log_path),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('qingying')


def get_logger(name):
    return logging.getLogger(name)
