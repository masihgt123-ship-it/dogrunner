
from pythonforandroid.recipes.pygame import Pygame2Recipe


class Pygame261Recipe(Pygame2Recipe):
    version = "2.6.1"
    url = "https://github.com/pygame/pygame/archive/refs/tags/2.6.1.tar.gz"
    hostpython_prerequisites = ["setuptools", "cython>=3.1"]


recipe = Pygame261Recipe()
