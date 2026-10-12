from kivy.app import App
from kivy.uix.label import Label


class TestApp(App):
    def build(self):
        return Label(text="HELLO - Kivy works", font_size="30sp")


TestApp().run()
