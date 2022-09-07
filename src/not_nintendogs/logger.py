import logging

logging.basicConfig(
    filename="game.log",
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
)

log = logging.getLogger(__file__)
