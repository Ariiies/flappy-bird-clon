"""
Configuración global y constantes para el clon de Flappy Bird.
"""
from pathlib import Path

# Configuración de Pantalla
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Flappy Bird - MVP Python 3.14"

# Física del Pájaro
GRAVITY = 0.42
FLAP_STRENGTH = -7.5
MAX_FALL_SPEED = 10.0
BIRD_X = 90
BIRD_RADIUS = 16

# Tuberías (Pipes) y Dificultad Dinámica
BASE_PIPE_SPEED = 1.9        # Velocidad inicial más lenta y accesible
SPEED_INCREMENT = 1.0       # Incremento de velocidad cada 5 puntos
MAX_PIPE_SPEED = 4.0         # Límite máximo de velocidad
PIPE_SPEED = BASE_PIPE_SPEED # Compatibilidad
PIPE_DISTANCE = 215          # Distancia horizontal uniforme entre tuberías
PIPE_GAP = 142               # Espacio vertical entre tuberías
PIPE_WIDTH = 70
PIPE_CAP_HEIGHT = 28
PIPE_CAP_OVERHANG = 4
PIPE_MIN_HEIGHT = 60
PIPE_SPAWN_INTERVAL = 1500  # Fallback de milisegundos

# Suelo y Escenario
GROUND_HEIGHT = 95
GROUND_SPEED = BASE_PIPE_SPEED

# Colores Retro (Paleta estilo arcade 8-bit / 16-bit)
COLOR_SKY = (112, 197, 206)
COLOR_SKY_TOP = (80, 175, 195)
COLOR_CLOUD = (245, 250, 255)
COLOR_CLOUD_SHADOW = (210, 225, 235)

COLOR_BUSH = (130, 205, 80)
COLOR_BUSH_DARK = (100, 170, 60)

COLOR_GROUND = (222, 216, 149)
COLOR_GROUND_LINE = (195, 185, 120)
COLOR_GRASS = (115, 191, 46)
COLOR_GRASS_LIGHT = (144, 225, 65)
COLOR_GRASS_SHADOW = (80, 140, 30)

COLOR_PIPE = (115, 191, 46)
COLOR_PIPE_LIGHT = (157, 232, 67)
COLOR_PIPE_DARK = (85, 141, 34)
COLOR_PIPE_BORDER = (40, 70, 20)

COLOR_BIRD = (252, 215, 53)
COLOR_BIRD_BELLY = (255, 240, 150)
COLOR_BIRD_SHADOW = (220, 160, 20)
COLOR_BIRD_BEAK = (244, 100, 25)
COLOR_BIRD_BORDER = (55, 45, 30)
COLOR_BIRD_WING = (255, 245, 180)

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (20, 20, 20)
COLOR_TEXT_OUTLINE = (45, 45, 45)
COLOR_GOLD = (255, 215, 0)
COLOR_SILVER = (192, 192, 192)
COLOR_BRONZE = (205, 127, 50)
COLOR_PLATINUM = (229, 228, 226)

# Estados del Juego
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_GAMEOVER = "GAMEOVER"
STATE_PAUSED = "PAUSED"

# Archivo de Guardado
HIGHSCORE_FILE = Path(__file__).resolve().parent.parent / "highscore.json"

