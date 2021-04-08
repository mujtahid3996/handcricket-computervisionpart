from kivy.properties import partial
from kivy.uix.screenmanager import Screen
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from cv2 import cv2
import threading
import time
import random

from Kivy_Tutorial.Result_Package.result_calculation import getMultipleValues, getTossResult
from Kivy_Tutorial.Hand_Gesture_Package.handGesture import main
from Kivy_Tutorial.Hand_Gesture_Package.gameMenuScript import GameMenuScreen

game_menu_obj = GameMenuScreen()


class GameScreen(Screen):
    num_frames, open_dialog_num = 0, 0
    icon_list = [
        './images/dhaka.png', './images/rangpur.jpg', './images/comilla.png', './images/ctg.png', './images/raj.png',
        './images/khulna.png'
    ]
    team_list= ['Dhaka Platoon', 'Rangpur Riders', 'Cumilla Warriors', 'Chattogram Challengers', 'Rajshahi Royals', 'Khulna Tigers']
    res_dialog_call = False
    human_team, app_team = "", ""

    time_count = StringProperty()
    human_score_text = StringProperty()
    app_score_text = StringProperty()
    target_text = StringProperty()
    human_image = StringProperty()
    app_image = StringProperty()

    def gamePlay(self):
        print("gamePlay Called")
        self.open_dialog_num += 1

        self.human_team, self.app_team, self.human_image, self.app_image = game_menu_obj.getTeamValues()
        if self.open_dialog_num == 1: self.tossCalc()
        if not game_menu_obj.getSound():
            game_menu_obj.play_sound()

        threading.Thread(target=self.doit, daemon=True).start()

    def tossCalc(self):
        is_toss_win, is_human_bat, toss = getTossResult()

        if toss == 1:
            toss_text = "Head"
        else:
            toss_text = "Tail"

        if is_toss_win:
            if is_human_bat:
                dialog_text = "Congratulations, You chose " + toss_text + "\nWin the toss and play batting"
            else:
                dialog_text = "Congratulations, You chose " + toss_text + "\nWin the toss and play bowling"
        else:
            if is_human_bat:
                dialog_text = "Sorry, You chose " + toss_text + "\nLoss the toss and play batting"
            else:
                dialog_text = "Sorry, You chose " + toss_text + "\nLoss the toss and play bowling"

        print(dialog_text)

        self.dialog = MDDialog(title="Toss Result",
                               text=dialog_text,
                               size_hint=(0.8, 1),
                               buttons=[MDFlatButton(text='Close', on_release=self.close_dialog)]
                               )
        self.dialog.open()

    def close_dialog(self, obj):
        try:
            self.dialog.dismiss()
        except:
            pass

    def doit(self):
        cam = cv2.VideoCapture(0)

        self.do_vid = True  # flag to stop loop

        while self.do_vid:
            ret, frame = cam.read()
            clone = main(frame, self.num_frames)
            self.num_frames += 1
            Clock.schedule_once(partial(self.display_frame, clone))

    def stop_vid(self):
        # stop the video capture loop
        self.do_vid = False
        game_menu_obj.stopMusic()
        print("stop_vid() called")

    def display_frame(self, frame, dt):
        self.time_count = str(time.strftime('%M:%S', time.gmtime(self.num_frames % 180)))
        is_human_bat, human_score, app_score, num_wickets, is_quit, target, turn_time = getMultipleValues()

        if is_human_bat:
            self.human_score_text = str(human_score)
            self.app_score_text = str(app_score) + "-" + str(num_wickets)
        else:
            self.human_score_text = str(human_score) + "-" + str(num_wickets)
            self.app_score_text = str(app_score)

        if turn_time == 1:
            self.target_text = "Target: " + str(target)

        if is_human_bat and is_quit:
            if human_score > target:
                print("Human wins")
                self.res_text = "Congratulations " + self.human_team + "\n Win the match"
            else:
                print("App wins")
                self.res_text = "Congratulations " + self.app_team + "\n Win the match"
        elif not is_human_bat and is_quit:
            if app_score > target:
                print("App wins for not is_bool")
                self.res_text = "Congratulations " + self.app_team + "\n Win the match"
            else:
                print("Human wins for not is_bool")
                self.res_text = "Congratulations " + self.human_team + "\n Win the match"

        if is_quit:
            self.res_dialog_call = not self.res_dialog_call
            if self.res_dialog_call:
                self.resultDialogBox(self.res_text)
            self.do_vid = False

        # create a Texture the correct size and format for the frame
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')

        # copy the frame data into the texture
        texture.blit_buffer(frame.tobytes(order=None), colorfmt='bgr', bufferfmt='ubyte')

        # flip the texture (otherwise the video is upside down
        texture.flip_vertical()

        # actually put the texture in the kivy Image widget
        self.ids.vid.texture = texture

    def resultDialogBox(self, text):
        print("Call")

        self.res_dialog = MDDialog(title="Game Result",
                               text= text,
                               size_hint=(0.8, 1),
                               buttons=[MDFlatButton(text='Close', on_release=self.close_resDialog)]
                               )
        self.res_dialog.open()

    def close_resDialog(self, obj):
        try:
            self.res_dialog.dismiss()
        except:
            pass
