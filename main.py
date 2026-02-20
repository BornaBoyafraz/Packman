import copy
import math
import os

import pygame

import ui
from board import boards


pygame.init()


# Core settings
WIDTH = 900
HEIGHT = 950
HUD_HEIGHT = ui.HUD_HEIGHT
GAME_HEIGHT = HEIGHT - HUD_HEIGHT
FPS = 60

# Gameplay settings
PLAYER_SPEED = 2
DEFAULT_LIVES = 3
POWERUP_FRAMES = 600
STARTUP_FRAMES = 180
LEVEL_NUMBER = 1

# File paths
ICON_CANDIDATES = ["PackManImage.png", "PackMan Image.png", "Packman Images/PackMan Image.png"]
HIGHSCORE_FILE = "highscore.txt"

# Start positions
PLAYER_START = (450, 663)
BLINKY_START = (56, 58, 0)
INKY_START = (440, 388, 2)
PINKY_START = (440, 438, 2)
CLYDE_START = (440, 438, 2)

# State constants
STATE_MENU = "menu"
STATE_CONTROLS = "controls"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"

# Fade settings
FADE_SPEED = 20

# Misc
BOARD_COLOR = (40, 108, 222)
PI = math.pi


def load_high_score():
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as high_score_file:
            return int(high_score_file.read().strip() or "0")
    except (ValueError, OSError):
        return 0


def save_high_score(value):
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as high_score_file:
            high_score_file.write(str(value))
    except OSError:
        pass


def resolve_existing_path(candidates):
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(f"None of these asset paths exist: {candidates}")


def load_scaled_image(candidates, size):
    if isinstance(candidates, str):
        candidates = [candidates]
    path = resolve_existing_path(candidates)
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
fonts = ui.create_fonts()
pygame.display.set_caption("PackMan")
try:
    icon_path = resolve_existing_path(ICON_CANDIDATES)
    pygame.display.set_icon(pygame.image.load(icon_path))
except FileNotFoundError:
    pass


# Assets
player_images = [
    load_scaled_image(
        [f"Packman Images/{index} packman.png", f"Packman Images/Player images/{index} packman.png"],
        (45, 45),
    )
    for index in range(1, 5)
]
blinky_img = load_scaled_image(["red ghost.png", "Packman Images/ghost images/red ghost.png"], (45, 45))
pinky_img = load_scaled_image(["pink ghost.png", "Packman Images/ghost images/pink ghost.png"], (45, 45))
inky_img = load_scaled_image(["blue ghost.png", "Packman Images/ghost images/blue ghost.png"], (45, 45))
clyde_img = load_scaled_image(["orange ghost.png", "Packman Images/ghost images/orange ghost.png"], (45, 45))
spooked_img = load_scaled_image(["powerup ghost.png", "Packman Images/ghost images/powerup ghost.png"], (45, 45))
dead_img = load_scaled_image(["dead ghost.png", "Packman Images/ghost images/dead ghost.png"], (45, 45))


# UI state
run = True
state = STATE_MENU
menu_index = 0
controls_index = 0
pause_index = 0
menu_button_rects = []
controls_button_rects = []
pause_button_rects = []
show_fps = False
music_enabled = True
sfx_enabled = True

# Fade transition state
transitioning = True
fade_mode = "in"
fade_alpha = 255
target_state = None

# Runtime gameplay values
level = copy.deepcopy(boards)
best_score = load_high_score()
score = 0
lives = DEFAULT_LIVES
level_number = LEVEL_NUMBER
counter = 0
direction = 0
direction_command = 0
power_counter = 0
startup_counter = 0
score_pop_timer = 0
player_x = PLAYER_START[0]
player_y = PLAYER_START[1]
blinky_x, blinky_y, blinky_direction = BLINKY_START
inky_x, inky_y, inky_direction = INKY_START
pinky_x, pinky_y, pinky_direction = PINKY_START
clyde_x, clyde_y, clyde_direction = CLYDE_START
flicker = False
powerup = False
moving = False
blinky_dead = False
inky_dead = False
pinky_dead = False
clyde_dead = False
blinky_box = False
inky_box = False
pinky_box = False
clyde_box = False
turns_allowed = [False, False, False, False]
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
ghost_speeds = [2, 2, 2, 2]


def start_transition(new_state):
    global transitioning, fade_mode, fade_alpha, target_state
    if transitioning:
        return
    transitioning = True
    fade_mode = "out"
    fade_alpha = 0
    target_state = new_state


def update_transition():
    global transitioning, fade_mode, fade_alpha, target_state, state
    if not transitioning:
        return
    if fade_mode == "out":
        fade_alpha = min(255, fade_alpha + FADE_SPEED)
        if fade_alpha >= 255:
            if target_state is not None:
                state = target_state
            target_state = None
            fade_mode = "in"
    else:
        fade_alpha = max(0, fade_alpha - FADE_SPEED)
        if fade_alpha <= 0:
            transitioning = False


def reset_round():
    global player_x, player_y, direction, direction_command
    global blinky_x, blinky_y, blinky_direction
    global inky_x, inky_y, inky_direction
    global pinky_x, pinky_y, pinky_direction
    global clyde_x, clyde_y, clyde_direction
    global startup_counter, powerup, power_counter, eaten_ghost
    global blinky_dead, inky_dead, pinky_dead, clyde_dead, moving

    player_x, player_y = PLAYER_START
    direction = 0
    direction_command = 0

    blinky_x, blinky_y, blinky_direction = BLINKY_START
    inky_x, inky_y, inky_direction = INKY_START
    pinky_x, pinky_y, pinky_direction = PINKY_START
    clyde_x, clyde_y, clyde_direction = CLYDE_START

    startup_counter = 0
    moving = False
    powerup = False
    power_counter = 0
    eaten_ghost = [False, False, False, False]
    blinky_dead = False
    inky_dead = False
    pinky_dead = False
    clyde_dead = False


def start_new_game():
    global level, score, lives, level_number, score_pop_timer
    level = copy.deepcopy(boards)
    score = 0
    lives = DEFAULT_LIVES
    level_number = LEVEL_NUMBER
    score_pop_timer = 0
    reset_round()


def lose_life_or_game_over():
    global lives, state
    if lives > 1:
        lives -= 1
        reset_round()
    else:
        lives = 0
        sync_high_score()
        start_transition(STATE_GAME_OVER)


def sync_high_score():
    global best_score
    if score > best_score:
        best_score = score


class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, ghost_id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = ghost_id
        self.turns, self.in_box = self.check_collisions()
        self.rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))

    def draw(self):
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))

    def check_collisions(self):
        # R, L, U, D
        num1 = GAME_HEIGHT // 32
        num2 = WIDTH // 30
        num3 = 15
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 or (
                level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)
            ):
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 or (
                level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)
            ):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or (
                level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)
            ):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or (
                level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)
            ):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or (
                        level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or (
                        level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 or (
                        level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 or (
                        level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or (
                        level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or (
                        level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 or (
                        level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 or (
                        level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)
                    ):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_clyde(self):
        # r, l, u, d
        # clyde is going to turn whenever advantageous for pursuit
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = WIDTH
        elif self.x_pos > WIDTH:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = WIDTH
        elif self.x_pos > WIDTH:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # r, l, u, d
        # inky turns up or down at any point to pursue, but left and right only on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = WIDTH
        elif self.x_pos > WIDTH:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d
        # pinky is going to turn left or right whenever advantageous, but only up or down on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = WIDTH
        elif self.x_pos > WIDTH:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction


def draw_board():
    num1 = GAME_HEIGHT // 32
    num2 = WIDTH // 30
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, "white", (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, "white", (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(
                    screen,
                    BOARD_COLOR,
                    (j * num2 + (0.5 * num2), i * num1),
                    (j * num2 + (0.5 * num2), i * num1 + num1),
                    3,
                )
            if level[i][j] == 4:
                pygame.draw.line(
                    screen,
                    BOARD_COLOR,
                    (j * num2, i * num1 + (0.5 * num1)),
                    (j * num2 + num2, i * num1 + (0.5 * num1)),
                    3,
                )
            if level[i][j] == 5:
                pygame.draw.arc(
                    screen,
                    BOARD_COLOR,
                    [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                    0,
                    PI / 2,
                    3,
                )
            if level[i][j] == 6:
                pygame.draw.arc(
                    screen,
                    BOARD_COLOR,
                    [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                    PI / 2,
                    PI,
                    3,
                )
            if level[i][j] == 7:
                pygame.draw.arc(
                    screen,
                    BOARD_COLOR,
                    [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1],
                    PI,
                    3 * PI / 2,
                    3,
                )
            if level[i][j] == 8:
                pygame.draw.arc(
                    screen,
                    BOARD_COLOR,
                    [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                    3 * PI / 2,
                    2 * PI,
                    3,
                )
            if level[i][j] == 9:
                pygame.draw.line(
                    screen,
                    "white",
                    (j * num2, i * num1 + (0.5 * num1)),
                    (j * num2 + num2, i * num1 + (0.5 * num1)),
                    3,
                )


def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))


def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = GAME_HEIGHT // 32
    num2 = WIDTH // 30
    num3 = 15
    # check collisions based on center x and center y of player +/- fudge number
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True
    return turns


def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += PLAYER_SPEED
    elif direction == 1 and turns_allowed[1]:
        play_x -= PLAYER_SPEED
    if direction == 2 and turns_allowed[2]:
        play_y -= PLAYER_SPEED
    elif direction == 3 and turns_allowed[3]:
        play_y += PLAYER_SPEED
    return play_x, play_y


def check_collisions(scor, power, power_count, eaten_ghosts, center_x, center_y):
    num1 = GAME_HEIGHT // 32
    num2 = WIDTH // 30
    if 0 < player_x < 870:
        tile = level[center_y // num1][center_x // num2]
        if tile == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if tile == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]
    return scor, power, power_count, eaten_ghosts


def build_ghosts():
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead, blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead, inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead, pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead, clyde_box, 3)
    return blinky, inky, pinky, clyde


def get_targets(blinky_obj, inky_obj, pinky_obj, clyde_obj):
    if player_x < 450:
        runaway_x = 900
    else:
        runaway_x = 0
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)
    if powerup:
        if not blinky_obj.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky_obj.dead and eaten_ghost[0]:
            if 340 < blinky_obj.x_pos < 560 and 340 < blinky_obj.y_pos < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

        if not inky_obj.dead and not eaten_ghost[1]:
            ink_target = (runaway_x, player_y)
        elif not inky_obj.dead and eaten_ghost[1]:
            if 340 < inky_obj.x_pos < 560 and 340 < inky_obj.y_pos < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target

        if not pinky_obj.dead:
            pink_target = (player_x, runaway_y)
        elif not pinky_obj.dead and eaten_ghost[2]:
            if 340 < pinky_obj.x_pos < 560 and 340 < pinky_obj.y_pos < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target

        if not clyde_obj.dead and not eaten_ghost[3]:
            clyde_target = (450, 450)
        elif not clyde_obj.dead and eaten_ghost[3]:
            if 340 < clyde_obj.x_pos < 560 and 340 < clyde_obj.y_pos < 500:
                clyde_target = (400, 100)
            else:
                clyde_target = (player_x, player_y)
        else:
            clyde_target = return_target
    else:
        if not blinky_obj.dead:
            if 340 < blinky_obj.x_pos < 560 and 340 < blinky_obj.y_pos < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target
        if not inky_obj.dead:
            if 340 < inky_obj.x_pos < 560 and 340 < inky_obj.y_pos < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky_obj.dead:
            if 340 < pinky_obj.x_pos < 560 and 340 < pinky_obj.y_pos < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde_obj.dead:
            if 340 < clyde_obj.x_pos < 560 and 340 < clyde_obj.y_pos < 500:
                clyde_target = (400, 100)
            else:
                clyde_target = (player_x, player_y)
        else:
            clyde_target = return_target

    return [blink_target, ink_target, pink_target, clyde_target]


def update_ghost_speeds():
    global ghost_speeds
    if powerup:
        ghost_speeds = [1, 1, 1, 1]
    else:
        ghost_speeds = [2, 2, 2, 2]
    if eaten_ghost[0]:
        ghost_speeds[0] = 2
    if eaten_ghost[1]:
        ghost_speeds[1] = 2
    if eaten_ghost[2]:
        ghost_speeds[2] = 2
    if eaten_ghost[3]:
        ghost_speeds[3] = 2
    if blinky_dead:
        ghost_speeds[0] = 4
    if inky_dead:
        ghost_speeds[1] = 4
    if pinky_dead:
        ghost_speeds[2] = 4
    if clyde_dead:
        ghost_speeds[3] = 4


def remaining_pellets():
    for row in level:
        if 1 in row or 2 in row:
            return True
    return False


def add_ghost_score():
    global score, score_pop_timer
    score += (2 ** eaten_ghost.count(True)) * 100
    score_pop_timer = 12


def update_gameplay():
    global counter, flicker, power_counter, powerup, eaten_ghost
    global startup_counter, moving, turns_allowed, direction
    global player_x, player_y
    global blinky_x, blinky_y, blinky_direction, blinky_dead
    global inky_x, inky_y, inky_direction, inky_dead
    global pinky_x, pinky_y, pinky_direction, pinky_dead
    global clyde_x, clyde_y, clyde_direction, clyde_dead
    global targets, score, score_pop_timer

    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True

    if powerup and power_counter < POWERUP_FRAMES:
        power_counter += 1
    elif powerup and power_counter >= POWERUP_FRAMES:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]

    if startup_counter < STARTUP_FRAMES:
        moving = False
        startup_counter += 1
    else:
        moving = True

    center_x = player_x + 23
    center_y = player_y + 24
    turns_allowed[:] = check_position(center_x, center_y)

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    update_ghost_speeds()
    blinky, inky, pinky, clyde = build_ghosts()
    targets[:] = get_targets(blinky, inky, pinky, clyde)

    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
        if not pinky_dead and not pinky.in_box:
            pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
        else:
            pinky_x, pinky_y, pinky_direction = pinky.move_clyde()
        if not inky_dead and not inky.in_box:
            inky_x, inky_y, inky_direction = inky.move_inky()
        else:
            inky_x, inky_y, inky_direction = inky.move_clyde()
        clyde_x, clyde_y, clyde_direction = clyde.move_clyde()

    if player_x > WIDTH:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    blinky, inky, pinky, clyde = build_ghosts()
    center_x = player_x + 23
    center_y = player_y + 24
    player_circle = pygame.Rect((center_x - 20, center_y - 20), (40, 40))

    previous_score = score
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost, center_x, center_y)
    if score > previous_score:
        score_pop_timer = 10

    if not powerup:
        if (
            (player_circle.colliderect(blinky.rect) and not blinky.dead)
            or (player_circle.colliderect(inky.rect) and not inky.dead)
            or (player_circle.colliderect(pinky.rect) and not pinky.dead)
            or (player_circle.colliderect(clyde.rect) and not clyde.dead)
        ):
            lose_life_or_game_over()
            return

    if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead:
        lose_life_or_game_over()
        return
    if powerup and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky.dead:
        lose_life_or_game_over()
        return
    if powerup and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky.dead:
        lose_life_or_game_over()
        return
    if powerup and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde.dead:
        lose_life_or_game_over()
        return

    if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
        blinky_dead = True
        eaten_ghost[0] = True
        add_ghost_score()
    if powerup and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]:
        inky_dead = True
        eaten_ghost[1] = True
        add_ghost_score()
    if powerup and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]:
        pinky_dead = True
        eaten_ghost[2] = True
        add_ghost_score()
    if powerup and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]:
        clyde_dead = True
        eaten_ghost[3] = True
        add_ghost_score()

    if blinky.in_box and blinky_dead:
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde_dead:
        clyde_dead = False

    if score_pop_timer > 0:
        score_pop_timer -= 1

    sync_high_score()
    if not remaining_pellets():
        sync_high_score()
        start_transition(STATE_WIN)


def draw_game_scene():
    screen.fill("black")
    draw_board()
    draw_player()
    blinky, inky, pinky, clyde = build_ghosts()
    blinky.draw()
    inky.draw()
    pinky.draw()
    clyde.draw()
    ui.draw_hud(
        screen,
        fonts,
        score,
        best_score,
        lives,
        level_number,
        show_fps,
        clock.get_fps(),
        score_pop_timer,
    )


def activate_menu_option(index):
    global run, controls_index
    if index == 0:
        start_new_game()
        start_transition(STATE_PLAYING)
    elif index == 1:
        controls_index = 0
        start_transition(STATE_CONTROLS)
    elif index == 2:
        sync_high_score()
        save_high_score(best_score)
        run = False


def activate_controls_option(index):
    global music_enabled, sfx_enabled
    if index == 0:
        music_enabled = not music_enabled
    elif index == 1:
        sfx_enabled = not sfx_enabled
    elif index == 2:
        start_transition(STATE_MENU)


def activate_pause_option(index):
    global run
    if index == 0:
        start_transition(STATE_PLAYING)
    elif index == 1:
        start_new_game()
        start_transition(STATE_PLAYING)
    elif index == 2:
        sync_high_score()
        save_high_score(best_score)
        run = False


def handle_menu_event(event):
    global menu_index
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            menu_index = (menu_index - 1) % 3
        elif event.key == pygame.K_DOWN:
            menu_index = (menu_index + 1) % 3
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            activate_menu_option(menu_index)
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            activate_menu_option(2)
    elif event.type == pygame.MOUSEMOTION:
        for index, button in enumerate(menu_button_rects):
            if button.collidepoint(event.pos):
                menu_index = index
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for index, button in enumerate(menu_button_rects):
            if button.collidepoint(event.pos):
                menu_index = index
                activate_menu_option(index)
                break


def handle_controls_event(event):
    global controls_index, music_enabled, sfx_enabled
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            controls_index = (controls_index - 1) % 3
        elif event.key == pygame.K_DOWN:
            controls_index = (controls_index + 1) % 3
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            activate_controls_option(controls_index)
        elif event.key == pygame.K_m:
            music_enabled = not music_enabled
        elif event.key == pygame.K_n:
            sfx_enabled = not sfx_enabled
        elif event.key == pygame.K_ESCAPE:
            start_transition(STATE_MENU)
    elif event.type == pygame.MOUSEMOTION:
        for index, button in enumerate(controls_button_rects):
            if button.collidepoint(event.pos):
                controls_index = index
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for index, button in enumerate(controls_button_rects):
            if button.collidepoint(event.pos):
                controls_index = index
                activate_controls_option(index)
                break


def handle_playing_event(event):
    global direction_command, run, pause_index
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
            direction_command = 0
        elif event.key == pygame.K_LEFT:
            direction_command = 1
        elif event.key == pygame.K_UP:
            direction_command = 2
        elif event.key == pygame.K_DOWN:
            direction_command = 3
        elif event.key in (pygame.K_p, pygame.K_ESCAPE):
            pause_index = 0
            start_transition(STATE_PAUSED)
        elif event.key == pygame.K_q:
            sync_high_score()
            save_high_score(best_score)
            run = False
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_RIGHT and direction_command == 0:
            direction_command = direction
        elif event.key == pygame.K_LEFT and direction_command == 1:
            direction_command = direction
        elif event.key == pygame.K_UP and direction_command == 2:
            direction_command = direction
        elif event.key == pygame.K_DOWN and direction_command == 3:
            direction_command = direction


def handle_pause_event(event):
    global pause_index
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            pause_index = (pause_index - 1) % 3
        elif event.key == pygame.K_DOWN:
            pause_index = (pause_index + 1) % 3
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            activate_pause_option(pause_index)
        elif event.key in (pygame.K_p, pygame.K_ESCAPE):
            start_transition(STATE_PLAYING)
        elif event.key == pygame.K_r:
            activate_pause_option(1)
    elif event.type == pygame.MOUSEMOTION:
        for index, button in enumerate(pause_button_rects):
            if button.collidepoint(event.pos):
                pause_index = index
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for index, button in enumerate(pause_button_rects):
            if button.collidepoint(event.pos):
                pause_index = index
                activate_pause_option(index)
                break


def handle_end_event(event):
    global run
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            start_new_game()
            start_transition(STATE_PLAYING)
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            sync_high_score()
            save_high_score(best_score)
            run = False


start_new_game()

while run:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sync_high_score()
            save_high_score(best_score)
            run = False
            continue

        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            show_fps = not show_fps
            continue

        if transitioning:
            continue

        if state == STATE_MENU:
            handle_menu_event(event)
        elif state == STATE_CONTROLS:
            handle_controls_event(event)
        elif state == STATE_PLAYING:
            handle_playing_event(event)
        elif state == STATE_PAUSED:
            handle_pause_event(event)
        elif state in (STATE_GAME_OVER, STATE_WIN):
            handle_end_event(event)

    if not transitioning and state == STATE_PLAYING:
        update_gameplay()

    if state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_WIN):
        draw_game_scene()
    else:
        ui.draw_gradient_background(screen, WIDTH, HEIGHT)

    menu_button_rects = []
    controls_button_rects = []
    pause_button_rects = []

    if state == STATE_MENU:
        menu_button_rects = ui.draw_menu(
            screen,
            fonts,
            "PackMan",
            "Classic maze chase with polished menus",
            ["Play", "Controls", "Quit"],
            menu_index,
            mouse_pos,
            mouse_down,
        )
    elif state == STATE_CONTROLS:
        controls_button_rects = ui.draw_controls_screen(
            screen,
            fonts,
            controls_index,
            mouse_pos,
            mouse_down,
            music_enabled,
            sfx_enabled,
        )
    elif state == STATE_PAUSED:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 130))
        screen.blit(dim, (0, 0))
        pause_button_rects = ui.draw_menu(
            screen,
            fonts,
            "Paused",
            "Select an option",
            ["Resume", "Restart", "Quit"],
            pause_index,
            mouse_pos,
            mouse_down,
        )
    elif state == STATE_GAME_OVER:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 145))
        screen.blit(dim, (0, 0))
        ui.draw_end_screen(screen, fonts, False, score, best_score)
    elif state == STATE_WIN:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 145))
        screen.blit(dim, (0, 0))
        ui.draw_end_screen(screen, fonts, True, score, best_score)

    update_transition()
    ui.draw_fade_overlay(screen, fade_alpha)
    pygame.display.flip()


sync_high_score()
save_high_score(best_score)
pygame.quit()
