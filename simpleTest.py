# coding=utf-8
# Insert in a script in Coppelia
# simRemoteApi.start(19999)
try:
    import sim
except:
    print('--------------------------------------------------------------')
    print('"sim.py" could not be imported. This means very probably that')
    print('either "sim.py" or the remoteApi library could not be found.')
    print('Make sure both are in the same folder as this file,')
    print('or appropriately adjust the file "sim.py"')
    print('--------------------------------------------------------------')
    print('')

import time
import cv2
import numpy as np
import detect_contours
import compare
import pandas as pd

print('Program started')
sim.simxFinish(-1)  # just in case, close all opened connections
clientID = sim.simxStart('127.0.0.1', 19998, True, True, 5000, 5)
robotname = 'lumibot'
targetname = 'Target1'
if clientID != -1:
    sim.simxStartSimulation(clientID, sim.simx_opmode_oneshot_wait)
    print('Connected to remote API server')
    sim.simxAddStatusbarMessage(clientID, 'Funcionando...', sim.simx_opmode_oneshot_wait)
    time.sleep(0.02)

    # Coletar handles
    erro, motorRight = sim.simxGetObjectHandle(clientID, "MotorDireito", sim.simx_opmode_oneshot_wait)
    erro, motorLeft = sim.simxGetObjectHandle(clientID, "MotorEsquerdo", sim.simx_opmode_oneshot_wait)
    time.sleep(0.11)

    sim.simxSetJointTargetVelocity(clientID, motorLeft, 1, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(clientID, motorRight, 1, sim.simx_opmode_oneshot)

    time.sleep(0.1)
    erro, robot = sim.simxGetObjectHandle(clientID, "RodaBoba", sim.simx_opmode_oneshot_wait)
    errorCode, (position_x, position_y, position_z) = sim.simxGetObjectPosition(clientID, robot, -1, sim.simx_opmode_streaming)

    errorCode, visionSensorHandle = sim.simxGetObjectHandle(clientID, 'Vision_sensor', sim.simx_opmode_oneshot_wait)
    errprCode, resolution, image = sim.simxGetVisionSensorImage(clientID, visionSensorHandle, 0, sim.simx_opmode_streaming)
    i = 0
    im = 0
    cumError = 0
    sumError = 0
    last_time = time.time()
    last_error = 0
    last_teta = 0
    r = 0
    l = 0
    df_error = pd.DataFrame(columns=['error', 'position_x', 'position_y', 'time'])
    print('Start')
    while True:
        i += 1
        time.sleep(0.005)

        errprCode, resolution, image = sim.simxGetVisionSensorImage(clientID, visionSensorHandle, 0, sim.simx_opmode_buffer)
        if len(image) > 0:
            sensorImage = []
            sensorImage = np.array(image, dtype=np.uint8)
            sensorImage.resize([resolution[0], resolution[1], 3])
            sensorImage = cv2.cvtColor(sensorImage, cv2.COLOR_BGR2GRAY)
            contours, img, canvas = detect_contours.detect_contours(sensorImage)
            if(contours and len(contours) > 0):
                time_now = time.time()
                gray, left_pixels, right_pixels, total, top_pixels, bottom_pixels = compare.compare(canvas)
                saida = compare.sub(left_pixels, right_pixels)
                dt = time_now - last_time
                errorCode, (position_x, position_y, position_z) = sim.simxGetObjectPosition(clientID, robot, -1, sim.simx_opmode_buffer)
                try:
                    df_error = df_error.append({'error': saida, 'position_x': position_x, 'position_y': position_y, 'time': time_now}, ignore_index=True)
                    df_error.to_csv(r'erro.csv', index=False)
                except:
                    print('a')
                if dt == 0:
                    dt = 1
                if((saida or saida == 0) and (last_error or last_error == 0)):
                    error = saida
                    d_error = (error - last_error)/dt
                    if (d_error == 0):
                        continue
                    im += 1
                    cv2.imwrite('images/'+str(im)+'.jpg', gray)
                    print('________________________________')
                    print(im)
                    print(left_pixels, right_pixels)
                    print('error = {} '.format(error))
                    sumError += abs(error)
                    cumError += error*dt

                    tolerance = 0

                    if(not (left_pixels > (right_pixels - tolerance) and left_pixels < (right_pixels + tolerance))):

                        kp = 1.5
                        ki = 2
                        kd = 1.5
                        # print('---')
                        # print('error*kp = {} '.format(up))
                        # print('ki*cumError = {} '.format(ui))
                        # print('kd*d_error = {} '.format(ud))

                        # kp = 0.3
                        # if(abs(error) > 0.50):
                        #     kp = 0.20
                        # if(total < 1024*0.2):
                        #     kp = 0.05

                        teta = compare.angle(error)  # Conversor
                        u = teta*kp
                        print('u = {} '.format(u))
                        wr, wl = compare.velocity(teta)
                        # wr = kp*wr
                        # wl = kp*wl

                        # if left_pixels < right_pixels*0.2:
                        #     wr = 0
                        # elif right_pixels < left_pixels*0.2:
                        #     wl = 0

                        # if error > 0 and total < 1024*0.2:
                        #     wr = 0
                        # elif total < 1024*0.2:
                        #     wl = 0
                        # print('total = {} '.format(total))
                        print('wr = {} '.format(wr))
                        print('wl = {} '.format(wl))

                        sim.simxSetJointTargetVelocity(clientID, motorLeft, wl, sim.simx_opmode_oneshot)
                        sim.simxSetJointTargetVelocity(clientID, motorRight, wr, sim.simx_opmode_oneshot)
                    else:
                        print('move on')
                        sim.simxSetJointTargetVelocity(clientID, motorLeft, 6, sim.simx_opmode_oneshot)
                        sim.simxSetJointTargetVelocity(clientID, motorRight, 6, sim.simx_opmode_oneshot)
                    last_error = error
                    last_time = time_now
            else:
                if im > 0:
                    print('-'*50)
                    print(im)
                    print('r: {}'.format(r))
                    print('l: {}'.format(l))
                    print('Mean error: {}'.format(sumError / im))
                    df_error.to_csv(r'erro.csv', index=False)
                    sim.simxStopSimulation(clientID, sim.simx_opmode_oneshot)
                    break

    sim.simxStopSimulation(clientID, sim.simx_opmode_oneshot)
    sim.simxFinish(clientID)
else:
    print('Failed connecting to remote API server')
print('Program ended')


'''
--------------
kp = 5
ki = 2.5
kd = 0.005
tempo = 7:14s
--------------
kp = 7
ki = 2.5
kd = 0.005
tempo = 6:40s
--------------
kp = 7
ki = 3.5
kd = 0.005
tempo = 6:35s
--------------
kp = 10
ki = 3.5
kd = 0.005
tempo = 6:19s
--------------
kp = 15
ki = 3.5
kd = 0.005
tempo = 6:11s
--------------
kp = 35
ki = 3.5
kd = 0.005
tempo = 5:36s
--------------







------------
941

'''

# print(canvas)
# print(contours)
# cv2.imwrite("result.png", canvas)
# cv2.imwrite('images/img_'+str(im)+'.jpg', canvas)