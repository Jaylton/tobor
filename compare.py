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
    # cv2.imwrite('images/novo.jpg', gray)

    # cv2.imwrite('images/right.jpg', right)
    # cv2.imwrite('images/left.jpg', left)
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


# img = cv2.imread('images/881.jpg')
# gray, left_pixels, right_pixels, total, top_pixels, bottom_pixels = compare(img)
# if(top_pixels < bottom_pixels*0.1 or bottom_pixels < top_pixels*0.1):
#     print(total, top_pixels, bottom_pixels, bottom_pixels < top_pixels*0.15)
# error = sub(left_pixels, right_pixels)
# teta = angle(error)
# wr, wl = velocity(teta)
# print(wr, wl)

# img = cv2.imread('images/10.jpg')
# gray, left_pixels, right_pixels = compare(img)
# error = sub(left_pixels, right_pixels)
# teta = angle(error)
# wr, wl = velocity(teta)
# print(wr, wl)

# img = cv2.imread('images/6.jpg')
# gray, left_pixels, right_pixels = compare(img)
# error = sub(left_pixels, right_pixels)
# teta = angle(error)
# wr, wl = velocity(teta)
# print(wr, wl)


# ON-OFF
# def sub(left_pixels, right_pixels):
#     # Obtendo o erro com base no valor de referência
#     if left_pixels > right_pixels:
#         return -(1 - right_pixels/left_pixels)
#     elif right_pixels > left_pixels:
#         return 1 - left_pixels/right_pixels
