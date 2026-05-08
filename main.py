import os
import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Rectangle, Color
from kivy.core.text import Label as CoreLabel

if os.name != "android":
    Window.size = (450, 800)


class CubeFallingGame(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cubes = []
        self.state = "START"
        self.score = 0
        self.base_speed = 5
        self.spawn_timer = 0

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # ---------- PATH ----------
        def p(path):
            return os.path.join(self.base_path, path.replace("/", os.sep))

        self.get_path = p

        # ---------- BACKGROUNDS ----------
        self.img_start_bg = self.get_path("assets/images/ui/start_bg.png")
        self.img_game_bg = self.get_path("assets/background/game_bg.png")
        self.img_over_bg = self.get_path("assets/images/ui/game_over.png")

        # ---------- CUBES ----------
        cube_dir = self.get_path("assets/images/cube")
        self.cube_images = []

        if os.path.exists(cube_dir):
            self.cube_images = [
                os.path.join(cube_dir, f)
                for f in sorted(os.listdir(cube_dir))
                if f.endswith(".png")
            ]

        # Shuffle system
        self.cube_queue = []
        if self.cube_images:
            self.cube_queue = self.cube_images.copy()
            random.shuffle(self.cube_queue)

        # ---------- MUSIC ----------
        music_path = self.get_path("assets/sound/music.wav")
        self.bg_music = SoundLoader.load(music_path)

        if self.bg_music:
            self.bg_music.loop = True
            self.bg_music.volume = 0.5
            self.bg_music.play()
        else:
            print("❌ Music not loaded")

        # ---------- BASKET ----------
        self.basket_size = (100, 100)
        self.basket_pos = [Window.width / 2 - 50, 50]

        Clock.schedule_interval(self.update, 1 / 60)
        self.draw()  # first frame fix

    # ---------------- TEXT ----------------
    def text(self, msg, size=30):
        label = CoreLabel(text=msg, font_size=size, bold=True)
        label.refresh()
        return label.texture

    # ---------------- TOUCH ----------------
    def on_touch_move(self, touch):
        if self.state == "PLAYING":
            self.basket_pos[0] = touch.x - self.basket_size[0] / 2

    def on_touch_down(self, touch):
        if self.state == "START":
            if Window.width/2 - 100 < touch.x < Window.width/2 + 100 and 130 < touch.y < 200:
                self.reset()

        elif self.state == "GAMEOVER":
            if Window.width/2 - 100 < touch.x < Window.width/2 + 100 and 240 < touch.y < 300:
                self.reset()

    # ---------------- RESET ----------------
    def reset(self):
        self.state = "PLAYING"
        self.score = 0
        self.cubes = []
        self.base_speed = 5
        self.spawn_timer = 0

        if self.cube_images:
            self.cube_queue = self.cube_images.copy()
            random.shuffle(self.cube_queue)

        if self.bg_music:
            self.bg_music.stop()
            self.bg_music.play()

    # ---------------- UPDATE ----------------
    def update(self, dt):

        self.draw()

        if self.state != "PLAYING":
            return

        speed = self.base_speed + (self.score // 5)

        self.spawn_timer += 1
        if self.spawn_timer > 25 and self.cube_images:

            x = random.randint(50, Window.width - 110)

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

    # ---------------- DRAW ----------------
    def draw(self):
        self.canvas.clear()

        with self.canvas:

            bg = self.img_game_bg if self.state == "PLAYING" else (
                self.img_start_bg if self.state == "START" else self.img_over_bg
            )

            if bg and os.path.exists(bg):
                Color(1, 1, 1, 1)
                Rectangle(source=bg, pos=(0, 0), size=Window.size)
            else:
                Color(0.2, 0.2, 0.2, 1)
                Rectangle(pos=(0, 0), size=Window.size)

            if self.state == "START":

                Color(0, 0.7, 1, 1)
                Rectangle(pos=(Window.width/2 - 100, 130), size=(200, 70))

                Color(1, 1, 1, 1)
                txt = self.text("PLAY", 40)
                Rectangle(texture=txt,
                          pos=(Window.width/2 - txt.width/2, 145),
                          size=txt.size)

            elif self.state == "PLAYING":

                Color(0, 0.4, 1, 1)
                Rectangle(pos=self.basket_pos, size=self.basket_size)

                Color(1, 1, 1, 1)
                for c in self.cubes:
                    Rectangle(source=c["img"], pos=c["pos"], size=(60, 60))

                score = self.text(f"Score: {self.score}", 35)
                Rectangle(texture=score,
                          pos=(20, Window.height - 60),
                          size=score.size)

            elif self.state == "GAMEOVER":

                score = self.text(f"Score: {self.score}", 45)
                Rectangle(texture=score,
                          pos=(Window.width/2 - score.width/2, Window.height/2 + 80),
                          size=score.size)

                Color(1, 0.7, 0, 1)
                Rectangle(pos=(Window.width/2 - 100, 240), size=(200, 70))

                txt = self.text("REPLAY", 40)
                Rectangle(texture=txt,
                          pos=(Window.width/2 - txt.width/2, 255),
                          size=txt.size)


class CatchApp(App):
    def build(self):
        self.title = "Cube Falling Game"
        return CubeFallingGame()


if __name__ == "__main__":
    CatchApp().run()
