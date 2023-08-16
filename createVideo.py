# imports
import os
import cv2
from tqdm import tqdm

def createVideo(path, outfolder, name, fps = 60):
    
    # set-up paths for images
    images = [os.path.join(path, i) for i in list(os.listdir(path))]

    # sort images in right order
    dictionary = {int(image[image.rindex("_")+1:image.rindex(".")]): image for image in images}
    indices = sorted(dictionary)
    images = [dictionary[i] for i in indices]

    # create video
    initial_frame = cv2.imread(images[0])
    height, width, layers = initial_frame.shape

    video = cv2.VideoWriter(name, 0, fps, (width, height))
    for image in images:
        video.write(cv2.imread(image))

    os.system(f"mv {name} {outfolder}")

    cv2.destroyAllWindows()
    video.release()
