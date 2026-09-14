import logging
import sys


def configure_logging():
    # Сбрасываем старые хендлеры, чтобы применить наш формат
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.removeHandler(root_logger.handlers[0])

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',  # Миллисекунды
        stream=sys.stdout,
    )

    # ЯВНО ставим уровень для нашего логгера
    logging.getLogger('app.middleware').setLevel(logging.INFO)
