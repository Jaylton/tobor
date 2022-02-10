
import cv2
import numpy as np
import delete_files


def detect_contours(img):
    img = (255-img)

    # Obtendo thresholding entre 127 e 255 de intensidade
    ret, thresh = cv2.threshold(img, 127, 255, 0)

    # Obtendo o contorno da imagem
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if(len(contours) > 0):
        img = (255-img)

        color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        canvas = color.copy()
        img = cv2.drawContours(color, contours, -1, (0, 255, 0), 1)

        return contours, img, canvas
    else:
        return False, False, False
