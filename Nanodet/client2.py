#!/usr/bin/python
# coding: utf-8
import math
import socket
import rospy
import threading
import time 
from std_msgs.msg import Float32
from geometry_msgs.msg import PoseStamped

global target_corner_msg
global t2
global flag  

def callback(data):
    global t2
    global flag
    global target_corner_msg
    target_corner_msg = PoseStamped()
    target_corner_msg.header.stamp = rospy.Time.now() 
    target_corner_msg.pose.position.y = data.data
    if(flag == True):
        flag = False
        t2 = threading.Thread(target=tcpip)
        t2.start()

def client():
    global flag
    flag = True
    rospy.init_node('client', anonymous=True)   
    rospy.Subscriber("trans", Float32, callback)
    rospy.spin()


def tcpip():
    yolo_target_pub = rospy.Publisher('yolo_target_corner', PoseStamped, queue_size=1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接服务端
    print ('connect state: ', s.connect_ex(('127.0.0.1', 8000)))
    while True:
        receive_msg = s.recv(39).decode()
        #print(len(receive_msg))
        msg = receive_msg.split(',')
        if msg[0] == '1':
            """ QuaternionStamped.x, y, z, w = xmin, ymin, xmax, ymax,   x = time, y= distance """
            cx = 317.657
            cy = 234.635
            f = 610.5250244140625
            xmin = float(msg[1])
            ymin = float(msg[2])
            xmax = float(msg[3])
            ymax = float(msg[4])
            px = (xmin + xmax)/2
            deltax = px-cx
            py = (ymin + ymax)/2
            deltay = py-cy
            dis = target_corner_msg.pose.position.y
            
            disz = dis/math.sqrt((abs(deltax)/f)*(abs(deltax)/f)+(abs(deltay)/f)*(abs(deltay)/f)+1)

            disx = disz*deltax/f
            disy = disz*deltay/f

            target_corner_msg.pose.orientation.x = disx*100
            target_corner_msg.pose.orientation.y = disy*100
            target_corner_msg.pose.orientation.z = disz*100
            target_corner_msg.pose.position.x = float(msg[5]) #time
            #print(time.time()-target_corner_msg.pose.position.x)
        # else:
        #    # print (" target not found ... ")
        #     target_corner_msg.pose.orientation.x = 0
        #     target_corner_msg.pose.orientation.y = 0
        #     target_corner_msg.pose.orientation.z = 0
        #     target_corner_msg.pose.orientation.w = 0
        #     target_corner_msg.pose.position.x = -1

            yolo_target_pub.publish(target_corner_msg)


if __name__ == "__main__":
    client()
