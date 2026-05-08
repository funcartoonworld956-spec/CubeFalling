import os
import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Rectangle, Color
from kivy.core.text import Label as CoreLabel


class CubeFallingGame(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cubes = []
        self.state = "START"
        self.score = 0
        self.base_speed = 5
        self.spawn_timer = 0

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        def p(path):
            return os.path.join(self.base_path, path)

        self.get_path = p

        self.img_start_bg = self.get_path("assets/images/ui/start_bg.png")
        self.img_game_bg = self.get_path("assets/background/game_bg.png")
        self.img_over_bg = self.get_path("assets/images/ui/game_over.png")

        cube_dir = self.get_path("assets/images/cube")
        self.cube_images = []

        if os.path.exists(cube_dir):
            self.cube_images = [
                os.path.join(cube_dir, f)
                for f in sorted(os.listdir(cube_dir))
                if f.endswith(".png")
            ]

        self.cube_queue = self.cube_images.copy()
        random.shuffle(self.cube_queue)

        # SAFE MUSIC
        self.bg_music = None
        try:
            music_path = self.get_path("assets/sound/music.wav")
            self.bg_music = SoundLoader.load(music_path)

            if self.bg_music:
                self.bg_music.loop = True
                self.bg_music.volume = 0.5
        except Exception as e:
            print("Music error:", e)

        self.basket_size = (100, 100)
        self.basket_pos = [Window.width / 2 - 50, 50]

        Clock.schedule_interval(self.update, 1 / 60)
        self.draw()

    def text(self, msg, size=30):
        label = CoreLabel(text=msg, font_size=size, bold=True)
        label.refresh()
        return label.texture

    def on_touch_move(self, touch):
        if self.state == "PLAYING":
            self.basket_pos[0] = touch.x - self.basket_size[0] / 2

    def on_touch_down(self, touch):
        if self.state == "START":
            self.reset()

        elif self.state == "GAMEOVER":
            self.reset()

    def reset(self):
        self.state = "PLAYING"
        self.score = 0
        self.cubes = []
        self.base_speed = 5
        self.spawn_timer = 0

        self.cube_queue = self.cube_images.copy()
        random.shuffle(self.cube_queue)

        if self.bg_music:
            self.bg_music.stop()
            self.bg_music.play()

    def update(self, dt):
        self.draw()

        if self.state != "PLAYING":
            return

        speed = self.base_speed + (self.score // 5)

        self.spawn_timer += 1

        if self.spawn_timer > 25 and self.cube_images:
            x = random.randint(50, int(Window.width) - 110)

            if not self.cube_queue:
                self.cube_queue = self.cube_images.copy()
                random.shuffle(self.cube_queue)

            cube_img = self.cube_queue.pop()

            self.cubes.append({
                "pos": [x, Window.height],
                "img": cube_img
            })

            self.spawn_timer = 0

        for c in self.cubes[:]:
            c["pos"][1] -= speed

            bx, by = self.basket_pos
            cx, cy = c["pos"]

            if bx < cx + 60 and bx + 100 > cx and by < cy + 60 and by + 100 > cy:
                self.cubes.remove(c)
                self.score += 1

            elif cy < 0:
                self.state = "GAMEOVER"
                if self.bg_music:
                    self.bg_music.stop()

    def draw(self):
        self.canvas.clear()

        with self.canvas:

            bg = self.img_game_bg if self.state == "PLAYING" else (
                self.img_start_bg if self.state == "START" else self.img_over_bg
            )

            if os.path.exists(bg):
                Color(1, 1, 1, 1)
                Rectangle(source=bg, pos=(0, 0), size=Window.size)
            else:
                Color(0.2, 0.2, 0.2, 1)
                Rectangle(pos=(0, 0), size=Window.size)

            if self.state == "PLAYING":
                Color(0, 0.4, 1, 1)
                Rectangle(pos=self.basket_pos, size=self.basket_size)

                Color(1, 1, 1, 1)
                for c in self.cubes:
                    Rectangle(source=c["img"], pos=c["pos"], size=(60, 60))


class CatchApp(App):
    def build(self):
        return CubeFallingGame()


if __name__ == "__main__":
    CatchApp().run()
