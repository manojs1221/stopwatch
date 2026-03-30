
import os
import re
import csv
from datetime import datetime

# Graphics and Input Fixes for Windows
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty, ColorProperty
from kivy.core.window import Window

KV = '''
<LapRow@BoxLayout>:
    text: ''
    size_hint_y: None
    height: '40dp'
    Label:
        text: root.text
        font_size: '18sp'
        color: (0.9, 0.9, 0.9, 1)

StopwatchRoot:

<StopwatchRoot>:
    orientation: 'vertical'
    padding: 20
    spacing: 15
    canvas.before:
        Color:
            rgba: app.bg_color
        Rectangle:
            pos: self.pos
            size: self.size

    # Header & Theme Toggle
    BoxLayout:
        size_hint_y: None
        height: '40dp'
        Label:
            text: "PRO STOPWATCH"
            bold: True
            halign: 'left'
            text_size: self.size
        Button:
            text: "TOGGLE THEME"
            size_hint_x: None
            width: '120dp'
            on_release: app.toggle_theme()

    # Timer Display
    Label:
        text: root.time_display
        font_size: '80sp'
        size_hint_y: 0.4
        bold: True

    # Main Controls
    BoxLayout:
        size_hint_y: None
        height: '80dp'
        spacing: 10
        
        Button:
            text: 'START (Space)' if not root.running else 'PAUSE (Space)'
            background_color: (0.2, 0.7, 0.3, 1) if not root.running else (0.9, 0.6, 0.2, 1)
            on_release: root.toggle()
        
        Button:
            text: 'LAP (L)'
            disabled: not root.running
            on_release: root.record_lap()
        
        Button:
            text: 'RESET (R)'
            background_color: (0.8, 0.2, 0.2, 1)
            on_release: root.reset()

    # Lap Management Header
    BoxLayout:
        size_hint_y: None
        height: '30dp'
        Label:
            text: "Laps Recorded"
            color: (0.6, 0.6, 0.6, 1)
            halign: 'left'
            text_size: self.size
        Button:
            text: "Export CSV"
            size_hint_x: None
            width: '100dp'
            on_release: root.export_to_csv()

    RecycleView:
        id: lap_list
        data: [{'text': str(x)} for x in root.laps]
        viewclass: 'LapRow'
        RecycleBoxLayout:
            default_size: None, '40dp'
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: 5
'''

class StopwatchRoot(BoxLayout):
    time_display = StringProperty("00:00.00")
    running = BooleanProperty(False)
    elapsed_time = NumericProperty(0)
    laps = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind keyboard
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if text == ' ':
            self.toggle()
        elif text == 'l':
            if self.running: self.record_lap()
        elif text == 'r':
            self.reset()
        return True

    def update(self, dt):
        self.elapsed_time += dt
        self.time_display = self.format_time(self.elapsed_time)

    def format_time(self, seconds_val):
        minutes = int(seconds_val // 60)
        seconds = int(seconds_val % 60)
        hundredths = int((seconds_val * 100) % 100)
        return f"{minutes:02}:{seconds:02}.{hundredths:02}"

    def toggle(self):
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.update, 1/60)
        else:
            self.running = False
            Clock.unschedule(self.update)

    def record_lap(self):
        # Use Regex to clean up the display string if needed
        clean_time = re.sub(r'\s+', '', self.time_display)
        lap_num = len(self.laps) + 1
        self.laps.insert(0, f"Lap {lap_num:02}: {clean_time}")

    def reset(self):
        self.running = False
        Clock.unschedule(self.update)
        self.elapsed_time = 0
        self.time_display = "00:00.00"
        self.laps = []

    def export_to_csv(self):
        if not self.laps:
            return
        filename = f"laps_{datetime.now().strftime('%Y%md_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Lap Number", "Timestamp"])
            for lap in reversed(self.laps):
                # Split "Lap 01: 00:05.12" into parts
                parts = lap.split(': ')
                writer.writerow([parts[0], parts[1]])
        print(f"Saved to {filename}")

class StopwatchApp(App):
    bg_color = ColorProperty((0.05, 0.05, 0.05, 1))
    
    def toggle_theme(self):
        # Switch between Dark Charcoal and Midnight Blue
        if self.bg_color == [0.05, 0.05, 0.05, 1]:
            self.bg_color = (0.1, 0.1, 0.2, 1)
        else:
            self.bg_color = (0.05, 0.05, 0.05, 1)

    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    StopwatchApp().run()
