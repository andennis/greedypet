import asyncio
import functools
import logging
import logging.config
import pathlib
import mergedeep
import yaml
import signal

from app_config import AppConfig, load_config
import data_collector as dc

logger = logging.getLogger(__name__)

LOG_LEVELS = list(map(logging.getLevelName, [logging.INFO, logging.DEBUG]))

APP_CONFIG_FILE = "config.yaml"
LOGGING_CONFIG_FILE = "logging.yaml"

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console_handler']
    },
    'handlers': {
        'console_handler': {
            'level': 'INFO',
            'formatter': 'console',
            'class': 'logging.StreamHandler',
        },
        'file_handler': {
            'level': 'INFO',
            'formatter': 'file',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '<IT MUST BY SET>',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        }
    },
    'formatters': {
        'console': {
            'format': '%(asctime)s | %(process)d | %(name)s | %(levelname)s | %(message)s'
        },
        'file': {
            'format': '%(asctime)s | %(process)d | %(name)s | %(levelname)s | %(message)s'
        }
    }
}


def _configure_logging(working_dir: pathlib.Path):
    with open(str(working_dir / LOGGING_CONFIG_FILE), "r") as f:
        cfg_from_file = yaml.safe_load(f)
        cfg = LOGGING_CONFIG.copy()
        pathlib.Path.mkdir(log_path := working_dir / "logs", exist_ok=True)
        cfg["handlers"]["file_handler"]["filename"] = log_path / "caterpillar.log"
        if cfg_from_file:
            mergedeep.merge(cfg, cfg_from_file)
        logging.config.dictConfig(cfg)

    logger.info("Logging has been configured")


async def run_data_collection(config: AppConfig, working_dir: str):
    def _signal_handler(sig):
        logger.info(f"Trading process is being stopped by {signal.Signals(sig).name} ...")
        asyncio.get_event_loop().remove_signal_handler(sig)
        task.cancel()

    ev_loop = asyncio.get_running_loop()
    for _sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
        ev_loop.add_signal_handler(_sig, functools.partial(_signal_handler, sig=signal.SIGINT))

    task = asyncio.create_task(dc.collecting_data(config))
    await task


def main():
    cwd = pathlib.Path(__file__).parent
    _configure_logging(cwd)
    config = load_config(str(cwd / APP_CONFIG_FILE))
    logger.info(f"Data collection has been started")
    asyncio.run(run_data_collection(config, str(cwd)))
    logger.info(f"Data collection gracefully finished")


if __name__ == "__main__":
    main()
