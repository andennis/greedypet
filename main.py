import os
import logging
import yaml
import signal
import sys
import click
import pathlib

from gp_config import load_config

logger = logging.getLogger(__name__)
LOG_LEVELS = list(map(logging.getLevelName, [logging.INFO, logging.DEBUG]))

cwd = pathlib.Path(__file__).parent
default_config_file = cwd / "gp_config.yaml"


def _configure_logging(log_dir: str, log_level: str):
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, f"greedypet-{os.getpid()}.log"),
        level=getattr(logging, log_level),
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
    with open(file_name, "r") as f:
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
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(exists=True),
    default=default_config_file,
)
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
    load_config(config_file)


if __name__ == "__main__":
    main()
