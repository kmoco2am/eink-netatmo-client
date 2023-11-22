import signal
import logging


class ProgramKilled(Exception):
    pass


def signal_handler(signum, frame):
    logging.info("Exiting ... " + str(signum))
    raise ProgramKilled


def configure_signals():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
