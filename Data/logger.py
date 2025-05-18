import logging
from enum import Enum
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LogLevel(Enum):
    DEBUG = logging.DEBUG  # 10
    INFO = logging.INFO  # 20
    WARNING = logging.WARNING  # 30
    ERROR = logging.ERROR  # 40
    CRITICAL = logging.CRITICAL  # 50


# Создаем обработчики вне функции
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(f"./logs/regress_run.log")

# Устанавливаем уровень логирования для каждого обработчика
console_handler.setLevel(LogLevel.DEBUG.value)  # Уровень для консольного обработчика
file_handler.setLevel(LogLevel.ERROR.value)  # Уровень для файлового обработчика

# Задаем форматирование
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S%p",
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)


def logger(name: str, level: LogLevel) -> logging.Logger:
    # Получаем существующий логгер
    logger = logging.getLogger(__name__)
    logger.setLevel(level.value)  # Set logger level using enum value

    # Добавляем обработчики только если они еще не добавлены
    if not console_handler in logger.handlers:
        logger.addHandler(console_handler)
    if not file_handler in logger.handlers:
        logger.addHandler(file_handler)

    return logger