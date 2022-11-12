
from billiards.gui import main_window
from billiards.utils.time import sharedTimer


if __name__ == "__main__":
    main_window()
    print(sharedTimer.stats())
