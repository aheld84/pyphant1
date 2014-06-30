from pyphant.core.H5FileHandler import H5FileHandler

# load the GUI example recipe
with H5FileHandler('quicktour.h5', 'r') as handler:
    recipe = handler.loadRecipe()

# access the Gradient worker by name
gradient = recipe.getWorker('Gradient')
