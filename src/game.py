"""
Motor principal del juego Flappy Bird: gestión de bucle, estados, colisiones y renderizado.
"""
import json
import random
import pygame
from src.audio import AudioManager
from src.bird import Bird
from src.config import (
    BASE_PIPE_SPEED,
    BIRD_RADIUS,
    FPS,
    GROUND_HEIGHT,
    HIGHSCORE_FILE,
    MAX_PIPE_SPEED,
    PIPE_DISTANCE,
    PIPE_SPAWN_INTERVAL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPEED_INCREMENT,
    STATE_GAMEOVER,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_START,
    TITLE,
)
from src.pipe import PipePair
from src.ui import UIManager
from src.world import World


class FlappyBirdGame:
    """Clase principal del juego Flappy Bird MVP."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Componentes del juego
        self.audio = AudioManager()
        self.ui = UIManager()
        self.world = World()
        self.bird = Bird()

        # Tuberías y lógica de spawn
        self.pipes: list[PipePair] = []
        self.last_pipe_spawn_time = 0

        # Puntuaciones
        self.score = 0
        self.highscore = self._load_highscore()
        self.is_new_record = False

        # Estado del juego
        self.state = STATE_START
        self.running = True

        # Efectos visuales de impacto y dificultad dinámica
        self.screen_shake_time = 0
        self.flash_alpha = 0
        self.speedup_timer = 0

    def get_current_speed(self) -> float:
        """Calcula la velocidad horizontal dinámica según el puntaje (aumenta cada 5 puntos)."""
        level = self.score // 5
        speed = BASE_PIPE_SPEED + (level * SPEED_INCREMENT)
        return min(speed, MAX_PIPE_SPEED)

    def get_current_level(self) -> int:
        """Retorna el nivel de velocidad actual (inicia en 1 y sube cada 5 puntos)."""
        return (self.score // 5) + 1

    def _load_highscore(self) -> int:
        """Carga el récord guardado en el archivo local JSON."""
        try:
            if HIGHSCORE_FILE.exists():
                with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return int(data.get("highscore", 0))
        except Exception as e:
            print(f"[Aviso] No se pudo cargar récord ({e}), iniciando en 0.")
        return 0

    def _save_highscore(self):
        """Guarda el récord en el archivo local JSON."""
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"highscore": self.highscore}, f, indent=2)
        except Exception as e:
            print(f"[Aviso] No se pudo guardar récord: {e}")

    def reset_game(self):
        """Reinicia la partida para volver al estado inicial."""
        self.bird.reset()
        self.pipes.clear()
        self.score = 0
        self.is_new_record = False
        self.last_pipe_spawn_time = pygame.time.get_ticks()
        self.screen_shake_time = 0
        self.flash_alpha = 0
        self.speedup_timer = 0

    def trigger_game_over(self):
        """Activa la transición al estado de Game Over con efectos visuales y sonoros."""
        if self.state == STATE_GAMEOVER:
            return

        self.state = STATE_GAMEOVER
        self.bird.alive = False
        self.audio.play("hit")
        self.audio.play("fall")

        # Efecto de sacudida y flash blanco de pantalla
        self.screen_shake_time = 12
        self.flash_alpha = 200

        # Actualizar récord si corresponde
        if self.score > self.highscore:
            self.highscore = self.score
            self.is_new_record = True
            self._save_highscore()

    def handle_flap(self):
        """Acción de aleteo o inicio de juego activada por tecla o click."""
        if self.state == STATE_START:
            self.state = STATE_PLAYING
            self.bird.flap()
            self.audio.play("flap")
            self.last_pipe_spawn_time = pygame.time.get_ticks()

        elif self.state == STATE_PLAYING:
            self.bird.flap()
            self.audio.play("flap")

        elif self.state == STATE_GAMEOVER:
            # Solo permitir reinicio cuando el pájaro ya haya caído al suelo
            floor_y = SCREEN_HEIGHT - GROUND_HEIGHT - BIRD_RADIUS
            if self.bird.y >= floor_y - 2:
                self.reset_game()
                self.state = STATE_START

    def handle_events(self):
        """Procesa entradas de teclado, ratón y ventana."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    if self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    else:
                        self.handle_flap()

                elif event.key == pygame.K_p:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                else:
                    self.handle_flap()

    def update(self, dt: float):
        """Actualiza la física y entidades según el estado actual."""
        # Reducción paulatina de efectos de pantalla y aviso de velocidad
        if self.screen_shake_time > 0:
            self.screen_shake_time -= 1
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 25)
        if self.speedup_timer > 0:
            self.speedup_timer -= 1

        floor_y = SCREEN_HEIGHT - GROUND_HEIGHT - BIRD_RADIUS
        current_speed = self.get_current_speed()

        if self.state == STATE_START:
            self.world.update(moving=True, speed=BASE_PIPE_SPEED)
            self.bird.update_idle(dt)

        elif self.state == STATE_PLAYING:
            self.world.update(moving=True, speed=current_speed)
            self.bird.update()

            # Comprobar choque con el suelo
            if self.bird.y >= floor_y:
                self.bird.y = floor_y
                self.trigger_game_over()
                return

            # Generación de nuevas tuberías espaciadas uniformemente
            should_spawn = False
            if not self.pipes:
                should_spawn = True
            else:
                last_pipe = self.pipes[-1]
                if (SCREEN_WIDTH + 10) - last_pipe.x >= PIPE_DISTANCE:
                    should_spawn = True

            if should_spawn:
                self.pipes.append(PipePair(SCREEN_WIDTH + 10))

            # Actualización y comprobación de tuberías con la velocidad dinámica
            for pipe in list(self.pipes):
                pipe.update(speed=current_speed)

                # Comprobar si el pájaro superó la tubería para sumar punto
                if not pipe.passed and (pipe.x + pipe.width) < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                    self.audio.play("score")

                    # Cada 5 puntos aumenta la velocidad y muestra alerta en pantalla
                    if self.score % 5 == 0:
                        self.speedup_timer = 70

                # Comprobar colisión
                if pipe.collides_with(self.bird):
                    self.trigger_game_over()
                    break

                # Eliminar tuberías que salieron de pantalla
                if pipe.is_offscreen():
                    self.pipes.remove(pipe)

        elif self.state == STATE_GAMEOVER:
            # El pájaro cae hasta tocar el suelo si no lo ha tocado
            if self.bird.y < floor_y:
                self.bird.vel_y += 0.5
                self.bird.y += self.bird.vel_y
                if self.bird.y > floor_y:
                    self.bird.y = floor_y
                self.bird.angle = -90.0
                self.bird._update_transformed_sprite()

        elif self.state == STATE_PAUSED:
            pass  # El juego está congelado

    def draw(self, dt: float):
        """Renderiza todas las capas de juego y la interfaz."""
        # Crear superficie para permitir sacudida de pantalla (screen shake)
        render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # 1. Fondo de cielo, nubes y arbustos lejanos
        self.world.draw_background(render_surf)

        # 2. Tuberías
        for pipe in self.pipes:
            pipe.draw(render_surf)

        # 3. Suelo frontal
        self.world.draw_ground(render_surf)

        # 4. Pájaro
        self.bird.draw(render_surf)

        # 5. Interfaz de usuario (HUD según estado)
        if self.state == STATE_START:
            self.ui.draw_start_screen(render_surf, dt)
        elif self.state == STATE_PLAYING:
            self.ui.draw_playing_hud(
                render_surf, self.score, level=self.get_current_level(), speedup_timer=self.speedup_timer
            )
        elif self.state == STATE_GAMEOVER:
            self.ui.draw_game_over_screen(
                render_surf, self.score, self.highscore, self.is_new_record, dt
            )
        elif self.state == STATE_PAUSED:
            self.ui.draw_playing_hud(
                render_surf, self.score, level=self.get_current_level(), speedup_timer=self.speedup_timer
            )
            self.ui.draw_pause_screen(render_surf)

        # 6. Destello de impacto (blanco semitransparente)
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(self.flash_alpha)
            render_surf.blit(flash_surf, (0, 0))

        # 7. Aplicar sacudida de pantalla y transferir a la pantalla principal
        offset_x = 0
        offset_y = 0
        if self.screen_shake_time > 0:
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)

        self.screen.fill((0, 0, 0))
        self.screen.blit(render_surf, (offset_x, offset_y))
        pygame.display.flip()

    def run(self):
        """Bucle principal de ejecución del juego a 60 FPS."""
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0  # delta time en segundos
                self.handle_events()
                self.update(dt)
                self.draw(dt)
        finally:
            pygame.quit()

