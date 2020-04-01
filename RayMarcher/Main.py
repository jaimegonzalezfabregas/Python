from copy import deepcopy
import math as m1
import numpy as np
import time
from PIL import Image
from multiprocessing import Pool

import sys
sys.stdout = open("Out.txt", "w")




# ObjetName,SizeMax,posX,posY,posZ
# Sfere,Rad,posX,PosY,Posz
# Point,PosX,PosY,PosZ,I,r
# Sun,AngleX,AngleY,I
SKY = [70,70,70]#[0,160,250]
CERO = 0.000001
INF = 1000000000
maxSteps = 100
maxDistance = 1000
objects=[["Sfere",1,0,0,0],["Sfere",1,0,0,1],["Sfere",1,0,0,2]]
lights=[["Point",2,1,0,1,0.3]]


def VectorFromAngle(aX,aY):
    # assert aY >= -m1.pi/2 and aY <= m1.pi/2
    # assert aX >= -m1.pi and aX <= m1.pi
    x=m1.cos(aX)*m1.sin(aY)
    y=m1.cos(aX)*m1.cos(aY)
    z=m1.sin(aX)
    return (x,y,z)

def Ray(cx,cy,cz,V,bounces):
    Vx = V[0]
    Vy = V[1]
    Vz = V[2]
    x = cx
    y = cy
    z = cz
    dir = [Vx,Vy,Vz]
    OBJ = []
    #Chocar con objeto
    hit = False
    StepCounter = 0
    maxDistance = MAXdistance(z,y,x)
    while not hit and maxSteps > StepCounter and maxDistance > PointDistance(x,y,z,cx,cy,cz):
        d = MINdistance(x,y,z)

        x = x + dir[0]*d[0] 
        y = y + dir[1]*d[0]
        z = z + dir[2]*d[0]
        if(d[0]<CERO):
            hit = True
            OBJ = d[1]
        StepCounter = StepCounter + 1 

               

    #ir a luces

    colorB = 0

    if not hit:
        return SKY
    else:
        for lam in lights:
            V = [0,0,1]
            intensity = 0

            if(lam[0]=="Point"):
                vx = -(x-lam[1])
                vy = -(y-lam[2])
                vz = -(z-lam[3])
                l = PointDistance(0,0,0,vx,vy,vz)
                V = [vx/l,vy/l,vz/l]
                intensity = lam[4]
            
                hit = False
                ilum = False
                lx = x + vx * 0.1
                ly = y + vy * 0.1
                lz = z + vz * 0.1

                while not hit and not ilum:


                    d = MINdistanceObjLamp(lx,ly,lz,lam)

                    lx = lx + V[0]*(d+CERO)     
                    ly = ly + V[1]*(d+CERO)
                    lz = lz + V[2]*(d+CERO)

                    if d<CERO :
                        hit = True
                    elif PointDistance(lx,ly,lz,lam[1],lam[2],lam[3])<lam[5] :
                        ilum = True
                        colorB = colorB + abs(intensity * m1.cos(angle(V,NormalEsf(x,y,z,OBJ))) * 1/PointDistance(x,y,z,lam[1],lam[2],lam[3])) 
            

                    
    colorB = colorB * ((1/(StepCounter+1)/50)+1)
    r = min(250*colorB+SKY[0]*((1/(StepCounter+1)/1000)+1),250)
    g = min(250*colorB+SKY[1]*((1/(StepCounter+1)/1000)+1),250)
    b = min(250*colorB+SKY[2]*((1/(StepCounter+1)/1000)+1),250)
    return [r,g,b]

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def length(v):
    return m1.sqrt(dotproduct(v, v))

def angle(v1, v2):
    a = dotproduct(v1, v2) / (length(v1) * length(v2))
    if(a<-1):
        a = -1
    elif(a>1):
        a = 1
    return m1.acos(a)

def PointDistance(x1,y1,z1,x2,y2,z2):
    return ((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)**.5

def SfereDistance(x,y,z,cx,cy,cz,r):
    return PointDistance(x,y,z,cx,cy,cz)-r

def NormalEsf(x,y,z,OBJ):
    # Sfere,Rad,posX,PosY,Posz
    return[x-OBJ[2],y-OBJ[3],z-OBJ[4]]
    


def MINdistanceObjLamp(x,y,z,l):
    return min(PointDistance(x,y,z,l[1],l[2],l[3]),MINdistance(x,y,z)[0])
    

def MINdistance(x,y,z):
    rets = distanceList(x,y,z)
    ret = INF
    I = 0
    Index = 0
    for r in rets:
        if(r<ret): 
            I = Index
            ret = r
        Index = Index+1
    
    return [ret,objects[I]]

def MAXdistance(x,y,z):
    rets = distanceList(x,y,z)
    ret = 0

    for rindex in range(len(rets)):
        r = rets[rindex]+objects[rindex][1]*2
        if(r>ret): 
            ret = r
    
    return ret


def distanceList(x,y,z):
    rets = []
    for obj in objects:
        if(obj[0]=="Sfere"):
            rets.append(SfereDistance(x,y,z,obj[2],obj[3],obj[4],obj[1]))
        
    return rets

def render(x,y,z,multiProz,w,h):
    StartMillis = int(round(time.time() * 1000))


    PreData = [ (b,x,y,z,w,h) for b in range(h) ]


    #columnN = 0
    #for column in data:
    #    elementN = 0
    #    
    #    for element in column:
    #        Vx = -1
    #        Vy = (columnN/len(data)*sensorL)-sensorL/2
    #        Vz = (elementN/len(column)*sensorL)-sensorL/2
    #        d = PointDistance(Vx,Vy,Vz,0,0,0)
    #        data[columnN][elementN]=Ray(x,y,z,Vx/d,Vy/d,Vz/d,0)
    #        elementN = elementN+1
    #    columnN = columnN+1

    if multiProz:
        p = Pool(4)
        data = p.map(threadRay, PreData)
    else:
        data = [ threadRay(Line) for Line in PreData]



    
    EndMillis = int(round(time.time() * 1000))
    print(EndMillis-StartMillis)
    img = Image.fromarray(np.asarray(data,dtype=np.uint8), 'RGB' )

    return img
# 0 1 2 3 4 5
#(b,x,y,z,w,h)
def threadRay(d):
    w=d[4]
    h=d[5]
    antires = 1/100
    sensorW = antires * w
    sensorH = antires * h

    columnN = d[0]
    x,y,z = d[1],d[2],d[3]

    #ret = []
    
    #elementN = 0
    #for element in range(w):
    #    Vx = -1
    #    Vy = ((columnN/h)*sensorH)-(sensorH/2)
    #    Vz = ((elementN/w)*sensorW)-(sensorW/2)
    #    ret.append(Ray(x,y,z,normalice(Vx,Vy,Vz),0))
    #    elementN = elementN+1

    return [ Ray(x,y,z,normalice(-1,((columnN/h)*sensorH)-(sensorH/2),((elementN/w)*sensorW)-(sensorW/2)),0) for elementN in range(w)]

def normalice(x,y,z):
    l = PointDistance(0,0,0,x,y,z)
    return (x/l,y/l,z/l)

def main():
    aspectRatio = (16,9)
    m = 20
    img = render(2,0,0,False,aspectRatio[0]*m,aspectRatio[1]*m)
    img.save('render.png')

    img.show()

main()
