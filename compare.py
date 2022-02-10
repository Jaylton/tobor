import numpy as np
import cv2


def compare(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convertendo imagem
    gray[gray > 150] = 255  # Acima de 150 é declarado com pixel branco
    gray[gray < 150] = 0  # Abaixo de 150 é declarado com pixel preto

    # Dividindo entre esquerda e direita
    left = gray[:, 0:16]
    right = gray[:, 16:32]
    top = gray[0:16, :]
    bottom = gray[16:32, :]

    left_pixels = 512 - cv2.countNonZero(left)  # Contando a quantidade de zeros
    right_pixels = 512 - cv2.countNonZero(right)  # Contando a quantidade de zeros
    top_pixels = 512 - cv2.countNonZero(top)  # Contando a quantidade de zeros
    bottom_pixels = 512 - cv2.countNonZero(bottom)  # Contando a quantidade de zeros
    return gray, left_pixels, right_pixels, 1024 - cv2.countNonZero(gray), top_pixels, bottom_pixels


def sub(left_pixels, right_pixels):
    # Obtendo o erro com base no valor de referência
    if left_pixels > right_pixels:
        return -(1 - right_pixels/left_pixels)
    elif right_pixels > left_pixels:
        return 1 - left_pixels/right_pixels


def angle(error):
    mod = abs(error)
    teta = 45*mod
    if error < 0:
        return -teta
    else:
        return teta


def velocity(teta):
    rads = np.deg2rad(teta)
    v = 0.2
    l = 0.105*2
    r = 0.062500/2
    wr = ((2*v)-(rads*l))/(2*r)
    wl = ((2*v)+(rads*l))/(2*r)
    return wr, wl
