# quicktour/quicktour/surfacevis.py
from pyphant.wxgui2.DataVisReg import DataVisReg
from pyphant.core.Connectors import TYPE_IMAGE
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np


class SurfaceVisualizer(object):
    name = "Surface"

    def __init__(self, fc, show=True):
        assert len(fc.dimensions) == 2, "2D FC expected"
        self.fc = fc
        self.draw()
        if show:
            self.show()

    def draw(self):
        fig = pyplot.figure()
        ax = fig.gca(projection='3d')
        y, x = np.meshgrid(*[d.data for d in self.fc.dimensions])
        z = self.fc.data
        zrange = z.max() - z.min()
        ax.plot_surface(
            x, y, z, cmap=cm.coolwarm, linewidth=0, rstride=1, cstride=1
            )
        ax.set_zlim(z.min() - zrange, z.max() + zrange)

    def show(self):
        pyplot.show()


DataVisReg.getInstance().registerVisualizer(
    TYPE_IMAGE, SurfaceVisualizer
    )
