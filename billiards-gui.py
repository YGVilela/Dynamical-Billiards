from billiards.billiards import Billiard
from billiards.geometry import ComposedPath, SimplePath
from billiards.gui import edit_initial_conditions
from billiards.time import sharedTimer

if __name__ == "__main__":
    path = SimplePath("0", "2*pi", "cos(t)", "sin(t)")
    boundary = ComposedPath([path])
    billiard = Billiard(boundary)
    edit_initial_conditions(billiard)
    print(sharedTimer.stats())
