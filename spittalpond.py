from spittalmodel import SpittalModel
from spittalexposure import SpittalExposure

class SpittalPond():
    """ Python interface to the Oasis Django API.

    This class provides an easy to use front-end interface
    to the Oasis mid-tier Django API.
    """

    def __init__(self, base_url, pub_user):
        # Initiating our sub classes
        self.model = SpittalModel(base_url, pub_user)
        self.exposure = SpittalExposure(base_url, pub_user)
