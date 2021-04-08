from kivy.uix.screenmanager import Screen
from kivy.core.audio import SoundLoader
from Kivy_Tutorial.Result_Package.result_calculation import whoPlay, set_numOfWickets
import random

toss, choice = 0, 0
human_image, app_image, human_team, app_team = '', '', '', ''
sound = None


class GameMenuScreen(Screen):
    data = {
        './images/dhaka.png': 'Dhaka Platoon',
        './images/rangpur.jpg': 'Rangpur Riders',
        './images/comilla.png': 'Cumilla Warriors',
        './images/ctg.png': 'Chattogram Challengers',
        './images/raj.png': 'Rajshahi Royals',
        './images/khulna.png': 'Khulna Tigers'
    }

    icon_list = [
        './images/dhaka.png', './images/rangpur.jpg', './images/comilla.png', './images/ctg.png', './images/raj.png',
        './images/khulna.png'
    ]

    team_list = ['Dhaka Platoon', 'Rangpur Riders', 'Cumilla Warriors', 'Chattogram Challengers', 'Rajshahi Royals',
                 'Khulna Tigers']

    icon_url = ""

    def callback(self, instance):
        print(instance.icon)
        self.icon_url = instance.icon

    def on_choice_checkbox_active(self, choice_no, checkbox, value):
        global choice

        if value:
            choice = choice_no
            print('The checkbox', checkbox, 'is active', 'and', checkbox.state, 'state', ' and choice no: ', choice_no)

    def on_toss_checkbox_active(self, toss_no, checkbox, value):
        global toss

        if value:
            toss = toss_no
            print('The checkbox', checkbox, 'is active', 'and', checkbox.state, 'state', ' and choice no: ', toss_no)

    def play_sound(self):
        global sound
        sound = SoundLoader.load('theme_song.mp3')
        if sound:
            sound.play()

    def stopMusic(self):
        global sound
        print("stopMusic() called")

        if sound:
            print("inside if")
            sound.stop()
            sound = None

    def getSound(self):
        global sound
        return sound

    def submit(self):
        global human_team, app_team, human_image, app_image
        try:
            idx = self.icon_list.index(self.icon_url)
            human_image= self.icon_list.pop(idx)
            human_team = self.team_list.pop(idx)
            randInt = random.randint(0, len(self.icon_list) - 1)
            app_image = self.icon_list[randInt]
            app_team = self.team_list[randInt]
            set_numOfWickets(int(self.ids.text_field.text))
            whoPlay(toss, choice)
            self.play_sound()
        except:
            pass

    def getTeamValues(self):
        global human_team, app_team, human_image, app_image

        return human_team, app_team, human_image, app_image

