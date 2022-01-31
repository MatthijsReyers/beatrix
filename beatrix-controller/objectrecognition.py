import cv2
from enum import Enum
import numpy as np
from tflite_runtime.interpreter import Interpreter 
import time



class RecognicedObject:

    def __init__(self, contour, center, label, confidence):
        self.contour = contour
        self.center = center
        self.label = label
        self.confidence = confidence

class Label(Enum):
    Circle = 1
    Diamond = 3
    Pentagon = 11
    Rectangle = 12
    Octagon = 10
    Ellipse = 5
    Triangle = 17
    Semicircle = 13
    Square = 15
    Geese = 7
    Farmhouse = 6 
    Tractor = 16
    Horse = 9
    Cow = 2
    Doghouse = 4
    Sheep = 14
    Cat = 0
    Goat = 8
    Unknown = 18

def gamma_correction(image, gamma):
    look_up_table = np.empty((1,256), np.uint8)
    for i in range(256):
        look_up_table[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    result_image = cv2.LUT(image, look_up_table)
    return result_image

def get_HSV_mask(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # minimum saturation is 40
    masked_image = cv2.inRange(hsv_image, (0,40,0), (255,255,255)) 
    return masked_image

def find_contours(image):
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
    thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (7,7)))

    # Find contours in thresh_gray after closing the gaps
    contours, _ = cv2.findContours(thresh_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    result_contours = list()
    result_centers = list()

    for contour in contours:
        if cv2.contourArea(contour) < 10000:
            continue
        result_contours.append(contour)


        moments = cv2.moments(contour)
        result_centers.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))

    return result_contours, result_centers

def anomaly_detection(contours, centers):

    normal_contours = list()
    normal_centers = list()
    anomolous_objects = list()

    for index in range(len(contours)):
        contour = contours[index]
        center = centers[index]
        rectangle = cv2.boundingRect(contour)
        x,y,w,h = rectangle
        if w > 800 or h > 800:
            object = RecognicedObject(contour, center, Label.Unknown, 1)
            anomolous_objects.append(object)
        else:
            normal_contours.append(contour)
            normal_centers.append(center)
    
    return normal_contours, normal_centers, anomolous_objects

def contour_image(image, contours):
    gray_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    cv2.drawContours(gray_image, contours, -1, (255), 3)
    
    contour_images = list()

    for index in range(len(contours)):
        contour = contours[index]
        rectangle = cv2.boundingRect(contour)
        x,y,w,h = rectangle
        cropped_image = gray_image[y: y+h, x: x+w]
        dh = 800
        dw = 800
        result_image = cv2.copyMakeBorder(cropped_image, (dh-h)//2, dh-h-(dh-h)//2, (dw-w)//2, dw-w-(dw-w)//2, cv2.BORDER_ISOLATED, value=(0,0,0))
        heigth, width = result_image.shape
        result_image = cv2.copyMakeBorder(result_image, (dh-heigth)//2, dh-heigth-(dh-heigth)//2, (dw-width)//2, dw-width-(dw-width)//2, cv2.BORDER_ISOLATED, value=(0,0,0))
        contour_images.append(result_image)
    
    return contour_images

def scale_images(images, scale):
    scaled_images = list()
    for image in images:
        height, width = image.shape
        scaled_image = cv2.resize(image, dsize=(int(width*scale), int(height*scale)),interpolation=cv2.INTER_AREA)
        scaled_images.append(scaled_image)
    return scaled_images

def draw_on_image(image, objects):
    for obj in objects:
        contour = obj.contour
        center = obj.center
        text = str(obj.label) + " " + str(obj.confidence)
        cv2.drawContours(image, contour, -1, (0,0,255), 3)    
        cv2.circle(image,center, 3, (0,0,255), 3)
        cv2.putText(image,text,center, 0, 1,(0,255,0),2,cv2.LINE_AA)
        
class ObjectRecognicer():
    
    def __init__(self, model_path_string):
        self.interpreter = Interpreter(model_path = model_path_string)
        self.interpreter.allocate_tensors()
        
        
    def object_recognition(self, image):
        # nothing here should influence the image
        copy_image = image.copy()

        # preprocess image
        preprocessed_image = gamma_correction(copy_image, 0.6)

        # get HSV mask
        masked_image = get_HSV_mask(preprocessed_image)

        # find contours
        contours, centers = find_contours(masked_image)

        # if contour too big (e.g. 2+ objects merged) -> Unknown label
        # separate anomolous objects
        contours, centers, objects = anomaly_detection(contours, centers)

        # get contour images
        contour_images = contour_image(copy_image, contours)

        # resize contour images to 96x96
        scaled_contour_images = scale_images(contour_images, 0.12)
        # scaled_contour_images = scale_images(contour_images, 0.20)

        # label contour images (if too low confidence also Unknown label)
        labels, confidences = self.label_images(scaled_contour_images)

        # return contours, centers, labels, confidences in a class
        for index in range(len(contours)):
            object = RecognicedObject(contours[index], centers[index], labels[index], confidences[index])
            objects.append(object)

        return objects
    
    def label_images(self, images):

        # Get input and output tensors.
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        
        labels = list()
        confidences = list()
        for image in images:
            
            # image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            c =  np.int16(image)
            c = cv2.subtract(c, 128)
            c = c.astype(np.int8)
            c = np.reshape(c, (1,96,96,1))
            # c = np.reshape(c, (1,160,160,3))
            self.interpreter.set_tensor(input_details[0]['index'], c)
            self.interpreter.invoke()

            # The function `get_tensor()` returns a copy of the tensor data.
            # Use `tensor()` in order to get a pointer to the tensor.
            output_data = self.interpreter.get_tensor(output_details[0]['index'])
            label = Label.Unknown
            confidence = 1
            for index in range(len(output_data[0])):
                if (output_data[0][index]+128)/256 > 0.3:
                    label = Label(index)
                    confidence = (output_data[0][index]+128)/256
            labels.append(label)
            confidences.append(confidence)
            print(label, confidence)

        return labels, confidences

# if __name__ == "__main__":
#     image = cv2.imread("sixObjects_22.jpeg")
#     recognicer = ObjectRecognicer("int8-model_3.lite")
#     start = time.time()
#     objects = recognicer.object_recognition(image)
#     end = time.time()
#     print("Total: ", end-start)
#     start_draw = time.time()
#     draw_on_image(image, objects)
#     end_draw = time.time()
#     print("Draw: ", end_draw - start_draw)
#     cv2.imwrite("test2.jpeg", image)