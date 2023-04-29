import os
import json
import openai
import subprocess
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.config import ConfigParser
from kivy.uix.togglebutton import ToggleButton
from kivy.core.text import LabelBase
from kivy.core.window import Window

# For Mozilla TTS
import pyttsx3

# Set the window background color
Window.clearcolor = (0.1, 0.1, 0.1, 1)

# Set up custom font for the cyberpunk theme
LabelBase.register(name="CyberpunkFont", fn_regular="C:\Voice_AI\disposabledroid-bb/CyberpunkFont_font.ttf")

def get_chat_gpt_response(api_key, prompt):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

def speak(screen, text):
    print(f"Speaking: {text}")
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    #screen.update_response_label("")

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=10)

        self.response_label = Label(text="Welcome to the CyberKoTeck Assistant!",
                                    font_name="CyberpunkFont",
                                    font_size=24,
                                    color=(0.75, 0.1, 0.9, 1))
        self.text_input = TextInput(hint_text="Type your message here", multiline=False,
                                    on_text_validate=self.send_message)
        send_button = Button(text="Send", on_press=self.send_message)

        layout.add_widget(self.response_label)
        layout.add_widget(self.text_input)
        layout.add_widget(send_button)
        self.add_widget(layout)

    def send_message(self, instance):
        app = App.get_running_app()
        api_key = app.get_api_key()

        if not api_key:
            app.show_api_key_popup()
            return

        chat_gpt_response = get_chat_gpt_response(api_key, self.text_input.text)
        self.response_label.text = f"CyberKoTek Assistant: {chat_gpt_response}"
        speak(self, chat_gpt_response)

        self.text_input.text = ""

    def update_response_label(self, text):
        self.response_label.text = text

class CyberpunkAssistantApp(App):
    def build(self):
        self.config = ConfigParser()
        self.config.read("settings.ini")

        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))

        return sm

    def build_config(self, config):
        config.setdefaults("openai", {"api_key": ""})

    def on_start(self):
        if not self.config.has_section("openai"):
            self.config.add_section("openai")
            self.config.write()

        if not self.config.has_option("openai", "api_key"):
            self.config.set("openai", "api_key", "")
            self.config.write()

        if not self.config.get("openai", "api_key"):
            self.show_api_key_popup()

    def show_api_key_popup(self):
        popup = Popup(title="Enter your OpenAI API Key")
        layout = BoxLayout(orientation="vertical", spacing=10)

        api_key_input = TextInput(hint_text="API Key")
        save_toggle = ToggleButton(text="Save API key", group="save_option", state="down")
        one_time_toggle = ToggleButton(text="Use one-time", group="save_option")

        save_button = Button(text="Submit")
        save_button.bind(on_press=lambda _: self.handle_api_key_submission(popup, api_key_input.text, save_toggle.state == "down"))

        layout.add_widget(api_key_input)
        layout.add_widget(save_toggle)
        layout.add_widget(one_time_toggle)
        layout.add_widget(save_button)
        popup.content = layout
        popup.open()
    
    def handle_api_key_submission(self, popup, api_key, save_key):
        if save_key:
            self.config.set("openai", "api_key", api_key)
            self.config.write()
        else:
            self.openai_api_key = api_key
        popup.dismiss()

    def get_api_key(self):
        return self.config.get("openai", "api_key") or getattr(self, "openai_api_key", None)

if __name__ == "__main__":
    CyberpunkAssistantApp().run()
