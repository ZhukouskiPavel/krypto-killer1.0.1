import logging
from sys import stdout

from loguru import logger

from core.settings import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelname

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        if frame:
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back  # type: ignore
                depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def set_default_handler() -> None:
    logger.remove()
    logger.add(
        stdout,
        level=settings.logging.level,
        serialize=settings.logging.json_logs,
        format=settings.logging.format,
    )


def configure_logging() -> None:
    intercept_handler = InterceptHandler()

    set_default_handler()

    seen = set()
    for name in logging.root.manager.loggerDict.keys():
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]
