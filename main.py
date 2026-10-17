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
                return Label(
                    text=text,
                    font_size="12sp",
                    text_size=(800, None),
                    halign="left",
                )

        ErrorApp().run()
    except Exception:
        print(text)


try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.audio import SoundLoader
    from kivy.core.text import Label as CoreLabel
    from kivy.core.window import Window
    from kivy.graphics import (
        Color, Ellipse, Line, Rectangle,
        RoundedRectangle, Triangle,
    )
    from kivy.uix.widget import Widget

    W, H = 900, 550
    WHITE = (255, 255, 255)
    BLACK = (15, 15, 20)
    YELLOW = (255, 215, 40)

    GRAVITY = 0.82
    JUMP = -15.4
    GROUND_Y = 385
    MAX_LEVEL = 25
    FIXED_SPEED = 7.5
    MAX_LIVES = 5

    LEVELS = {
        1:  {"gap": 440, "ow": 44, "oh": 50, "need": 7},
        2:  {"gap": 410, "ow": 48, "oh": 65, "need": 8},
        3:  {"gap": 385, "ow": 52, "oh": 75, "need": 8},
        4:  {"gap": 360, "ow": 46, "oh": 95, "need": 9},
        5:  {"gap": 340, "ow": 56, "oh": 78, "need": 9},
        6:  {"gap": 325, "ow": 42, "oh": 115, "need": 10},
        7:  {"gap": 310, "ow": 50, "oh": 88, "need": 10},
        8:  {"gap": 295, "ow": 44, "oh": 125, "need": 11},
        9:  {"gap": 280, "ow": 58, "oh": 85, "need": 11},
        10: {"gap": 265, "ow": 38, "oh": 138, "need": 12},
        11: {"gap": 255, "ow": 54, "oh": 98, "need": 12},
        12: {"gap": 245, "ow": 44, "oh": 128, "need": 13},
        13: {"gap": 235, "ow": 62, "oh": 90, "need": 13},
        14: {"gap": 225, "ow": 40, "oh": 145, "need": 14},
        15: {"gap": 210, "ow": 55, "oh": 140, "need": 15},
        16: {"gap": 265, "ow": 44, "oh": 105, "need": 15},
        17: {"gap": 260, "ow": 48, "oh": 112, "need": 16},
        18: {"gap": 255, "ow": 42, "oh": 125, "need": 16},
        19: {"gap": 250, "ow": 50, "oh": 115, "need": 17},
        20: {"gap": 245, "ow": 44, "oh": 135, "need": 17},
        21: {"gap": 240, "ow": 42, "oh": 128, "need": 18},
        22: {"gap": 235, "ow": 48, "oh": 120, "need": 18},
        23: {"gap": 230, "ow": 40, "oh": 140, "need": 19},
        24: {"gap": 225, "ow": 44, "oh": 135, "need": 19},
        25: {"gap": 220, "ow": 46, "oh": 140, "need": 20},
    }

    THEMES = {
        1: {"sky": (140, 210, 245), "ground": (65, 165, 80),
            "obs": (140, 85, 45), "name": "meadow"},
        2: {"sky": (25, 75, 50), "ground": (15, 95, 40),
            "obs": (75, 45, 20), "name": "jungle"},
        3: {"sky": (255, 205, 130), "ground": (215, 155, 80),
            "obs": (50, 135, 55), "name": "desert"},
        4: {"sky": (12, 16, 45), "ground": (45, 48, 60),
            "obs": (160, 50, 50), "name": "city"},
        5: {"sky": (195, 225, 245), "ground": (235, 245, 255),
            "obs": (110, 150, 180), "name": "snow"},
        6: {"sky": (65, 18, 15), "ground": (40, 15, 15),
            "obs": (220, 85, 20), "name": "lava"},
        7: {"sky": (115, 205, 240), "ground": (240, 205, 135),
            "obs": (205, 120, 50), "name": "beach"},
        8: {"sky": (22, 18, 35), "ground": (48, 42, 58),
            "obs": (160, 75, 220), "name": "cave"},
        9: {"sky": (245, 160, 100), "ground": (165, 85, 35),
            "obs": (115, 55, 25), "name": "autumn"},
        10: {"sky": (8, 10, 28), "ground": (35, 40, 65),
             "obs": (60, 180, 210), "name": "space"},
        11: {"sky": (255, 200, 215), "ground": (110, 160, 80),
             "obs": (130, 70, 45), "name": "sakura"},
        12: {"sky": (40, 60, 42), "ground": (32, 52, 28),
             "obs": (70, 95, 45), "name": "swamp"},
        13: {"sky": (160, 205, 235), "ground": (190, 225, 245),
             "obs": (115, 175, 220), "name": "ice"},
        14: {"sky": (255, 130, 80), "ground": (150, 65, 35),
             "obs": (185, 85, 45), "name": "canyon"},
        15: {"sky": (30, 20, 55), "ground": (50, 32, 75),
             "obs": (240, 195, 60), "name": "final"},
        16: {"sky": (15, 30, 55), "ground": (25, 65, 60),
             "obs": (150, 70, 210), "name": "mushroom"},
        17: {"sky": (255, 195, 225), "ground": (180, 110, 180),
             "obs": (240, 85, 155), "name": "candy"},
        18: {"sky": (35, 42, 65), "ground": (45, 65, 80),
             "obs": (100, 135, 165), "name": "storm"},
        19: {"sky": (210, 185, 140), "ground": (130, 115, 75),
             "obs": (150, 135, 100), "name": "ruins"},
        20: {"sky": (35, 45, 55), "ground": (65, 70, 80),
             "obs": (210, 130, 35), "name": "factory"},
        21: {"sky": (135, 200, 165), "ground": (45, 110, 65),
             "obs": (65, 155, 65), "name": "bamboo"},
        22: {"sky": (100, 195, 235), "ground": (220, 180, 110),
             "obs": (125, 75, 40), "name": "pirate"},
        23: {"sky": (145, 165, 185), "ground": (90, 115, 125),
             "obs": (100, 125, 150), "name": "mist"},
        24: {"sky": (15, 12, 30), "ground": (38, 25, 55),
             "obs": (130, 65, 170), "name": "shadow"},
        25: {"sky": (75, 40, 100), "ground": (145, 100, 45),
             "obs": (245, 195, 65), "name": "palace"},
    }

    def make_sound(path, typ):
        rate = 22050
        length = (
            0.16 if typ == "coin"
            else 1.0 if typ == "laugh"
            else 0.25
        )
        data = bytearray()
        samples = int(rate * length)

        for i in range(samples):
            t = i / rate

            if typ == "coin":
                # Soft ding with a smooth attack and fade-out.
                attack = min(1.0, t / 0.006)
                release = min(
                    1.0, (samples - 1 - i) / (rate * 0.025)
                )
                envelope = attack * release * math.exp(-20 * t)
                tone = (
                    math.sin(2 * math.pi * 880 * t)
                    + 0.22 * math.sin(2 * math.pi * 1320 * t)
                ) / 1.22
                v = tone * envelope * 0.18
            else:
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

            data += struct.pack("<h", int(v * 32767))

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
            self._text_cache = {}

            self.level = 1
            self.score = 0
            self.coins = 0
            self.lives = MAX_LIVES

            self.px = 140.0
            self.py = float(GROUND_Y)
            self.pw, self.ph = 70, 58
            self.vel = 0.0
            self.speed = FIXED_SPEED

            self.transition = False
            self.won = False
            self.ttime = 0
            self.tick = 0
            self.accumulator = 0.0

            self.obstacles = []
            self.coin_items = []
            self.jump_btn = (690, 455, 180, 72)

            self.begin_level()
            Clock.schedule_interval(self.update, 1 / 60.0)

        def level_cfg(self):
            return LEVELS[self.level]

        def theme(self):
            return THEMES[self.level]

        def _load_sounds(self, directory):
            try:
                os.makedirs(directory, exist_ok=True)
                for name in ("jump", "hit", "laugh", "win", "coin"):
                    path = os.path.join(directory, name + ".wav")
                    make_sound(path, name)
                    self.sounds[name] = SoundLoader.load(path)
            except Exception:
                self.sounds = {}

        def play(self, name):
            sound = self.sounds.get(name)
            if sound:
                try:
                    sound.stop()
                    sound.play()
                except Exception:
                    pass

        def make_obstacles(self):
            cfg = self.level_cfg()
            self.obstacles = []
            for i in range(4):
                self.obstacles.append([
                    850.0 + i * cfg["gap"],
                    GROUND_Y - cfg["oh"] + 54,
                    cfg["ow"],
                    cfg["oh"],
                ])

        def make_coins(self):
            # Exactly level * 5 coins per level attempt.
            cfg = self.level_cfg()
            count = self.level * 5
            self.coin_total = count
            self.level_coins = 0
            self.coin_items = []

            for i in range(count):
                section = i * cfg["need"] / float(count)
                obstacle_index = int(section)
                fraction = section - obstacle_index

                if fraction < 0.38:
                    x = (
                        850 + obstacle_index * cfg["gap"]
                        + cfg["ow"] / 2
                    )
                    y = min(315, GROUND_Y - cfg["oh"] + 28)
                    x += fraction * 45
                else:
                    x = (
                        850 + obstacle_index * cfg["gap"]
                        + cfg["ow"]
                        + (cfg["gap"] - cfg["ow"]) * 0.55
                        + (fraction - 0.6) * 30
                    )
                    y = 405

                self.coin_items.append([float(x), float(y)])

        def begin_level(self):
            self.px = 140.0
            self.py = float(GROUND_Y)
            self.vel = 0.0
            self.passed = 0
            self.speed = FIXED_SPEED

            # Restore these values if the attempt fails.
            self.start_score = self.score
            self.start_coins = self.coins

            self.make_obstacles()
            self.make_coins()

        def reset_level(self):
            self.lives -= 1
            self.score = self.start_score
            self.coins = self.start_coins

            if self.lives <= 0:
                if self.level <= 10:
                    self.level = 1
                elif self.level <= 20:
                    self.level = 10
                else:
                    self.level = 20

                self.lives = MAX_LIVES
                self.score = 0
                self.coins = 0

            self.transition = False
            self.ttime = 0
            self.begin_level()
            self.play("hit")

        def restart_game(self):
            self.level = 1
            self.score = 0
            self.coins = 0
            self.lives = MAX_LIVES
            self.won = False
            self.transition = False
            self.ttime = 0
            self.begin_level()

        def jump(self):
            if self.won or self.transition:
                return
            if self.py >= GROUND_Y - 2:
                self.vel = JUMP
                self.play("jump")

        def on_touch_down(self, touch):
            if self.won:
                self.restart_game()
            else:
                self.jump()
            return True

        def update(self, dt):
            try:
                # Fixed simulation steps keep speed consistent.
                self.accumulator += min(dt, 0.1)
                while self.accumulator >= 1 / 60.0:
                    self.step()
                    self.accumulator -= 1 / 60.0
                self.draw()
            except Exception:
                Clock.unschedule(self.update)
                self.show_error(traceback.format_exc())

        def show_error(self, msg):
            from kivy.uix.label import Label

            self.canvas.clear()
            self.clear_widgets()
            self.add_widget(Label(
                text=msg,
                font_size="12sp",
                pos=self.pos,
                size=self.size,
                text_size=self.size,
                halign="left",
                valign="top",
            ))

        def step(self):
            self.tick += 1

            if self.won:
                return

            if self.transition:
                self.ttime += 1
                if self.ttime >= 150:
                    self.transition = False
                    self.ttime = 0
                    self.begin_level()
                return

            self.vel += GRAVITY
            self.py += self.vel

            if self.py >= GROUND_Y:
                self.py = float(GROUND_Y)
                self.vel = 0.0

            cfg = self.level_cfg()

            dog_box = (
                self.px + 10,
                self.py - 8,
                self.pw - 10,
                55,
            )

            for obstacle in self.obstacles:
                obstacle[0] -= self.speed

            for coin in self.coin_items:
                coin[0] -= self.speed

            for o in self.obstacles:
                hit = (
                    dog_box[0] < o[0] + o[2]
                    and dog_box[0] + dog_box[2] > o[0]
                    and dog_box[1] < o[1] + o[3]
                    and dog_box[1] + dog_box[3] > o[1]
                )
                if hit:
                    self.reset_level()
                    return

            remaining = []
            collected = False

            for x, y in self.coin_items:
                nearest_x = max(
                    dog_box[0], min(x, dog_box[0] + dog_box[2])
                )
                nearest_y = max(
                    dog_box[1], min(y, dog_box[1] + dog_box[3])
                )

                if (x - nearest_x) ** 2 + (y - nearest_y) ** 2 <= 15 ** 2:
                    self.coins += 1
                    self.level_coins += 1
                    collected = True
                elif x > -30:
                    remaining.append([x, y])

            self.coin_items = remaining
            if collected:
                self.play("coin")

            for o in self.obstacles:
                if o[0] + o[2] < -30:
                    o[0] = max(
                        other[0] for other in self.obstacles
                    ) + cfg["gap"]

                    self.passed += 1
                    self.score += 1

                    if self.passed >= cfg["need"]:
                        self.complete_level()
                        return

        def complete_level(self):
            if self.level >= MAX_LEVEL:
                self.won = True
                self.play("win")
                return

            self.level += 1

            if self.level % 5 == 0:
                self.transition = True
                self.ttime = 0
                self.play("laugh")
            else:
                self.begin_level()

        def view(self):
            scale = (
                min(self.width / float(W), self.height / float(H))
                if self.width and self.height else 1
            )
            ox = self.x + (self.width - W * scale) / 2
            oy = self.y + (self.height - H * scale) / 2
            return scale, ox, oy

        def col(self, color, alpha=1):
            Color(
                color[0] / 255.0,
                color[1] / 255.0,
                color[2] / 255.0,
                alpha,
            )

        def rect(self, color, x, y, w, h, radius=0, a=1):
            scale, ox, oy = self.view()
            self.col(color, a)
            pos = (ox + x * scale, oy + (H - y - h) * scale)
            size = (max(1, w * scale), max(1, h * scale))

            if radius:
                RoundedRectangle(
                    pos=pos, size=size, radius=[radius * scale]
                )
            else:
                Rectangle(pos=pos, size=size)

        def ellipse(self, color, x, y, w, h, a=1):
            scale, ox, oy = self.view()
            self.col(color, a)
            Ellipse(
                pos=(ox + x * scale, oy + (H - y - h) * scale),
                size=(max(1, w * scale), max(1, h * scale)),
            )

        def polygon(self, color, points):
            scale, ox, oy = self.view()
            self.col(color)
            flat = []
            for x, y in points:
                flat.extend([ox + x * scale, oy + (H - y) * scale])

            if len(points) == 3:
                Triangle(points=flat)
            else:
                Line(points=flat, width=1.5, close=True)

        def line(self, color, p1, p2, width):
            scale, ox, oy = self.view()
            self.col(color)
            Line(
                points=[
                    ox + p1[0] * scale,
                    oy + (H - p1[1]) * scale,
                    ox + p2[0] * scale,
                    oy + (H - p2[1]) * scale,
                ],
                width=max(1, width * scale),
                cap="round",
            )

        def text(self, txt, size, color, x, y, center=False):
            scale, ox, oy = self.view()
            key = (txt, int(max(8, size * scale)))
            texture = self._text_cache.get(key)

            if texture is None:
                if len(self._text_cache) > 400:
                    self._text_cache.clear()
                label = CoreLabel(text=txt, font_size=key[1])
                label.refresh()
                texture = label.texture
                self._text_cache[key] = texture

            if texture is None:
                return

            tw, th = texture.size
            gx = ox + x * scale - (tw / 2 if center else 0)
            gy = oy + (H - y) * scale - th
            self.col(color)
            Rectangle(texture=texture, pos=(gx, gy), size=(tw, th))

        def dog(self, x, y):
            t = self.tick
            in_air = self.py < GROUND_Y - 2
            wag = math.sin(t * 0.45) * 12
            leg1 = math.sin(t * 0.4) * 8 if not in_air else -6
            leg2 = -leg1 if not in_air else 4

            if not in_air:
                self.ellipse(
                    (20, 20, 25), x + 8, GROUND_Y + 44,
                    60, 10, 0.35,
                )

            self.line(
                (185, 120, 60),
                (x + 8, y + 15),
                (x - 14, y + 5 + wag), 7,
            )
            self.ellipse(
                (170, 110, 55), x + 12 + leg2, y + 26, 12, 22
            )
            self.ellipse(
                (170, 110, 55), x + 46 - leg2, y + 26, 12, 22
            )
            self.ellipse((230, 170, 105), x + 6, y + 8, 54, 34)
            self.ellipse((255, 230, 185), x + 18, y + 16, 32, 22)
            self.ellipse(
                (210, 150, 85), x + 18 + leg1, y + 27, 12, 22
            )
            self.ellipse(
                (210, 150, 85), x + 50 - leg1, y + 27, 12, 22
            )
            self.ellipse((230, 170, 105), x + 40, y - 10, 36, 34)

            ear_sway = math.sin(t * 0.35) * 3
            self.polygon((160, 95, 45), [
                (x + 45, y - 8),
                (x + 36, y + 10 + ear_sway),
                (x + 52, y + 2),
            ])

            self.ellipse((250, 205, 155), x + 58, y - 3, 20, 16)
            self.ellipse((35, 30, 30), x + 72, y - 5, 8, 7)
            self.ellipse(WHITE, x + 54, y - 8, 12, 13)
            self.ellipse((30, 30, 45), x + 58, y - 7, 6, 7)
            self.ellipse(WHITE, x + 60, y - 8, 2.5, 2.5)
            self.rect((220, 45, 55), x + 43, y + 14, 15, 6, 2)
            self.ellipse(YELLOW, x + 49, y + 18, 5, 5)

        def cat(self, x, y):
            color = (90, 85, 95)
            dark = (60, 55, 65)
            self.ellipse(
                (20, 20, 25), x - 65, y + 115, 130, 24, 0.3
            )
            self.ellipse(color, x - 55, y + 35, 110, 85)
            self.ellipse(color, x - 42, y - 15, 84, 70)
            self.polygon(dark, [
                (x - 38, y - 10), (x - 28, y - 40),
                (x - 8, y - 14),
            ])
            self.polygon(dark, [
                (x + 8, y - 14), (x + 28, y - 40),
                (x + 38, y - 10),
            ])
            self.ellipse((255, 235, 80), x - 28, y - 2, 22, 26)
            self.ellipse((255, 235, 80), x + 6, y - 2, 22, 26)
            self.ellipse((25, 25, 25), x - 18, y + 2, 7, 18)
            self.ellipse((25, 25, 25), x + 14, y + 2, 7, 18)
            self.polygon((255, 140, 165), [
                (x - 6, y + 20), (x + 6, y + 20), (x, y + 28),
            ])
            tail = math.sin(self.ttime * 0.16) * 30
            self.line(
                dark, (x - 50, y + 70),
                (x - 95 + tail, y + 50), 12,
            )

        def draw_coin(self, x, y):
            width = 10 + abs(math.sin(self.tick * 0.12)) * 16
            self.ellipse(
                (255, 225, 90), x - width / 2 - 3,
                y - 16, width + 6, 32, 0.22,
            )
            self.ellipse(
                (210, 140, 15), x - width / 2, y - 13, width, 26
            )
            self.ellipse(
                (255, 215, 45), x - width / 2 + 2,
                y - 11, max(2, width - 4), 22,
            )
            if width > 17:
                self.line(
                    (255, 250, 180), (x, y - 7), (x, y + 7), 2
                )

        def obstacle(self, obstacle, color, name):
            x, y, w, h = obstacle
            dark = tuple(max(0, value - 50) for value in color)
            light = tuple(min(255, value + 50) for value in color)

            if name in ("meadow", "jungle", "swamp", "bamboo"):
                self.rect(color, x + 4, y, w - 8, h, 6)
                self.rect(dark, x + 8, y + 4, w - 16, h - 8, 4)
                if name == "bamboo":
                    for offset in range(15, h, 23):
                        self.rect(light, x + 3, y + offset, w - 6, 5, 2)
                else:
                    self.ellipse(
                        (40, 150, 60), x - 4, y - 10, w + 8, 20
                    )

            elif name == "desert":
                green = (45, 155, 60)
                self.rect(green, x + w * 0.3, y, w * 0.4, h, 8)
                self.rect(green, x, y + h * 0.35, w, 14, 6)
                self.rect(green, x, y + h * 0.18, 12, h * 0.22, 5)
                self.rect(
                    green, x + w - 12, y + h * 0.25,
                    12, h * 0.22, 5,
                )

            elif name in ("cave", "ice", "shadow"):
                self.polygon(light, [
                    (x, y + h), (x + w / 2, y), (x + w, y + h),
                ])
                self.polygon(color, [
                    (x + 4, y + h), (x + w / 2, y + 8),
                    (x + w - 4, y + h),
                ])

            elif name == "mushroom":
                self.rect(
                    (185, 170, 220), x + 8, y + 12,
                    w - 16, h - 12, 6,
                )
                self.ellipse(color, x - 5, y - 5, w + 10, 32)
                self.ellipse(WHITE, x + 5, y + 2, 8, 8)
                self.ellipse(WHITE, x + w - 15, y + 8, 7, 7)

            else:
                self.rect(dark, x + 3, y + 3, w, h, 8)
                self.rect(color, x, y, w, h, 8)
                self.rect(
                    light, x + 5, y + 6,
                    max(6, w * 0.26), h - 12, 4,
                )

                if name == "factory":
                    for offset in range(12, h - 5, 24):
                        self.rect(
                            (35, 35, 40), x + 5, y + offset,
                            w - 10, 8, 2,
                        )
                elif name == "pirate":
                    self.line(
                        dark, (x + 4, y + 5),
                        (x + w - 4, y + h - 5), 3,
                    )
                    self.line(
                        dark, (x + w - 4, y + 5),
                        (x + 4, y + h - 5), 3,
                    )
                elif name == "candy":
                    for offset in range(12, h - 8, 22):
                        self.rect(
                            WHITE, x + 3, y + offset, w - 6, 7, 3
                        )

        def draw_background(self, theme):
            name = theme["name"]
            t = self.tick
            self.rect(theme["sky"], 0, 0, W, H)

            if name == "meadow":
                self.ellipse((255, 230, 80), 730, 60, 75, 75)
                self.ellipse(WHITE, 120, 80, 110, 45, 0.8)
                self.ellipse(WHITE, 450, 110, 140, 50, 0.7)
                self.ellipse((50, 140, 65), -50, 310, 480, 220)
                self.ellipse((58, 155, 75), 350, 320, 600, 200)

            elif name == "jungle":
                self.rect((18, 55, 30), 0, 180, W, 250)
                for x in (80, 280, 520, 750):
                    self.rect((55, 35, 15), x + 20, 240, 24, 200)
                    self.ellipse((20, 110, 45), x - 30, 160, 125, 110)
                    self.ellipse((10, 90, 35), x - 15, 120, 95, 80)

            elif name == "desert":
                self.ellipse((255, 220, 110), 720, 50, 85, 85)
                self.ellipse((235, 175, 95), -80, 330, 520, 180)
                self.ellipse((220, 160, 85), 320, 320, 650, 190)

            elif name == "city":
                self.ellipse((240, 240, 250), 750, 50, 60, 60)
                buildings = [
                    (30, 160, 90), (140, 210, 110),
                    (270, 140, 85), (380, 250, 120),
                    (520, 180, 100), (640, 230, 130),
                    (790, 150, 85),
                ]
                for x, y, width in buildings:
                    self.rect((24, 28, 48), x, y, width, 440 - y)
                    for wx in range(x + 12, x + width - 15, 22):
                        for wy in range(y + 16, 420, 28):
                            self.rect(
                                (245, 215, 90), wx, wy,
                                10, 14, 2, 0.85,
                            )

            elif name == "snow":
                self.ellipse((245, 250, 255), 100, 310, 500, 200)
                self.ellipse((230, 238, 250), 480, 330, 500, 180)
                for i in range(16):
                    self.ellipse(
                        WHITE, (i * 59 + t * 2) % W,
                        (i * 37 + t * 3) % 430, 6, 6, 0.75,
                    )
                self.ellipse(WHITE, 700, 360, 48, 48)
                self.ellipse(WHITE, 708, 335, 32, 32)
                self.ellipse((240, 120, 30), 720, 348, 8, 5)

            elif name == "lava":
                self.polygon((45, 18, 18), [
                    (60, 440), (230, 180), (400, 440),
                ])
                self.polygon((55, 22, 22), [
                    (460, 440), (660, 210), (860, 440),
                ])
                self.ellipse((255, 90, 20), 215, 175, 30, 15)
                self.ellipse((255, 90, 20), 645, 205, 30, 15)

            elif name == "beach":
                self.rect((60, 160, 225), 0, 330, W, 100)
                self.ellipse(WHITE, 0, 328, W, 10, 0.4)
                self.ellipse((255, 220, 80), 720, 50, 80, 80)
                self.rect((110, 70, 30), 120, 250, 16, 180)
                self.ellipse((40, 160, 60), 60, 220, 135, 45)

            elif name == "cave":
                for x in range(0, W, 70):
                    height = 45 + (x % 3) * 20
                    self.polygon((35, 30, 48), [
                        (x, 0), (x + 35, height), (x + 70, 0),
                    ])
                self.polygon((180, 80, 255), [
                    (220, 440), (230, 390), (240, 440),
                ])
                self.polygon((130, 60, 230), [
                    (660, 440), (672, 380), (684, 440),
                ])

            elif name == "autumn":
                self.ellipse((255, 180, 60), 750, 60, 70, 70)
                for x in (120, 400, 720):
                    self.rect((90, 50, 25), x + 20, 260, 20, 170)
                    self.ellipse((220, 95, 30), x - 30, 160, 120, 110)
                    self.ellipse((245, 150, 40), x - 10, 190, 80, 75)

            elif name == "space":
                for i in range(25):
                    radius = 3 if i % 2 == 0 else 5
                    self.ellipse(
                        WHITE, (i * 73) % W, (i * 41) % 400,
                        radius, radius, 0.8,
                    )
                self.ellipse((215, 120, 80), 680, 90, 75, 75)
                self.ellipse((240, 190, 130), 645, 118, 145, 20, 0.6)

            elif name == "sakura":
                self.ellipse((255, 235, 220), 750, 50, 70, 70)
                for x in (100, 460, 760):
                    self.rect((75, 45, 30), x + 18, 250, 20, 180)
                    self.ellipse((255, 160, 185), x - 35, 140, 130, 115)
                    self.ellipse((255, 195, 210), x - 15, 160, 90, 85)

            elif name == "swamp":
                self.rect((25, 42, 25), 0, 360, W, 80)
                for x in (160, 550):
                    self.rect((45, 38, 24), x + 15, 220, 25, 210)
                    self.ellipse((35, 80, 40), x - 30, 140, 120, 95)

            elif name == "ice":
                self.polygon((180, 220, 245), [
                    (100, 440), (250, 170), (420, 440),
                ])
                self.polygon((210, 240, 255), [
                    (350, 440), (520, 210), (690, 440),
                ])

            elif name == "canyon":
                self.ellipse((255, 110, 60), 740, 60, 75, 75)
                self.rect((170, 70, 40), 0, 270, 280, 170)
                self.rect((195, 85, 45), 260, 320, 300, 120)
                self.rect((150, 60, 35), 540, 240, 360, 200)

            elif name == "final":
                self.ellipse((255, 215, 60), 450, 80, 90, 90)
                for x in (90, 280, 620, 810):
                    self.rect((90, 60, 120), x, 210, 35, 230)
                    self.rect((140, 90, 170), x - 10, 195, 55, 20)

            elif name == "mushroom":
                for i, x in enumerate((70, 240, 450, 650, 820)):
                    y = 290 + (i % 2) * 35
                    self.rect(
                        (130, 140, 190), x + 22, y, 20, 150, 8
                    )
                    self.ellipse(
                        (115, 65, 180), x - 20, y - 35, 105, 60
                    )
                    for dx in (0, 30, 55):
                        self.ellipse(
                            (140, 245, 235), x + dx, y - 20, 10, 10
                        )
                for i in range(14):
                    self.ellipse(
                        (120, 255, 210), (i * 71 + t) % W,
                        150 + (i * 43) % 240, 4, 4, 0.7,
                    )

            elif name == "candy":
                self.ellipse((255, 230, 245), -70, 300, 480, 200)
                self.ellipse((200, 160, 235), 400, 300, 550, 220)
                for i, x in enumerate((100, 320, 580, 800)):
                    self.rect(WHITE, x + 20, 250, 9, 180, 4)
                    self.ellipse(
                        (255, 110 + i * 20, 170),
                        x - 15, 180, 80, 80,
                    )
                    self.ellipse(WHITE, x + 5, 200, 40, 40, 0.7)

            elif name == "storm":
                for x in (40, 280, 560, 770):
                    self.ellipse((65, 72, 95), x, 90, 160, 65)
                for i in range(30):
                    x = (i * 47 - t * 5) % W
                    y = (i * 31 + t * 10) % 430
                    self.line(
                        (135, 175, 215), (x, y), (x - 8, y + 20), 1
                    )
                if t % 210 < 10:
                    self.line(YELLOW, (650, 140), (615, 210), 5)
                    self.line(YELLOW, (615, 210), (650, 205), 5)
                    self.line(YELLOW, (650, 205), (610, 285), 5)

            elif name == "ruins":
                self.ellipse((240, 210, 145), 740, 65, 75, 75)
                for i, x in enumerate((60, 240, 480, 730)):
                    top = 230 + (i % 2) * 45
                    self.rect(
                        (145, 130, 100), x, top, 45, 440 - top
                    )
                    self.rect(
                        (175, 160, 120), x - 10, top - 15, 65, 20
                    )
                    self.rect(
                        (110, 105, 75), x + 8, top + 20, 7, 100
                    )
                self.rect((155, 140, 105), 60, 215, 225, 20)

            elif name == "factory":
                for x in (50, 300, 580):
                    self.rect((55, 65, 75), x, 280, 190, 160)
                    self.rect((80, 85, 90), x + 35, 150, 30, 135)
                    for i in range(3):
                        self.ellipse(
                            (105, 110, 120),
                            x + 20 + i * 12,
                            130 - i * 30 - (t % 40),
                            55 + i * 12, 40, 0.4,
                        )
                    for dx in (20, 75, 130):
                        self.rect(
                            (255, 180, 70), x + dx, 320, 30, 40, 3
                        )

            elif name == "bamboo":
                self.ellipse((210, 235, 190), 720, 70, 80, 80)
                for i in range(12):
                    x = i * 83
                    top = 100 + (i % 3) * 40
                    self.rect(
                        (45, 120, 65), x, top, 15, 440 - top, 5
                    )
                    for y in range(top + 30, 430, 45):
                        self.rect(
                            (95, 160, 85), x - 2, y, 19, 5, 2
                        )
                        self.ellipse(
                            (45, 140, 65), x + 4, y - 22, 45, 13
                        )

            elif name == "pirate":
                self.rect((40, 140, 195), 0, 315, W, 125)
                self.ellipse((240, 205, 135), -90, 360, 460, 130)
                self.ellipse((240, 205, 135), 550, 350, 440, 140)
                self.rect((90, 55, 30), 400, 330, 180, 35, 10)
                self.rect((100, 65, 35), 480, 190, 8, 145)
                self.polygon((245, 235, 210), [
                    (490, 195), (490, 305), (565, 305),
                ])
                self.rect((25, 25, 30), 440, 195, 40, 28)
                self.ellipse(WHITE, 451, 200, 16, 13)

            elif name == "mist":
                for x, height in ((-70, 200), (220, 270), (530, 180)):
                    self.polygon((100, 125, 150), [
                        (x, 440), (x + 180, height), (x + 390, 440),
                    ])
                    self.polygon((220, 230, 235), [
                        (x + 140, height + 55),
                        (x + 180, height),
                        (x + 220, height + 55),
                    ])
                for i in range(4):
                    x = (i * 280 + t * 0.5) % 1200 - 250
                    self.ellipse(
                        (225, 235, 240), x, 260 + i * 32,
                        400, 65, 0.3,
                    )

            elif name == "shadow":
                self.ellipse((185, 150, 225), 730, 65, 75, 75)
                self.ellipse(theme["sky"], 710, 52, 75, 75)
                for x in (70, 260, 490, 740):
                    self.rect((30, 20, 45), x, 210, 22, 230)
                    self.line(
                        (30, 20, 45),
                        (x + 10, 270), (x - 35, 210), 10,
                    )
                    self.line(
                        (30, 20, 45),
                        (x + 10, 290), (x + 60, 220), 10,
                    )
                    self.ellipse((180, 80, 230), x + 2, 330, 5, 5)
                    self.ellipse((180, 80, 230), x + 12, 330, 5, 5)

            elif name == "palace":
                self.ellipse((255, 225, 130), 720, 60, 85, 85)
                self.rect((185, 145, 70), 240, 240, 420, 200)
                for x in (200, 350, 510, 650):
                    self.rect((220, 180, 85), x, 180, 65, 260)
                    self.polygon((245, 205, 75), [
                        (x - 10, 180), (x + 32, 115),
                        (x + 75, 180),
                    ])
                    self.rect(
                        (90, 55, 100), x + 20, 230, 25, 45, 10
                    )
                self.rect((100, 60, 70), 410, 330, 80, 110, 30)

            self.rect(theme["ground"], 0, 440, W, 110)
            self.rect((0, 0, 0), 0, 440, W, 4, a=0.2)

        def draw(self):
            self.canvas.clear()

            with self.canvas:
                self.col(BLACK)
                Rectangle(pos=self.pos, size=self.size)

                if self.won:
                    self.rect((15, 10, 30), 0, 0, W, H)
                    self.text(
                        "YOU WIN!", 72, YELLOW, W / 2, 100, True
                    )
                    self.text(
                        "All 25 levels completed!", 30,
                        WHITE, W / 2, 205, True,
                    )
                    self.text(
                        "Score: %d" % self.score, 32,
                        WHITE, W / 2, 270, True,
                    )
                    self.text(
                        "Coins: %d" % self.coins, 32,
                        YELLOW, W / 2, 325, True,
                    )
                    self.text(
                        "Tap anywhere to play again!", 26,
                        WHITE, W / 2, 430, True,
                    )
                    return

                if self.transition:
                    self.rect((12, 10, 22), 0, 0, W, H)
                    x = W / 2 + math.sin(self.ttime * 0.12) * 110
                    y = 210 + math.sin(self.ttime * 0.1) * 8
                    self.cat(x, y)
                    self.text(
                        "HAHAHAHA!", 56, WHITE, W / 2, 375, True
                    )
                    if self.ttime > 35:
                        self.text(
                            "MEOW! YOU CANNOT PASS!", 36,
                            YELLOW, W / 2, 435, True,
                        )
                    self.text(
                        "LEVEL %d" % self.level, 34,
                        (120, 230, 140), W / 2, 490, True,
                    )
                    return

                theme = self.theme()
                self.draw_background(theme)

                for o in self.obstacles:
                    if -80 < o[0] < W + 50:
                        self.obstacle(o, theme["obs"], theme["name"])

                for x, y in self.coin_items:
                    if -30 < x < W + 30:
                        self.draw_coin(x, y)

                self.dog(self.px, self.py)

                # Jump button. Tapping anywhere also jumps.
                x, y, width, height = self.jump_btn
                self.rect(
                    (25, 25, 30), x + 4, y + 4,
                    width, height, 18, 0.4,
                )
                self.rect(
                    (255, 195, 45), x, y, width, height, 18
                )
                self.rect(
                    (255, 225, 120), x + 6, y + 6,
                    width - 12, 16, 8, 0.5,
                )
                self.text("JUMP", 32, BLACK, x + 46, y + 24)

                # Score and level panel.
                self.rect((0, 0, 0), 14, 14, 270, 122, 14, 0.55)
                self.text(
                    "Score: %d" % self.score, 23, WHITE, 28, 24
                )
                self.text(
                    "Level: %d / %d" % (self.level, MAX_LEVEL),
                    23, WHITE, 28, 52,
                )
                self.text(
                    "Progress: %d / %d" % (
                        self.passed, self.level_cfg()["need"]
                    ),
                    20, YELLOW, 28, 82,
                )
                self.text(
                    theme["name"].upper(), 16,
                    (210, 225, 245), 28, 108,
                )

                # Lives and coin panel.
                self.rect((0, 0, 0), 610, 14, 276, 108, 14, 0.55)
                self.text(
                    "Lives: %d / 5" % self.lives,
                    25, (255, 140, 150), 628, 24,
                )
                self.text(
                    "Coins: %d" % self.coins,
                    24, YELLOW, 628, 57,
                )
                self.text(
                    "This level: %d / %d" % (
                        self.level_coins, self.coin_total
                    ),
                    19, WHITE, 628, 90,
                )

    class DogRunnerApp(App):
        def build(self):
            self.title = "Dog Runner"
            try:
                return Game(self.user_data_dir)
            except Exception:
                from kivy.uix.label import Label
                return Label(
                    text=traceback.format_exc(),
                    font_size="12sp",
                    text_size=(Window.width, None),
                    halign="left",
                )

        def on_pause(self):
            return True

except Exception:
    ERROR_TEXT = traceback.format_exc()


if __name__ == "__main__":
    if ERROR_TEXT is not None:
        show_fatal(ERROR_TEXT)
    else:
        DogRunnerApp().run()
