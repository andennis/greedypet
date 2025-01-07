import os
import logging
import logging.config
import yaml
import signal
import click
import pathlib
import asyncio
import functools
import mergedeep

import market_execution as mexec
from gp_config import load_config, GPConfig


logger = logging.getLogger(__name__)
LOG_LEVELS = list(map(logging.getLevelName, [logging.INFO, logging.DEBUG]))

APP_CONFIG_FILE = "gp_config.yaml"
LOGGING_CONFIG_FILE = "gp_logging.yaml"

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
    with (open(str(working_dir / LOGGING_CONFIG_FILE), "r") as f):
        cfg_from_file = yaml.safe_load(f)
        cfg = LOGGING_CONFIG.copy()
        pathlib.Path.mkdir(log_path := working_dir / "logs", exist_ok=True)
        cfg["handlers"]["file_handler"]["filename"] = log_path / "greedypet.log"
        if cfg_from_file:
            mergedeep.merge(cfg, cfg_from_file)
        logging.config.dictConfig(cfg)

    logger.info("Logging has been configured")


async def run_trades(config: GPConfig, working_dir: str):
    def _signal_handler(sig):
        logger.info(f"Trading process is being stopped by {signal.Signals(sig).name} ...")
        asyncio.get_event_loop().remove_signal_handler(sig)
        for tsk in tasks:
            tsk.cancel()

    ev_loop = asyncio.get_running_loop()
    for _sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
        ev_loop.add_signal_handler(_sig, functools.partial(_signal_handler, sig=signal.SIGINT))

    mexec.init_market_execution(config, working_dir)
    tasks = [
        asyncio.create_task(mexec.reading_market_trades(config)),
        asyncio.create_task(mexec.tracking_trade_signals(config)),
        # asyncio.create_task(mexec.making_market_trades(config))
    ]
    await asyncio.gather(*tasks)


@click.command()
@click.option(
    "-w",
    "--working-dir",
    type=click.Path(exists=True),
    default=".",
)
@click.option("-n", "--name", default=f"gp-{os.getpid()}")
def main(working_dir: str, name: str):
    if working_dir:
        os.chdir(working_dir)
    cwd = pathlib.Path(__file__).parent

    _configure_logging(cwd)
    config = load_config(str(cwd / APP_CONFIG_FILE))
    logger.info(f"Bot {name} started")
    asyncio.run(run_trades(config, str(cwd)))
    logger.info(f"Bot {name} gracefully finished")


if __name__ == "__main__":
    main()
