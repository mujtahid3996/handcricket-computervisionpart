import cv2
import math

from Kivy_Tutorial.Result_Package.result_calculation import randomOutputGenerator

# global variables
bg = None


def run_avg(image, accumWeight):
    global bg
    # initialize the background
    if bg is None:
        bg = image.copy().astype("float")
        return

    # compute weighted average, accumulate it and update the background
    cv2.accumulateWeighted(image, bg, accumWeight)


def segment(image, threshold=25):
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
        # based on contour area, get the maximum contour which is the hand
        segmented = max(cnts, key=cv2.contourArea)
        return (thresholded, segmented)


def count(thresholded, segmented):
    try:
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

    except:
        pass


def main(frame, num_frames):
    try:
        # initialize accumulated weight
        accumWeight = 0.5

        # region of interest (ROI) coordinates
        top, right, bottom, left = 10, 350, 225, 590


        # flip the frame so that it is not the mirror view
        frame = cv2.flip(frame, 1)

        # clone the frame
        clone = frame.copy()

        # get the height and width of the frame
        (height, width) = frame.shape[:2]

        # get the ROI
        roi = frame[top:bottom, right:left]

        # convert the roi to grayscale and blur it
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # to get the background, keep looking till a threshold is reached
        # so that our weighted average model gets calibrated
        if num_frames < 30:
            run_avg(gray, accumWeight)
            if num_frames == 1:
                print("[STATUS] please wait! calibrating...")
            elif num_frames == 29:
                print("[STATUS] calibration successfull...")
        else:
            # segment the hand region
            hand = segment(gray)

            # check whether hand region is segmented
            if hand is not None:
                # if yes, unpack the thresholded image and
                # segmented region
                (thresholded, segmented) = hand

                # draw the segmented region and display the frame
                cv2.drawContours(clone, [segmented + (right, top)], -1, (0, 0, 255))

                # count the number of fingers
                fingers = count(thresholded, segmented)

                if num_frames % 180 == 0 and fingers and fingers < 6:
                    randomOutputGenerator(fingers)
                    print("Fingers temp : ", fingers)

                # show the thresholded image
                cv2.imshow("Thesholded", thresholded)

        # draw the segmented hand
        cv2.rectangle(clone, (left, top), (right, bottom), (0, 255, 0), 2)

        # increment the number of frames
        num_frames += 1

        # display the frame with segmented hand
        cv2.imshow("Video Feed", clone)
        return clone
    except:
        pass