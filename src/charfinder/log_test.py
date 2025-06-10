import logging

from charfinder.utils.logger import setup_logging

setup_logging()

logger = logging.getLogger("charfinder")
logger.debug("This is a debug log to file only")
logger.info("This is an info log to both console (if verbose) and file")

logging.shutdown()  # << flush logs!
