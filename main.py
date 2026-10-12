import math
import os
import struct
import traceback
import wave

ERROR_TEXT = None

def show_fatal(text):
    try:
        from kivy.app import App
        from kivy.uix.label import Label
        class ErrorApp(App):
            def build(self):
                return Label(text=text, font_size="12sp", halign="left", valign="top")
        ErrorApp().run()
    except:
        print(text)

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.audio import SoundLoader
    from kivy.core.text import Label as CoreLabel
    from kivy.core.window import Window
    from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle
    from kivy.uix.widget import Widget

    W, H = 900, 550
    WHITE = (255, 255, 255)
    BLACK = (8, 8, 12)
    YELLOW = (255, 220, 50)
    PINK = (220, 100, 120)

    GRAVITY = 0.82
    JUMP = -15.2
    GROUND_Y = 385
    MAX_LEVEL = 15
    FIXED_SPEED = 7.5

    LEVELS = {
        1: {"gap": 430, "ow": 42, "oh": 48, "need": 8},
        2: {"gap": 400, "ow": 48, "oh": 62, "need": 8},
        3: {"gap": 375, "ow": 52, "oh": 78, "need": 9},
        4: {"gap": 350, "ow": 46, "oh": 100, "need": 9},
        5: {"gap": 335, "ow": 58, "oh": 72, "need": 10},
        6: {"gap": 320, "ow": 40, "oh": 118, "need": 10},
        7: {"gap": 305, "ow": 50, "oh": 88, "need": 11},
        8: {"gap": 290, "ow": 44, "oh": 130, "need": 11},
        9: {"gap": 280, "ow": 60, "oh": 80, "need": 12},
        10: {"gap": 265, "ow": 36, "oh": 145, "need": 12},
        11: {"gap": 255, "ow": 54, "oh": 96, "need": 13},
        12: {"gap": 245, "ow": 42, "oh": 125, "need": 13},
        13: {"gap": 235, "ow": 64, "oh": 85, "need": 14},
        14: {"gap": 225, "ow": 38, "oh": 150, "need": 14},
        15: {"gap": 210, "ow": 56, "oh": 140, "need": 16},
    }

    THEMES = {
        1: ((135, 206, 235), (90, 160, 105), (46, 168, 72), (28, 120, 48), (120, 72, 32), BLACK, "meadow"),
        2: ((28, 70, 48), (18, 90, 40), (16, 78, 32), (10, 48, 20), (40, 28, 16), WHITE, "jungle"),
        3: ((250, 196, 120), (196, 140, 78), (214, 170, 96), (176, 128, 64), (130, 82, 42), BLACK, "desert"),
        4: ((10, 14, 42), (22, 26, 58), (18, 22, 40), (12, 14, 28), (170, 170, 80), WHITE, "city"),
        5: ((186, 214, 232), (210, 220, 230), (236, 242, 248), (200, 214, 226), (120, 140, 160), BLACK, "snow"),
        6: ((78, 22, 16), (48, 18, 16), (36, 16, 14), (22, 10, 10), (96, 28, 16), WHITE, "lava"),
        7: ((120, 196, 230), (64, 150, 190), (232, 196, 120), (196, 156, 82), (72, 110, 130), BLACK, "beach"),
        8: ((18, 16, 28), (32, 28, 40), (42, 36, 48), (24, 20, 30), (90, 80, 110), WHITE, "cave"),
        9: ((232, 150, 90), (170, 90, 40), (150, 78, 32), (110, 52, 22), (90, 42, 18), WHITE, "autumn"),
        10: ((6, 8, 24), (12, 14, 36), (10, 12, 28), (6, 8, 18), (180, 190, 220), WHITE, "space"),
        11: ((255, 186, 206), (210, 120, 150), (120, 170, 90), (70, 120, 55), (150, 70, 100), BLACK, "sakura"),
        12: ((48, 70, 42), (30, 55, 28), (34, 58, 30), (20, 40, 22), (60, 48, 24), WHITE, "swamp"),
        13: ((150, 190, 220), (90, 130, 170), (180, 210, 230), (120, 160, 190), (70, 110, 150), BLACK, "ice"),
        14: ((255, 120, 70), (180, 70, 40), (120, 55, 35), (80, 32, 22), (70, 28, 18), WHITE, "canyon"),
        15: ((28, 18, 48), (70, 40, 90), (40, 24, 64), (22, 12, 40), (230, 190, 70), WHITE, "final"),
    }

    def make_sound(path, typ):
        rate = 22050
        length = 0.25 if typ != "laugh" else 1.0
        data = bytearray()
        for i in range(int(rate * length)):
            t = i / rate
            if typ == "jump":
                freq, vol = 450 + 900 * t, 0.30
            elif typ == "hit":
                freq, vol = 220 - 140 * t, 0.45
            elif typ == "win":
                freq, vol = 520 + 240 * t, 0.35
            else:
                freq = 450 if int(t * 9) % 2 == 0 else 300
                vol = 0.35
            v = math.sin(2 * math.pi * freq * t) * vol
            data += struct.pack("<h", int(max(-1, min(1, v)) * 32767))
        with wave.open(path, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(rate)
            f.writeframes(bytes(data))

    class Game(Widget):
        def __init__(self, sound_dir, **kw):
            super().__init__(**kw)
            self.sounds = {}
            self._load_sounds(sound_dir)
            self.level = 1
            self.score = 0
            self.passed = 0
            self.speed = FIXED_SPEED
            self.px = 140.0
            self.py = float(GROUND_Y)
            self.pw, self.ph = 74, 66
            self.vel = 0.0
            self.transition = False
            self.won = False
            self.ttime = 0
            self.tick = 0
            self.obstacles = []
            self.jump_btn = (690, 455, 180, 72)
            self._text_cache = {}
            self.make_obstacles()
            Clock.schedule_interval(self.update, 1 / 60.0)

        def level_cfg(self):
            return LEVELS.get(self.level, LEVELS[MAX_LEVEL])

        def theme(self):
            return THEMES.get(self.level, THEMES[MAX_LEVEL])

        def _load_sounds(self, d):
            try:
                for name in ("jump", "hit", "laugh", "win"):
                    p = os.path.join(d, name + ".wav")
                    make_sound(p, name)
                    self.sounds[name] = SoundLoader.load(p)
            except:
                self.sounds = {}

        def play(self, name):
            s = self.sounds.get(name)
            if not s: return
            try:
                s.stop()
                s.play()
            except:
                pass

        def make_obstacles(self):
            c = self.level_cfg()
            self.obstacles = [[760 + i * c["gap"], 430, c["ow"], c["oh"]] for i in range(4)]

        def begin_level(self):
            self.px = 140.0
            self.py = float(GROUND_Y)
            self.vel = 0.0
            self.passed = 0
            self.speed = FIXED_SPEED
            self.make_obstacles()

        def reset_level(self):
            self.begin_level()
            self.play("hit")

        def jump(self):
            if self.won or self.transition: return
            if self.py >= GROUND_Y - 1:
                self.vel = JUMP
                self.play("jump")

        def on_touch_down(self, touch):
            if self.won:
                self.level = 1
                self.score = 0
                self.won = False
                self.transition = False
                self.begin_level()
                return True
            self.jump()
            return True

        def update(self, dt):
            try:
                self._update(dt)
            except:
                Clock.unschedule(self.update)
                self.show_error(traceback.format_exc())

        def show_error(self, msg):
            from kivy.uix.label import Label
            self.canvas.clear()
            self.clear_widgets()
            self.add_widget(Label(text=msg, font_size="12sp", pos=self.pos, size=self.size,
                                  text_size=self.size, halign="left", valign="top"))

        def _update(self, dt):
            self.tick += 1
            if self.won:
                self.draw()
                return
            if self.transition:
                self.ttime += 1
                if self.ttime >= 150:
                    self.transition = False
                    self.ttime = 0
                    self.begin_level()
                self.draw()
                return

            self.vel += GRAVITY
            self.py += self.vel
            if self.py >= GROUND_Y:
                self.py = float(GROUND_Y)
                self.vel = 0.0

            cfg = self.level_cfg()
            gap, need = cfg["gap"], cfg["need"]
            for o in self.obstacles:
                o[0] -= self.speed
                hit = (self.px < o[0] + o[2] and self.px + self.pw > o[0] and
                       self.py < o[1] + o[3] and self.py + self.ph > o[1])
                if hit:
                    self.reset_level()
                    break
                if o[0] + o[2] < -20:
                    o[0] = max(x[0] for x in self.obstacles) + gap
                    o[2], o[3] = cfg["ow"], cfg["oh"]
                    self.passed += 1
                    self.score += 1
                    if self.passed >= need:
                        if self.level < MAX_LEVEL:
                            self.level += 1
                            if self.level >= 5:
                                self.transition = True
                                self.ttime = 0
                                self.play("laugh")
                            else:
                                self.begin_level()
                        else:
                            self.won = True
                            self.play("win")
                        break
            self.draw()

        def view(self):
            s = min(self.width / float(W), self.height / float(H)) if self.width and self.height else 1
            ox = (self.width - W * s) / 2 + self.x
            oy = (self.height - H * s) / 2 + self.y
            return s, ox, oy

        def col(self, c, a=1):
            Color(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, a)

        def rect(self, c, x, y, w, h, radius=0, a=1):
            s, ox, oy = self.view()
            self.col(c, a)
            pos = (ox + x * s, oy + (H - y - h) * s)
            size = (max(1, w * s), max(1, h * s))
            if radius:
                RoundedRectangle(pos=pos, size=size, radius=[radius * s])
            else:
                Rectangle(pos=pos, size=size)

        def ellipse(self, c, x, y, w, h, a=1):
            s, ox, oy = self.view()
            self.col(c, a)
            Ellipse(pos=(ox + x * s, oy + (H - y - h) * s), size=(max(1, w * s), max(1, h * s)))

        def polygon(self, c, pts):
            s, ox, oy = self.view()
            self.col(c)
            flat = []
            for x, y in pts:
                flat += [ox + x * s, oy + (H - y) * s]
            if len(pts) == 3:
                Triangle(points=flat)
            else:
                Line(points=flat, width=1, close=True)

        def line(self, c, p1, p2, width):
            s, ox, oy = self.view()
            self.col(c)
            Line(points=[ox + p1[0] * s, oy + (H - p1[1]) * s,
                         ox + p2[0] * s, oy + (H - p2[1]) * s],
                 width=max(1, width * s), cap="round")

        def text(self, txt, size, c, x, y, center=False):
            s, ox, oy = self.view()
            key = (txt, int(max(8, size * s)))
            tex = self._text_cache.get(key)
            if tex is None:
                if len(self._text_cache) > 400: self._text_cache.clear()
                lab = CoreLabel(text=txt, font_size=key[1])
                lab.refresh()
                tex = lab.texture
                self._text_cache[key] = tex
            if tex is None: return
            tw, th = tex.size
            gx = ox + x * s - (tw / 2.0 if center else 0)
            gy = oy + (H - y) * s - th
            self.col(c)
            Rectangle(texture=tex, pos=(gx, gy), size=(tw, th))

        # ==================== سگ خیلی قشنگ‌تر ====================
        def dog(self, x, y):
            t = self.tick
            wag = math.sin(t * 0.28) * 18
            ear = math.sin(t * 0.35) * 3

            self.ellipse((30, 30, 30), x + 8, y - 6, 62, 14, 0.35)
            self.line((180, 120, 70), (x + 20, y + 34), (x - 18, y + 18 + wag), 11)
            self.line((225, 170, 110), (x + 20, y + 34), (x - 16, y + 20 + wag), 6)
            self.ellipse((230, 175, 115), x + 8, y + 24, 58, 40)
            self.ellipse((210, 155, 95), x + 12, y + 26, 48, 32)
            self.polygon((185, 115, 70), [(x + 14, y + 56), (x + 24, y + 82 + ear), (x + 36, y + 56)])
            self.polygon((185, 115, 70), [(x + 40, y + 56), (x + 50, y + 82 + ear), (x + 62, y + 56)])
            self.polygon((255, 180, 190), [(x + 20, y + 60), (x + 26, y + 74), (x + 32, y + 60)])
            self.polygon((255, 180, 190), [(x + 44, y + 60), (x + 50, y + 74), (x + 56, y + 60)])
            self.ellipse((230, 175, 115), x + 18, y + 28, 46, 42)
            self.ellipse((255, 255, 255), x + 24, y + 40, 16, 18)
            self.ellipse((255, 255, 255), x + 46, y + 40, 16, 18)
            self.ellipse((40, 40, 40), x + 28, y + 44, 7, 9)
            self.ellipse((40, 40, 40), x + 50, y + 44, 7, 9)
            self.ellipse((255, 255, 255), x + 29, y + 45, 3, 3)
            self.ellipse((255, 255, 255), x + 51, y + 45, 3, 3)
            self.ellipse((50, 50, 50), x + 42, y + 32, 9, 7)
            self.ellipse((255, 120, 150), x + 34, y + 18, 18, 14)
            self.ellipse((185, 115, 70), x + 12, y - 2, 20, 24)
            self.ellipse((185, 115, 70), x + 44, y - 2, 20, 24)

        # ==================== گربه خاکستری ====================
        def cat(self, x, y):
            c = (95, 90, 100)
            c2 = (65, 60, 70)
            self.ellipse((20, 20, 20), x - 70, y + 55, 140, 30, 0.3)
            self.ellipse(c, x - 75, y + 85, 150, 140)
            self.ellipse(c, x - 55, y + 40, 110, 100)
            self.polygon(c2, [(x - 50, y + 95), (x - 35, y + 145), (x - 5, y + 100)])
            self.polygon(c2, [(x + 5, y + 100), (x + 35, y + 145), (x + 50, y + 95)])
            self.ellipse((255, 230, 80), x - 38, y + 65, 26, 34)
            self.ellipse((255, 230, 80), x + 12, y + 65, 26, 34)
            self.ellipse((30, 30, 30), x - 28, y + 72, 8, 18)
            self.ellipse((30, 30, 30), x + 22, y + 72, 8, 18)
            self.polygon((255, 150, 170), [(x - 6, y + 95), (x + 6, y + 95), (x, y + 105)])
            tail = math.sin(self.ttime * 0.15) * 25
            self.line(c2, (x + 70, y + 140), (x + 115 + tail, y + 170), 14)

        def obstacle(self, o, color):
            x, y, w, h = o
            dark = tuple(max(0, v - 55) for v in color)
            light = tuple(min(255, v + 45) for v in color)
            self.rect(dark, x + 5, y + 8, w, h, 10)
            self.rect(color, x, y, w, h, 10)
            self.rect(light, x + 6, y + 10, max(8, w * 0.3), h - 16, 5)
            self.rect(dark, x, y, w, 12, 5)

        def draw_background(self, theme):
            sky, ground, _, _, _, _, name = theme
            self.rect(sky, 0, 0, W, H)
            self.rect(ground, 0, 430, W, 120)

            if name == "meadow":
                self.rect((70, 150, 60), 50, 410, 120, 30)
                self.rect((70, 150, 60), 300, 400, 180, 40)
            elif name == "desert":
                self.ellipse((220, 180, 100), 200, 420, 180, 25)
            elif name == "snow":
                self.rect((240, 245, 255), 0, 430, W, 120)
            elif name == "final":
                self.rect((50, 30, 80), 0, 430, W, 120)

            if name in ["meadow", "beach", "autumn"]:
                self.ellipse((255, 230, 80), 750, 80, 55, 55)
            elif name in ["space", "cave", "final"]:
                self.ellipse((240, 240, 255), 750, 70, 45, 45)

        def draw(self):
            self.canvas.clear()
            with self.canvas:
                self.col(BLACK)
                Rectangle(pos=self.pos, size=self.size)

                if self.won:
                    self.rect((20, 15, 40), 0, 0, W, H)
                    self.ellipse((255, 215, 90), 450, 160, 70, 70)
                    self.text("YOU WIN!", 78, YELLOW, W // 2, 260, True)
                    self.text("Score: %d" % self.score, 38, WHITE, W // 2, 340, True)
                    self.text("Tap to play again", 30, WHITE, W // 2, 410, True)
                    return

                if self.transition:
                    self.rect((10, 10, 20), 0, 0, W, H)
                    walk = math.sin(self.ttime * 0.11) * 95
                    cat_x = W // 2 + walk
                    cy = 195 + int(math.sin(self.ttime * 0.09) * 10)
                    self.cat(cat_x, cy)
                    self.text("HAHAHAHA!", 58, WHITE, W // 2, 390, True)
                    if self.ttime > 35:
                        self.text("MEOW!", 44, YELLOW, W // 2 + 130, 330, True)
                    if self.ttime > 75:
                        self.text("RUN DOGGY!", 38, WHITE, W // 2 - 110, 460, True)
                    self.text("LEVEL %d" % self.level, 38, YELLOW, W // 2, 510, True)
                    return

                theme = self.theme()
                self.draw_background(theme)
                self.dog(self.px, self.py)
                for o in self.obstacles:
                    if -80 < o[0] < W + 40:
                        self.obstacle(o, (95, 95, 95))

                b = self.jump_btn
                self.rect((35, 35, 42), b[0] + 5, b[1] + 5, b[2], b[3], 18)
                self.rect((255, 200, 50), b[0], b[1], b[2], b[3], 18)
                self.text("JUMP", 34, BLACK, b[0] + 48, b[1] + 24)

                self.rect((0, 0, 0), 12, 12, 260, 100, 14, 0.4)
                self.text("Score  %d" % self.score, 28, WHITE, 30, 30)
                self.text("Level  %d / %d" % (self.level, MAX_LEVEL), 28, WHITE, 30, 58)
                self.text("%d / %d" % (self.passed, self.level_cfg()["need"]), 24, YELLOW, 30, 86)

    class DogRunnerApp(App):
        def build(self):
            self.title = "Dog Runner"
            try:
                return Game(self.user_data_dir)
            except:
                from kivy.uix.label import Label
                return Label(text=traceback.format_exc(), font_size="12sp",
                             text_size=(Window.width, None), halign="left")

except Exception:
    ERROR_TEXT = traceback.format_exc()

if __name__ == "__main__":
    if ERROR_TEXT is not None:
        show_fatal(ERROR_TEXT)
    else:
        DogRunnerApp().run()
