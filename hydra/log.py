from errno import EEXIST

__author__ = 'jm'

import logging
import os
import sys


logging.getLogger()

LOG_NAME = 'hydrad'


def initialise(options):
    """
The default logger grabs every level of logs.
Give the user the means to filter the logs from the gui window.
    """
    if options.logfile:
        try:
            os.makedirs(os.path.abspath(os.path.dirname(options.logfile)))
        except OSError, e:
            if e.errno != EEXIST:
                print "There was an error creating the log directory, exiting... (%s)" % e
                sys.exit(1)
    #logging.setupLogger(filename=options.logfile, filemode='w')


def get_logger():
    """
    :return: the default logger object
    """
    return logging.getLogger(LOG_NAME)
