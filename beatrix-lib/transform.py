from typing import Tuple
import numpy as np
import math

# Real dimensions of the board in centimeters.
BOARD_WIDTH = 30
BOARD_DEPTH = 21

wd_tl = np.array([ 9.43, -35.2, 4.54])
wd_tr = np.array([-18.52, -33.42, 5.09])
wd_bl = np.array([ 11.02, -15.73, 1.02])
wd_br = np.array([-16.58, -15.46, 2.15])
board = [wd_tl,wd_tr,wd_bl,wd_br]

of_1 = (wd_tl - wd_tr) 
of_2 = (wd_bl - wd_br)

# Coordinates of the bottom/top/left/right center of the board (in world space).
wd_tc = (wd_tl + wd_tr) / 2
wd_bc = (wd_bl + wd_br) / 2
wd_rc = (wd_br + wd_tr) / 2
wd_lc = (wd_bl + wd_tl) / 2

# List of significant board locations (makes it easier to plot).
wd_board = [wd_tl, wd_tr, wd_bl, wd_br, wd_tc, wd_bc, wd_rc, wd_lc]

# Corners of the board as shown in the camera frame.
img_bl = np.array([260, 1060])
img_tl = np.array([257, 5])
img_tr = np.array([1793,0])
img_br = np.array([1808,1060])

# List of significant board locations (for easy plotting) in image.
img_board = [img_bl, img_tl, img_tr, img_br]

def camera_to_board(p: Tuple[float,float]) -> Tuple[float,float]:
    """ Converts coordinates (in px) of a camera frame to a location on the board (in cm where (0,0) is
    the bottom left of the board and (1,1) the top right) """
    width = (img_br[0] - img_bl[0] + img_tr[0] - img_tl[0]) / 2
    height = (img_bl[1] - img_tl[1] + img_br[1] - img_tr[1]) / 2
    
    x = (p[0] - img_bl[0])/width * BOARD_WIDTH
    y = (1 - (p[1] - img_tl[1])/height) * BOARD_DEPTH
    return (x,y)

# Precomputed offset vectors used for board world conversion.
of_1 = (wd_tl - wd_tr) 
of_2 = (wd_bl - wd_br)

def board_to_world(p: Tuple[float,float]) -> Tuple[float, float, float]:
    """ Converts a set of board coordinates (in cm where (0,0) is the bottom left of the board) to world
    coordinates as used by the inverse kinematics library. """
    x = p[0] / BOARD_WIDTH
    y = p[1] / BOARD_DEPTH
    basis = wd_tl*y + wd_bl*(1-y)
    offset = of_1*y + of_2*(1-y)
    return basis - offset*x

if __name__ == '__main__':
    def test(point, expected, title:str=None):
        if title: print('[T] Running test:',title)
        real = board_to_world(point)
        diff = abs(sum(real - expected))
        assert diff < 0.001
        print('[*] Passed!')

    point = np.array([BOARD_WIDTH/2, BOARD_DEPTH/2])
    expected = (wd_tl+wd_tr+wd_bl+wd_br) / 4
    test(point, expected, title='Center of the board.')
    
    point = np.array([BOARD_WIDTH/2, 0])
    expected = (wd_bl+wd_br) / 2
    test(point, expected, title='Bottom Center of the board.')
