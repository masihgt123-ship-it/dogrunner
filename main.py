import math
import os
import struct
import wave

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.label import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import (Color, Ellipse, Line, Rectangle,
                           RoundedRectangle, Triangle)
from kivy.uix.widget import Widget

W, H = 900, 550

WHITE = (255, 255, 255)
BLACK = (5, 5, 5)
YELLOW = (255, 220, 50)
SKY = (135, 206, 235)
GREEN = (50, 180, 70)
DARKGREEN = (20, 90, 35)
BROWN = (120, 70, 30)
DARKBROWN = (55, 35, 20)
DOG = (190, 130, 70)
DOGDARK = (110, 70, 35)
PINK = (220, 100, 120)
SAND = (225, 180, 100)

GRAVITY = 0.8
JUMP = -15
DISTANCE = 400
GROUND_Y = 385


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

        self.level = 1
        self.score = 0
        self.passed = 0
        self.speed = 7
        self.px = 120.0
        self.py = float(GROUND_Y)
        self.pw, self.ph = 70, 65
        self.vel = 0.0
        self.transition = False
        self.ttime = 0
        self.obstacles = []
        self.make_obstacles()

        self.left_btn = (30, 470, 100, 55)
        self.right_btn = (145, 470, 100, 55)
        self.jump_btn = (260, 470, 120, 55)
        self.touches = {}
        self._text_cache = {}

        Clock.schedule_interval(self.update, 1 / 60.0)

    # ---------- sound ----------
    def _load_sounds(self, d):
        try:
            for name in ("jump", "hit", "laugh"):
                p = os.path.join(d, name + ".wav")
                make_sound(p, name)
                self.sounds[name] = SoundLoader.load(p)
        except Exception:
            self.sounds = {}

    def play(self, name):
        s = self.sounds.get(name)
        if s:
            try:
                s.stop()
                s.play()
            except Exception:
                pass

    # ---------- game ----------
    def make_obstacles(self):
        self.obstacles = [[700 + i * DISTANCE, 430, 45, 50] for i in range(3)]

    def reset_level(self):
        self.px = 120.0
        self.py = float(GROUND_Y)
        self.vel = 0.0
        self.passed = 0
        self.speed = 7
        self.make_obstacles()
        self.play("hit")

    def jump(self):
        if self.py >= GROUND_Y and not self.transition:
            self.vel = JUMP
            self.play("jump")

    def in_rect(self, pos, r):
        gx, gy = pos
        return r[0] <= gx <= r[0] + r[2] and r[1] <= gy <= r[1] + r[3]

    def to_game(self, touch):
        s, ox, oy = self.view()
        return (touch.x - ox) / s, H - (touch.y - oy) / s

    def on_touch_down(self, touch):
        g = self.to_game(touch)
        if self.in_rect(g, self.left_btn):
            self.touches[touch.uid] = "L"
        elif self.in_rect(g, self.right_btn):
            self.touches[touch.uid] = "R"
        elif self.in_rect(g, self.jump_btn):
            self.jump()
        return True

    def on_touch_up(self, touch):
        self.touches.pop(touch.uid, None)
        return True

    def update(self, dt):
        try:
            self._update(dt)
        except Exception:
            import traceback
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
        if self.transition:
            self.ttime += 1
            if self.ttime >= 180:
                self.transition = False
                self.ttime = 0
                self.px = 120.0
                self.py = float(GROUND_Y)
                self.vel = 0.0
                self.passed = 0
                self.speed = 7
                self.make_obstacles()
            self.draw()
            return

        for d in self.touches.values():
            if d == "L":
                self.px -= 6
            elif d == "R":
                self.px += 6
        self.px = max(0, min(W - self.pw, self.px))

        self.vel += GRAVITY
        self.py += self.vel
        if self.py >= GROUND_Y:
            self.py = float(GROUND_Y)
            self.vel = 0.0

        for o in self.obstacles:
            o[0] -= self.speed
            if (self.px < o[0] + o[2] and self.px + self.pw > o[0]
                    and self.py < o[1] + o[3] and self.py + self.ph > o[1]):
                self.reset_level()
                break
            if o[0] + o[2] < 0:
                o[0] = max(x[0] for x in self.obstacles) + DISTANCE
                self.passed += 1
                self.score += 1
                if self.passed % 4 == 0:
                    self.speed += 2
                if self.passed >= 10 and self.level < 3:
                    self.level += 1
                    self.transition = True
                    self.ttime = 0
                    self.play("laugh")
        self.draw()

    # ---------- drawing helpers ----------
    def view(self):
        s = min(self.width / W, self.height / H)
        ox = (self.width - W * s) / 2 + self.x
        oy = (self.height - H * s) / 2 + self.y
        return s, ox, oy

    def col(self, c):
        Color(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, 1)

    def rect(self, c, x, y, w, h, radius=0):
        s, ox, oy = self.view()
        self.col(c)
        pos = (ox + x * s, oy + (H - y - h) * s)
        size = (w * s, h * s)
        if radius:
            RoundedRectangle(pos=pos, size=size, radius=[radius * s])
        else:
            Rectangle(pos=pos, size=size)

    def ellipse(self, c, x, y, w, h):
        s, ox, oy = self.view()
        self.col(c)
        Ellipse(pos=(ox + x * s, oy + (H - y - h) * s), size=(w * s, h * s))

    def circle(self, c, cx, cy, r):
        self.ellipse(c, cx - r, cy - r, 2 * r, 2 * r)

    def polygon(self, c, pts):
        s, ox, oy = self.view()
        self.col(c)
        (x1, y1), (x2, y2), (x3, y3) = pts
        Triangle(points=[ox + x1 * s, oy + (H - y1) * s,
                         ox + x2 * s, oy + (H - y2) * s,
                         ox + x3 * s, oy + (H - y3) * s])

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
        key = (txt, int(size * s))
        tex = self._text_cache.get(key)
        if tex is None:
            if len(self._text_cache) > 300:
                self._text_cache.clear()
            lab = CoreLabel(text=txt, font_size=max(8, int(size * s)))
            lab.refresh()
            tex = lab.texture
            self._text_cache[key] = tex
        tw, th = tex.size
        gx = ox + x * s - (tw / 2.0 if center else 0)
        gy = oy + (H - y) * s - th
        self.col(c)
        Rectangle(texture=tex, pos=(gx, gy), size=(tw, th))

    # ---------- scenes ----------
    def dog(self, x, y):
        self.line(DOGDARK, (x + 15, y + 32), (x - 5, y + 12), 8)
        self.ellipse(DOG, x + 10, y + 25, 50, 32)
        self.circle(DOG, x + 52, y + 24, 24)
        self.ellipse(DOGDARK, x + 34, y, 17, 32)
        self.ellipse(DOGDARK, x + 57, y + 2, 17, 30)
        self.circle(BLACK, x + 59, y + 19, 4)
        self.circle(BLACK, x + 75, y + 29, 6)
        self.rect(DOGDARK, x + 17, y + 48, 11, 20, 5)
        self.rect(DOGDARK, x + 44, y + 48, 11, 20, 5)

    def cat(self, x, y):
        c = (5, 5, 5)
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
        self.polygon(WHITE, [(x - 35, y + 82), (x - 20, y + 112), (x - 5, y + 82)])
        self.polygon(WHITE, [(x + 5, y + 82), (x + 20, y + 112), (x + 35, y + 82)])
        self.line(WHITE, (x - 25, y + 50), (x - 105, y + 30), 3)
        self.line(WHITE, (x - 25, y + 60), (x - 110, y + 70), 3)
        self.line(WHITE, (x + 25, y + 50), (x + 105, y + 30), 3)
        self.line(WHITE, (x + 25, y + 60), (x + 110, y + 70), 3)

    def level1(self):
        self.rect(SKY, 0, 0, W, H)
        self.circle(YELLOW, 760, 80, 45)
        self.polygon((100, 160, 110), [(0, 350), (180, 180), (350, 350)])
        self.polygon((80, 140, 100), [(300, 350), (500, 150), (720, 350)])
        self.rect(GREEN, 0, 450, W, 100)
        for x in (40, 350, 600, 850):
            self.rect(BROWN, x, 300, 25, 150)
            self.circle(DARKGREEN, x + 12, 285, 55)

    def level2(self):
        self.rect((30, 65, 50), 0, 0, W, H)
        self.rect((80, 120, 90), 0, 350, W, 100)
        self.rect((20, 75, 30), 0, 450, W, 100)
        for x in (20, 170, 330, 500, 670, 830):
            self.rect(DARKBROWN, x, 230, 45, 220)
            self.circle(DARKGREEN, x + 20, 220, 75)

    def level3(self):
        self.rect((245, 190, 120), 0, 0, W, H)
        self.circle((255, 220, 70), 760, 90, 65)
        self.polygon((190, 125, 75), [(0, 360), (180, 220), (330, 360)])
        self.polygon((175, 110, 65), [(280, 360), (500, 180), (730, 360)])
        self.rect(SAND, 0, 360, W, 190)
        for x in range(0, W, 180):
            self.arc_top((170, 120, 60), x, 400, 160, 50, 4)
        green = (40, 130, 55)
        for x in (80, 470, 800):
            self.rect(green, x, 300, 25, 100)
            self.rect(green, x - 25, 325, 25, 15)
            self.rect(green, x + 25, 345, 25, 15)

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            self.col(BLACK)
            Rectangle(pos=self.pos, size=self.size)

            if self.transition:
                self.rect(BLACK, 0, 0, W, H)
                if self.ttime < 150:
                    cy = 220 + int(math.sin(self.ttime * 0.08) * 8)
                    self.cat(W // 2, cy)
                    self.text("HAHAHAHA!", 60, WHITE, W // 2, 400, True)
                    if self.ttime > 50:
                        self.text("HAHAHAHAHAHAHAHA!", 32, WHITE,
                                  W // 2, 475, True)
                else:
                    self.text("LEVEL " + str(self.level), 80, WHITE,
                              W // 2, 230, True)
                return

            if self.level == 1:
                self.level1()
                ocol, tcol = BROWN, BLACK
            elif self.level == 2:
                self.level2()
                ocol, tcol = DARKBROWN, WHITE
            else:
                self.level3()
                ocol, tcol = (125, 80, 45), BLACK

            self.dog(self.px, self.py)
            for o in self.obstacles:
                self.rect(ocol, o[0], o[1], o[2], o[3], 8)

            for b, label, dx in ((self.left_btn, "<", 38),
                                 (self.right_btn, ">", 38),
                                 (self.jump_btn, "JUMP", 28)):
                self.rect((65, 65, 65), b[0], b[1], b[2], b[3], 12)
                self.text(label, 32, WHITE, b[0] + dx, b[1] + 14)

            self.text("Score: %d" % self.score, 32, tcol, 20, 20)
            self.text("Speed: %d" % self.speed, 32, tcol, 20, 55)
            self.text("Level: %d" % self.level, 32, tcol, 20, 90)


class DogRunnerApp(App):
    def build(self):
        self.title = "Dog Runner"
        try:
            return Game(self.user_data_dir)
        except Exception:
            import traceback
            from kivy.uix.label import Label
            return Label(text=traceback.format_exc(), font_size="12sp",
                         text_size=(Window.width, None), halign="left")


if __name__ == "__main__":
    DogRunnerApp().run()
