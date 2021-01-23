import rospy
from sensor_msgs.msg import Image
import cv2
import numpy as np

def callback(data):
    img = np.ndarray(shape=(data.height, data.width, 3),
	               dtype=np.uint8, buffer=data.data)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imshow('img',img_rgb)
    cv2.waitKey(1)
def listener():
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/camera/color/image_raw", Image, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
