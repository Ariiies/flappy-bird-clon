"""
Clase PipePair: genera, actualiza y renderiza las tuberías superior e inferior.
"""
import random
import pygame
from src.config import (
    COLOR_PIPE,
    COLOR_PIPE_BORDER,
    COLOR_PIPE_DARK,
    COLOR_PIPE_LIGHT,
    GROUND_HEIGHT,
    PIPE_CAP_HEIGHT,
    PIPE_CAP_OVERHANG,
    PIPE_GAP,
    PIPE_MIN_HEIGHT,
    PIPE_SPEED,
    PIPE_WIDTH,
    SCREEN_HEIGHT,
)


class PipePair:
    """Representa una pareja de tuberías (superior e inferior) con espacio de paso."""

    def __init__(self, x: float):
        self.x = float(x)
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        self.passed = False

        # Altura del suelo disponible
        playable_height = SCREEN_HEIGHT - GROUND_HEIGHT

        # Determinar posición aleatoria de la apertura (gap)
        min_top = PIPE_MIN_HEIGHT
        max_top = playable_height - self.gap - PIPE_MIN_HEIGHT
        self.gap_top = random.randint(min_top, max_top)
        self.gap_bottom = self.gap_top + self.gap

        # Superficies cacheadas
        self.top_surface = self._build_top_pipe()
        self.bottom_surface = self._build_bottom_pipe()

        self.top_rect = self.top_surface.get_rect(topleft=(int(self.x), 0))
        self.bottom_rect = self.bottom_surface.get_rect(topleft=(int(self.x), self.gap_bottom))

        self.top_mask = pygame.mask.from_surface(self.top_surface)
        self.bottom_mask = pygame.mask.from_surface(self.bottom_surface)

    def _draw_pipe_body(self, surf: pygame.Surface, rect: pygame.Rect):
        """Dibuja el cuerpo de una tubería con sombreado 3D arcade."""
        # Borde exterior oscuro
        pygame.draw.rect(surf, COLOR_PIPE_BORDER, rect)

        # Relleno principal verde
        inner_rect = rect.inflate(-4, -4)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(surf, COLOR_PIPE, inner_rect)

            # Brillo cilíndrico izquierdo
            highlight_rect = pygame.Rect(inner_rect.x + 3, inner_rect.y, 6, inner_rect.height)
            pygame.draw.rect(surf, COLOR_PIPE_LIGHT, highlight_rect)

            # Sombra cilíndrica derecha
            shadow_rect = pygame.Rect(inner_rect.right - 9, inner_rect.y, 7, inner_rect.height)
            pygame.draw.rect(surf, COLOR_PIPE_DARK, shadow_rect)

    def _draw_pipe_cap(self, surf: pygame.Surface, rect: pygame.Rect):
        """Dibuja la corona/tapa saliente de la tubería con bisel y relieve."""
        pygame.draw.rect(surf, COLOR_PIPE_BORDER, rect)
        inner = rect.inflate(-4, -4)
        if inner.width > 0 and inner.height > 0:
            pygame.draw.rect(surf, COLOR_PIPE, inner)
            # Brillo superior/izquierdo
            pygame.draw.rect(surf, COLOR_PIPE_LIGHT, pygame.Rect(inner.x + 3, inner.y, 6, inner.height))
            # Sombra derecha
            pygame.draw.rect(surf, COLOR_PIPE_DARK, pygame.Rect(inner.right - 9, inner.y, 7, inner.height))

    def _build_top_pipe(self) -> pygame.Surface:
        """Genera la superficie de la tubería superior con su corona en la base."""
        total_w = self.width + (PIPE_CAP_OVERHANG * 2)
        total_h = self.gap_top
        surf = pygame.Surface((total_w, max(1, total_h)), pygame.SRCALPHA)

        # Cuerpo
        body_h = max(0, total_h - PIPE_CAP_HEIGHT)
        if body_h > 0:
            body_rect = pygame.Rect(PIPE_CAP_OVERHANG, 0, self.width, body_h + 2)
            self._draw_pipe_body(surf, body_rect)

        # Corona al final inferior
        cap_y = max(0, total_h - PIPE_CAP_HEIGHT)
        cap_rect = pygame.Rect(0, cap_y, total_w, PIPE_CAP_HEIGHT)
        self._draw_pipe_cap(surf, cap_rect)

        return surf

    def _build_bottom_pipe(self) -> pygame.Surface:
        """Genera la superficie de la tubería inferior con su corona en la parte superior."""
        total_w = self.width + (PIPE_CAP_OVERHANG * 2)
        playable_height = SCREEN_HEIGHT - GROUND_HEIGHT
        total_h = playable_height - self.gap_bottom
        surf = pygame.Surface((total_w, max(1, total_h)), pygame.SRCALPHA)

        # Corona arriba
        cap_rect = pygame.Rect(0, 0, total_w, PIPE_CAP_HEIGHT)
        self._draw_pipe_cap(surf, cap_rect)

        # Cuerpo
        body_y = PIPE_CAP_HEIGHT - 2
        body_h = max(0, total_h - body_y)
        if body_h > 0:
            body_rect = pygame.Rect(PIPE_CAP_OVERHANG, body_y, self.width, body_h)
            self._draw_pipe_body(surf, body_rect)

        return surf

    def update(self, speed: float = PIPE_SPEED):
        """Mueve la tubería hacia la izquierda a la velocidad indicada."""
        self.x -= speed
        # Actualizar posiciones de rectángulos de colisión
        # Ajustamos x restando el overhang para alineación precisa
        draw_x = int(self.x - PIPE_CAP_OVERHANG)
        self.top_rect.topleft = (draw_x, 0)
        self.bottom_rect.topleft = (draw_x, self.gap_bottom)

    def draw(self, surface: pygame.Surface):
        """Dibuja ambas tuberías."""
        surface.blit(self.top_surface, self.top_rect)
        surface.blit(self.bottom_surface, self.bottom_rect)

    def collides_with(self, bird) -> bool:
        """Comprueba colisión precisa basada en máscaras de píxeles."""
        # Comprobación de bounding box rápida primero
        if self.top_rect.colliderect(bird.rect):
            offset = (bird.rect.x - self.top_rect.x, bird.rect.y - self.top_rect.y)
            if self.top_mask.overlap(bird.mask, offset):
                return True

        if self.bottom_rect.colliderect(bird.rect):
            offset = (bird.rect.x - self.bottom_rect.x, bird.rect.y - self.bottom_rect.y)
            if self.bottom_mask.overlap(bird.mask, offset):
                return True

        return False

    def is_offscreen(self) -> bool:
        """Indica si la tubería salió completamente por la izquierda."""
        return self.x + self.width + (PIPE_CAP_OVERHANG * 2) < 0

