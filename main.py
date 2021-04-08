import threading
from functools import partial
import cv2
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import math
import imutils

# global variables
bg = None


class MainScreen(Screen):
    pass


class Manager(ScreenManager):
    pass


Builder.load_string('''
<MainScreen>:
    name: "Test"

    FloatLayout:
        Label:
            text: "Webcam from OpenCV?"
            pos_hint: {"x":0.0, "y":0.8}
            size_hint: 1.0, 0.2

        Image:
            # this is where the video will show
            # the id allows easy access
            id: vid
            size_hint: 1, 0.6
            allow_stretch: True  # allow the video image to be scaled
            keep_ratio: True  # keep the aspect ratio so people don't look squashed
            pos_hint: {'center_x':0.5, 'top':0.8}

        Button:
            text: 'Stop Video'
            pos_hint: {"x":0.0, "y":0.0}
            size_hint: 1.0, 0.2
            font_size: 50
            on_release: app.stop_vid()
''')


class Main(App):

    aWeight = 0.5

    # region of interest (ROI) coordinates
    top, right, bottom, left = 10, 350, 225, 590

    # initialize num of frames
    num_frames = 0

    # --------------------------------------------------
    # To find the running average over the background
    # --------------------------------------------------
    def run_avg(self, image):
        global bg
        # initialize the background
        if bg is None:
            bg = image.copy().astype("float")
            return

        # compute weighted average, accumulate it and update the background
        cv2.accumulateWeighted(image, bg, self.aWeight)

    # ---------------------------------------------
    # To segment the region of hand in the image
    # ---------------------------------------------
    def segment(self, image, threshold=25):
        global bg
        # find the absolute difference between background and current frame
        diff = cv2.absdiff(bg.astype("uint8"), image)

        # threshold the diff image so that we get the foreground
        thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]

        # get the contours in the thresholded image
        (cnts, _) = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # return None, if no contours detected
        if len(cnts) == 0:
            return
        else:
            # analyze the contours
            print("Number of Contours found = " + str(len(cnts)))
            cv2.drawContours(image, cnts, -1, (0, 255, 0), 3)
            cv2.imshow('All Contours', image)

            # based on contour area, get the maximum contour which is the hand
            segmented = max(cnts, key=cv2.contourArea)
            cv2.drawContours(image, segmented, -1, (0, 255, 0), 3)
            cv2.imshow('Max Contour', image)

            return (thresholded, segmented)

    # --------------------------------------------------------------
    # To count the number of fingers in the segmented hand region
    # --------------------------------------------------------------
    def count(self, thresholded, segmented):
        # find the convex hull of the segmented hand region
        hull = cv2.convexHull(segmented, returnPoints=False)
        defects = cv2.convexityDefects(segmented, hull)

        # Bascially indicates how much finger is visible in screen
        countDefects = 0

        for i in range(defects.shape[0]):
            # Returns start point, end point, farthest point, approximate distance to farthest point
            s, e, f, d = defects[i, 0]
            start = tuple(segmented[s][0])
            end = tuple(segmented[e][0])
            far = tuple(segmented[f][0])

            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

            # This angle is used while hand is moving around
            angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

            # If angle < 90 degree then treat as a finger
            if angle <= 90:
                countDefects += 1

        return (countDefects + 1)

    def build(self):

        # start the camera access code on a separate thread
        # if this was done on the main thread, GUI would stop
        # daemon=True means kill this thread when app stops
        threading.Thread(target=self.doit, daemon=True).start()

        sm = ScreenManager()
        self.main_screen = MainScreen()
        sm.add_widget(self.main_screen)
        return sm

    def doit(self):
        cam = cv2.VideoCapture(0)

        # this code is run in a separate thread
        self.do_vid = True  # flag to stop loop

        # start processing loop
        while (self.do_vid):
            ret, frame = cam.read()

            frame = imutils.resize(frame, width=700)

            frame = cv2.flip(frame, 1)

            # clone the frame
            clone = frame.copy()

            # get the ROI
            roi = frame[self.top:self.bottom, self.right:self.left]

            # convert the roi to grayscale and blur it
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            if self.num_frames < 30:
                self.run_avg(gray)
            else:
                # segment the hand region
                hand = self.segment(gray)

                # check whether hand region is segmented
                if hand is not None:
                    # if yes, unpack the thresholded image and
                    # segmented region
                    (thresholded, segmented) = hand

                    # draw the segmented region and display the frameq
                    cv2.drawContours(clone, [segmented + (self.right, self.top)], -1, (0, 0, 255))

                    # count the number of fingers
                    fingers = self.count(thresholded, segmented)

                    cv2.putText(clone, str(fingers), (70, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                    # show the thresholded image
                    cv2.imshow("Thesholded", thresholded)

            cv2.rectangle(clone, (self.left, self.top), (self.right, self.bottom), (0, 255, 0), 2)

            self.num_frames += 1
            Clock.schedule_once(partial(self.display_frame, clone))

    def stop_vid(self):
        # stop the video capture loop
        self.do_vid = False

    def display_frame(self, frame, dt):
        # display the current video frame in the kivy Image widget

        # create a Texture the correct size and format for the frame
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')

        # copy the frame data into the texture
        texture.blit_buffer(frame.tobytes(order=None), colorfmt='bgr', bufferfmt='ubyte')

        # flip the texture (otherwise the video is upside down
        texture.flip_vertical()

        # actually put the texture in the kivy Image widget
        self.main_screen.ids.vid.texture = texture

Main().run()

