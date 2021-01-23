from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32
import rospy
from cat.msg import zzw
import matplotlib.pyplot as plt
import threading

global nanox
global nanoy
global nanoz  
global deltax
global deltay 
global deltaz
global flag

def arucocallback(data):
    #uav cordinates
    global flag
    global nanox
    global nanoy
    global nanoz 
    global deltax
    global deltay 
    global deltaz 
    deltax = data.pose.position.x-nanoz
    deltay = data.pose.position.y+nanox
    deltaz = data.pose.position.z-nanoy
    if(flag == True):
        flag = False
        t2 = threading.Thread(target=plotrealtime)
        t2.start()


def plotrealtime():
    global deltax
    global deltay 
    global deltaz 
    i = 1
    plt.ion()   # 开启一个画图的窗口
    ax=[]  # 定义一个 x 轴的空列表用来接收动态的数据
    ay=[]
    az=[]
    t=[]
    while True: 
        if(len(ax)>=51 and len(ay)>=51 and len(az)>=51 and len(t)>=51):
            px = ax[len(ax)-50:]
            py = ay[len(ay)-50:]
            pz = az[len(az)-50:]    
            pt = t[len(t)-50:]
        else:
            px = ax
            py = ay
            pz = az
            pt = t

        i = i + 0.1
        t.append(i)
        ax.append(deltax)  # 添加 i 到 x 轴的数据中
        ay.append(deltay)
        az.append(deltaz) # 添加 i 的平方到 y 轴的数据中
        plt.clf()  # 清除之前画的图
        plt.plot(pt,px,'r.-',pt,py,'g.-',pt,pz,'b.-') # 画出当前 ax 列表和 ay 列表中的值的图形

        plt.pause(0.3)  # 暂停一秒
        plt.ioff()  # 关闭画图的窗口



def nanocallback(data):
    #xyz cordinates
    global nanox
    global nanoy
    global nanoz 
    nanox = data.pose.orientation.x
    nanoy = data.pose.orientation.y
    nanoz = data.pose.orientation.z



def compare():
    rospy.init_node('compare', anonymous=True)   
    rospy.Subscriber("aruco_detect/send_data_small", zzw, arucocallback)
    rospy.Subscriber("yolo_target_corner", PoseStamped, nanocallback)
    rospy.spin()


if __name__ == "__main__":
    global flag
    flag = True
    compare()
