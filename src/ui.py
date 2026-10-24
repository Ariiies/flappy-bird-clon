"""
Manejador de la interfaz de usuario (HUD, pantallas de título, game over y puntajes).
"""
import math
import pygame
from src.config import (
    COLOR_BLACK,
    COLOR_BRONZE,
    COLOR_GOLD,
    COLOR_PLATINUM,
    COLOR_SILVER,
    COLOR_TEXT_OUTLINE,
    COLOR_WHITE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class UIManager:
    """Renderiza textos con contorno retro, panel de puntuaciones y medallas."""

    def __init__(self):
        pygame.font.init()
        # Usar fuentes predeterminadas integradas de Pygame (garantizan consistencia en cualquier OS)
        self.font_big = pygame.font.Font(None, 52)
        self.font_med = pygame.font.Font(None, 34)
        self.font_small = pygame.font.Font(None, 22)
        self.pulse_timer = 0.0

    def render_text_with_outline(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        outline_color: tuple[int, int, int] = COLOR_TEXT_OUTLINE,
        thickness: int = 2,
    ) -> pygame.Surface:
        """Crea una superficie con el texto y un contorno grueso estilo arcade."""
        base_surf = font.render(text, True, color)
        outline_surf = font.render(text, True, outline_color)

        w = base_surf.get_width() + thickness * 2
        h = base_surf.get_height() + thickness * 2
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Dibujar el contorno en 8 direcciones
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx != 0 or dy != 0:
                    surf.blit(outline_surf, (dx + thickness, dy + thickness))

        # Dibujar el texto principal encima
        surf.blit(base_surf, (thickness, thickness))
        return surf

    def draw_playing_hud(
        self, surface: pygame.Surface, score: int, level: int = 1, speedup_timer: int = 0
    ):
        """Muestra el puntaje actual centrado y aviso de aceleración cada 5 puntos."""
        score_surf = self.render_text_with_outline(str(score), self.font_big, COLOR_WHITE, thickness=3)
        rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(score_surf, rect)

        # Indicador sutil de nivel actual en esquina superior derecha
        if level > 1:
            lvl_surf = self.render_text_with_outline(f"Nv. {level}", self.font_small, COLOR_GOLD, thickness=1)
            lvl_rect = lvl_surf.get_rect(topright=(SCREEN_WIDTH - 15, 15))
            surface.blit(lvl_surf, lvl_rect)

        # Banner temporal de aceleración cada 5 puntos
        if speedup_timer > 0:
            msg = f"¡MÁS RÁPIDO! (Nv. {level})"
            speed_surf = self.render_text_with_outline(
                msg, self.font_small, (255, 230, 80), outline_color=(50, 40, 10), thickness=2
            )
            speed_rect = speed_surf.get_rect(center=(SCREEN_WIDTH // 2, 105))
            surface.blit(speed_surf, speed_rect)

    def draw_start_screen(self, surface: pygame.Surface, dt: float):
        """Pantalla de inicio con logo estilizado y llamada a la acción."""
        self.pulse_timer += dt * 4.0

        # Título principal
        title_surf = self.render_text_with_outline(
            "FLAPPY BIRD", self.font_big, COLOR_GOLD, outline_color=(60, 40, 10), thickness=3
        )
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(title_surf, title_rect)

        # Subtítulo "MVP Python 3.14"
        sub_surf = self.render_text_with_outline("PYTHON 3.14 + PYGAME", self.font_small, COLOR_WHITE, thickness=2)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 160))
        surface.blit(sub_surf, sub_rect)

        # Instrucción parpadeante
        alpha_factor = (math.sin(self.pulse_timer) + 1.0) / 2.0  # de 0.0 a 1.0
        if alpha_factor > 0.2:
            prompt_surf = self.render_text_with_outline(
                "PULSA [ESPACIO] O CLICK", self.font_med, COLOR_WHITE, thickness=2
            )
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 380))
            surface.blit(prompt_surf, prompt_rect)

            hint_surf = self.render_text_with_outline(
                "PARA ALETEAR Y COMENZAR", self.font_small, (240, 240, 240), thickness=2
            )
            hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, 415))
            surface.blit(hint_surf, hint_rect)

    def draw_game_over_screen(
        self, surface: pygame.Surface, score: int, highscore: int, is_new_record: bool, dt: float
    ):
        """Cartel de Game Over con tablero de estadísticas y medalla."""
        self.pulse_timer += dt * 4.0

        # 1. Cartel de "GAME OVER"
        go_surf = self.render_text_with_outline(
            "GAME OVER", self.font_big, (235, 75, 60), outline_color=(70, 20, 20), thickness=3
        )
        go_rect = go_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(go_surf, go_rect)

        # 2. Tablero de puntuación estilo caja arcade
        card_w, card_h = 280, 170
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = 175
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # Sombra de la caja
        pygame.draw.rect(surface, (40, 40, 40), card_rect.move(4, 4), border_radius=10)
        # Borde exterior oscuro
        pygame.draw.rect(surface, (80, 60, 40), card_rect, border_radius=10)
        # Relleno color pergamino/oro viejo
        inner_rect = card_rect.inflate(-6, -6)
        pygame.draw.rect(surface, (232, 222, 175), inner_rect, border_radius=8)
        # Borde interior fino
        pygame.draw.rect(surface, (210, 195, 140), inner_rect.inflate(-6, -6), width=2, border_radius=6)

        # Sección Medalla
        medal_title = self.render_text_with_outline("MEDALLA", self.font_small, (140, 110, 50), thickness=1)
        surface.blit(medal_title, (card_x + 22, card_y + 20))

        # Dibuja la medalla si califica
        medal_color = None
        medal_name = "---"
        if score >= 40:
            medal_color = COLOR_PLATINUM
            medal_name = "PLATINO"
        elif score >= 30:
            medal_color = COLOR_GOLD
            medal_name = "ORO"
        elif score >= 20:
            medal_color = COLOR_SILVER
            medal_name = "PLATA"
        elif score >= 10:
            medal_color = COLOR_BRONZE
            medal_name = "BRONCE"

        medal_center = (card_x + 58, card_y + 85)
        if medal_color:
            pygame.draw.circle(surface, (60, 50, 30), medal_center, 24)
            pygame.draw.circle(surface, medal_color, medal_center, 22)
            pygame.draw.circle(surface, (255, 255, 255), (medal_center[0] - 6, medal_center[1] - 6), 6)
            # Nombre de la medalla
            m_text = self.render_text_with_outline(medal_name, self.font_small, (80, 60, 30), thickness=1)
            surface.blit(m_text, m_text.get_rect(center=(medal_center[0], medal_center[1] + 34)))
        else:
            pygame.draw.circle(surface, (190, 180, 145), medal_center, 22)
            dash = self.render_text_with_outline("-", self.font_med, (130, 120, 95), thickness=1)
            surface.blit(dash, dash.get_rect(center=medal_center))

        # Sección Puntuación
        score_lbl = self.render_text_with_outline("PUNTOS", self.font_small, (140, 110, 50), thickness=1)
        surface.blit(score_lbl, (card_x + 150, card_y + 18))

        score_val = self.render_text_with_outline(str(score), self.font_med, COLOR_WHITE, thickness=2)
        score_val_rect = score_val.get_rect(topright=(card_x + card_w - 24, card_y + 36))
        surface.blit(score_val, score_val_rect)

        # Sección Mejor Puntuación
        best_lbl = self.render_text_with_outline("MEJOR", self.font_small, (140, 110, 50), thickness=1)
        surface.blit(best_lbl, (card_x + 150, card_y + 80))

        best_val = self.render_text_with_outline(str(highscore), self.font_med, COLOR_WHITE, thickness=2)
        best_val_rect = best_val.get_rect(topright=(card_x + card_w - 24, card_y + 98))
        surface.blit(best_val, best_val_rect)

        # Insignia de NUEVO RÉCORD
        if is_new_record:
            rec_surf = self.render_text_with_outline(
                "¡NUEVO!", self.font_small, (240, 50, 50), outline_color=(255, 255, 255), thickness=1
            )
            surface.blit(rec_surf, (card_x + 115, card_y + 82))

        # 3. Prompt de reinicio
        alpha_factor = (math.sin(self.pulse_timer) + 1.0) / 2.0
        if alpha_factor > 0.25:
            restart_surf = self.render_text_with_outline(
                "PULSA [ESPACIO] PARA REINTENTAR", self.font_small, COLOR_WHITE, thickness=2
            )
            r_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, 385))
            surface.blit(restart_surf, r_rect)

    def draw_pause_screen(self, surface: pygame.Surface):
        """Overlay semitransparente cuando el juego está en pausa."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        surface.blit(overlay, (0, 0))

        p_surf = self.render_text_with_outline("JUEGO EN PAUSA", self.font_big, COLOR_WHITE, thickness=3)
        p_rect = p_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        surface.blit(p_surf, p_rect)

        c_surf = self.render_text_with_outline(
            "PULSA [P] O [ESPACIO] PARA CONTINUAR", self.font_small, (220, 220, 220), thickness=2
        )
        c_rect = c_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        surface.blit(c_surf, c_rect)
