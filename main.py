import os
from email.policy import default

import click
import logging
import yaml
import signal
import sys
from bot_config import BOT_CONFIG

logger = logging.getLogger(__name__)
LOG_LEVELS = [logging.getLevelName(logging.INFO), logging.getLevelName(logging.DEBUG)]

def _configure_logging(log_dir: str, log_level):
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, f"greedypet-{os.getpid()}.log"),
        level=logging.getLevelNamesMapping()[log_level],
        format="%(asctime)s | %(process)d | %(name)s | %(levelname)s | %(message)s",
    )

    # Configure console log
    fmt = logging.Formatter(
        "%(asctime)s | %(process)d | %(name)s | %(levelname)s | %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)
    logger.info("Logging has been configured")


def _load_config(file_name: str):
    with open(file_name, 'r') as f:
        cfg = yaml.safe_load(f)
        logger.info(f"Config loaded from {file_name}")
        return cfg

def _signal_handler(sig, frame):
    logger.info("Bot stopped")
    sys.exit(0)

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGQUIT, _signal_handler)

@click.command()
@click.option("-c", "--config", "config_file", type=click.Path(exists=True), default="bot_config.yaml")
@click.option("-n", "--name", default=f"bot-{os.getpid()}")
@click.option(
    "-ll",
    "--log-level",
    type=click.Choice(LOG_LEVELS),
    default=logging.getLevelName(logging.INFO),
)
@click.option("-ld", "--log-dir", type=click.Path(exists=True), default="/tmp")
def main(config_file: str, name: str, log_level: str, log_dir: str):
    _configure_logging(log_dir, log_level)
    logger.info(f"Bot {name} started")

    config = _load_config(config_file)
    BOT_CONFIG.update(config)


if __name__ == "__main__":
    main()
