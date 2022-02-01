from typing import Tuple
import numpy as np
import math

BOARD_WIDTH = 30 # cm
BOARD_DEPTH = 21 # cm

wd_tl = np.array([ 9.43, -35.2, 4.54])
wd_tr = np.array([-18.52, -33.42, 5.09])
wd_bl = np.array([ 11.02, -15.73, 1.02])
wd_br = np.array([-16.58, -15.46, 2.15])
board = [wd_tl,wd_tr,wd_bl,wd_br]

of_1 = (wd_tl - wd_tr) 
of_2 = (wd_bl - wd_br)

wd_tc = (wd_tl + wd_tr) / 2
wd_bc = (wd_bl + wd_br) / 2
wd_rc = (wd_br + wd_tr) / 2
wd_lc = (wd_bl + wd_tl) / 2


def camera_to_board(p: Tuple[float,float]) -> Tuple[float,float]:
    """ Converts coordinates (in px) of a camera frame to a location on the board (in cm where (0,0) is
    the bottom left of the board and (1,1) the top right) """
    
    return (0,0)

def board_to_world(p: Tuple[float,float]) -> Tuple[float, float, float]:
    """ Converts a set of board coordinates (in cm where (0,0) is the bottom left of the board) to world
    coordinates as used by the inverse kinematics library. """
    x = p[0] / BOARD_WIDTH
    y = p[1] / BOARD_DEPTH
    basis = wd_tl*y + wd_bl*(1-y)
    offset = of_1*y + of_2*(1-y)
    return basis - offset*x

def plot_line_p(p1, p2, ax):
    ax.plot(
        [p1[0], p2[0]], 
        [p1[1], p2[1]], 
        [p1[2], p2[2]], 
        color='#0000ff');

def plot_normal_p(p, ax, color='#ff0000'):
    ax.scatter3D(p[0], p[1], p[2], color=color)


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    def test(point, expected, title:str=None):
        if title: print('[T] Running test:',title)
        real = board_to_world(point)
        diff = abs(sum(real - expected))
        assert diff < 0.001
        print('[*] Passed!')

    def demo():
        fig = plt.figure()
        ax = plt.axes(projection='3d')

        for p in board:
            plot_normal_p(p, ax, color='#ff0000')
        for p in [wd_tc, wd_bc, wd_rc, wd_lc]:
            plot_normal_p(p, ax, color='#ff6600')

    point = np.array([BOARD_WIDTH/2, BOARD_DEPTH/2])
    expected = (wd_tl+wd_tr+wd_bl+wd_br) / 4
    test(point, expected, title='Center of the board.')
    
    point = np.array([BOARD_WIDTH/2, 0])
    expected = (wd_bl+wd_br) / 2
    test(point, expected, title='Bottom Center of the board.')
