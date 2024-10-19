import os
import logging
import yaml
import signal
import click
import pathlib
import asyncio
import functools

from gp_config import load_config, GPConfig

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


async def _read_market_trades(config: GPConfig):
    logger.info(f"Trades reading started")
    try:
        while True:
            logger.info(f"Read trades")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info(f"Trades reading finished")


async def _track_trade_signals(config: GPConfig):
    logger.info(f"Trade signals tracking started")
    try:
        while True:
            logger.info(f"Track trade signals")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info(f"Trade signals tracking finished")


async def _make_market_trades(config: GPConfig):
    logger.info(f"Trading started")
    try:
        while True:
            logger.info(f"Make trading")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info(f"Trading finished")


async def run_trades(config: GPConfig):
    def _signal_handler(sig):
        logger.info(f"Trading process is being stopped by {signal.Signals(sig).name} ...")
        asyncio.get_event_loop().remove_signal_handler(sig)
        for tsk in tasks:
            tsk.cancel()

    ev_loop = asyncio.get_running_loop()
    for _sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
        ev_loop.add_signal_handler(_sig, functools.partial(_signal_handler, sig=signal.SIGINT))

    tasks = [
        asyncio.create_task(_read_market_trades(config)),
        asyncio.create_task(_track_trade_signals(config)),
        asyncio.create_task(_make_market_trades(config))
    ]
    await asyncio.gather(*tasks)


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
    config = load_config(config_file)
    asyncio.run(run_trades(config))
    logger.info(f"Bot {name} gracefully finished")


if __name__ == "__main__":
    main()
