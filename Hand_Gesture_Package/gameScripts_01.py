# from kivy.properties import partial
# from kivy.uix.screenmanager import Screen
# from kivy.graphics.texture import Texture
# from kivy.clock import Clock
# from kivy.properties import StringProperty
# from cv2 import cv2
# from sklearn.metrics import pairwise
# import threading
# import math
# import time
# import numpy as np
#
# from Kivy_Tutorial.Result_Package.result_calculation import *
# from Kivy_Tutorial.Hand_Gesture_Package.gameMenuScript import GameMenuScreen
#
# bg = None
# game_menu_screen = GameMenuScreen()
#
#
# class GameScreen(Screen):
#     aWeight = 0.5
#     top, right, bottom, left = 10, 350, 225, 590
#     num_frames = 0
#     is_bool = False
#     human_score, app_score, num_wickets = 0, 0, 0
#
#     time_count = StringProperty()
#     human_score_text = StringProperty()
#     app_score_text = StringProperty()
#
#     def run_avg(self, image):
#         global bg
#
#         # initialize the background
#         if bg is None:
#             bg = image.copy().astype("float")
#             return
#
#         # compute weighted average, accumulate it and update the background
#         cv2.accumulateWeighted(image, bg, self.aWeight)
#
#     def segment(self, image, threshold=25):
#
#         # threshold the image to get the foreground which is the hand
#         thresholded = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)[1]
#
#         # show the thresholded image
#         cv2.imshow("Thesholded", thresholded)
#
#         # get the contours in the thresholded image
#         (cnts, _) = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#         # return None, if no contours detected
#         if len(cnts) == 0:
#             return
#         else:
#             # analyze the contours
#             print("Number of Contours found = " + str(len(cnts)))
#             cv2.drawContours(image, cnts, -1, (0, 255, 0), 3)
#
#             # based on contour area, get the maximum contour which is the hand
#             segmented = max(cnts, key=cv2.contourArea)
#             cv2.drawContours(image, segmented, -1, (0, 255, 0), 3)
#
#             return (thresholded, segmented)
#
#     def count(self, thresholded, segmented):
#         # find the convex hull of the segmented hand region
#         chull = cv2.convexHull(segmented)
#
#         # find the most extreme points in the convex hull
#         extreme_top = tuple(chull[chull[:, :, 1].argmin()][0])
#         extreme_bottom = tuple(chull[chull[:, :, 1].argmax()][0])
#         extreme_left = tuple(chull[chull[:, :, 0].argmin()][0])
#         extreme_right = tuple(chull[chull[:, :, 0].argmax()][0])
#
#         # find the center of the palm
#         cX = int((extreme_left[0] + extreme_right[0]) / 2)
#         cY = int((extreme_top[1] + extreme_bottom[1]) / 2)
#
#         # find the maximum euclidean distance between the center of the palm
#         # and the most extreme points of the convex hull
#         distance = pairwise.euclidean_distances([(cX, cY)], Y=[extreme_left, extreme_right, extreme_top, extreme_bottom])[0]
#         maximum_distance = distance[distance.argmax()]
#
#         # calculate the radius of the circle with 80% of the max euclidean distance obtained
#         radius = int(0.8 * maximum_distance)
#
#         # find the circumference of the circle
#         circumference = (2 * np.pi * radius)
#
#         # take out the circular region of interest which has
#         # the palm and the fingers
#         circular_roi = np.zeros(thresholded.shape[:2], dtype="uint8")
#
#         # draw the circular ROI
#         cv2.circle(circular_roi, (cX, cY), radius, 255, 1)
#
#         # take bit-wise AND between thresholded hand using the circular ROI as the mask
#         # which gives the cuts obtained using mask on the thresholded hand image
#         circular_roi = cv2.bitwise_and(thresholded, thresholded, mask=circular_roi)
#
#         # compute the contours in the circular ROI
#         (cnts, _) = cv2.findContours(circular_roi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#
#         # initalize the finger count
#         count = 0
#
#         # loop through the contours found
#         for c in cnts:
#             # compute the bounding box of the contour
#             (x, y, w, h) = cv2.boundingRect(c)
#
#             # increment the count of fingers only if -
#             # 1. The contour region is not the wrist (bottom area)
#             # 2. The number of points along the contour does not exceed
#             #     25% of the circumference of the circular ROI
#             if ((cY + (cY * 0.25)) > (y + h)) and ((circumference * 0.25) > c.shape[0]):
#                 count += 1
#
#         return count
#
#     def gamePlay(self):
#
#         print("gamePlay Called")
#
#         threading.Thread(target=self.doit, daemon=True).start()
#
#     def doit(self):
#         cam = cv2.VideoCapture(0)
#
#         # this code is run in a separate thread
#         self.do_vid = True  # flag to stop loop
#
#         # start processing loop
#         while (self.do_vid):
#             ret, frame = cam.read()
#
#             frame = cv2.flip(frame, 1)
#
#             # clone the frame
#             clone = frame.copy()
#
#             # get the ROI
#             roi = frame[self.top:self.bottom, self.right:self.left]
#
#             # convert the roi to grayscale and blur it
#             gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#             gray = cv2.GaussianBlur(gray, (7, 7), 0)
#
#             if self.num_frames < 30:
#                 self.run_avg(gray)
#                 if self.num_frames == 1:
#                     print("[STATUS] please wait! calibrating...")
#                 elif self.num_frames == 29:
#                     print("[STATUS] calibration successfull...")
#             else:
#                 # segment the hand region
#                 hand = self.segment(gray)
#
#                 # check whether hand region is segmented
#                 if hand is not None:
#                     # if yes, unpack the thresholded image and
#                     # segmented region
#                     (thresholded, segmented) = hand
#
#                     # draw the segmented region and display the frameq
#                     cv2.drawContours(clone, [segmented + (self.right, self.top)], -1, (0, 0, 255))
#
#                     # count the number of fingers
#                     fingers = self.count(thresholded, segmented)
#
#                     if (self.num_frames % 180) == 0:
#                         print(fingers)
#                         is_bool, human, app, num_wickets = randomOutputGenerator(fingers)
#                         self.set_updates(is_bool, human, app, num_wickets)
#
#                     # show the thresholded image
#                     cv2.imshow("Thesholded", thresholded)
#
#             cv2.rectangle(clone, (self.left, self.top), (self.right, self.bottom), (0, 255, 0), 2)
#
#             self.num_frames += 1
#             Clock.schedule_once(partial(self.display_frame, clone))
#
#     def stop_vid(self):
#         # stop the video capture loop
#         self.do_vid = False
#         print("stop_vid() called")
#
#     def set_updates(self, is_bool, human, app, num_wickets):
#         self.is_bool = is_bool
#         self.human_score = human
#         self.app_score = app
#         self.num_wickets = num_wickets
#
#     def get_Updates(self):
#         return (self.is_bool, self.human_score, self.app_score, self.num_wickets)
#
#     def display_frame(self, frame, dt):
#
#         self.time_count = str(time.strftime('%M:%S', time.gmtime(self.num_frames%180)))
#         is_bool, human_score, app_score, num_wickets = self.get_Updates()
#
#         if is_bool:
#             self.human_score_text = str(human_score)
#             self.app_score_text = str(app_score) + "-" + str(num_wickets)
#         else:
#             self.human_score_text = str(human_score) + "-" + str(num_wickets)
#             self.app_score_text = str(app_score)
#
#         # create a Texture the correct size and format for the frame
#         texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
#
#         # copy the frame data into the texture
#         texture.blit_buffer(frame.tobytes(order=None), colorfmt='bgr', bufferfmt='ubyte')
#
#         # flip the texture (otherwise the video is upside down
#         texture.flip_vertical()
#
#         # actually put the texture in the kivy Image widget
#         self.ids.vid.texture = texture
