from turtle import circle
import cv2
import numpy as np
from enum import Enum
from scipy import ndimage
import os

class Shapes(Enum):
    Circle = "Circle"
    Diamond = "Diamond"
    Pentagon = "Pentagon"
    Rectangle = "Rectangle"
    Octagon = "Octagon"
    Ellipse = "Ellipse"
    Triangle = "Triangle"
    Semicircle = "Semicircle"
    Square = "Square"
    Geese = "Geese"
    Farmhouse = "Farmhouse"
    Tractor = "Tractor"
    Horse = "Horse"
    Cow = "Cow"
    Doghouse = "Doghouse"
    Sheep = "Sheep"
    Cat = "Cat"
    Goat = "Goat"

oneObject = {
    1: [Shapes.Goat],
    2: [Shapes.Goat],
    3: [Shapes.Goat],
    4: [Shapes.Goat],
    5: [Shapes.Horse],
    6: [Shapes.Horse],
    7: [Shapes.Horse],
    8: [Shapes.Horse],
    9: [Shapes.Horse],
    10: [Shapes.Horse],
    11: [Shapes.Horse],
    12: [Shapes.Horse],
    13: [Shapes.Cow],
    14: [Shapes.Cow],
    15: [Shapes.Cow],
    16: [Shapes.Cow],
    17: [Shapes.Circle],
    18: [Shapes.Circle],
    19: [Shapes.Circle],
    20: [Shapes.Circle],
    21: [Shapes.Farmhouse],
    22: [Shapes.Farmhouse],
    23: [Shapes.Farmhouse],
    24: [Shapes.Farmhouse],
    25: [Shapes.Pentagon],
    26: [Shapes.Pentagon],
    27: [Shapes.Pentagon],
    28: [Shapes.Square],
    29: [Shapes.Square],
    30: [Shapes.Square],
    31: [Shapes.Rectangle],
    32: [Shapes.Rectangle],
    33: [Shapes.Rectangle],
    34: [Shapes.Rectangle],
    35: [Shapes.Ellipse],
    36: [Shapes.Ellipse],
    37: [Shapes.Ellipse],
    38: [Shapes.Ellipse],
    39: [Shapes.Semicircle],
    40: [Shapes.Semicircle],
    41: [Shapes.Semicircle],
    42: [Shapes.Semicircle],
    43: [Shapes.Tractor],
    44: [Shapes.Tractor],
    45: [Shapes.Tractor],
    46: [Shapes.Tractor],
    47: [Shapes.Geese],
    48: [Shapes.Geese],
    49: [Shapes.Geese],
    50: [Shapes.Geese],
    51: [Shapes.Triangle],
    52: [Shapes.Triangle],
    53: [Shapes.Triangle],
    54: [Shapes.Triangle],
    55: [Shapes.Sheep],
    56: [Shapes.Sheep],
    57: [Shapes.Sheep],
    58: [Shapes.Sheep],
    59: [Shapes.Diamond],
    60: [Shapes.Diamond],
    61: [Shapes.Diamond],
    62: [Shapes.Diamond],
    63: [Shapes.Cat],
    64: [Shapes.Cat],
    65: [Shapes.Cat],
    66: [Shapes.Cat],
    67: [Shapes.Cat],
    68: [Shapes.Doghouse],
    69: [Shapes.Doghouse],
    70: [Shapes.Doghouse],
    71: [Shapes.Doghouse],
    72: [Shapes.Octagon],
    73: [Shapes.Octagon],
    74: [Shapes.Octagon],
    75: [Shapes.Octagon],
}

# From top left to top right, bottom left to bottom right
sixObjects = {
    1: [Shapes.Sheep, Shapes.Farmhouse, Shapes.Goat, Shapes.Geese, Shapes.Cat, Shapes.Cow],
    2: [Shapes.Sheep, Shapes.Farmhouse, Shapes.Goat, Shapes.Geese, Shapes.Cat, Shapes.Cow],
    3: [Shapes.Sheep, Shapes.Farmhouse, Shapes.Geese, Shapes.Goat, Shapes.Semicircle, Shapes.Cow],
    4: [Shapes.Cow, Shapes.Farmhouse, Shapes.Geese, Shapes.Diamond, Shapes.Semicircle, Shapes.Sheep],
    5: [Shapes.Cow, Shapes.Farmhouse, Shapes.Geese, Shapes.Diamond, Shapes.Semicircle, Shapes.Sheep],
    6: [Shapes.Cow, Shapes.Geese, Shapes.Farmhouse, Shapes.Diamond, Shapes.Semicircle, Shapes.Octagon],
    7: [Shapes.Diamond, Shapes.Doghouse, Shapes.Farmhouse, Shapes.Cow, Shapes.Semicircle, Shapes.Octagon],
    8: [Shapes.Diamond, Shapes.Doghouse, Shapes.Farmhouse, Shapes.Rectangle, Shapes.Semicircle, Shapes.Octagon],
    9: [Shapes.Rectangle, Shapes.Doghouse, Shapes.Tractor, Shapes.Diamond, Shapes.Semicircle, Shapes.Octagon],
    10: [Shapes.Rectangle, Shapes.Doghouse, Shapes.Tractor, Shapes.Diamond, Shapes.Pentagon, Shapes.Octagon],
    11: [Shapes.Rectangle, Shapes.Doghouse, Shapes.Tractor, Shapes.Pentagon, Shapes.Circle, Shapes.Octagon],
    12: [Shapes.Rectangle, Shapes.Doghouse, Shapes.Tractor, Shapes.Pentagon, Shapes.Circle, Shapes.Triangle],
    13: [Shapes.Rectangle, Shapes.Ellipse, Shapes.Tractor, Shapes.Pentagon, Shapes.Circle, Shapes.Triangle],
    14: [Shapes.Ellipse, Shapes.Rectangle, Shapes.Tractor, Shapes.Pentagon, Shapes.Circle, Shapes.Triangle],
    15: [Shapes.Square, Shapes.Rectangle, Shapes.Tractor, Shapes.Pentagon, Shapes.Circle, Shapes.Triangle],
    16: [Shapes.Square, Shapes.Rectangle, Shapes.Tractor, Shapes.Pentagon, Shapes.Circle, Shapes.Triangle],
    17: [Shapes.Tractor, Shapes.Rectangle, Shapes.Square, Shapes.Pentagon, Shapes.Circle, Shapes.Triangle],
    18: [Shapes.Tractor, Shapes.Rectangle, Shapes.Square, Shapes.Pentagon, Shapes.Circle, Shapes.Triangle],
    19: [Shapes.Tractor, Shapes.Pentagon, Shapes.Square, Shapes.Rectangle, Shapes.Circle, Shapes.Triangle],
    20: [Shapes.Pentagon, Shapes.Tractor, Shapes.Square, Shapes.Rectangle, Shapes.Circle, Shapes.Triangle],
    21: [Shapes.Pentagon, Shapes.Tractor, Shapes.Square, Shapes.Rectangle, Shapes.Circle, Shapes.Triangle],
    22: [Shapes.Pentagon, Shapes.Ellipse, Shapes.Square, Shapes.Rectangle, Shapes.Circle, Shapes.Triangle],
    23: [Shapes.Pentagon, Shapes.Ellipse, Shapes.Square, Shapes.Rectangle, Shapes.Doghouse, Shapes.Triangle],
    24: [Shapes.Pentagon, Shapes.Ellipse, Shapes.Square, Shapes.Doghouse, Shapes.Rectangle, Shapes.Triangle],
    25: [Shapes.Pentagon, Shapes.Semicircle, Shapes.Square, Shapes.Doghouse, Shapes.Rectangle, Shapes.Triangle],
    26: [Shapes.Pentagon, Shapes.Octagon, Shapes.Square, Shapes.Doghouse, Shapes.Rectangle, Shapes.Triangle],
    27: [Shapes.Pentagon, Shapes.Octagon, Shapes.Square, Shapes.Doghouse, Shapes.Rectangle, Shapes.Diamond],
    28: [Shapes.Pentagon, Shapes.Octagon, Shapes.Square, Shapes.Doghouse, Shapes.Goat, Shapes.Diamond],
    29: [Shapes.Pentagon, Shapes.Cow, Shapes.Square, Shapes.Doghouse, Shapes.Goat, Shapes.Diamond],
    30: [Shapes.Pentagon, Shapes.Cow, Shapes.Square, Shapes.Geese, Shapes.Goat, Shapes.Diamond],
    31: [Shapes.Pentagon, Shapes.Cow, Shapes.Square, Shapes.Geese, Shapes.Goat, Shapes.Farmhouse],
    32: [Shapes.Pentagon, Shapes.Cow, Shapes.Square, Shapes.Geese, Shapes.Goat, Shapes.Farmhouse],
    33: [Shapes.Pentagon, Shapes.Cow, Shapes.Square, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse],
    34: [Shapes.Pentagon, Shapes.Cow, Shapes.Horse, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse],
    35: [Shapes.Pentagon, Shapes.Cow, Shapes.Horse, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse],
    36: [Shapes.Pentagon, Shapes.Cow, Shapes.Horse, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse],
    37: [Shapes.Sheep, Shapes.Cow, Shapes.Horse, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse],
    38: [Shapes.Sheep, Shapes.Cow, Shapes.Horse, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse],
    39: [Shapes.Sheep, Shapes.Cow, Shapes.Horse, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse],
    40: [Shapes.Sheep, Shapes.Cow, Shapes.Horse, Shapes.Cat, Shapes.Goat, Shapes.Farmhouse]
}

def find_contours(image):
    """
        Find the contours of an image from its mask. It uses functions such as blurring, eliminating noise and combining contours to find the correct contours.
        parameters:
            image: a masked image to find contours in
    """
    # try to eliminate noise
    thresh_gray = cv2.GaussianBlur(image, (9, 9), 0)
    thresh_gray = cv2.dilate(thresh_gray, None, iterations=2)
    thresh_gray = cv2.erode(thresh_gray, None, iterations=2)

    # find contours
    contours, _ = cv2.findContours(thresh_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # combine contours: https://stackoverflow.com/questions/60259169/how-to-group-nearby-contours-in-opencv-python-zebra-crossing-detection 

    # Erase small contours, and contours which small aspect ratio (close to a square)
    for c in contours:
        area = cv2.contourArea(c)

        # Fill very small contours with zero (erase small contours).
        if area < 10:
            cv2.fillPoly(thresh_gray, pts=[c], color=0)
            continue

    # Use "close" morphological operation to close the gaps between contours
    # https://stackoverflow.com/questions/18339988/implementing-imcloseim-se-in-opencv
    # unfortunately this is not possible for inference, since the function is very slow on the Pi, but is necessary here to get decent shapes.
    # Though, better calibration of HSV filters could do the same.
    thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (51,51)))

    # Find contours in thresh_gray after closing the gaps
    contours, _ = cv2.findContours(thresh_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    result_contours = list()
    result_centers = list()

    # only keep contours that are large enough
    for contour in contours:
        if cv2.contourArea(contour) < 10000:
            continue
        result_contours.append(contour)

        # get the centers of the contours
        moments = cv2.moments(contour)
        result_centers.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
    

    return result_contours, result_centers

def get_HSV_mask(image):
    """
        Get a mask of the image that only keeps the pixels that lay in the predetermined bounds
        parameters:
            image: the image to create a mask for
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # minimum saturation is 40
    masked_image = cv2.inRange(hsv_image, (0,40,0), (255,255,255)) # CHANGE ACCORDINGLY
    return masked_image

def gamma_correction(image, gamma):
    """
        Gamma correction function to brighten/darken the image.
        Parameters:
            image: the image to brighten / darken
            gamma: the gamma value, <1 means brighten the image, >1 means darken the image
    """
    look_up_table = np.empty((1,256), np.uint8)
    for i in range(256):
        look_up_table[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    result_image = cv2.LUT(image, look_up_table)
    return result_image

def contour_image(image, contours):
    """
        Get white and black contour images for each contour. 
        parameters:
            image: the original image where the contours originate from
            contours: the contours of the objects
    """
    gray_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    cv2.drawContours(gray_image, contours, -1, (255), 3)
    
    contour_images = list()

    for index in range(len(contours)):
        contour = contours[index]
        rectangle = cv2.boundingRect(contour)
        x,y,w,h = rectangle
        # only get the part of the image which contains the contour we are after
        cropped_image = gray_image[y: y+h, x: x+w]
        dh = 800
        dw = 800
        # pad the image to an 800x800 size, done twice to avoid some inexplicable bugs.
        result_image = cv2.copyMakeBorder(cropped_image, (dh-h)//2, dh-h-(dh-h)//2, (dw-w)//2, dw-w-(dw-w)//2, cv2.BORDER_ISOLATED, value=(0,0,0))
        heigth, width = result_image.shape
        if heigth != 800 or width != 800:
            result_image = cv2.copyMakeBorder(result_image, (dh-heigth)//2, dh-heigth-(dh-heigth)//2, (dw-width)//2, dw-width-(dw-width)//2, cv2.BORDER_ISOLATED, value=(0,0,0))
        contour_images.append(result_image)
    return contour_images

def writeImage(image, object, index, prefix = "", affix = ""):
    """
        Write image to the right folder with specified file name
    """
    string = "processed-dataset/" + object  + "/" + prefix + str(index) + "_" + object + affix + ".jpeg"
    cv2.imwrite(string, image)


def handle_oneObject(image, objects, index):
    gamma = 0.55

    for i in range(3):
        copy = image.copy()
        # preprocess image
        preprocessed_image = gamma_correction(copy, gamma + i*0.05)

        # get HSV image
        masked_image = get_HSV_mask(preprocessed_image)
        
        # find contours
        contours, centers = find_contours(masked_image)

        height, width, channels = image.shape
        height = height//2
        width = width//2
        
        # find center contour
        contours = closest_contour([width, height], contours, centers)
       
        if len(contours) != 1:
            print("oneObject_" + str(index) + " failed!")
            return

        images = contour_image(copy, contours)
        contour_img = images[0]
        object = objects[0]
        for j in range(3):
            scaled_image = scale_image(contour_img.copy(), 0.5+j*.25)
            for k in range(3):
                rotated_image = rotate_image(scaled_image.copy(), 15*k)
                writeImage(rotated_image, object.value, index, "oneObject_", "_G_" + str(gamma + 0.05*i) + "_R_" + str(k*15) + "_S_" + str(0.5+0.25*j))

def scale_image(image, scale):
    """
        Scale image while keeping its dimensions (zo zooming out)
        parameters:
            image: image to scale
            scale: scalar to zoom out (<1)
    """
    # scale image by the scalar, then pad to 800x800
    h, w = image.shape
    h = int(h*scale)
    w = int(w*scale)
    dh, dw = 800, 800
    small_image = cv2.resize(image, dsize=(w, h),interpolation=cv2.INTER_AREA)
    result_image = cv2.copyMakeBorder(small_image, (dh-h)//2, (dh-h)//2, (dw-w)//2, (dw-w)//2, cv2.BORDER_ISOLATED, value=(0,0,0))
    return result_image

def rotate_image(image, angle):
    """
        Rotate image while keeping its dimensions
        parameters:
            image: image to rotate
            angle: angle to rotate
    """
    rotated_image = ndimage.rotate(image, angle, reshape=True)
    height, width = rotated_image.shape
    scaled_image = scale_image(rotated_image, 800/height)
    return scaled_image

def closest_contour(center, contours, centers):
    """
        Find closest contour to the given center
    """
    width = center[0]
    height = center[1]
    minimum = 1000000
    closest_contour = None
    for index in range(min(len(contours), len(centers))):
        if (height-centers[index][1])**2 + (width-centers[index][0])**2 < minimum:
            minimum = (height-centers[index][1])**2 + (width-centers[index][0])**2
            closest_contour = contours[index]
    return [closest_contour]

def create_folder_structure():
    """
        Create folder structure for processed data
    """
    os.mkdir("processed-dataset")
    for shape in Shapes:
        os.mkdir("processed-dataset/" + shape.value)

def main():
    try:
        create_folder_structure()
    except FileExistsError:
        pass
    for key in oneObject.keys():
        image = cv2.imread("dataset/oneObject/oneObject_" + str(key) + ".jpeg")
        handle_oneObject(image, oneObject[key], key)

if __name__ == "__main__":
    main()
