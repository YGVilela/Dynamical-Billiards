
import sys
from billiards.gui import welcome_window


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        dataFolder = sys.argv[1]
    else:
        dataFolder = "data"

    welcome_window(dataFolder)
