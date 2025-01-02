import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox

WIDTH = 600
HEIGHT = 600
ROWS = 30

OBSTACLE_COUNT = 10
BASE_SPEED = 10
ACCELERATED_SPEED = 20
SLOWED_SPEED = 5
BONUS_DURATION = 30
BONUS_PROBABILITY = 0.02
BONUS_ON_FIELD_TIME = 300
BONUS_TYPES = ["ACCELERATION", "SLOWDOWN"]

MINE_APPEAR_CHANCE = 0.3
MINE_MAX_COUNT = 3
MINE_LIFETIME_TICKS = 120
MINE_REQUIRED_DISTANCE = 7

# Длительность анимации взрыва (в тиках)
EXPLOSION_TICKS = 15

class Cube:
    def __init__(self, start_pos, dirnx=0, dirny=0, color=(255, 0, 0)):
        self.pos = start_pos
        self.dirnx = dirnx
        self.dirny = dirny
        self.color = color
        self.rows = ROWS
        self.w = WIDTH

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        x, y = self.pos
        self.pos = (x + self.dirnx, y + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i, j = self.pos
        pygame.draw.rect(surface, self.color, (i*dis+1, j*dis+1, dis-2, dis-2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i*dis + centre - radius, j*dis + 8)
            circleMiddle2 = (i*dis + dis - radius*2, j*dis + 8)
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)

class Snake:
    def __init__(self, color, start_pos):
        self.color = color
        self.head = Cube(start_pos)
        self.body = [self.head]
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        elif keys[pygame.K_RIGHT]:
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        elif keys[pygame.K_UP]:
            self.dirnx = 0
            self.dirny = -1
            self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        elif keys[pygame.K_DOWN]:
            self.dirnx = 0
            self.dirny = 1
            self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        for i, c in enumerate(self.body):
            pos = c.pos[:]
            if pos in self.turns:
                turn = self.turns[pos]
                c.move(turn[0], turn[1])
                if i == len(self.body)-1:
                    self.turns.pop(pos)
            else:
                c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head = Cube(pos)
        self.body = [self.head]
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny
        x, y = tail.pos
        if dx == 1 and dy == 0:
            self.body.append(Cube((x-1, y)))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((x+1, y)))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((x, y-1)))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((x, y+1)))
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

class Mine:
    def __init__(self, pos):
        self.pos = pos
        self.timer = MINE_LIFETIME_TICKS
        self.color = (200, 0, 0)
        self.state = "idle"
        self.explosion_timer = 0

    def update(self, headPos):
        if self.state == "idle":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "exploding"
                self.explosion_timer = EXPLOSION_TICKS
        elif self.state == "exploding":
            # Если змея в радиусе 1 клетки, она погибает
            hx, hy = headPos
            mx, my = self.pos
            if abs(hx - mx) <= 1 and abs(hy - my) <= 1:
                return "KILL_SNAKE"
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.state = "done"
        return None

    def draw(self, surface):
        dis = WIDTH // ROWS
        i, j = self.pos
        if self.state == "idle":
            pygame.draw.rect(surface, self.color, (i*dis+1, j*dis+1, dis-2, dis-2))
        elif self.state == "exploding":
            center_x = i*dis + dis//2
            center_y = j*dis + dis//2
            max_radius = dis*2
            progress = (EXPLOSION_TICKS - self.explosion_timer) / float(EXPLOSION_TICKS)
            r = int(progress * max_radius)
            pygame.draw.circle(surface, (255, 160, 0), (center_x, center_y), r)

def drawGrid(w, rows, surface):
    sizeBtwn = w // rows
    x = 0
    y = 0
    for l in range(rows):
        x += sizeBtwn
        y += sizeBtwn
        pygame.draw.line(surface, (255,255,255), (x, 0), (x, w))
        pygame.draw.line(surface, (255,255,255), (0, y), (w, y))

def randomPosition(rows, exclude_positions=None):
    if exclude_positions is None:
        exclude_positions = set()
    while True:
        x = random.randrange(0, rows)
        y = random.randrange(0, rows)
        if (x, y) not in exclude_positions:
            return (x, y)

def distanceManhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def createObstacles(snake_obj, count=10):
    obstacles_list = []
    occupied = {c.pos for c in snake_obj.body}
    for _ in range(count):
        pos = randomPosition(ROWS, occupied)
        obstacles_list.append(Cube(pos, color=(128,128,128)))
        occupied.add(pos)
    return obstacles_list

def redrawWindow(win, snake_obj, snack, bonus, obstacles, mines):
    win.fill((0,0,0))
    drawGrid(WIDTH, ROWS, win)
    snack.draw(win)
    if bonus:
        bonus.draw(win)
    for obs in obstacles:
        obs.draw(win)
    for m in mines:
        m.draw(win)
    snake_obj.draw(win)
    pygame.display.update()

def trySpawnMine(snake_head, snake_body, obstacles, mines, snack, bonus):
    exclude = {c.pos for c in snake_body} | {obs.pos for obs in obstacles} | {m.pos for m in mines}
    if bonus:
        exclude.add(bonus.pos)
    exclude.add(snack.pos)
    possible_positions = []
    for x in range(ROWS):
        for y in range(ROWS):
            if (x,y) not in exclude:
                if distanceManhattan(snake_head, (x,y)) >= MINE_REQUIRED_DISTANCE:
                    possible_positions.append((x,y))
    if not possible_positions:
        return None
    return random.choice(possible_positions)

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake with bomb explosion animation")

    s = Snake(color=(255,0,0), start_pos=(ROWS//2, ROWS//2))
    s.addCube()
    obstacles = createObstacles(s, OBSTACLE_COUNT)
    mines = []
    exclude = {c.pos for c in s.body} | {obs.pos for obs in obstacles}
    snack_pos = randomPosition(ROWS, exclude)
    snack = Cube(snack_pos, color=(0,255,0))
    bonus = None
    bonus_type = None
    bonus_timer = 0
    bonus_duration_snake = 0
    current_speed = BASE_SPEED
    clock = pygame.time.Clock()
    run = True

    while run:
        pygame.time.delay(50)
        clock.tick(current_speed)
        s.move()
        headPos = s.head.pos

        if not (0 <= headPos[0] < ROWS and 0 <= headPos[1] < ROWS):
            print("Score:", len(s.body))
            s.reset((ROWS//2, ROWS//2))
            obstacles = createObstacles(s, OBSTACLE_COUNT)
            mines = []
            exclude = {c.pos for c in s.body} | {obs.pos for obs in obstacles}
            snack_pos = randomPosition(ROWS, exclude)
            snack = Cube(snack_pos, color=(0,255,0))
            bonus = None
            bonus_timer = 0
            current_speed = BASE_SPEED
            bonus_duration_snake = 0

        for obs in obstacles:
            if headPos == obs.pos:
                print("Score:", len(s.body))
                s.reset((ROWS//2, ROWS//2))
                obstacles = createObstacles(s, OBSTACLE_COUNT)
                mines = []
                exclude = {c.pos for c in s.body} | {o.pos for o in obstacles}
                snack_pos = randomPosition(ROWS, exclude)
                snack = Cube(snack_pos, color=(0,255,0))
                bonus = None
                bonus_timer = 0
                current_speed = BASE_SPEED
                bonus_duration_snake = 0
                break

        for m in mines:
            if headPos == m.pos and m.state == "idle":
                print("Score:", len(s.body))
                s.reset((ROWS//2, ROWS//2))
                obstacles = createObstacles(s, OBSTACLE_COUNT)
                mines = []
                exclude = {c.pos for c in s.body} | {o.pos for o in obstacles}
                snack_pos = randomPosition(ROWS, exclude)
                snack = Cube(snack_pos, color=(0,255,0))
                bonus = None
                bonus_timer = 0
                current_speed = BASE_SPEED
                bonus_duration_snake = 0
                break

        if headPos == snack.pos:
            s.addCube()
            exclude = {c.pos for c in s.body} | {obs.pos for obs in obstacles} | {m.pos for m in mines}
            if bonus:
                exclude.add(bonus.pos)
            snack_pos = randomPosition(ROWS, exclude)
            snack = Cube(snack_pos, color=(0,255,0))
            if len(mines) < MINE_MAX_COUNT:
                if random.random() < MINE_APPEAR_CHANCE:
                    new_pos = trySpawnMine(s.head.pos, s.body, obstacles, mines, snack, bonus)
                    if new_pos:
                        mines.append(Mine(new_pos))

        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z: z.pos, s.body[x+1:])):
                print("Score:", len(s.body))
                s.reset((ROWS//2, ROWS//2))
                obstacles = createObstacles(s, OBSTACLE_COUNT)
                mines = []
                exclude = {c.pos for c in s.body} | {o.pos for o in obstacles}
                snack_pos = randomPosition(ROWS, exclude)
                snack = Cube(snack_pos, color=(0,255,0))
                bonus = None
                bonus_timer = 0
                current_speed = BASE_SPEED
                bonus_duration_snake = 0
                break

        if bonus is None:
            if random.random() < BONUS_PROBABILITY:
                exclude = {c.pos for c in s.body} | {obs.pos for obs in obstacles} | {m.pos for m in mines} | {snack.pos}
                pos = randomPosition(ROWS, exclude)
                bonus_type = random.choice(BONUS_TYPES)
                if bonus_type == "ACCELERATION":
                    color = (255, 255, 0)
                else:
                    color = (0, 255, 255)
                bonus = Cube(pos, color=color)
                bonus_timer = BONUS_ON_FIELD_TIME
        else:
            bonus_timer -= 1
            if bonus_timer <= 0:
                bonus = None
                bonus_type = None

        if bonus and headPos == bonus.pos:
            if bonus_type == "ACCELERATION":
                current_speed = ACCELERATED_SPEED
                bonus_duration_snake = BONUS_DURATION
            elif bonus_type == "SLOWDOWN":
                current_speed = SLOWED_SPEED
                bonus_duration_snake = BONUS_DURATION
            bonus = None
            bonus_type = None
            bonus_timer = 0

        if bonus_duration_snake > 0:
            bonus_duration_snake -= 1
            if bonus_duration_snake <= 0:
                current_speed = BASE_SPEED

        mines_to_remove = []
        for m in mines:
            action = m.update(headPos)
            if action == "KILL_SNAKE":
                print("Score:", len(s.body))
                s.reset((ROWS//2, ROWS//2))
                obstacles = createObstacles(s, OBSTACLE_COUNT)
                mines = []
                exclude = {c.pos for c in s.body} | {o.pos for o in obstacles}
                snack_pos = randomPosition(ROWS, exclude)
                snack = Cube(snack_pos, color=(0,255,0))
                bonus = None
                bonus_timer = 0
                current_speed = BASE_SPEED
                bonus_duration_snake = 0
                break
            if m.state == "done":
                mines_to_remove.append(m)

        for rem in mines_to_remove:
            if rem in mines:
                mines.remove(rem)

        redrawWindow(win, s, snack, bonus, obstacles, mines)

if __name__ == "__main__":
    main()
