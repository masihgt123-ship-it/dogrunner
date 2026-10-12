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
                return Label(text=text, font_size="12sp",
                             halign="left", valign="top")

        ErrorApp().run()
    except Exception:
        print(text)


try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.audio import SoundLoader
    from kivy.core.text import Label as CoreLabel
    from kivy.core.window import Window
    from kivy.graphics import (Color, Ellipse, Line, Rectangle,
                               RoundedRectangle, Triangle)
    from kivy.uix.widget import Widget

    W, H = 900, 550
    WHITE = (255, 255, 255)
    BLACK = (8, 8, 12)
    YELLOW = (255, 220, 50)
    GREEN = (50, 180, 70)
    DARKGREEN = (20, 90, 35)
    BROWN = (120, 70, 30)
    DOG = (190, 130, 70)
    DOGDARK = (110, 70, 35)
    PINK = (220, 100, 120)

    GRAVITY = 0.82
    JUMP = -15.2
    GROUND_Y = 385
    MAX_LEVEL = 15
    FIXED_SPEED = 7.5   # سرعت همه لول‌ها یکسان

    LEVELS = {
        1:  {"gap": 430, "ow": 42, "oh": 48,  "need": 8},
        2:  {"gap": 400, "ow": 48, "oh": 62,  "need": 8},
        3:  {"gap": 375, "ow": 52, "oh": 78,  "need": 9},
        4:  {"gap": 350, "ow": 46, "oh": 100, "need": 9},
        5:  {"gap": 335, "ow": 58, "oh": 72,  "need": 10},
        6:  {"gap": 320, "ow": 40, "oh": 118, "need": 10},
        7:  {"gap": 305, "ow": 50, "oh": 88,  "need": 11},
        8:  {"gap": 290, "ow": 44, "oh": 130, "need": 11},
        9:  {"gap": 280, "ow": 60, "oh": 80,  "need": 12},
        10: {"gap": 265, "ow": 36, "oh": 145, "need": 12},
        11: {"gap": 255, "ow": 54, "oh": 96,  "need": 13},
        12: {"gap": 245, "ow": 42, "oh": 125, "need": 13},
        13: {"gap": 235, "ow": 64, "oh": 85,  "need": 14},
        14: {"gap": 225, "ow": 38, "oh": 150, "need": 14},
        15: {"gap": 210, "ow": 56, "oh": 140, "need": 16},
    }

    THEMES = {
        1:  ((135, 206, 235), (90, 160, 105), (46, 168, 72), (28, 120, 48), (120, 72, 32), BLACK, "meadow"),
        2:  ((28, 70, 48), (18, 90, 40), (16, 78, 32), (10, 48, 20), (40, 28, 16), WHITE, "jungle"),
        3:  ((250, 196, 120), (196, 140, 78), (214, 170, 96), (176, 128, 64), (130, 82, 42), BLACK, "desert"),
        4:  ((10, 14, 42), (22, 26, 58), (18, 22, 40), (12, 14, 28), (170, 170, 80), WHITE, "city"),
        5:  ((186, 214, 232), (210, 220, 230), (236, 242, 248), (200, 214, 226), (120, 140, 160), BLACK, "snow"),
        6:  ((78, 22, 16), (48, 18, 16), (36, 16, 14), (22, 10, 10), (96, 28, 16), WHITE, "lava"),
        7:  ((120, 196, 230), (64, 150, 190), (232, 196, 120), (196, 156, 82), (72, 110, 130), BLACK, "beach"),
        8:  ((18, 16, 28), (32, 28, 40), (42, 36, 48), (24, 20, 30), (90, 80, 110), WHITE, "cave"),
        9:  ((232, 150, 90), (170, 90, 40), (150, 78, 32), (110, 52, 22), (90, 42, 18), WHITE, "autumn"),
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
            except Exception:
                self.sounds = {}

        def play(self, name):
            s = self.sounds.get(name)
            if not s:
                return
            try:
                s.stop()
                s.play()
            except Exception:
                pass

        def make_obstacles(self):
            c = self.level_cfg()
            self.obstacles = [[760 + i * c["gap"], 430, c["ow"], c["oh"]]
                              for i in range(4)]

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
            if self.won or self.transition:
                return
            if self.py >= GROUND_Y - 1:
                self.vel = JUMP
                self.play("jump")

        def in_rect(self, pos, r):
            gx, gy = pos
            return r[0] <= gx <= r[0] + r[2] and r[1] <= gy <= r[1] + r[3]

        def to_game(self, touch):
            s, ox, oy = self.view()
            if s <= 0:
                return 0, 0
            return (touch.x - ox) / s, H - (touch.y - oy) / s

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
            except Exception:
                Clock.unschedule(self.update)
                self.show_error(traceback.format_exc())

        def show_error(self, msg):
            from kivy.uix.label import Label
            self.canvas.clear()
            self.clear_widgets()
            self.add_widget(Label(text=msg, font_size="12sp", pos=self.pos,
                                  size=self.size, text_size=self.size,
                                  halign="left", valign="top"))

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
                hit = (self.px < o[0] + o[2] and self.px + self.pw > o[0]
                       and self.py < o[1] + o[3] and self.py + self.ph > o[1])
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
            Ellipse(pos=(ox + x * s, oy + (H - y - h) * s),
                    size=(max(1, w * s), max(1, h * s)))

        def circle(self, c, cx, cy, r, a=1):
            self.ellipse(c, cx - r, cy - r, 2 * r, 2 * r, a)

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

        def arc_top(self, c, x, y, w, h, width):
            s, ox, oy = self.view()
            self.col(c)
            cx, cy = x + w / 2.0, y + h / 2.0
            pts = []
            for i in range(25):
                a = math.pi * i / 24
                gx = cx + (w / 2.0) * math.cos(a)
                gy = cy - (h / 2.0) * math.sin(a)
                pts += [ox + gx * s, oy + (H - gy) * s]
            Line(points=pts, width=max(1, width * s))

        def text(self, txt, size, c, x, y, center=False):
            s, ox, oy = self.view()
            key = (txt, int(max(8, size * s)))
            tex = self._text_cache.get(key)
            if tex is None:
                if len(self._text_cache) > 400:
                    self._text_cache.clear()
                lab = CoreLabel(text=txt, font_size=key[1])
                lab.refresh()
                tex = lab.texture
                self._text_cache[key] = tex
            if tex is None:
                return
            tw, th = tex.size
            gx = ox + x * s - (tw / 2.0 if center else 0)
            gy = oy + (H - y) * s - th
            self.col(c)
            Rectangle(texture=tex, pos=(gx, gy), size=(tw, th))

        def cloud(self, x, y, sc, c):
            self.ellipse(c, x, y, 70 * sc, 28 * sc)
            self.ellipse(c, x + 22 * sc, y - 12 * sc, 46 * sc, 34 * sc)
            self.ellipse(c, x + 48 * sc, y, 54 * sc, 24 * sc)

        def scene(self):
            sky, hill, ground, ground2, ocol, tcol, kind = self.theme()
            self.rect(sky, 0, 0, W, H)
            bob = math.sin(self.tick * 0.03)

            if kind == "space":
                for i in range(28):
                    sx = (i * 97 + self.tick) % 940 - 20
                    sy = 20 + (i * 53) % 300
                    self.circle(WHITE, sx, sy, 1 + (i % 3), 0.85)
                self.circle((240, 230, 190), 760, 90, 34)
                self.circle((20, 24, 48), 748, 82, 28)
            elif kind == "city":
                self.circle((230, 230, 210), 140, 78, 28)
                for i, (x, bh) in enumerate(((30, 180), (130, 240), (250, 160),
                                             (380, 280), (520, 200), (660, 260), (800, 190))):
                    self.rect((28 + i * 3, 32, 62), x, 430 - bh, 78, bh, 2)
                    for wy in range(450 - bh, 410, 36):
                        self.rect(YELLOW, x + 12, wy, 12, 14, 2)
                        self.rect(YELLOW, x + 42, wy, 12, 14, 2)
            elif kind == "cave":
                self.circle((70, 60, 40), 700, 70, 18, 0.7)
                for x in (40, 180, 340, 520, 700):
                    self.polygon((26, 24, 34), [(x, 300), (x + 40, 80), (x + 110, 300)])
            elif kind == "lava":
                self.circle((255, 120, 40), 730, 100, 58)
                self.circle((255, 210, 80), 730, 100, 28)
                self.polygon((50, 18, 16), [(0, 340), (160, 150), (320, 340)])
                self.polygon((70, 24, 18), [(280, 350), (520, 130), (760, 350)])
            elif kind == "snow":
                self.circle(WHITE, 760, 80, 36)
                self.polygon((225, 230, 236), [(0, 340), (180, 170), (360, 340)])
                self.polygon((210, 218, 228), [(300, 350), (540, 150), (780, 350)])
                for i in range(16):
                    self.circle(WHITE, (i * 70 + self.tick) % 940, 40 + (i * 37) % 220, 2, 0.8)
            elif kind == "desert":
                self.circle((255, 214, 80), 760, 86, 50)
                self.polygon((196, 142, 80), [(0, 350), (200, 200), (380, 350)])
                self.polygon((176, 122, 68), [(300, 360), (540, 180), (800, 360)])
            elif kind == "beach":
                self.circle(YELLOW, 120, 80, 42)
                self.cloud(280, 70, 1.1, WHITE)
                self.cloud(560, 110, 0.9, WHITE)
                self.rect((64, 156, 198), 0, 250, W, 120)
                self.rect((40, 120, 170), 0, 300, W, 70)
            elif kind == "jungle":
                self.cloud(100, 60, 1.0, (180, 210, 170))
                for x in (20, 160, 340, 520, 700, 840):
                    self.rect((36, 24, 14), x, 210, 28, 220)
                    self.circle((16, 90, 36), x + 14, 190, 62)
            elif kind == "autumn":
                self.circle((255, 170, 70), 720, 90, 48)
                self.polygon((150, 70, 30), [(0, 340), (170, 180), (340, 340)])
                for x in (80, 300, 560, 780):
                    self.rect((90, 48, 22), x, 250, 18, 180)
                    self.circle((190, 60, 24), x + 8, 240, 42)
            elif kind == "sakura":
                self.circle((255, 244, 210), 150, 78, 36)
                self.cloud(420, 60, 1.0, WHITE)
                for x in (60, 250, 470, 700):
                    self.rect((92, 58, 48), x, 250, 16, 180)
                    self.circle((235, 120, 160), x + 8, 230, 48)
                    self.circle((255, 180, 200), x + 28, 250, 22)
            elif kind == "swamp":
                self.cloud(200, 50, 1.3, (70, 90, 60))
                for x in (40, 220, 430, 650):
                    self.ellipse((24, 40, 22), x, 300, 150, 36, 0.8)
                    self.rect((40, 28, 16), x + 40, 230, 10, 80)
            elif kind == "ice":
                self.polygon((200, 220, 235), [(0, 330), (120, 140), (240, 330)])
                self.polygon((170, 200, 220), [(200, 350), (400, 120), (620, 350)])
                self.polygon((190, 215, 230), [(560, 340), (730, 160), (900, 340)])
            elif kind == "canyon":
                self.circle((255, 200, 90), 160, 90, 46)
                self.polygon((150, 60, 36), [(0, 360), (140, 140), (280, 360)])
                self.polygon((120, 42, 28), [(220, 370), (460, 120), (700, 370)])
                self.polygon((90, 30, 22), [(620, 360), (780, 180), (920, 360)])
            elif kind == "final":
                self.circle((255, 210, 90), 450, 110 + bob * 6, 54)
                self.circle((255, 240, 180), 450, 110 + bob * 6, 24)
                for i in range(10):
                    self.circle((255, 220, 120), (i * 90 + 20), 40 + (i % 4) * 30, 2, 0.9)
            else:
                self.circle(YELLOW, 760, 78, 42)
                self.cloud(80, 55, 1.15, WHITE)
                self.cloud(360, 95, 0.85, WHITE)
                self.polygon((100, 168, 112), [(0, 340), (180, 175), (360, 340)])
                self.polygon((78, 148, 100), [(280, 350), (520, 160), (760, 350)])
                for x in (50, 340, 640):
                    self.rect(BROWN, x, 280, 18, 150)
                    self.circle(DARKGREEN, x + 9, 265, 46)

            self.rect(ground2, 0, 455, W, 95)
            self.rect(ground, 0, 430, W, 28)
            if kind == "lava":
                for x in range(20, W, 130):
                    self.ellipse((255, 90, 24), x, 448, 78, 22)
            elif kind == "beach":
                self.rect((40, 130, 180), 0, 430, W, 10)
            elif kind == "snow":
                self.rect(WHITE, 0, 424, W, 10)
            return ocol, tcol

        def dog(self, x, y):
            wag = math.sin(self.tick * 0.35) * 8
            self.line(DOGDARK, (x + 16, y + 30), (x - 8, y + 16 + wag), 7)
            self.ellipse(DOG, x + 8, y + 24, 52, 34)
            self.ellipse((210, 160, 110), x + 14, y + 30, 28, 16)
            self.circle(DOG, x + 54, y + 22, 23)
            self.ellipse(DOGDARK, x + 30, y - 2, 15, 30)
            self.ellipse(DOGDARK, x + 54, y, 15, 28)
            self.circle(WHITE, x + 62, y + 16, 6)
            self.circle(BLACK, x + 64, y + 16, 3)
            self.ellipse(BLACK, x + 70, y + 26, 12, 8)
            self.circle(PINK, x + 78, y + 30, 4)
            self.rect(DOGDARK, x + 18, y + 46, 10, 18, 4)
            self.rect(DOGDARK, x + 42, y + 46, 10, 18, 4)
            self.circle(PINK, x + 23, y + 46, 4)
            self.circle(PINK, x + 47, y + 46, 4)

        def cat(self, x, y):
            c = (12, 12, 16)
            self.ellipse(c, x - 90, y + 80, 180, 170)
            self.circle(c, x, y, 105)
            self.polygon(c, [(x - 85, y - 60), (x - 65, y - 145), (x - 10, y - 80)])
            self.polygon(c, [(x + 10, y - 80), (x + 65, y - 145), (x + 85, y - 60)])
            self.ellipse(YELLOW, x - 65, y - 25, 38, 55)
            self.ellipse(YELLOW, x + 27, y - 25, 38, 55)
            self.ellipse(BLACK, x - 52, y - 15, 8, 35)
            self.ellipse(BLACK, x + 40, y - 15, 8, 35)
            self.polygon(PINK, [(x - 14, y + 30), (x + 14, y + 30), (x, y + 48)])
            self.arc_top(WHITE, x - 65, y + 35, 130, 95, 7)

        def obstacle(self, o, color):
            x, y, w, h = o
            dark = tuple(max(0, v - 40) for v in color)
            light = tuple(min(255, v + 50) for v in color)
            self.rect(dark, x + 4, y + 6, w, h, 8)
            self.rect(color, x, y, w, h, 8)
            self.rect(light, x + 4, y + 6, max(6, w * 0.28), h - 14, 4)
            self.rect(dark, x, y, w, 10, 4)

        def draw(self):
            self.canvas.clear()
            with self.canvas:
                self.col(BLACK)
                Rectangle(pos=self.pos, size=self.size)

                if self.won:
                    self.rect((18, 12, 36), 0, 0, W, H)
                    self.circle((255, 210, 80), 450, 150, 60)
                    self.text("YOU WIN!", 72, YELLOW, W // 2, 280, True)
                    self.text("Score: %d" % self.score, 36, WHITE, W // 2, 360, True)
                    self.text("Tap to play again", 28, WHITE, W // 2, 430, True)
                    return

                if self.transition:
                    self.rect(BLACK, 0, 0, W, H)
                    # گربه از لول ۵ به بعد راه می‌رود
                    walk = math.sin(self.ttime * 0.12) * 90
                    cat_x = W // 2 + walk
                    cy = 210 + int(math.sin(self.ttime * 0.1) * 8)
                    self.cat(cat_x, cy)

                    self.text("HAHAHAHA!", 54, WHITE, W // 2, 400, True)
                    if self.ttime > 40:
                        self.text("MEOW!", 42, YELLOW, W // 2 + 120, 340, True)
                    if self.ttime > 80:
                        self.text("RUN DOGGY!", 36, WHITE, W // 2 - 100, 470, True)
                    self.text("LEVEL %d" % self.level, 36, YELLOW, W // 2, 520, True)
                    return

                ocol, tcol = self.scene()
                self.dog(self.px, self.py)
                for o in self.obstacles:
                    if -80 < o[0] < W + 40:
                        self.obstacle(o, ocol)

                b = self.jump_btn
                self.rect((40, 40, 48), b[0] + 4, b[1] + 4, b[2], b[3], 16)
                self.rect((255, 196, 40), b[0], b[1], b[2], b[3], 16)
                self.text("JUMP", 32, BLACK, b[0] + 48, b[1] + 22)

                self.rect((0, 0, 0), 12, 12, 250, 92, 12, 0.35)
                self.text("Score  %d" % self.score, 26, WHITE, 28, 28)
                self.text("Level  %d / %d" % (self.level, MAX_LEVEL), 26, WHITE, 28, 58)
                self.text("%d / %d" % (self.passed, self.level_cfg()["need"]), 22, YELLOW, 28, 88)

    class DogRunnerApp(App):
        def build(self):
            self.title = "Dog Runner"
            try:
                return Game(self.user_data_dir)
            except Exception:
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
