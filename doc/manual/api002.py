from pyphant.core.CompositeWorker import CompositeWorker
from pyphant.core.H5FileHandler import H5FileHandler

# create a recipe
recipe = CompositeWorker()
# ... fill the recipe (e.g. Listing 1)

# save it
with H5FileHandler('quicktour_api.h5', 'w') as handler:
    handler.saveRecipe(recipe, saveResults=True)

# load a recipe
with H5FileHandler('quicktour_api.h5', 'r') as handler:
    recipe = handler.loadRecipe()
