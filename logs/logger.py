import logging
from datetime import datetime
import pathlib
from pathlib import  Path

class CustomFormatter(logging.Formatter):
    logging.COMBAT_CONTROL = 22  # between WARNING and INFO
    logging.addLevelName(logging.COMBAT_CONTROL, 'COMBAT_CONTROL')

    logging.STARTING_DEVICE = 23  # between WARNING and INFO
    logging.addLevelName(logging.STARTING_DEVICE, 'STARTING_DEVICE')

    logging.GUIDED_MISSILE = 24  # between WARNING and INFO
    logging.addLevelName(logging.GUIDED_MISSILE, 'GUIDED_MISSILE')

    logging.DISPATCHER = 25  # between WARNING and INFO
    logging.addLevelName(logging.DISPATCHER, 'DISPATCHER')

    logging.RADAR = 26  # between WARNING and INFO
    logging.addLevelName(logging.RADAR, 'RADAR')

    logging.AERO_ENV = 27  # between WARNING and INFO
    logging.addLevelName(logging.AERO_ENV, 'AERO_ENV')

    logging.AIRPLANE = 28  # between WARNING and INFO
    logging.addLevelName(logging.AIRPLANE, 'AIRPLANE')

    black_back = "\x1b[40;1m"
    cyan = "\x1b[36;1m"
    grey = "\x1b[37;1m"
    yellow = '\x1b[33;1m'
    purple = '\x1b[35;1m'
    blue = '\x1b[34;1m'
    green = '\x1b[32;1m'
    white = "\x1b[39;1m"
    red = "\x1b[31;20m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)-15s - %(message)s"

    FORMATS = {
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.INFO: white + format + reset,
        logging.COMBAT_CONTROL: cyan + format + reset,
        logging.STARTING_DEVICE: yellow + format + reset,
        logging.GUIDED_MISSILE: purple + format + reset,
        logging.DISPATCHER: blue + format + reset,
        logging.RADAR: green + format + reset,
        logging.AERO_ENV: grey + format + reset,
        logging.AIRPLANE: black_back + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)



logger = logging.getLogger(__name__)
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y %H_%M_%S")
filename = Path.cwd().resolve().parent / Path("logs") / Path(dt_string + ".log")
logging.basicConfig(filename=filename,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

setattr(logger, 'combat_control', lambda message, *args: logger._log(logging.COMBAT_CONTROL, message, args))
setattr(logger, 'starting_device', lambda message, *args: logger._log(logging.STARTING_DEVICE, message, args))
setattr(logger, 'guided_missile', lambda message, *args: logger._log(logging.GUIDED_MISSILE, message, args))
setattr(logger, 'dispatcher', lambda message, *args: logger._log(logging.DISPATCHER, message, args))
setattr(logger, 'radar', lambda message, *args: logger._log(logging.RADAR, message, args))
setattr(logger, 'aero_env', lambda message, *args: logger._log(logging.AERO_ENV, message, args))
setattr(logger, 'airplane', lambda message, *args: logger._log(logging.AIRPLANE, message, args))

logger.info('Цвета логов')
logger.combat_control('combat_control')
logger.starting_device('starting_device')
logger.guided_missile('guided_missile')
logger.dispatcher('dispatcher')
logger.radar('radar')
logger.aero_env('aero_env')
logger.airplane('airplane')
