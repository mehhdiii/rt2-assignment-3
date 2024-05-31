from __future__ import print_function

import time
import pprint
from sr.robot import *
import math
from consts import *

xr, yr = (0, 0)
theta = math.pi/4
linearSpeed = 2
angularSpeed = 1.2

def updateRobotLocalization(t, linearSpeed, angularSpeed):
    global xr, yr, theta
    
    xr+=linearSpeed*t*math.cos(theta)
    yr+=linearSpeed*t*math.sin(theta)
    theta = math.atan(yr/(xr+0.0001))

# def moveToGoal(R, xgoal, ygoal):
#     global xr, yr
#     requiredTheta = math.atan2((ygoal-yr), (xgoal-xr))
#     print('requiredTheta', requiredTheta)
#     print(xr, yr)
#     if requiredTheta > 0.5:
#         spinLeft(R, 0.1)

#         print('right')
#         # moveStraight(R, 0.1)
#     elif requiredTheta < -0.5:
#         print('left')
#         spinRight(R, 0.1)

#         # moveStraight(R, 0.1)  
#     while True:
#         requiredD = math.sqrt((ygoal-yr)**2 + (xgoal - xr)**2)
#         print(requiredD, requiredTheta)
#         if requiredD < 2:
#             break
#         moveStraight(R, 0.01)  
        
        

def moveStraight(R, t):
    '''Moves the robot in a straight line for t seconds in forward direction'''
    R.motors[0].m0.power = 50
    R.motors[0].m1.power = 50
    time.sleep(t)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
    updateRobotLocalization(t, linearSpeed, 0)


def moveBack(R, t):
    '''Moves the robot in a straight line for t seconds in backwards direction'''
    R.motors[0].m0.power = -50
    R.motors[0].m1.power = -50
    time.sleep(t)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0 
    updateRobotLocalization(t, -linearSpeed, 0)


def spinRight(R, t):
    '''Spins the robot for t seconds in clockwise direction'''
    R.motors[0].m0.power = 50
    R.motors[0].m1.power = -50
    time.sleep(t)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
    updateRobotLocalization(t, 0, angularSpeed)


def spinLeft(R, t):
    '''Spins the robot for t seconds in anti-clockwise direction'''
    R.motors[0].m0.power = -50
    R.motors[0].m1.power = 50
    time.sleep(t)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
    updateRobotLocalization(t, 0, -angularSpeed)

def seeObject(R, code):
    for i in R.see():
        if i.info.code == code:
            return i

def MoveTowardsObject(R, info, movingForDrop=False):
    time_to_reach_object = time.time()

    '''Moves the robot towards the object by self-adjusting pose to grab it'''
    while True:
        print(xr, yr)
        obj = seeObject(R, info.code)
        if (obj==None):
            #if object is not seen anymore, rotate: 
            spinRight(R, 0.1)
            continue
        # print(obj.dist, obj.rot_y)
        if obj.dist < 0.4 and not movingForDrop:
            print(info, obj.info)
            break
        elif obj.dist < 0.6 and movingForDrop:
            break
        elif obj.rot_y > 5:
            spinRight(R, 0.01)
            # moveStraight(R, 0.1)
        elif obj.rot_y < -5:
            spinLeft(R, 0.01)
            # moveStraight(R, 0.1)  
        else:
            moveStraight(R, 0.01)  
    time_to_reach_object = time.time() - time_to_reach_object

    with open('measurements.txt', 'a+') as file:
        file.writelines(['time_to_reach_object: ' + str(time_to_reach_object) + '\n'])


def getClosestUnivisitedObject(visitedObjects):
    '''Returns the closest object that has not been visited yet'''
    closestObject = None
    closestObjectDistance = 100000
    print()
    print('seen objects:', [(i.dist, i.info.code) for i in R.see()])
    print()
    for i in R.see():
        if i.info not in visitedObjects and i.dist < closestObjectDistance:
            closestObject = i
            closestObjectDistance = i.dist
    print('closestObject', closestObject)
    return closestObject


def lookForNextObject(R, visitedObjects):
    time_to_look_for_object = time.time()
    while True:
        nextObject = getClosestUnivisitedObject(visitedObjects)
        if nextObject !=None: 
            time_to_look_for_object = time.time() - time_to_look_for_object
            with open('measurements.txt', 'a+') as file:
                file.writelines(['time_to_look_for_object: ' + str(time_to_look_for_object) + '\n'])
            return nextObject
        else:
            spinLeft(R, 0.1)
            continue



R = Robot()
#STEPS: 
#1. initially align the robot towards the object.
#2. move the robot towards the object while self adjusting its pose. Grab the object when it is close enough.
#3. move the robot back to the center and release the object.

#NOTES: 
#1. We hard code picking up the first object
#2. All other objects are picked up by moving the robot towards the object and self adjusting its pose.

visitedObjects = []
xgoal, ygoal = 5, 5

with open('measurements.txt', 'a+') as file:
    file.writelines(['BOXES: ' + str(TOKENS_PER_CIRCLE) + '\n'])


total_time = time.time()

while TOKENS_PER_CIRCLE != len(visitedObjects):
    obj = lookForNextObject(R, visitedObjects)
    if obj == None:
        # if no objects left, we end the simulation
        break
    MoveTowardsObject(R, obj.info)
    R.grab()

    # place the robot near the last marker:
    if (len(visitedObjects)==0):
        time.sleep(0.1)
        # moveBack(R, 1)
        # spinRight(R, 0.6)
        R.release()
        moveBack(R, 1)

        visitedObjects.append(obj.info)
    else:
        moveBack(R, 1.5)
        spinRight(R, 0.6)
        goalObject = visitedObjects[-1]
        
        MoveTowardsObject(R, visitedObjects[-1], movingForDrop=True)
        R.release()
        visitedObjects.append(obj.info)
    moveBack(R, 1)

    # print(R.see())
    # print(xr, yr)

total_time = time.time() - total_time
with open('measurements.txt', 'a+') as file:
    file.writelines(['total_time: ' + str(total_time) + '\n\n'])

# #pick and drop first object to the center
# moveStraight(R, 1.25)
# spinRight(R, 0.3)
# moveStraight(R, 1.5)
# print(R.see())
# R.grab()
# moveStraight(R, 1.3)
# spinLeft(R, 0.6)
# moveStraight(R, 2.2)
# print(R.release())
# moveBack(R, 2.3)

# # #pick and drop second object to the center
# spinRight(R, 0.7)
# MoveTowardsObject(R)
# moveBack(R, 1.2)
# spinLeft(R, 0.58)
# moveStraight(R, 2.8)
# R.release()
# moveBack(R, 2.3)

# # pick and drop third object to the center
# spinRight(R, 0.4)
# MoveTowardsObject(R)
# spinLeft(R, 0.8)
# moveStraight(R, 3)
# R.release()
# moveBack(R, 1)

# # pick and drop fourth object to the center
# spinRight(R, 0.6)
# MoveTowardsObject(R)
# spinLeft(R, 1)
# moveStraight(R, 3)
# R.release()
# moveBack(R, 1)

# # pick and drop fifth object to the center
# spinRight(R, 0.7)
# MoveTowardsObject(R)
# spinLeft(R, 1)
# moveStraight(R, 3)
# R.release()
# moveBack(R, 1)

# # pick and drop sixth object to the center
# spinRight(R, 0.6)
# MoveTowardsObject(R)
# spinLeft(R, 1)
# moveStraight(R, 3)
# R.release()
# moveBack(R, 1)