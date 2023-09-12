import sys
import os
import cv2

from pandas import read_csv
from matplotlib.pyplot import figure
from math import pi, isnan
from progress.bar import Bar

# Routine to plot each iteration in one file

# Read args
orbitsFolder = sys.argv[1]
saveFolder = sys.argv[2]
videoLength = 0.0
if len(sys.argv) >= 4:
    videoLength = float(sys.argv[3])
    if isnan(videoLength):
        print(f"Couldn't convert video length {sys.argv[3]}. Won't generate video.")
        videoLength = 0.0

# Read orbits
orbitFiles = os.listdir(orbitsFolder)
orbits = [read_csv(os.path.join(orbitsFolder, fileName)) for fileName in orbitFiles]

# Separate each iteration
fig = figure()
images = []
tArray = []
thetaArray = []
thetaMinusArray = []
bar = Bar(
    'Reading', suffix='%(percent)d%% - %(eta)ds',
    max=len(orbits[0])
)

for iteration in range(len(orbits[0])):
    # Get point for each orbit
    t = []
    theta = []
    thetaMinus = []
    for orbit in orbits:
        obj = orbit.loc[iteration]
        t.append(obj.t)
        theta.append(obj.theta)
        thetaMinus.append(pi - obj.theta)

    # Prepare figure
    fig.clf(True)
    axPhase = fig.add_subplot()
    axPhase.set_aspect('equal')
    axPhase.set_xlim([
        0.0,
        2*pi
    ])
    axPhase.set_ylim([0, pi])

    # I'm sure there's a better way...
    axPhase.scatter(t, thetaMinus, s=1, c = "blue")
    axPhase.scatter(t, theta, s=1, c = "green")

    bar.next()

    # Save figure
    imagePath = os.path.join(saveFolder, f"{iteration}.png")
    fig.savefig(imagePath)
    images.append(imagePath)

bar.finish()

if videoLength > 0:
    print("Generating video")
    video_name = os.path.join(saveFolder, "video.avi")

    frame = cv2.imread(images[0])
    height, width, layers = frame.shape

    fps = len(images)/videoLength
    video = cv2.VideoWriter(video_name, 0, fps, (width,height))

    for image in images:
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()