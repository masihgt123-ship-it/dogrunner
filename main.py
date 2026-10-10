import pygame
import math
import wave
import struct
import sys

pygame.init()

W, H = 900, 550
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Dog Runner")
clock = pygame.time.Clock()

# ---------- SOUND ----------
def make_sound(name, typ):
    rate = 22050
    length = 0.25 if typ != "laugh" else 1.0
    data = bytearray()

    for i in range(int(rate * length)):
        t = i / rate

        if typ == "jump":
            freq = 450 + 900 * t
            vol = 0.30
        elif typ == "hit":
            freq = 220 - 140 * t
            vol = 0.45
        else:
            freq = 450 if int(t * 9) % 2 == 0 else 300
            vol = 0.35

        v = math.sin(2 * math.pi * freq * t) * vol
        data += struct.pack("<h", int(v * 32767))

    with wave.open(name, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(data)

try:
    make_sound("jump.wav", "jump")
    make_sound("hit.wav", "hit")
    make_sound("cat_laugh.wav", "laugh")

    pygame.mixer.init()
    jump_sound = pygame.mixer.Sound("jump.wav")
    hit_sound = pygame.mixer.Sound("hit.wav")
    laugh_sound = pygame.mixer.Sound("cat_laugh.wav")
    SOUND = True
except:
    SOUND = False

def play(s):
    if SOUND:
        s.play()

# ---------- COLORS ----------
WHITE=(255,255,255)
BLACK=(5,5,5)
YELLOW=(255,220,50)
SKY=(135,206,235)
GREEN=(50,180,70)
DARKGREEN=(20,90,35)
BROWN=(120,70,30)
DARKBROWN=(55,35,20)
DOG=(190,130,70)
DOGDARK=(110,70,35)
PINK=(220,100,120)
SAND=(225,180,100)

font=pygame.font.Font(None,32)
bigfont=pygame.font.Font(None,80)
laughfont=pygame.font.Font(None,60)

# ---------- PLAYER ----------
player=pygame.Rect(120,385,70,65)
player_y=385
velocity=0
GRAVITY=.8
JUMP=-15

# ---------- GAME ----------
level=1
score=0
passed=0
speed=7
DISTANCE=400

transition=False
transition_time=0

obstacles=[]

def make_obstacles():
    obstacles.clear()
    for i in range(3):
        obstacles.append(
            pygame.Rect(700+i*DISTANCE,430,45,50)
        )

def reset_level():
    global player_y,velocity,passed,speed
    player.x=120
    player_y=385
    velocity=0
    passed=0
    speed=7
    make_obstacles()
    play(hit_sound)

# ---------- DOG ----------
def draw_dog(x,y):
    pygame.draw.line(
        screen,DOGDARK,(x+15,y+32),(x-5,y+12),8
    )
    pygame.draw.ellipse(
        screen,DOG,(x+10,y+25,50,32)
    )
    pygame.draw.circle(
        screen,DOG,(x+52,y+24),24
    )

    pygame.draw.ellipse(
        screen,DOGDARK,(x+34,y,17,32)
    )
    pygame.draw.ellipse(
        screen,DOGDARK,(x+57,y+2,17,30)
    )

    pygame.draw.circle(
        screen,BLACK,(x+59,y+19),4
    )
    pygame.draw.circle(
        screen,BLACK,(x+75,y+29),6
    )

    pygame.draw.rect(
        screen,DOGDARK,(x+17,y+48,11,20),border_radius=5
    )
    pygame.draw.rect(
        screen,DOGDARK,(x+44,y+48,11,20),border_radius=5
    )

# ---------- CAT ----------
def draw_cat(x,y):
    c=(5,5,5)

    pygame.draw.ellipse(
        screen,c,(x-90,y+80,180,170)
    )
    pygame.draw.circle(
        screen,c,(x,y),105
    )

    pygame.draw.polygon(
        screen,c,
        [(x-85,y-60),(x-65,y-145),(x-10,y-80)]
    )
    pygame.draw.polygon(
        screen,c,
        [(x+10,y-80),(x+65,y-145),(x+85,y-60)]
    )

    pygame.draw.ellipse(
        screen,YELLOW,(x-65,y-25,38,55)
    )
    pygame.draw.ellipse(
        screen,YELLOW,(x+27,y-25,38,55)
    )

    pygame.draw.ellipse(
        screen,BLACK,(x-52,y-15,8,35)
    )
    pygame.draw.ellipse(
        screen,BLACK,(x+40,y-15,8,35)
    )

    pygame.draw.polygon(
        screen,PINK,
        [(x-14,y+30),(x+14,y+30),(x,y+48)]
    )

    pygame.draw.arc(
        screen,WHITE,
        (x-65,y+35,130,95),0,math.pi,7
    )

    pygame.draw.polygon(
        screen,WHITE,
        [(x-35,y+82),(x-20,y+112),(x-5,y+82)]
    )
    pygame.draw.polygon(
        screen,WHITE,
        [(x+5,y+82),(x+20,y+112),(x+35,y+82)]
    )

    pygame.draw.line(
        screen,WHITE,(x-25,y+50),(x-105,y+30),3
    )
    pygame.draw.line(
        screen,WHITE,(x-25,y+60),(x-110,y+70),3
    )
    pygame.draw.line(
        screen,WHITE,(x+25,y+50),(x+105,y+30),3
    )
    pygame.draw.line(
        screen,WHITE,(x+25,y+60),(x+110,y+70),3
    )

# ---------- LEVEL 1 ----------
def draw_level1():
    screen.fill(SKY)

    pygame.draw.circle(
        screen,YELLOW,(760,80),45
    )

    pygame.draw.polygon(
        screen,(100,160,110),
        [(0,350),(180,180),(350,350)]
    )

    pygame.draw.polygon(
        screen,(80,140,100),
        [(300,350),(500,150),(720,350)]
    )

    pygame.draw.rect(
        screen,GREEN,(0,450,W,100)
    )

    for x in [40,350,600,850]:
        pygame.draw.rect(
            screen,BROWN,(x,300,25,150)
        )
        pygame.draw.circle(
            screen,DARKGREEN,(x+12,285),55
        )

# ---------- LEVEL 2 ----------
def draw_level2():
    screen.fill((30,65,50))

    pygame.draw.rect(
        screen,(80,120,90),(0,350,W,100)
    )

    pygame.draw.rect(
        screen,(20,75,30),(0,450,W,100)
    )

    for x in [20,170,330,500,670,830]:
        pygame.draw.rect(
            screen,DARKBROWN,(x,230,45,220)
        )
        pygame.draw.circle(
            screen,DARKGREEN,(x+20,220),75
        )

# ---------- LEVEL 3 ----------
def draw_level3():
    screen.fill((245,190,120))

    pygame.draw.circle(
        screen,(255,220,70),(760,90),65
    )

    pygame.draw.polygon(
        screen,(190,125,75),
        [(0,360),(180,220),(330,360)]
    )

    pygame.draw.polygon(
        screen,(175,110,65),
        [(280,360),(500,180),(730,360)]
    )

    pygame.draw.rect(
        screen,SAND,(0,360,W,190)
    )

    for x in range(0,W,180):
        pygame.draw.arc(
            screen,(170,120,60),
            (x,400,160,50),0,math.pi,4
        )

    # cacti
    for x in [80,470,800]:
        pygame.draw.rect(
            screen,(40,130,55),(x,300,25,100)
        )
        pygame.draw.rect(
            screen,(40,130,55),(x-25,325,25,15)
        )
        pygame.draw.rect(
            screen,(40,130,55),(x+25,345,25,15)
        )

# ---------- BUTTONS ----------
left_button=pygame.Rect(30,470,100,55)
right_button=pygame.Rect(145,470,100,55)
jump_button=pygame.Rect(260,470,120,55)

def jump():
    global velocity

    if player_y >= 385 and not transition:
        velocity=JUMP
        play(jump_sound)

# ---------- START ----------
make_obstacles()
running=True

while running:

    clock.tick(60)

    # ---------- EVENTS ----------
    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:

            if event.key==pygame.K_LEFT:
                player.x-=12

            elif event.key==pygame.K_RIGHT:
                player.x+=12

            elif event.key==pygame.K_SPACE:
                jump()

        if event.type==pygame.MOUSEBUTTONDOWN:

            m=pygame.mouse.get_pos()

            if left_button.collidepoint(m):
                player.x-=12

            elif right_button.collidepoint(m):
                player.x+=12

            elif jump_button.collidepoint(m):
                jump()

    # ---------- CAT TRANSITION ----------
    if transition:

        transition_time+=1
        screen.fill(BLACK)

        if transition_time < 150:

            cy=220+int(
                math.sin(transition_time*.08)*8
            )

            draw_cat(W//2,cy)

            t=laughfont.render(
                "HAHAHAHA!",True,WHITE
            )

            screen.blit(
                t,
                (W//2-t.get_width()//2,400)
            )

            if transition_time>50:

                t2=font.render(
                    "HAHAHAHAHAHAHAHA!",True,WHITE
                )

                screen.blit(
                    t2,
                    (W//2-t2.get_width()//2,475)
                )

        else:

            t=bigfont.render(
                "LEVEL "+str(level),
                True,WHITE
            )

            screen.blit(
                t,
                (W//2-t.get_width()//2,230)
            )

        pygame.display.update()

        if transition_time>=180:

            transition=False
            transition_time=0

            player.x=120
            player_y=385
            velocity=0
            passed=0
            speed=7

            make_obstacles()

        continue

    # ---------- PLAYER ----------
    player.x=max(
        0,
        min(W-player.width,player.x)
    )

    velocity+=GRAVITY
    player_y+=velocity

    if player_y>=385:
        player_y=385
        velocity=0

    player.y=int(player_y)

    # ---------- OBSTACLES ----------
    for obstacle in obstacles:

        obstacle.x-=speed

        # hit
        if player.colliderect(obstacle):

            reset_level()
            break

        # passed
        if obstacle.right<0:

            obstacle.x=(
                max(o.x for o in obstacles)
                + DISTANCE
            )

            passed+=1
            score+=1

            # speed +2 every 4 obstacles
            if passed%4==0:
                speed+=2

            # next level
            if passed>=10 and level<3:

                level+=1
                transition=True
                transition_time=0

                play(laugh_sound)

    # ---------- BACKGROUND ----------
    if level==1:
        draw_level1()
        obstacle_color=BROWN
        text_color=BLACK

    elif level==2:
        draw_level2()
        obstacle_color=DARKBROWN
        text_color=WHITE

    else:
        draw_level3()
        obstacle_color=(125,80,45)
        text_color=BLACK

    # ---------- DRAW DOG ----------
    draw_dog(player.x,player.y)

    # ---------- DRAW OBSTACLES ----------
    for obstacle in obstacles:
        pygame.draw.rect(
            screen,
            obstacle_color,
            obstacle,
            border_radius=8
        )

    # ---------- BUTTONS ----------
    for button in [
        left_button,
        right_button,
        jump_button
    ]:
        pygame.draw.rect(
            screen,
            (65,65,65),
            button,
            border_radius=12
        )

    screen.blit(
        font.render("<",True,WHITE),
        (left_button.centerx-8,
         left_button.centery-15)
    )

    screen.blit(
        font.render(">",True,WHITE),
        (right_button.centerx-8,
         right_button.centery-15)
    )

    screen.blit(
        font.render("JUMP",True,WHITE),
        (jump_button.x+28,
         jump_button.y+15)
    )

    # ---------- TEXT ----------
    screen.blit(
        font.render(
            "Score: "+str(score),
            True,text_color
        ),
        (20,20)
    )

    screen.blit(
        font.render(
            "Speed: "+str(speed),
            True,text_color
        ),
        (20,55)
    )

    screen.blit(
        font.render(
            "Level: "+str(level),
            True,text_color
        ),
        (20,90)
    )

    pygame.display.update()

pygame.quit()
sys.exit()
