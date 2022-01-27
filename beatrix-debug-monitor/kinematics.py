from lib.chain import ik_chain
from abc import abstractmethod

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
    def __init__(self):
        self.chain = ik_chain

    def inverse(self, position:(float,float,float)) -> list:
        return self.chain.inverse_kinematics(position)

    def forward(self, angles:list) -> (float,float,float):
        return [0,0,0]
