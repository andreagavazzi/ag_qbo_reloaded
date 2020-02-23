#!/usr/bin/env python

import roslib
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import imutils

def init():

    rospy.init_node('color_tracker', anonymous=True)

    # Create the window
    cv2.namedWindow('OpenCV', 0)

    """ Create the cv_bridge object """
    global bridge
    global coord_pub
    bridge = CvBridge()

    """ Subscribe to the raw camera image topic and publish the coordinates of the center"""
    image_sub = rospy.Subscriber("/camera/color/image_raw", Image, callback)
    coord_pub = rospy.Publisher('coords', String, queue_size=10)

def callback(data):
    colorLower = (73, 225, 73)
    colorUpper = (133, 285, 193)
    try:
        """ Convert the raw image to OpenCV format """
        cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
        frame = imutils.resize(cv_image, width=600)
        blurred = cv2.GaussianBlur(cv_image, (13, 13), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 0, 255), 2)
                cv2.circle(frame, center, 3, (0, 0, 255))
                coord = str(int(x)) + ',' + str(int(y))
                cv2.putText(frame, coord, (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

                coord_pub.publish(coord)

    except CvBridgeError, e:
        print e
    
    # Mostra il video
    cv2.imshow('OpenCV', frame)
    # Mostra la maschera
    #cv2.imshow('OpenCV1', mask) 

    cv2.waitKey(3)


def main():
      try:
        rospy.spin()
      except KeyboardInterrupt:
        print "Shutting down vison node."
      cv2.destroyAllWindows()

if __name__ == '__main__':
    init()
    main()
