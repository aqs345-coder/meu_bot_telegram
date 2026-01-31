import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_handler = RotatingFileHandler(
        "bot.log", maxBytes=5*1024*1024, backupCount=2, encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(log_format))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, stream_handler]
    )

    logger = logging.getLogger("SETUP")
    logger.info("✅ Sistema de logs iniciado com sucesso!")
