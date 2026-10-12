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
    BLACK = (15, 15, 20)
    YELLOW = (255, 215, 40)
    PINK = (240, 110, 130)

    GRAVITY = 0.82
    JUMP = -15.4
    GROUND_Y = 385
    MAX_LEVEL = 15
    FIXED_SPEED = 7.5

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
    }

    THEMES = {
        1:  {"sky": (140, 210, 245), "ground": (65, 165, 80),   "obs": (140, 85, 45),   "name": "meadow"},
        2:  {"sky": (25, 75, 50),    "ground": (15, 95, 40),    "obs": (75, 45, 20),    "name": "jungle"},
        3:  {"sky": (255, 205, 130), "ground": (215, 155, 80),  "obs": (50, 135, 55),   "name": "desert"},
        4:  {"sky": (12, 16, 45),    "ground": (45, 48, 60),    "obs": (160, 50, 50),   "name": "city"},
        5:  {"sky": (195, 225, 245), "ground": (235, 245, 255), "obs": (110, 150, 180), "name": "snow"},
        6:  {"sky": (65, 18, 15),    "ground": (40, 15, 15),    "obs": (220, 85, 20),   "name": "lava"},
        7:  {"sky": (115, 205, 240), "ground": (240, 205, 135), "obs": (205, 120, 50),  "name": "beach"},
        8:  {"sky": (22, 18, 35),    "ground": (48, 42, 58),    "obs": (160, 75, 220),  "name": "cave"},
        9:  {"sky": (245, 160, 100), "ground": (165, 85, 35),   "obs": (115, 55, 25),   "name": "autumn"},
        10: {"sky": (8, 10, 28),     "ground": (35, 40, 65),    "obs": (60, 180, 210),  "name": "space"},
        11: {"sky": (255, 200, 215), "ground": (110, 160, 80),  "obs": (130, 70, 45),   "name": "sakura"},
        12: {"sky": (40, 60, 42),    "ground": (32, 52, 28),    "obs": (70, 95, 45),    "name": "swamp"},
        13: {"sky": (160, 205, 235), "ground": (190, 225, 245), "obs": (115, 175, 220), "name": "ice"},
        14: {"sky": (255, 130, 80),  "ground": (150, 65, 35),   "obs": (185, 85, 45),   "name": "canyon"},
        15: {"sky": (30, 20, 55),    "ground": (50, 32, 75),    "obs": (240, 195, 60),  "name": "final"},
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
            self.pw, self.ph = 70, 58
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
            self.obstacles = []
            cur_x = 850
            for _ in range(4):
                self.obstacles.append([cur_x, GROUND_Y - c["oh"] + 54, c["ow"], c["oh"]])
                cur_x += c["gap"]

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
            if self.py >= GROUND_Y - 2:
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
            dog_box = (self.px + 10, self.py - self.ph + 10, self.pw - 15, self.ph - 10)

            for o in self.obstacles:
                o[0] -= self.speed
                hit = (dog_box[0] < o[0] + o[2] and dog_box[0] + dog_box[2] > o[0] and
                       dog_box[1] < o[1] + o[3] and dog_box[1] + dog_box[3] > o[1])
                if hit:
                    self.reset_level()
                    break

                if o[0] + o[2] < -30:
                    max_x = max(ob[0] for ob in self.obstacles)
                    o[0] = max_x + gap
                    o[2] = cfg["ow"]
                    o[3] = cfg["oh"]
                    o[1] = GROUND_Y - cfg["oh"] + 54
                    self.passed += 1
                    self.score += 1
                    if self.passed >= need:
                        if self.level < MAX_LEVEL:
                            self.level += 1
                            if self.level in (5, 10, 15):
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
                Line(points=flat, width=1.5, close=True)

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

        # ==================== سگ دونده اصلاح‌شده رو به جلو ====================
        def dog(self, x, y):
            t = self.tick
            in_air = self.py < GROUND_Y - 2
            wag = math.sin(t * 0.45) * 12
            leg1 = math.sin(t * 0.4) * 8 if not in_air else -6
            leg2 = -leg1 if not in_air else 4

            # سایه زیر پاها
            if not in_air:
                self.ellipse((20, 20, 25), x + 8, GROUND_Y + 44, 60, 10, 0.35)

            # دم پشت سر (سمت چپ چون سگ رو به راست می‌دود)
            self.line((185, 120, 60), (x + 8, y + 15), (x - 14, y + 5 + wag), 7)

            # پاهای عقب (تیره تر)
            self.ellipse((170, 110, 55), x + 12 + leg2, y + 26, 12, 22)
            self.ellipse((170, 110, 55), x + 46 - leg2, y + 26, 12, 22)

            # بدن سگ
            self.ellipse((230, 170, 105), x + 6, y + 8, 54, 34)
            self.ellipse((255, 230, 185), x + 18, y + 16, 32, 22)

            # پاهای جلو (روشن تر)
            self.ellipse((210, 150, 85), x + 18 + leg1, y + 27, 12, 22)
            self.ellipse((210, 150, 85), x + 50 - leg1, y + 27, 12, 22)

            # گردن و سر (در سمت راست، بالاتر از بدن)
            self.ellipse((230, 170, 105), x + 40, y - 10, 36, 34)

            # گوش آویزان
            ear_sway = math.sin(t * 0.35) * 3
            self.polygon((160, 95, 45), [
                (x + 45, y - 8),
                (x + 36, y + 10 + ear_sway),
                (x + 52, y + 2)
            ])

            # پوزه و بینی رو به جلو (راست)
            self.ellipse((250, 205, 155), x + 58, y - 3, 20, 16)
            self.ellipse((35, 30, 30), x + 72, y - 5, 8, 7) # بینی مشکی

            # چشم براق
            self.ellipse(WHITE, x + 54, y - 8, 12, 13)
            self.ellipse((30, 30, 45), x + 58, y - 7, 6, 7)
            self.ellipse(WHITE, x + 60, y - 8, 2.5, 2.5)

            # قلاده قرمز زیبا
            self.rect((220, 45, 55), x + 43, y + 14, 15, 6, radius=2)
            self.ellipse(YELLOW, x + 49, y + 18, 5, 5)

        # ==================== گربه شیطون ترنزیشن ====================
        def cat(self, x, y):
            c = (90, 85, 95)
            c2 = (60, 55, 65)
            self.ellipse((20, 20, 25), x - 65, y + 115, 130, 24, 0.3)
            self.ellipse(c, x - 55, y + 35, 110, 85)
            self.ellipse(c, x - 42, y - 15, 84, 70)
            self.polygon(c2, [(x - 38, y - 10), (x - 28, y - 40), (x - 8, y - 14)])
            self.polygon(c2, [(x + 8, y - 14), (x + 28, y - 40), (x + 38, y - 10)])
            self.ellipse((255, 235, 80), x - 28, y - 2, 22, 26)
            self.ellipse((255, 235, 80), x + 6, y - 2, 22, 26)
            self.ellipse((25, 25, 25), x - 18, y + 2, 7, 18)
            self.ellipse((25, 25, 25), x + 14, y + 2, 7, 18)
            self.polygon((255, 140, 165), [(x - 6, y + 20), (x + 6, y + 20), (x, y + 28)])
            tail = math.sin(self.ttime * 0.16) * 30
            self.line(c2, (x - 50, y + 70), (x - 95 + tail, y + 50), 12)

        # ==================== مانع‌های متنوع با استایل هر تم ====================
        def obstacle(self, o, color, theme_name):
            x, y, w, h = o
            dark = tuple(max(0, v - 50) for v in color)
            light = tuple(min(255, v + 50) for v in color)

            if theme_name in ("meadow", "jungle", "swamp"):
                # تنه درخت و برگ‌های روی آن
                self.rect(color, x + 4, y, w - 8, h, radius=6)
                self.rect(dark, x + 8, y + 4, w - 16, h - 8, radius=4)
                self.ellipse((40, 150, 60), x - 4, y - 10, w + 8, 20)
            elif theme_name == "desert":
                # کاکتوس
                self.rect((45, 155, 60), x + w * 0.3, y, w * 0.4, h, radius=8)
                self.rect((45, 155, 60), x, y + h * 0.35, w, 14, radius=6)
                self.rect((45, 155, 60), x, y + h * 0.18, 12, h * 0.22, radius=5)
                self.rect((45, 155, 60), x + w - 12, y + h * 0.25, 12, h * 0.22, radius=5)
            elif theme_name in ("cave", "ice"):
                # قندیل و کریستال نوک‌تیز
                self.polygon(light, [(x, y + h), (x + w // 2, y), (x + w, y + h)])
                self.polygon(color, [(x + 4, y + h), (x + w // 2, y + 8), (x + w - 4, y + h)])
            else:
                # موانع کلاسیک شیک با سایه روشن
                self.rect(dark, x + 3, y + 3, w, h, radius=8)
                self.rect(color, x, y, w, h, radius=8)
                self.rect(light, x + 5, y + 6, max(6, w * 0.26), h - 12, radius=4)

        # ==================== تمام ۱۵ تم با جزییات کامل ====================
        def draw_background(self, th):
            name = th["name"]
            sky, ground = th["sky"], th["ground"]
            self.rect(sky, 0, 0, W, H)

            t = self.tick

            if name == "meadow":
                # خورشید و ابرهای دشت
                self.ellipse((255, 230, 80), 730, 60, 75, 75)
                self.ellipse(WHITE, 120, 80, 110, 45, 0.8)
                self.ellipse(WHITE, 450, 110, 140, 50, 0.7)
                # تپه‌های سبز پشت
                self.ellipse((50, 140, 65), -50, 310, 480, 220)
                self.ellipse((58, 155, 75), 350, 320, 600, 200)

            elif name == "jungle":
                # درخت‌های متراکم جنگل استوایی
                self.rect((18, 55, 30), 0, 180, W, 250)
                for tx in (80, 280, 520, 750):
                    self.rect((55, 35, 15), tx + 20, 240, 24, 200)
                    self.ellipse((20, 110, 45), tx - 30, 160, 125, 110)
                    self.ellipse((10, 90, 35), tx - 15, 120, 95, 80)

            elif name == "desert":
                # آفتاب کویر و تپه‌های شنی چند لایه
                self.ellipse((255, 220, 110), 720, 50, 85, 85)
                self.ellipse((235, 175, 95), -80, 330, 520, 180)
                self.ellipse((220, 160, 85), 320, 320, 650, 190)

            elif name == "city":
                # آسمان‌خراش‌های نورانی و ماه شبانه
                self.ellipse((240, 240, 250), 750, 50, 60, 60)
                bldgs = [(30, 160, 90), (140, 210, 110), (270, 140, 85), (380, 250, 120),
                         (520, 180, 100), (640, 230, 130), (790, 150, 85)]
                for bx, by, bw in bldgs:
                    self.rect((24, 28, 48), bx, by, bw, 440 - by)
                    # پنجره‌های روشن
                    for wx in range(bx + 12, bx + bw - 15, 22):
                        for wy in range(by + 16, 420, 28):
                            self.rect((245, 215, 90), wx, wy, 10, 14, 2, 0.85)

            elif name == "snow":
                # دانه‌های برف و تپه‌های یخ‌زده
                self.ellipse((245, 250, 255), 100, 310, 500, 200)
                self.ellipse((230, 238, 250), 480, 330, 500, 180)
                # بارش برف
                for i in range(16):
                    sx = (i * 59 + t * 2) % W
                    sy = (i * 37 + t * 3) % 430
                    self.ellipse(WHITE, sx, sy, 6, 6, 0.75)
                # آدم برفی در پس‌زمینه
                self.ellipse(WHITE, 700, 360, 48, 48)
                self.ellipse(WHITE, 708, 335, 32, 32)
                self.ellipse((240, 120, 30), 720, 348, 8, 5)

            elif name == "lava":
                # آتشفشان و گدازه‌ها
                self.polygon((45, 18, 18), [(60, 440), (230, 180), (400, 440)])
                self.polygon((55, 22, 22), [(460, 440), (660, 210), (860, 440)])
                # گدازه دهانه آتشفشان
                self.ellipse((255, 90, 20), 215, 175, 30, 15)
                self.ellipse((255, 90, 20), 645, 205, 30, 15)

            elif name == "beach":
                # ساحل دریا، آب و نخل
                self.rect((60, 160, 225), 0, 330, W, 100) # آب دریا
                self.ellipse(WHITE, 0, 328, W, 10, 0.4)    # کف موج دریا
                self.ellipse((255, 220, 80), 720, 50, 80, 80) # خورشید تابستانی
                # درخت نخل
                self.rect((110, 70, 30), 120, 250, 16, 180)
                self.ellipse((40, 160, 60), 60, 220, 135, 45)

            elif name == "cave":
                # قندیل‌های سقف غار
                for cx in range(0, W, 70):
                    h_c = 45 + (cx % 3) * 20
                    self.polygon((35, 30, 48), [(cx, 0), (cx + 35, h_c), (cx + 70, 0)])
                # کریستال درخشان زمین
                self.polygon((180, 80, 255), [(220, 440), (230, 390), (240, 440)])
                self.polygon((130, 60, 230), [(660, 440), (672, 380), (684, 440)])

            elif name == "autumn":
                # درختان خزان و برگ‌های نارنجی
                self.ellipse((255, 180, 60), 750, 60, 70, 70)
                for tx in (120, 400, 720):
                    self.rect((90, 50, 25), tx + 20, 260, 20, 170)
                    self.ellipse((220, 95, 30), tx - 30, 160, 120, 110)
                    self.ellipse((245, 150, 40), tx - 10, 190, 80, 75)

            elif name == "space":
                # ستاره‌های چشمک‌زن و سیاره زحل
                for i in range(25):
                    sx = (i * 73) % W
                    sy = (i * 41) % 400
                    r = 3 if i % 2 == 0 else 5
                    self.ellipse(WHITE, sx, sy, r, r, 0.8)
                # سیاره بزرگ و حلقه‌دار
                self.ellipse((215, 120, 80), 680, 90, 75, 75)
                self.ellipse((240, 190, 130), 645, 118, 145, 20, 0.6)

            elif name == "sakura":
                # شکوفه‌های صورتی ژاپنی
                self.ellipse((255, 235, 220), 750, 50, 70, 70)
                for tx in (100, 460, 760):
                    self.rect((75, 45, 30), tx + 18, 250, 20, 180)
                    self.ellipse((255, 160, 185), tx - 35, 140, 130, 115)
                    self.ellipse((255, 195, 210), tx - 15, 160, 90, 85)

            elif name == "swamp":
                # درختان مرموز مرداب
                self.rect((25, 42, 25), 0, 360, W, 80)
                for tx in (160, 550):
                    self.rect((45, 38, 24), tx + 15, 220, 25, 210)
                    self.ellipse((35, 80, 40), tx - 30, 140, 120, 95)

            elif name == "ice":
                # کوه‌های عظیم یخ (Iceberg)
                self.polygon((180, 220, 245), [(100, 440), (250, 170), (420, 440)])
                self.polygon((210, 240, 255), [(350, 440), (520, 210), (690, 440)])

            elif name == "canyon":
                # دیواره‌های لایه‌لایه سرخ‌رنگ دره گرند کانیون
                self.ellipse((255, 110, 60), 740, 60, 75, 75)
                self.rect((170, 70, 40), 0, 270, 280, 170)
                self.rect((195, 85, 45), 260, 320, 300, 120)
                self.rect((150, 60, 35), 540, 240, 360, 200)

            elif name == "final":
                # کهکشان نهایی و ستون‌های باستانی
                self.ellipse((255, 215, 60), 450, 80, 90, 90)
                for px in (90, 280, 620, 810):
                    self.rect((90, 60, 120), px, 210, 35, 230)
                    self.rect((140, 90, 170), px - 10, 195, 55, 20)

            # زمین مشترک هر تم
            self.rect(ground, 0, 440, W, 110)
            self.rect((0, 0, 0), 0, 440, W, 4, a=0.2) # خط لبه زمین

        def draw(self):
            self.canvas.clear()
            with self.canvas:
                self.col(BLACK)
                Rectangle(pos=self.pos, size=self.size)

                if self.won:
                    self.rect((15, 10, 30), 0, 0, W, H)
                    self.ellipse((255, 215, 90), 450, 140, 80, 80)
                    self.text("YOU WIN!", 76, YELLOW, W // 2, 250, True)
                    self.text("Total Score: %d" % self.score, 36, WHITE, W // 2, 330, True)
                    self.text("Tap anywhere to play again!", 26, WHITE, W // 2, 400, True)
                    return

                if self.transition:
                    self.rect((12, 10, 22), 0, 0, W, H)
                    walk = math.sin(self.ttime * 0.12) * 110
                    cat_x = W // 2 + walk
                    cy = 210 + int(math.sin(self.ttime * 0.1) * 8)
                    self.cat(cat_x, cy)
                    self.text("HAHAHAHA!", 56, WHITE, W // 2, 380, True)
                    if self.ttime > 35:
                        self.text("MEOW! YOU CANNOT PASS!", 38, YELLOW, W // 2, 440, True)
                    self.text("LEVEL %d" % self.level, 36, (120, 230, 140), W // 2, 495, True)
                    return

                th = self.theme()
                self.draw_background(th)

                # رسم موانع
                for o in self.obstacles:
                    if -80 < o[0] < W + 50:
                        self.obstacle(o, th["obs"], th["name"])

                # رسم سگ
                self.dog(self.px, self.py)

                # دکمه پرش زیبا (پایین سمت راست)
                b = self.jump_btn
                self.rect((25, 25, 30), b[0] + 4, b[1] + 4, b[2], b[3], 18, 0.4)
                self.rect((255, 195, 45), b[0], b[1], b[2], b[3], 18)
                self.rect((255, 225, 120), b[0] + 6, b[1] + 6, b[2] - 12, 16, 8, 0.5)
                self.text("JUMP", 32, BLACK, b[0] + 46, b[1] + 24)

                # پنل امتیاز و مرحله (بالا سمت چپ)
                self.rect((0, 0, 0), 14, 14, 250, 95, 14, 0.45)
                self.text("Score: %d" % self.score, 24, WHITE, 28, 26)
                self.text("Level: %d / %d" % (self.level, MAX_LEVEL), 24, WHITE, 28, 54)
                cfg = self.level_cfg()
                self.text("Progress: %d / %d" % (self.passed, cfg["need"]), 20, YELLOW, 28, 80)

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
