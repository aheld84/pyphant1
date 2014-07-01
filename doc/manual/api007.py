class Visualizer(object):
    name = "Name"

    def __init__(self, stuffToVisualize, show=True):
        # extract and store stuff from stuffToVisualize
        # needed for visualization
        self.some_method_to_draw_stuff()
        if show:
            self.some_method_to_show_stuff()

    def some_method_to_draw_stuff(self):
        # render stuff into a buffer
        pass

    def some_method_to_show_stuff(self):
        # actually show stuff in a GUI window
        pass
