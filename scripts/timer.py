import logging
import time
import numpy as np
import matplotlib.pyplot as plt
from engineering_notation import EngNumber as eng  # only from pip
import atexit


LOGGING_LEVEL = logging.INFO


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def my_logger(name):
    # logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    # create console handler
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger


log = my_logger(__name__)

timers = {}
times = {}


class Timer:
    def __init__(self, timer_name='', delay=None,
                 show_hist=False, numpy_file=None):
        """ Make a Timer() in a _with_ statement for a block of code.
        The timer is started when the block is entered and stopped when exited.
        The Timer _must_ be used in a with statement.
        :param timer_name: the str by which this timer is repeatedly called
            and which it is named when summary is printed on exit
        :param delay: set this to a value to simply accumulate
            this externally determined interval
        :param show_hist: whether to plot a histogram with pyplot
        :param numpy_file: optional numpy file path
        """
        self.timer_name = timer_name
        self.show_hist = show_hist
        self.numpy_file = numpy_file
        self.delay = delay

        if self.timer_name not in timers.keys():
            timers[self.timer_name] = self
        if self.timer_name not in times.keys():
            times[self.timer_name] = []

    def __enter__(self):
        if self.delay is None:
            self.start = time.time()
        return self

    def __exit__(self, *args):
        if self.delay is None:
            self.end = time.time()
            self.interval = self.end - self.start  # measured in seconds
        else:
            self.interval = self.delay
        times[self.timer_name].append(self.interval)

    def print_timing_info(self, logger=None):
        """ Prints the timing information accumulated for this Timer
        :param logger: write to the supplied logger,
            otherwise use the built-in logger
        """
        if len(times) == 0:
            log.error(f'Timer {self.timer_name} has no statistics; was it used without a "with" statement?')
            return
        a = np.array(times[self.timer_name])
        timing_mean = np.mean(a) # todo use built in print method for timer
        timing_std = np.std(a)
        timing_median = np.median(a)
        timing_min = np.min(a)
        timing_max = np.max(a)
        s='{} n={}: {}s +/- {}s (median {}s, min {}s max {}s)'.format(self.timer_name, len(a),
                                                                      eng(timing_mean), eng(timing_std),
                                                                      eng(timing_median), eng(timing_min),
                                                                      eng(timing_max))

        if logger is not None:
            logger.info(s)
        else:
            log.info(s)


def print_timing_info():
    for k, v in times.items():  # k is the name, v is the list of times
        a = np.array(v)
        timing_mean = np.mean(a)
        timing_std = np.std(a)
        timing_median = np.median(a)
        timing_min = np.min(a)
        timing_max = np.max(a)
        log.info('== Timing statistics from all Timer ==\n{} n={}: {}s +/- {}s (median {}s, min {}s max {}s)'.format(k, len(a),
                                                                          eng(timing_mean), eng(timing_std),
                                                                          eng(timing_median), eng(timing_min),
                                                                          eng(timing_max)))
        if timers[k].numpy_file is not None:
            try:
                log.info(f'saving timing data for {k} in numpy file {timers[k].numpy_file}')
                log.info('there are {} times'.format(len(a)))
                np.save(timers[k].numpy_file, a)
            except Exception as e:
                log.error(f'could not save numpy file {timers[k].numpy_file}; caught {e}')

        if timers[k].show_hist:

            def plot_loghist(x, bins):
                hist, bins = np.histogram(x, bins=bins) # histogram x linearly
                if len(bins)<2 or bins[0]<=0:
                    log.error(f'cannot plot histogram since bins={bins}')
                    return
                logbins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), len(bins)) # use resulting bin ends to get log bins
                plt.hist(x, bins=logbins) # now again histogram x, but with the log-spaced bins, and plot this histogram
                plt.xscale('log')

            dt = np.clip(a,1e-6, None)
            # logbins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), len(bins))
            try:
                plot_loghist(dt,bins=100)
                plt.xlabel('interval[ms]')
                plt.ylabel('frequency')
                plt.title(k)
                plt.show()
            except Exception as e:
                log.error(f'could not plot histogram: got {e}')


atexit.register(print_timing_info)
