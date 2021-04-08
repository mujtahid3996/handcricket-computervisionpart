from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList
from kivy.uix.screenmanager import Screen
from Kivy_Tutorial.Hand_Gesture_Package.gameScript import GameScreen
from Kivy_Tutorial.Hand_Gesture_Package.gameMenuScript import GameMenuScreen

Window.size = (300, 500)


class HomeScreen(Screen):
    pass


class DemoApp(MDApp):
    class ContentNavigationDrawer(BoxLayout):
        pass

    class DrawerList(ThemableBehavior, MDList):
        pass

    def build(self):
        screen = Builder.load_file('main.kv')
        return screen


DemoApp().run()
