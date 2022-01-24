from source import robotarm as rb

"""
    Init_pos and bounds needs to be checked before running!
"""

# bounds = [{"min angle": 80, "max angle": 100},  # base
#           {"min angle": 80, "max angle": 100},  # shoulder
#           {"min angle": 80, "max angle": 100},  # elbow
#           {"min angle": 80, "max angle": 100},  # wrist
#           {"min angle": 80, "max angle": 100}]  # grabber

parameters =   [{"servo": "single", "min angle": 80, "max angle":100, "actuation range": 270, "mirrored": False, "port": 0}, # base
                {"servo": "dual", "min angle": 80, "max angle":100, "actuation range": 180, "mirrored": [False, True], "port": [1,2]}, # shoulder
                {"servo": "single", "min angle": 80, "max angle":100, "actuation range": 180, "mirrored": False, "port": 3}, # elbow
                {"servo": "single", "min angle": 80, "max angle":100, "actuation range": 180, "mirrored": False, "port": 4}, # wrist
                {"servo": "single", "min angle": 80, "max angle":100, "actuation range": 180, "mirrored": False, "port": 5}] # grabber


init_pos = [90, 90, 90, 90, 90]
new_pos = [110, 100, 90, 80, 70]

testarm = rb.RobotArm(parameters, init_pos)
old_pos = testarm.get_angle()
testarm.set_arm(old_pos, new_pos, 3)
