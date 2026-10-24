"""
Manejador del entorno visual: fondo con gradiente, nubes con paralaje y suelo animado.
"""
import pygame
from src.config import (
    COLOR_BUSH,
    COLOR_BUSH_DARK,
    COLOR_CLOUD,
    COLOR_CLOUD_SHADOW,
    COLOR_GRASS,
    COLOR_GRASS_LIGHT,
    COLOR_GRASS_SHADOW,
    COLOR_GROUND,
    COLOR_GROUND_LINE,
    COLOR_SKY,
    COLOR_SKY_TOP,
    GROUND_HEIGHT,
    GROUND_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class World:
    """Gestiona el fondo dinámico, colinas lejanas y el suelo en movimiento continuo."""

    def __init__(self):
        self.ground_x = 0.0
        self.cloud_x = 0.0
        self.bush_x = 0.0

        # Superficies precargadas para máximo rendimiento
        self.sky_surface = self._create_sky_gradient()
        self.bush_surface = self._create_bush_strip()
        self.cloud_surface = self._create_cloud_strip()

    def _create_sky_gradient(self) -> pygame.Surface:
        """Genera un fondo con suave gradiente de cielo."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(COLOR_SKY_TOP[0] + (COLOR_SKY[0] - COLOR_SKY_TOP[0]) * ratio)
            g = int(COLOR_SKY_TOP[1] + (COLOR_SKY[1] - COLOR_SKY_TOP[1]) * ratio)
            b = int(COLOR_SKY_TOP[2] + (COLOR_SKY[2] - COLOR_SKY_TOP[2]) * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        return surf

    def _create_cloud_strip(self) -> pygame.Surface:
        """Crea una franja continua de nubes esponjosas para paralaje."""
        width = SCREEN_WIDTH * 2
        height = 120
        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Generar varias nubes a lo largo de la franja
        cloud_positions = [(60, 40), (220, 25), (380, 50), (540, 35), (700, 45)]
        for cx, cy in cloud_positions:
            # Sombra de nube
            pygame.draw.circle(surf, COLOR_CLOUD_SHADOW, (cx - 20, cy + 8), 24)
            pygame.draw.circle(surf, COLOR_CLOUD_SHADOW, (cx + 20, cy + 8), 24)
            pygame.draw.circle(surf, COLOR_CLOUD_SHADOW, (cx, cy + 2), 32)
            pygame.draw.rect(surf, COLOR_CLOUD_SHADOW, (cx - 30, cy + 6, 60, 26))

            # Nube blanca
            pygame.draw.circle(surf, COLOR_CLOUD, (cx - 20, cy + 6), 23)
            pygame.draw.circle(surf, COLOR_CLOUD, (cx + 20, cy + 6), 23)
            pygame.draw.circle(surf, COLOR_CLOUD, (cx, cy), 31)
            pygame.draw.rect(surf, COLOR_CLOUD, (cx - 30, cy + 4, 60, 24))

        return surf

    def _create_bush_strip(self) -> pygame.Surface:
        """Crea la silueta de colinas/arbustos del horizonte."""
        width = SCREEN_WIDTH * 2
        height = 50
        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Colinas redondeadas
        for x in range(0, width, 40):
            r = 30
            cy = height + 10
            pygame.draw.circle(surf, COLOR_BUSH_DARK, (x + 20, cy), r)
            pygame.draw.circle(surf, COLOR_BUSH, (x + 20, cy - 2), r - 3)

        return surf

    def update(self, moving: bool = True, speed: float = GROUND_SPEED):
        """Actualiza el desplazamiento del suelo y paralaje de nubes según la velocidad actual."""
        if not moving:
            return

        # Nubes (paralaje muy lento)
        self.cloud_x -= 0.35
        if self.cloud_x <= -SCREEN_WIDTH:
            self.cloud_x += SCREEN_WIDTH

        # Arbustos del horizonte (paralaje proporcional)
        self.bush_x -= speed * 0.35
        if self.bush_x <= -SCREEN_WIDTH:
            self.bush_x += SCREEN_WIDTH

        # Suelo (sincronizado con la velocidad de las tuberías)
        self.ground_x -= speed
        # El patrón del suelo se repite cada 24px
        if self.ground_x <= -24.0:
            self.ground_x += 24.0

    def draw_background(self, surface: pygame.Surface):
        """Dibuja el cielo, nubes y siluetas antes de las tuberías."""
        surface.blit(self.sky_surface, (0, 0))

        # Nubes
        surface.blit(self.cloud_surface, (int(self.cloud_x), 60))

        # Arbustos horizonte justo sobre el suelo
        bush_y = SCREEN_HEIGHT - GROUND_HEIGHT - 35
        surface.blit(self.bush_surface, (int(self.bush_x), bush_y))

    def draw_ground(self, surface: pygame.Surface):
        """Dibuja el suelo animado con césped y franjas diagonales retro."""
        ground_top = SCREEN_HEIGHT - GROUND_HEIGHT

        # 1. Relleno principal de tierra/arena
        ground_rect = pygame.Rect(0, ground_top, SCREEN_WIDTH, GROUND_HEIGHT)
        pygame.draw.rect(surface, COLOR_GROUND, ground_rect)

        # 2. Franja de césped superior (16px)
        grass_rect = pygame.Rect(0, ground_top, SCREEN_WIDTH, 14)
        pygame.draw.rect(surface, COLOR_GRASS, grass_rect)

        # Borde superior de césped (luz)
        pygame.draw.line(surface, COLOR_GRASS_LIGHT, (0, ground_top), (SCREEN_WIDTH, ground_top), 2)
        # Borde inferior de césped (sombra)
        pygame.draw.line(surface, COLOR_GRASS_SHADOW, (0, ground_top + 14), (SCREEN_WIDTH, ground_top + 14), 2)

        # Dientes de césped animados
        tooth_w = 12
        offset = int(self.ground_x) % tooth_w
        for tx in range(-tooth_w, SCREEN_WIDTH + tooth_w, tooth_w):
            x_pos = tx + offset
            pts = [(x_pos, ground_top + 14), (x_pos + tooth_w // 2, ground_top + 18), (x_pos + tooth_w, ground_top + 14)]
            pygame.draw.polygon(surface, COLOR_GRASS_SHADOW, pts)

        # 3. Franjas diagonales clásicas del suelo
        stripe_width = 14
        stripe_spacing = 28
        for sx in range(-stripe_spacing * 2, SCREEN_WIDTH + stripe_spacing * 2, stripe_spacing):
            x_pos = sx + int(self.ground_x)
            pts = [
                (x_pos, ground_top + 20),
                (x_pos + stripe_width, ground_top + 20),
                (x_pos + stripe_width - 15, SCREEN_HEIGHT),
                (x_pos - 15, SCREEN_HEIGHT),
            ]
            pygame.draw.polygon(surface, COLOR_GROUND_LINE, pts)

        # Línea de separación inferior
        pygame.draw.line(surface, COLOR_GROUND_LINE, (0, ground_top + 20), (SCREEN_WIDTH, ground_top + 20), 2)

