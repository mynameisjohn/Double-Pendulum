# 
# 
# File: batUtil.py
#
# Description: A script that generates a graphical user interface designed for
# easy interaction with a scale model of the Tadarida Brasiliensis bat. The GUI allows
# for posing of the model at 18 specific keyframes during its wing cycle, and also allows
# for rendering of both the entire cycle and individual frames. 
# 
# Author: John Joseph
#

import maya.cmds as cmds
import math

#solve for the angular accelerations ddTh1 and ddTh2 based on the angles and velocities at this frame
def ddTh1(th1,th2,dTh1,dTh2):
	return -(G*((2.0*M1+M2)*math.sin(th1)+M2*math.sin(th1-2.0*th2))+L1*M2*math.sin(2.0*(th1-th2))*(dTh1**2)+2.0*L2*M2*math.sin(th1-th2)*(dTh2**2)) / (2.0*L1*(M1+M2-M2*(math.cos(th1-th2))**2))
	
def ddTh2(th1,th2,dTh1,dTh2):
	return (math.sin(th1-th2)*(G*(M1+M2)*math.cos(th1)+L1*(M1+M2)*(dTh1**2)+L2*M2*math.cos(th1-th2)*(dTh2**2))) / (L2*(M1+M2-M2*(math.cos(th1-th2)**2)))

#Advance x0 by v*dt via Euler Method
def eulerAdvance(x0, v, dt):
  return x0 + dt * v

#Numerically solve equation via RK4
def solveRK(data, dt):
	a1=data[0]
	x1=data[1]
	b1=data[2]
	y1=data[3]
	c1=ddTh1(a1,x1,b1,y1)
	z1=ddTh2(a1,x1,b1,y1)
	
	a2=eulerAdvance(a1,b1,(dt/2.0))
	x2=eulerAdvance(x1,y1,(dt/2.0))
	b2=eulerAdvance(b1,c1,(dt/2.0))
	y2=eulerAdvance(y1,z1,(dt/2.0))
	c2=ddTh1(a2,x2,b2,y2)
	z2=ddTh2(a2,x2,b2,y2)
	
	a3=eulerAdvance(a1,b2,(dt/2.0))
	x3=eulerAdvance(x1,y2,(dt/2.0))
	b3=eulerAdvance(b1,c2,(dt/2.0))
	y3=eulerAdvance(y1,z2,(dt/2.0))
	c3=ddTh1(a3,x3,b3,y3)
	z3=ddTh2(a3,x3,b3,y3)
	
	a4=eulerAdvance(a1,b3,dt)
	x4=eulerAdvance(x1,y3,dt)
	b4=eulerAdvance(b1,c3,dt)
	y4=eulerAdvance(y1,z3,dt)
	c4=ddTh1(a4,x4,b4,y4)
	z4=ddTh2(a4,x4,b4,y4)
	
	s=b1+2.0*b2+2.0*b3+b4
	data[0]=eulerAdvance(a1,s,dt/6.0)
	
	s=y1+2.0*y2+2.0*y3+y4
	data[1]=eulerAdvance(x1,s,dt/6.0)
	
	s=c1+2.0*c2+2.0*c3+c4
	data[2]=eulerAdvance(b1,s,dt/6.0)
	
	s=z1+2.0*z2+2.0*z3+z4
	data[3]=eulerAdvance(y1,s,dt/6.0)

	return

#define the physical quantities for mass, length, and gravity
M1=1.0
M2=1.0
L1=1.0
L2=1.0
G=-9.8

#tuple representing 4 state variables: th1, th2, dTh1, dTh2
data = []
#define the initial state of our system (initial angles th1 th2, and initial angular velocities dTh1 and dTh2)
data.append(1.57)
data.append(1.57/3.0)
data.append(1.0)
data.append(-1.0)
	
#define our timestep DT as well as a variable to keep track of current time t
DT=0.04
t=0.0

#variables used when dealing with frames (tMax_f is in seconds)
fps=60
tMax_f=60
updateRate=2
frameCount=fps*tMax_f/updateRate
tMax=float(frameCount)*DT
currentFrame=1

#begin our simulation
while (t<tMax):
	#at every iteration, move to the current frame and set keyframes for both the arms
	cmds.currentTime(currentFrame)
	#we convert our angle in radians to degrees, and subtract 180 degrees to fit into Maya's world
	cmds.setAttr("doublePendulum|top.rotateX",data[0]*180.0/math.pi-180.0)
	#note that, because of the way Maya organizes objects, we must subtract the first rotation from the second
	cmds.setAttr("bottom.rotateX",data[1]*180.0/math.pi-180.0 - (data[0]*180.0/math.pi-180.0))
	#after rotating appropriately, set the keys
	cmds.setKeyframe("doublePendulum|top.rx")
	cmds.setKeyframe("bottom.rx")
	
	solveRK(data,DT)
	
	#update the current frame and current time
	currentFrame = currentFrame+updateRate
	t = t + DT

print "Done"