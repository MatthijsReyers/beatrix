from lib.chain import ik_chain
from abc import abstractmethod
from ikpy.chain import Chain

class Kinematics():
    def __init__(self):
        pass

    @abstractmethod
    def inverse(self, position:(float,float,float)) -> list:
        raise NotImplemented

    @abstractmethod
    def forward(self, angles:list) -> (float,float,float):
        raise NotImplemented

class IkPyKinematics(Kinematics):
    def __init__(self, chain: Chain):
        self.chain = chain

    def inverse(self, position:(float,float,float)) -> list: # TODO omzetten naar dict
        return self.chain.inverse_kinematics(position)

    def forward(self, angles:list) -> (float,float,float):
        return [0,0,0]
