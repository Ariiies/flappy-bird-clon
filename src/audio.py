"""
Manejador de efectos de sonido procedurales para Flappy Bird.
Sintetiza audio chiptune retro en memoria sin necesidad de archivos externos.
"""
import io
import math
import struct
import pygame


class AudioManager:
    """Gestiona y sintetiza efectos de sonido 8-bit usando la librería estándar."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.enabled = False
        self.sounds = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1, buffer=512)
            self.enabled = True
            self._synthesize_all()
        except Exception as err:
            # Si el sistema no tiene dispositivo de audio activo, el juego continuará sin sonido
            print(f"[Audio] Dispositivo de audio no disponible ({err}). Modo silencioso activado.")
            self.enabled = False

    def _create_sound_from_samples(self, samples: list[float]) -> pygame.mixer.Sound | None:
        """Convierte una lista de muestras flotantes (-1.0 a 1.0) en un Sound de pygame."""
        try:
            buf = bytearray()
            for s in samples:
                # Clamp entre -1.0 y 1.0
                clamped = max(-1.0, min(1.0, s))
                int_val = int(clamped * 32767)
                buf.extend(struct.pack("<h", int_val))
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _synthesize_all(self):
        """Genera todos los efectos sonoros en memoria."""
        # 1. Salto (Flap): Chirp ascendente rápido
        flap_samples = []
        duration = 0.09
        n = int(self.sample_rate * duration)
        for i in range(n):
            t = i / self.sample_rate
            # Frecuencia sube de 350 Hz a 750 Hz
            freq = 350 + (400 * (i / n))
            phase = 2 * math.pi * freq * t
            # Onda cuadrada suave + decaimiento
            envelope = 1.0 - (i / n) ** 0.8
            val = (1.0 if math.sin(phase) > 0 else -1.0) * 0.25 * envelope
            flap_samples.append(val)
        self.sounds["flap"] = self._create_sound_from_samples(flap_samples)

        # 2. Punto (Score): Dos notas brillantes estilo moneda arcade (C6 -> G6)
        score_samples = []
        duration = 0.16
        n = int(self.sample_rate * duration)
        half_n = n // 2
        for i in range(n):
            t = i / self.sample_rate
            freq = 1046.50 if i < half_n else 1567.98  # C6 luego G6
            local_i = i if i < half_n else i - half_n
            local_n = half_n
            envelope = 1.0 - (local_i / local_n) ** 1.2
            phase = 2 * math.pi * freq * t
            # Mezcla de seno y triangular
            sine = math.sin(phase)
            tri = (2 / math.pi) * math.asin(max(-1.0, min(1.0, math.sin(phase))))
            val = ((sine * 0.6) + (tri * 0.4)) * 0.28 * envelope
            score_samples.append(val)
        self.sounds["score"] = self._create_sound_from_samples(score_samples)

        # 3. Golpe (Hit): Ruido percusivo descendente con saturación
        hit_samples = []
        duration = 0.15
        n = int(self.sample_rate * duration)
        for i in range(n):
            t = i / self.sample_rate
            freq = max(60, 280 - (220 * (i / n)))
            envelope = (1.0 - (i / n)) ** 2
            # Generador pseudo-ruido controlado
            noise = ((math.sin(i * 1234.567) * 43758.5453) % 2.0) - 1.0
            tone = math.sin(2 * math.pi * freq * t)
            val = (tone * 0.5 + noise * 0.5) * 0.4 * envelope
            hit_samples.append(val)
        self.sounds["hit"] = self._create_sound_from_samples(hit_samples)

        # 4. Caída / Game Over (Fall)
        fall_samples = []
        duration = 0.25
        n = int(self.sample_rate * duration)
        for i in range(n):
            t = i / self.sample_rate
            freq = max(80, 500 - (380 * (i / n)))
            envelope = 1.0 - (i / n)
            val = math.sin(2 * math.pi * freq * t) * 0.25 * envelope
            fall_samples.append(val)
        self.sounds["fall"] = self._create_sound_from_samples(fall_samples)

    def play(self, name: str):
        """Reproduce un sonido si el sistema de audio está activo."""
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

