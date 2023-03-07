import logging
# general logger for all control/si_toolkit users. Produces nice output format with live hyperlinks for pycharm users
# to use it, just call log=get_logger() at the top of your python file
# all these loggers share the same logger name 'Control_Toolkit'

LOGGING_LEVEL = logging.DEBUG # usually INFO is good
class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    # see https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output/7995762#7995762

    # \x1b[ (ESC[) is the CSI introductory sequence for ANSI https://en.wikipedia.org/wiki/ANSI_escape_code
    # The control sequence CSI n m, named Select Graphic Rendition (SGR), sets display attributes.
    grey = "\x1b[2;37m" # 2 faint, 37 gray
    yellow = "\x1b[33;21m"
    cyan = "\x1b[0;36m" # 0 normal 36 cyan
    green = "\x1b[31;21m" # dark green
    red = "\x1b[31;21m" # bold red
    bold_red = "\x1b[31;1m"
    light_blue = "\x1b[1;36m"
    blue = "\x1b[1;34m"
    reset = "\x1b[0m"
    # File "{file}", line {max(line, 1)}'.replace("\\", "/")
    format = '[%(levelname)s]: %(asctime)s - %(name)s - %(message)s (File "%(pathname)s", line %(lineno)d, in %(funcName)s)'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: red + format + reset,
        logging.ERROR: bold_red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record).replace("\\", "/") #replace \ with / for pycharm links


def get_logger(name='ControlToolkit'):
    """ Use get_logger to define a logger with useful color output and info and warning turned on according to the global LOGGING_LEVEL.

    :param name: ignored -- all loggers here have the name 'ControlToolkit' so that all can be affected uniformly

    :returns: the logger.
    """
    # logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger('ControlToolkit') # tobi changed so all have same name so we can uniformly affect all of them
    logger.setLevel(LOGGING_LEVEL)
    # create console handler if this logger does not have handler yet
    if len(logger.handlers)==0:
        ch = logging.StreamHandler()
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)
    return logger