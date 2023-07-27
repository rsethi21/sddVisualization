# imports
import os
import cv2
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description="This software allows you to create a video of images generated from draw3D.py software")
parser.add_argument('-p', '--path', help='path to folder with images', required=True)
parser.add_argument('-o', '--output', help='path to output movie file (avi)', required=False, default='./movie.avi')
parser.add_argument('-s', '--sort', help='sort images (images must have number before extension (i.e. name_#.extension)', default=False, action=argparse.BooleanOptionalAction)
parser.add_argument('-f', '--fps', help='adjust frames per second for video', required=False, default=30)

def prepareImages(path, sort = False):

    # set-up paths for images
    image_path = path
    images = [os.path.join(image_path, i) for i in list(os.listdir(image_path))]
    
    # sort images in right order
    if sort:
        try:
            dictionary = {int(image[image.rindex("_")+1:image.rindex(".")]): image for image in images}
            indices = sorted(dictionary)
            images = [dictionary[i] for i in indices]
        except ValueError:
            print("Utilized the incorrect image file name formating! Must follow the following syntax:\n[filename]_[#].[extension]")

    return images

def video(images, fps, outputpath):

    # create video
    name = outputpath
    
    initial_frame = cv2.imread(images[0])
    height, width, layers = initial_frame.shape
    
    video = cv2.VideoWriter(name, 0, fps, (width, height))
    
    for image in tqdm(images):
        video.write(cv2.imread(image))
        
    cv2.destroyAllWindows()
    video.release()


if __name__ == "__main__":
    
    args = parser.parse_args()
    
    images = prepareImages(args.path, sort = args.sort)

    video(images, int(args.fps), args.output)