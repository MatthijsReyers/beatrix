from source import robotarm as rb

"""
    Init_pos and bounds needs to be checked before running!
"""

bounds = [{"min angle": 80, "max angle": 100},  # base
          {"min angle": 80, "max angle": 100},  # shoulder
          {"min angle": 80, "max angle": 100},  # elbow
          {"min angle": 80, "max angle": 100},  # wrist
          {"min angle": 80, "max angle": 100}]  # grabber

init_pos = [90, 90, 90, 90, 90]
new_pos = [110, 100, 90, 80, 70]

testarm = rb.RobotArm(bounds, init_pos)
old_pos = testarm.get_angle()
testarm.set_arm(old_pos, new_pos, 3)
