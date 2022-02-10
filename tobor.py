
import sim
import time
import cv2
import numpy as np
import detect_contours
import compare
import pandas as pd

print('Program started')
sim.simxFinish(-1)  # just in case, close all opened connections
clientID = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)

if clientID != -1:
    sim.simxStartSimulation(clientID, sim.simx_opmode_oneshot_wait)
    print('Connected to remote API server')
    sim.simxAddStatusbarMessage(clientID, 'Funcionando...', sim.simx_opmode_oneshot_wait)
    time.sleep(0.02)

    # Coletar handles
    erro, motorLeft = sim.simxGetObjectHandle(clientID, "MotorDireito", sim.simx_opmode_oneshot_wait)
    erro, motorRight = sim.simxGetObjectHandle(clientID, "MotorEsquerdo", sim.simx_opmode_oneshot_wait)
    time.sleep(0.11)

    sim.simxSetJointTargetVelocity(clientID, motorLeft, 4.0, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(clientID, motorRight, 4.0, sim.simx_opmode_oneshot)

    time.sleep(0.1)
    erro, robot = sim.simxGetObjectHandle(clientID, "Carro", sim.simx_opmode_oneshot_wait)
    errorCode, visionSensorHandle = sim.simxGetObjectHandle(clientID, 'Vision_sensor', sim.simx_opmode_oneshot_wait)
    errprCode, resolution, image = sim.simxGetVisionSensorImage(clientID, visionSensorHandle, 0, sim.simx_opmode_streaming)

    cumError = 0
    sumError = 0
    last_time = time.time()
    last_error = 0

    print('Start')
    while True:
        errprCode, resolution, image = sim.simxGetVisionSensorImage(clientID, visionSensorHandle, 0, sim.simx_opmode_buffer)
        if len(image) > 0:
            sensorImage = []
            sensorImage = np.array(image, dtype=np.uint8)
            sensorImage.resize([resolution[0], resolution[1], 3])
            sensorImage = cv2.cvtColor(sensorImage, cv2.COLOR_BGR2GRAY)
            contours, img, canvas = detect_contours.detect_contours(sensorImage)

            if(contours and len(contours) > 0):
                time_now = time.time()
                left_pixels, right_pixels = compare.compare(canvas)  # buscando a quantidade de pixels não nulos de cada lado (esquerdo e direito)
                saida = compare.sub(left_pixels, right_pixels)  # calculando o erro com no referencial que deve ser 1

                dt = time_now - last_time  # diferencial de tempo
                if dt == 0:
                    dt = 1
                if((saida or saida == 0) and (last_error or last_error == 0)):
                    error = saida
                    d_error = error - last_error/dt  # derivada com base no último ponto
                    if (d_error == 0):
                        continue
                    cumError += error*dt  # integral

                tolerance = 50  # Tolerância da quantidade de pixels na diferencia dos lados
                if(not (left_pixels > (right_pixels - tolerance) and left_pixels < (right_pixels + tolerance))):

                    kp = 35
                    up = error*kp
                    ki = 4.5
                    ui = ki*cumError
                    kd = 0.15
                    ud = kd*d_error

                    u = up + ui + ud
                    if(u < 0):
                        # to right
                        sim.simxSetJointTargetVelocity(clientID, motorRight, abs(u), sim.simx_opmode_oneshot)
                        sim.simxSetJointTargetVelocity(clientID, motorLeft, 0, sim.simx_opmode_oneshot)
                    else:
                        # to left
                        sim.simxSetJointTargetVelocity(clientID, motorLeft, abs(u), sim.simx_opmode_oneshot)
                        sim.simxSetJointTargetVelocity(clientID, motorRight, 0, sim.simx_opmode_oneshot)
                else:
                    # move on
                    sim.simxSetJointTargetVelocity(clientID, motorLeft, 4, sim.simx_opmode_oneshot)
                    sim.simxSetJointTargetVelocity(clientID, motorRight, 4, sim.simx_opmode_oneshot)
                last_error = error
                last_time = time_now

else:
    print('Failed connecting to remote API server')
print('Program ended')
