from controller import Controller

class AutoPilot:

    def __init__(self, controller: Controller):
        self.controller = controller
        self.running = False

