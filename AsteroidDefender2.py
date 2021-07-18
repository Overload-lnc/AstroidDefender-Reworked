import random
import pygame
import time
from pygame.locals import *


def shitty_logo(duration, text_path, screen, names=None):
    text_path += "\\" if text_path[-1] != "\\" else ""
    paths = []
    if names is None:
        paths = [text_path + "overload_logo.png"]
    else:
        for name in names:
            paths.append(text_path + name)
    amount = 1 if names is None else len(names)
    for i in range(amount):
        logo = pygame.image.load(paths[i])
        loc = (screen.get_size()[0] / 2 - logo.get_size()[0] / 2, screen.get_size()[1] / 2 - logo.get_size()[1] / 2)
        screen.fill((0, 0, 0))
        screen.blit(logo, loc)
        pygame.display.update()
        time.sleep(duration / amount)


class Button:
    def __init__(self, x, y, width, length):
        self.body = Rect(x, y, width, length)
        self.colors = [(255, 255, 255), (255, 255, 255), (255, 255, 255), (0, 0, 0)]
        self.shape_width = 0

        self.text = None
        self.rendered = None
        self.font = None
        self.offsets = [0, 0]

    def detect(self):
        return self.body.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

    def set_shape_attribs(self, width, color1, color2=None):
        self.colors[1] = color1
        if color2 is None:
            self.colors[2] = color1
        else:
            self.colors[2] = color2
        self.shape_width = width

    def set_text_attribs(self, text, color1=None, font=None, offsets=None):
        self.text = text
        self.colors[3] = color1 if color1 is not None else self.colors[3]
        self.font = font if font is not None else self.font
        self.offsets = offsets if offsets is not None else self.offsets

        self.rendered = self.font.render(text, True, self.colors[3])

    def draw(self, screen):
        self.colors[0] = self.colors[int(self.body.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])) + 1]
        pygame.draw.rect(screen, self.colors[0], self.body, self.shape_width)
        if self.rendered is not None:
            screen.blit(self.rendered, (self.body.x + self.offsets[0], self.body.y + self.offsets[1]))


pygame.init()
pygame.font.init()
font31 = pygame.font.Font("fonts/Montserrat.ttf", 30)
font32 = pygame.font.Font("fonts/Montserrat.ttf", 15)
screen = pygame.display.set_mode((500, 600))
pygame.display.set_caption("Asteroid Defender 2")
# pygame.display.set_icon(path) : used for giving the game screen a custom icon

clock = pygame.time.Clock()

char_text = pygame.image.load("text\\char.png")
char = char_text.get_rect()
char.x = 250 - char.width / 2
char.y = 520 - char.height
char_vector = [0, 0]
score = 0
combo = 0
combo_counter = 81
combo_loc = (0, 0)
score_counter = 0
shiftPressed = False
shiftEnable = False

# start/restart
button1 = Button(310, 540, 80, 20)
button1.set_shape_attribs(0, (255, 255, 255), (150, 150, 150))
button1.set_text_attribs("Start", (0, 0, 0), pygame.font.Font("fonts/roboto.ttf", 14), [22, 0])
# life mode
button2 = Button(310, 565, 80, 20)
button2.set_shape_attribs(0, (255, 255, 255), (150, 150, 150))
button2.set_text_attribs("Life Mode", (0, 0, 0), pygame.font.Font("fonts/roboto.ttf", 14), [4, 0])
# quit
button3 = Button(400, 540, 80, 20)
button3.set_shape_attribs(0, (255, 0, 0), (255, 60, 60))
button3.set_text_attribs("Quit", (0, 0, 0), pygame.font.Font("fonts/roboto.ttf", 14), [24, 0])
# extra ammo
button4 = Button(400, 565, 80, 20)
button4.set_shape_attribs(0, (255, 255, 255), (150, 150, 150))
button4.set_text_attribs("Extra Ammo", (0, 0, 0), pygame.font.Font("fonts/roboto.ttf", 13), [0, 0])

ast_text = pygame.image.load("text\\ast.png")
astList = [ast_text.get_rect(), ast_text.get_rect()]
astFalling = [False, False]
astCanFall = [False, False]
x_limit = 500 - astList[0].width
extra_y = 40 + astList[0].height - 18
astList[0].x = -50

proj_text = pygame.image.load("text\\proj.png")
projList = [proj_text.get_rect(), proj_text.get_rect(), proj_text.get_rect()]
projFired = [False, False, False]
projHit = [False, False, False]
spawn_x = char.width / 2 - projList[0].width / 2

font = pygame.font.SysFont("myanmartext", 17)
font2 = pygame.font.SysFont("consolas", 12)
font3 = pygame.font.SysFont("bauhaus93", 16)
text = font31.render("Score: 0", True, (255, 255, 255))
empty_clip = font32.render("EMPTY CLIP", True, (255, 0, 0))
combo_text = font31.render("x0", True, (234, 61, 11))
empty_counter = 81

hearth_text = pygame.image.load("text\\hearth.png")
hearth_width = hearth_text.get_rect().width
proj_icon = pygame.image.load("text\\proj_icon.png")
proj_icon_width = proj_icon.get_rect().width
run = True
life_mode = False
started = False
health = 0
update = 0
listLens = [len(projList), len(astList)]
empty_sound = pygame.mixer.Sound("sfx\\empty.wav")

shitty_logo(3, "text\\", screen)

while run:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or (button3.detect() and event.type == MOUSEBUTTONDOWN):
            run = False
        elif event.type == KEYDOWN and started:
            if event.key == K_a:
                char_vector[0] = -speed
            elif event.key == K_d:
                char_vector[0] = speed
            elif event.key == K_LSHIFT and shiftEnable:
                shiftPressed = True
            elif event.key == K_SPACE:
                try:
                    f_index = projFired.index(False)  # false index
                    projFired[f_index] = True
                    projList[f_index].x = char.x + spawn_x
                    projList[f_index].y = char.y
                except ValueError:
                    empty_counter = 0
                    pygame.mixer.Sound.play(empty_sound)
        elif event.type == KEYUP and started:
            if (event.key == K_a and char_vector[0] in (-1, -2, -3)) or ( event.key == K_d and char_vector[0] in (1, 2, 3)):
                char_vector[0] = 0
            elif event.key == K_LSHIFT and shiftEnable:
                shiftPressed = False
                if char_vector[0] > 0:
                    char_vector[0] = speed
                elif char_vector[0] < 0:
                    char_vector[0] = -speed
        elif event.type == MOUSEBUTTONDOWN:
            if button1.detect():
                if started:
                    started = False
                    astFalling = [False, False]
                    astCanFall = [False, False]
                    projHit = [False, False, False]
                    if listLens[0] == 5:
                        projHit.append(False)
                        projHit.append(False)
                    shiftEnable = False
                    shiftPressed = False
                    combo_counter = 81
                    char.x = 500 / 2 - char.width / 2
                else:
                    started = True
                    empty_counter = 81
                    update = 0
                    score = 0
                    score_counter = 0
                    speed = 1
                    velocity = 3
                    gravity = 1
                    char.x = 500 / 2 - char.width / 2
                    combo = 0
                    # first ast spawn
                    astList[0].x = random.randint(0, x_limit)
                    astList[0].y = -astList[0].height
                    astCanFall[0] = True
            elif not started:
                if button2.detect():
                    health = 5 * int(not life_mode)
                    life_mode = not life_mode
                elif button4.detect():
                    if listLens[0] == 3:
                        listLens[0] = 5
                        projList.append(proj_text.get_rect())
                        projList.append(proj_text.get_rect())
                        projFired.append(False)
                        projFired.append(False)
                        projHit.append(False)
                        projHit.append(False)
                    else:
                        listLens[0] = 3
                        projList = projList[:3]
                        projFired = projFired[:3]
                        projHit = projHit[:3]

    if shiftPressed:
        if char_vector[0] > 1:
            char_vector[0] = speed - 1
        elif char_vector[0] < -1:
            char_vector[0] = -speed + 1
    char.move_ip(char_vector)  # add ip at the end of the function to affect the provided object
    if char.x < 0:
        char.x = 0
    elif char.x > 500 - char.width:
        char.x = 500 - char.width
    # update
    if score_counter == 5:
            speed = 2
    elif score_counter == 10:
            extra_y = 80 + astList[0].height - 18
            gravity = 2
    elif score_counter == 15:
            speed = 3
            shiftEnable = True
            astCanFall[1] = True
    elif score_counter == 20:
            velocity = 4
    elif score_counter == 30:
            extra_y = 120 + astList[0].height - 18
    # button1 text update
    if started and button1.text == "Start":
        button1.set_text_attribs("Restart", offsets=[14, 0])
    elif not started and button1.text == "Restart":
        button1.set_text_attribs("Start", offsets=[26, 0])

    for i in range(listLens[0]):  # proj
        for i3 in range(projFired.count(False)):  # icon drawing
            screen.blit(proj_icon, (10 + i3 * (proj_icon_width + 7), 575, 6, 17))
        if projFired[i] is True:
            proj = projList[i]
            proj.move_ip([0, -velocity])
            screen.blit(proj_text, proj)
            if proj.y < -6:  # go up & out the map
                proj.x = -50
                proj.y = 0
                projFired[i] = False
                combo *= int(projHit[i])
                projHit[i] = False
            else:  # if it's still in the map check if it hit an ast
                for i2 in range(listLens[1]):
                    if astFalling[i2] and astCanFall[i2]:
                        proj2 = astList[i2]  # ast object
                        if proj2.colliderect(proj):  # check if it hit an asteroid
                            score += 1 * ((combo + 5) // 5)
                            score_counter += 1
                            combo += 1
                            combo_text = font31.render(f"x{combo}", True, (234, 61, 11))
                            combo_counter = 0
                            combo_loc = (proj2.x, proj2.y)
                            astFalling[i2] = False
                            projHit[i] = True
    for i in range(listLens[1]):  # ast
            proj = astList[i]
            if astFalling[i]:
                proj.move_ip(0, gravity)
                screen.blit(ast_text, proj)
                if proj.y > 600:  # go down & out the map
                    score -= 1
                    astFalling[i] = False
                    combo = 0  # combo test
                    health -= int(life_mode)
            else:
                if astCanFall[i]:
                    proj.x = random.randint(0, x_limit)
                    proj.y = -random.randint(astList[i].height, extra_y)
                    astFalling[i] = True
    if life_mode:  # hearth
            for i in range(health):
                screen.blit(hearth_text, (5 + i * (hearth_width + 5), 550, 23, 21))
            if health <= 0:
                started = False
                astFalling = [False, False]
                astCanFall = [False, False]
    if empty_counter < 81:  # empty clip
        screen.blit(empty_clip, (char.x + 30, char.y))
        empty_counter += 1
    if combo_counter < 81:  # combo effect
        screen.blit(combo_text, combo_loc)
        combo_counter += 1
    if shiftEnable:
        if shiftPressed:
            status = font32.render(f"Speed: Slow", True, (255, 255, 255))
        else:
            status = font32.render(f"Speed: Normal", True, (255, 255, 255))
        screen.blit(status, (140, 570))
    screen.blit(char_text, char)
    text = font31.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (140, 544))
    button1.draw(screen)
    button3.draw(screen)
    if not started:
        button2.draw(screen)
        button4.draw(screen)
    pygame.display.update()
    clock.tick(80)  # set FPS limit to 80
pygame.quit()
