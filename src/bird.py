"""
Clase Bird: maneja la física, animación y renderizado procedimental del pájaro.
"""
import math
import pygame
from src.config import (
    BIRD_RADIUS,
    BIRD_X,
    COLOR_BIRD,
    COLOR_BIRD_BEAK,
    COLOR_BIRD_BELLY,
    COLOR_BIRD_BORDER,
    COLOR_BIRD_SHADOW,
    COLOR_BIRD_WING,
    COLOR_BLACK,
    COLOR_WHITE,
    FLAP_STRENGTH,
    GRAVITY,
    MAX_FALL_SPEED,
    SCREEN_HEIGHT,
)


class Bird:
    def __init__(self, x: float = BIRD_X, y: float = SCREEN_HEIGHT / 2):
        self.x = float(x)
        self.y = float(y)
        self.start_y = float(y)
        self.vel_y = 0.0
        self.angle = 0.0
        self.alive = True

        # Animación de aleteo
        self.anim_tick = 0
        self.frame_index = 0
        self.frames = self._generate_bird_frames()

        # Imagen actual y rectángulo
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        self.mask = pygame.mask.from_surface(self.image)

        # Temporizador para efecto de balanceo en menú de inicio
        self.hover_timer = 0.0

    def _generate_bird_frames(self) -> list[pygame.Surface]:
        """Crea proceduralmente 3 frames de animación (ala arriba, centro, abajo)."""
        width, height = 36, 26
        frames = []

        wing_offsets = [-5, 0, 5]  # Posición vertical del ala en cada frame

        for wing_y_offset in wing_offsets:
            surf = pygame.Surface((width, height), pygame.SRCALPHA)

            # 1. Borde exterior del cuerpo (elipse oscura)
            body_rect = pygame.Rect(2, 2, 28, 22)
            pygame.draw.ellipse(surf, COLOR_BIRD_BORDER, body_rect)

            # 2. Relleno principal del cuerpo (amarillo)
            inner_rect = pygame.Rect(4, 4, 24, 18)
            pygame.draw.ellipse(surf, COLOR_BIRD, inner_rect)

            # 3. Sombra inferior del cuerpo
            shadow_rect = pygame.Rect(5, 12, 22, 9)
            pygame.draw.ellipse(surf, COLOR_BIRD_SHADOW, shadow_rect)
            pygame.draw.ellipse(surf, COLOR_BIRD, pygame.Rect(5, 4, 22, 14))

            # 4. Panza / vientre claro
            belly_rect = pygame.Rect(6, 12, 14, 8)
            pygame.draw.ellipse(surf, COLOR_BIRD_BELLY, belly_rect)

            # 5. Pico naranja con borde
            beak_points = [(26, 11), (35, 15), (26, 19)]
            pygame.draw.polygon(surf, COLOR_BIRD_BORDER, [(p[0] + 1, p[1]) for p in beak_points])
            pygame.draw.polygon(surf, COLOR_BIRD_BORDER, beak_points)
            pygame.draw.polygon(surf, COLOR_BIRD_BEAK, [(26, 12), (34, 15), (26, 18)])

            # 6. Ojo grande de Flappy Bird
            eye_center = (21, 9)
            pygame.draw.circle(surf, COLOR_BIRD_BORDER, eye_center, 6)
            pygame.draw.circle(surf, COLOR_WHITE, eye_center, 5)
            # Pupila negra mirando al frente
            pupil_center = (23, 9)
            pygame.draw.circle(surf, COLOR_BLACK, pupil_center, 2)
            # Brillo blanco
            pygame.draw.circle(surf, COLOR_WHITE, (24, 8), 1)

            # 7. Ala según frame
            wing_y = 11 + wing_y_offset
            wing_rect = pygame.Rect(5, wing_y, 14, 9)
            pygame.draw.ellipse(surf, COLOR_BIRD_BORDER, wing_rect)
            pygame.draw.ellipse(surf, COLOR_BIRD_WING, pygame.Rect(6, wing_y + 1, 12, 7))

            frames.append(surf)

        return frames

    def flap(self):
        """Impulso vertical al aletear."""
        if not self.alive:
            return
        self.vel_y = FLAP_STRENGTH
        # Reiniciar animación al aletear para respuesta inmediata
        self.frame_index = 2

    def update_idle(self, dt: float):
        """Movimiento suave de oscilación vertical cuando está en pantalla de inicio."""
        self.hover_timer += dt * 5.0
        self.y = self.start_y + math.sin(self.hover_timer) * 7.0
        self.angle = 0.0

        # Animar aleteo pausado
        self.anim_tick += 1
        if self.anim_tick % 8 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        self._update_transformed_sprite()

    def update(self):
        """Actualización de física en juego."""
        # Aplicar gravedad
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.y += self.vel_y

        # Evitar atravesar el techo
        if self.y < BIRD_RADIUS:
            self.y = BIRD_RADIUS
            self.vel_y = 0.0

        # Cálculo de rotación dinámica
        if self.vel_y < 0:
            # Subiendo: inclinación hacia arriba (hasta ~28 grados)
            target_angle = max(-25.0, self.vel_y * 4.0)
            self.angle = -target_angle
        else:
            # Cayendo: gira progresivamente hacia abajo hasta -90 grados
            self.angle -= 4.2
            if self.angle < -90.0:
                self.angle = -90.0

        # Animación de alas (sólo aletea si no está picando en picada vertical)
        if self.alive and self.angle > -60.0:
            self.anim_tick += 1
            if self.anim_tick % 5 == 0:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            # En caída libre las alas quedan fijas
            self.frame_index = 1

        self._update_transformed_sprite()

    def _update_transformed_sprite(self):
        """Aplica rotación al sprite actual y recalcula máscara para colisiones."""
        base_surf = self.frames[self.frame_index]
        self.image = pygame.transform.rotate(base_surf, self.angle)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface: pygame.Surface):
        """Dibuja el pájaro en la superficie."""
        surface.blit(self.image, self.rect)

    def reset(self, y: float = SCREEN_HEIGHT / 2):
        """Reinicia el estado del pájaro para una nueva partida."""
        self.y = float(y)
        self.start_y = float(y)
        self.vel_y = 0.0
        self.angle = 0.0
        self.alive = True
        self.hover_timer = 0.0
        self.frame_index = 0
        self._update_transformed_sprite()

