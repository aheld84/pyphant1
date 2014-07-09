# import all necessary classes
from pyphant.core.CompositeWorker import CompositeWorker
from ImageProcessing.ImageLoaderWorker import ImageLoaderWorker
from ImageProcessing.Gradient import Gradient
from Statistics.Histogram import Histogram

# create a recipe aka CompositeWorker
recipe = CompositeWorker()

# instantiate an ImageLoader worker, insert it into the recipe
# and set the filename parameter
loader = ImageLoaderWorker()
recipe.addWorker(loader)
loader.paramFilename.value = "1.5.01.tiff"

# instantiate a Gradient worker, insert it into the recipe
# and connect it to the ImageLoader worker
gradient = Gradient()
recipe.addWorker(gradient)
gradient.getSockets()[0].insert(loader.getPlugs()[0])

# instantiate a Histogram worker, insert it into the recipe,
# set its bins parameter and connect it to the Gradient worker
histogram = Histogram()
recipe.addWorker(histogram)
histogram.paramBins.value = 50
histogram.getSockets()[0].insert(gradient.getPlugs()[0])

# request the result from the Histogram worker's plug
result = histogram.getPlugs()[0].getResult()
print result.data.mean()
