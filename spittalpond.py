from spittalmodel import SpittalModel
from spittalexposure import SpittalExposure
from spittalrun import SpittalRun
import logging

class SpittalPond():
    """ Python interface to the Oasis Django API.

    This class provides an easy to use front-end interface
    to the Oasis mid-tier Django API.
    """

    # TODO: Fix the the default log location below to work on Windows.
    def __init__(self, base_url, pub_user,
                 log_file='/var/tmp/logger.log', log_level=logging.INFO):
        # Initiating our sub classes
        logger = logging.getLogger('spittalpond')
        logger.propagate = False
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)

        logger.info('Initating new spittalpond instance.')

        self.model = SpittalModel(base_url, pub_user)
        self.exposure = SpittalExposure(base_url, pub_user)
        self.run = SpittalRun(base_url, pub_user)
