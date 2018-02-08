import numpy as np
import pygame
from pygame.locals import QUIT, Rect, KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE, K_a, K_d, K_s, K_w
import random as rnd
from definition import *


class Field(object):
    def __init__(self, p, es):
        self.turn = 0
        self.field = np.array([[0 if (x & 1 or y & 1) and (x != 0 and x != FIELD_COL-1) else 1 for x in range(FIELD_COL)]
                       if y != 0 and y != FIELD_ROW-1 else [1 for _ in range(FIELD_COL)]
                      for y in range(FIELD_ROW)])
        self.field[p.pos_y][p.pos_x] = 3
        for e in es:
            self.field[e.pos_y][e.pos_x] = 4
        while True:
            goal_pos = (rnd.randrange(0, FIELD_COL), rnd.randrange(1, FIELD_ROW-1))
            if self.field[goal_pos[1]][[goal_pos[0]]] == 0 or self.field[goal_pos[1]][[goal_pos[0]]] == 1:
                break
        self.goal_pos = goal_pos
        self.field[self.goal_pos[1]][self.goal_pos[0]] = 5

    def check_empty(self, x, y, ptype=False):
        if self.field[y][x] == 1 or self.field[y][x] == 2:
            return False
        elif (self.goal_pos[0] == x and self.goal_pos[1] == y) and ptype != True:
            return False
        elif self.field[y][x] == 4 and ptype != True:
            return False
        else:
            return True

    def draw(self, player_pos_x, player_pos_y, *objects):
        if player_pos_x <= VIEW_COL // 2:
            xview_start = 0
            xview_end = VIEW_COL
        elif player_pos_x >= FIELD_COL - (VIEW_COL // 2):
            xview_start = FIELD_COL - VIEW_COL
            xview_end = FIELD_COL
        else:
            xview_start = player_pos_x - (VIEW_COL // 2)
            xview_end = player_pos_x + (VIEW_COL // 2) + 1
        if player_pos_y <= VIEW_ROW // 2:
            yview_start = 0
            yview_end = VIEW_ROW
        elif player_pos_y >= FIELD_ROW - (VIEW_ROW // 2):
            yview_start = FIELD_ROW - VIEW_ROW
            yview_end = FIELD_ROW
        else:
            yview_start = player_pos_y - (VIEW_ROW // 2)
            yview_end = player_pos_y + (VIEW_ROW // 2) + 1
        view_field = self.field[yview_start: yview_end, xview_start: xview_end].tolist()

        SURFACE.fill(color[1])
        SURFACE.blit(controlImg, (0,0))

        player = objects[0]
        inViewer = lambda o: (o.pos_x >= xview_start and o.pos_x < xview_end 
                              and o.pos_y >= yview_start and o.pos_y < yview_end)
        enemys = [enm for enm in objects[1] if inViewer(enm)]
        blocks = [blk for blk in objects[2] if inViewer(blk)]
        enemy_index = 0
        block_index = 0

        for y in range(VIEW_ROW):
            for x in range(VIEW_COL):
                x_pos = 25 + x * 25
                y_pos = 10 + y * 25
                c_idx = view_field[y][x] if view_field[y][x] <= 2 else 0
                if c_idx == 1:
                    SURFACE.blit(wallImg, (x_pos, y_pos))
                else:
                    pygame.draw.rect(SURFACE, color[c_idx], (x_pos, y_pos, 24, 24))
                    if view_field[y][x] == 2:
                        blocks[block_index].draw(x_pos, y_pos)
                        block_index += 1
                    if view_field[y][x] == 3:
                        player.draw(x_pos, y_pos-10)
                    elif view_field[y][x] == 4:
                        enemys[enemy_index].draw(x_pos, y_pos-10)
                        enemy_index += 1
                    elif view_field[y][x] == 5:
                        pygame.draw.rect(SURFACE, color[5], (x_pos, y_pos, 24, 24))


class Block(object):
    def __init__(self, field, x, y):
        field[y][x] = 2
        self.pos_x = x
        self.pos_y = y
        self.life = 50
        self.mark = 2

    def breaking(self, field):
        field[self.pos_y][self.pos_x] = 0

    def draw(self, x_pos, y_pos):
        pygame.draw.rect(SURFACE, (0, 105+3*self.life, 0), (x_pos, y_pos, 24, 24))


class Agent(object):
    def __init__(self, x, y, mark, agentImg):
        self.pos_x = x
        self.pos_y = y
        self.direction = 2
        self.images = []
        for i in range(4):
            image = pygame.Surface((25, 25), pygame.SRCALPHA)
            image.set_alpha(0)
            image.blit(agentImg, (0, 0), Rect(i*25, 0, 25, 25))
            self.images.append(image)
        self.mark = mark

    def pos_reset(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def move(self, field, x, y):
        field[self.pos_y][self.pos_x] = 0
        self.pos_x = x
        self.pos_y = y
        field[self.pos_y][self.pos_x] = self.mark

    def draw(self, x_pos, y_pos):
        SURFACE.blit(self.images[self.direction], (x_pos, y_pos))


class Player(Agent):
    def __init__(self, x, y):
        super().__init__(x, y, 3, playerImg)
        self.item_num = MAX_ITEM
        self.direction = 2

    def pos_reset(self):
        super().pos_reset(1, 1)

    def put(self, field, put_x, put_y):
        if self.item_num > 0:
            self.item_num -= 1
            return Block(field, put_x, put_y)
        else:
            return None


class Enemy(Agent):
    def __init__(self, x, y, speed=1):
        super().__init__(x, y, 4, enemyImg)
        self.speed = speed
        self.move_history = None

    def pos_reset(self):
        super().pos_reset(FIELD_COL-2, FIELD_ROW-2)

    def move_strategy(self, px, py):
        # A:0 >:1 V:2 <:3

        if rnd.random() < 0.5:
            if self.pos_x < px:
                self.direction = 3
                return (self.pos_x + 1, self.pos_y)
            elif self.pos_x > px:
                self.direction = 0
                return (self.pos_x - 1, self.pos_y)
        else:
            if self.pos_y < py:
                self.direction = 1
                return (self.pos_x, self.pos_y + 1)
            elif self.pos_y > py:
                self.direction = 2
                return (self.pos_x, self.pos_y - 1)

        return (self.pos_x, self.pos_y)


pygame.init()
SURFACE = pygame.display.set_mode((775, 570))
pygame.display.set_caption("地上最大の作戦")
FPSCLOCK = pygame.time.Clock()

titleImg = pygame.image.load("img/title.png").convert()
gameclearImg = pygame.image.load("img/clear.png").convert()
controlImg = pygame.image.load("img/control.png").convert_alpha()
playerImg = pygame.image.load("img/player.png").convert_alpha()
enemyImg = pygame.image.load("img/enemy.png").convert_alpha()
wallImg = pygame.image.load("img/wall.png").convert_alpha()

#selectSound = pygame.mixer.Sound("select.mp3")


def mainloop():
    state = State.Title
    t_state = TitleState.Start
    plr = None
    enm = None
    fld = None
    suicide = False
    key = None
    keys = set([])

    while True:
        if state is State.Play:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYUP:
                    keys.discard(event.key)
                elif event.type == KEYDOWN:
                    keys.add(event.key)
        else:
            key = None
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    key = event.key

        if state is State.Title:
            plr = Player(1, 1)
            enms = [Enemy(FIELD_COL-2, FIELD_ROW-2, 2), Enemy(1, FIELD_ROW-2, 2), Enemy(FIELD_COL-2, 1, 2)]
            blcks = []
            fld = Field(plr, enms)

            SURFACE.blit(titleImg, (0,0))
            if key == K_SPACE:
                state = State.Play
                #selectSound.play()
                key = None
                keys.clear()

        elif state is State.Setting:
            print("setting")

        elif state is State.Play:
            print("> turn: {}".format(fld.turn))
            print("> item: {}".format(plr.item_num))
            # player move
            if fld.turn % ENEMY_SPEED == 0:
                next_px, next_py = plr.pos_x, plr.pos_y
                if K_RIGHT in keys:
                    next_px += 1
                    plr.direction = 0
                elif K_LEFT  in keys:
                    next_px -= 1
                    plr.direction = 1
                elif K_DOWN in keys:
                    next_py += 1
                    plr.direction = 2
                elif K_UP in keys:
                    next_py -= 1
                    plr.direction = 3
                elif K_SPACE in keys:
                    pass
                    #suicide = True

                if fld.check_empty(next_px, next_py, ptype=True):
                    print(">>> player move!")
                    plr.move(fld.field, next_px, next_py)

                # put
                put_x, put_y = plr.pos_x, plr.pos_y
                if K_d in keys:
                    put_x += 1
                elif K_a in keys:
                    put_x -= 1
                elif K_s in keys:
                    put_y += 1
                elif K_w in keys:
                    put_y -= 1

                if fld.check_empty(put_x, put_y) and not (put_x == plr.pos_x and put_y == plr.pos_y):
                    print(">>> put!")
                    put_blck = plr.put(fld.field, put_x, put_y)
                    if put_blck != None:
                        blcks.append(put_blck)
                        blcks.sort(key=lambda b: b.pos_x + b.pos_y*FIELD_COL)

            # enemy move
            for enm in enms:
                if enm.speed == 1:
                    if fld.turn % ENEMY_SPEED != 0:
                        continue
                next_ex, next_ey = enm.move_strategy(plr.pos_x, plr.pos_y)

                if fld.check_empty(next_ex, next_ey):
                    print(">>> enemy move!")
                    enm.move(fld.field, next_ex, next_ey)

            enms.sort(key=lambda e: e.pos_x + e.pos_y*FIELD_COL)

            # block break
            for i, b in enumerate(blcks):
                b.life -= 1
                if b.life == 0:
                    b.breaking(fld.field)
                    del blcks[i]

            # draw
            fld.draw(plr.pos_x, plr.pos_y, plr, enms, blcks)

            # gameover check
            contact = False
            for enm in enms:
                contact = contact or (plr.pos_x == enm.pos_x and plr.pos_y == enm.pos_y)
            if contact or suicide: # or fld.turn > MAX_TURN:
                print("you lose...")
                state = State.GameOver
            elif plr.pos_x == fld.goal_pos[0] and plr.pos_y == fld.goal_pos[1]:
                print("you win...")
                state = State.GameClear
                #SURFACE.blit(gameclearImg, (0,0))

            fld.turn += 1

        elif state is State.GameOver:
            fld.draw(plr.pos_x, plr.pos_y, plr, enms, blcks)
            if key == K_SPACE:
                #fld.turn = 0
                #plr.pos_reset()
                #enm.pos_reset()
                suicide = False
                state = State.Title
                #selectSound.play()

        elif state is State.GameClear:
            SURFACE.blit(gameclearImg, (0,0))
            if key == K_SPACE:
                #fld.turn = 0
                #plr.pos_reset()
                #enm.pos_reset()
                suicide = False
                state = State.Title
                #selectSound.play()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == "__main__":
    mainloop()
