"""
Pruebas automáticas y smoke tests para el MVP de Flappy Bird.
Se ejecutan sin necesidad de ventana física gracias al dummy video driver de SDL.
"""
import os
import sys
from pathlib import Path

# Agregar directorio raíz al sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Forzar controladores virtuales de SDL para entornos sin display físico o pruebas automáticas
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    STATE_START,
    STATE_PLAYING,
    STATE_GAMEOVER,
    STATE_PAUSED,
    GROUND_HEIGHT,
    BIRD_RADIUS,
)
from src.audio import AudioManager
from src.bird import Bird
from src.pipe import PipePair
from src.world import World
from src.ui import UIManager
from src.game import FlappyBirdGame


def test_audio_manager_initialization():
    audio = AudioManager()
    # Verifica que el manejador inicialice sin excepciones
    assert audio is not None
    assert "flap" in audio.sounds
    assert "score" in audio.sounds
    assert "hit" in audio.sounds
    assert "fall" in audio.sounds


def test_bird_mechanics():
    bird = Bird(x=90, y=300)
    assert bird.alive is True
    assert bird.vel_y == 0.0

    # Test flap
    bird.flap()
    assert bird.vel_y < 0  # Velocidad ascendente negativa

    # Test physics update
    initial_y = bird.y
    bird.update()
    assert bird.y != initial_y
    assert bird.rect is not None
    assert bird.mask is not None

    # Test idle update
    bird.reset()
    bird.update_idle(0.016)
    assert bird.alive is True


def test_pipe_pair():
    pipe = PipePair(x=300)
    assert pipe.top_rect.width > 0
    assert pipe.bottom_rect.width > 0
    assert pipe.gap_bottom > pipe.gap_top
    assert not pipe.passed

    # Test movement standard and custom speed
    x_before = pipe.x
    pipe.update(speed=2.0)
    assert abs(pipe.x - (x_before - 2.0)) < 1e-4

    pipe.update(speed=3.5)
    assert abs(pipe.x - (x_before - 5.5)) < 1e-4

    # Test bird collision
    # Pájaro dentro del cuerpo de la tubería inferior
    bird = Bird(x=pipe.bottom_rect.centerx, y=pipe.bottom_rect.centery)
    assert pipe.collides_with(bird) is True

    # Pájaro centrado dentro del gap (sin colisión)
    bird.y = (pipe.gap_top + pipe.gap_bottom) / 2
    bird._update_transformed_sprite()
    assert pipe.collides_with(bird) is False


def test_dynamic_speed_scaling():
    game = FlappyBirdGame()
    # Puntuación 0 a 4 -> Nivel 1, velocidad base
    game.score = 0
    assert game.get_current_level() == 1
    assert abs(game.get_current_speed() - 1.9) < 1e-4

    game.score = 4
    assert game.get_current_level() == 1
    assert abs(game.get_current_speed() - 1.9) < 1e-4

    # Puntuación 5 a 9 -> Nivel 2 (+0.25)
    game.score = 5
    assert game.get_current_level() == 2
    assert abs(game.get_current_speed() - 2.15) < 1e-4

    # Puntuación 10 a 14 -> Nivel 3 (+0.50)
    game.score = 10
    assert game.get_current_level() == 3
    assert abs(game.get_current_speed() - 2.40) < 1e-4

    # Puntuación 20 -> Nivel 5 (+1.00)
    game.score = 20
    assert game.get_current_level() == 5
    assert abs(game.get_current_speed() - 2.90) < 1e-4

    # Puntuación muy alta -> tope en MAX_PIPE_SPEED (4.0)
    game.score = 100
    assert game.get_current_speed() <= 4.0


def test_world_rendering():
    world = World()
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    world.draw_background(surf)
    world.draw_ground(surf)
    world.update(moving=True, speed=2.5)
    # Comprobar que no hay errores de dibujo y que ground_x actualiza
    assert world.sky_surface is not None


def test_ui_rendering():
    ui = UIManager()
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    ui.draw_start_screen(surf, 0.016)
    ui.draw_playing_hud(surf, score=5, level=2, speedup_timer=50)
    ui.draw_game_over_screen(surf, score=15, highscore=20, is_new_record=False, dt=0.016)
    ui.draw_pause_screen(surf)


def test_game_loop_headless_simulation():
    game = FlappyBirdGame()
    assert game.state == STATE_START

    # Iniciar juego con un aleteo
    game.handle_flap()
    assert game.state == STATE_PLAYING

    # Simular 30 cuadros manteniendo el pájaro volando con aleteos
    for i in range(30):
        if i % 10 == 0:
            game.handle_flap()
        game.update(1.0 / 60.0)
        game.draw(1.0 / 60.0)

    assert game.state == STATE_PLAYING
    assert game.bird.alive is True

    # Probar pausa
    event_p = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
    pygame.event.post(event_p)
    game.handle_events()
    assert game.state == STATE_PAUSED

    # Despausar
    pygame.event.post(event_p)
    game.handle_events()
    assert game.state == STATE_PLAYING

    # Forzar game over
    game.trigger_game_over()
    assert game.state == STATE_GAMEOVER
    assert game.bird.alive is False


if __name__ == "__main__":
    print("Ejecutando pruebas manuales...")
    test_audio_manager_initialization()
    test_bird_mechanics()
    test_pipe_pair()
    test_dynamic_speed_scaling()
    test_world_rendering()
    test_ui_rendering()
    test_game_loop_headless_simulation()
    print("¡Todas las pruebas pasaron exitosamente!")
