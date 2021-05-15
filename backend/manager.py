from typing import List
from models import Endpoint


class APIManager:

    def __init__(self):
        self.endpoints = []

    def set_endpoints(self, endpoints: List[Endpoint]):
        self.endpoints = endpoints
        self.reset()

    def reset(self):
        pass

    def run(self):
        pass

    def stop(self):
        pass
