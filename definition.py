import sys
from enum import Enum

FIELD_ROW = 59
FIELD_COL = 79
VIEW_ROW = 17
VIEW_COL = 29
ENEMY_SPEED = 2
MAX_TURN = (FIELD_ROW + FIELD_COL) * 20 * ENEMY_SPEED
MAX_ITEM = 10
FPS = 10 * ENEMY_SPEED

color = ((255, 255, 255), (0, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0), (150, 150, 255))
State = Enum("State", "Title Setting Play GameOver GameClear")
TitleState = Enum("TitleState", "Start Setting Rule Score")
