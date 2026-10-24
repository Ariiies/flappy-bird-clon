# Flappy Bird Clone - MVP en Pygame y Python 3.14

Un clon minimalista, limpio, modular y altamente efectivo del clásico **Flappy Bird**, construido con **Python 3.14** y **Pygame-CE** (`pygame-ce 2.5.8+`).

Diseñado con **cero dependencias de archivos de audio o imágenes externas**: todos los sprites (el pájaro con animación de aleteo y rotación dinámica, las tuberías con sombreado 3D arcade, las nubes con paralaje y el suelo en movimiento) y los efectos de sonido retro (aleteo, moneda/punto, colisión y caída) se generan **procedimentalmente en tiempo real** en memoria.

---

## 🎮 Controles del Juego

| Acción | Control |
|---|---|
| **Aletear / Comenzar / Reintentar** | `ESPACIO`, `FLECHA ARRIBA` o `CLICK IZQUIERDO` |
| **Pausar / Reanudar** | Tecla `P` |
| **Salir del juego** | Tecla `ESC` o `Q` |

---

## 🚀 Requisitos y Entorno Conda

El entorno virtual de Conda se llama **`pyproyect`** con **Python 3.14**:

### 1. Activar el entorno Conda
```bash
conda activate pyproyect
```

### 2. Ejecutar el juego
```bash
python main.py
```

*(O directamente sin activar el shell):*
```bash
conda run -n pyproyect python main.py
```

### 3. Ejecutar las pruebas automáticas
```bash
conda run -n pyproyect python tests/test_game.py
```

---

## 📂 Estructura del Proyecto

```text
pyproyect/
├── src/
│   ├── __init__.py         # Inicializador del paquete
│   ├── config.py           # Constantes globales: físicas, dimensiones, paleta de colores
│   ├── audio.py            # Sintetizador procedural de audio chiptune 8-bit (sin archivos wav/mp3)
│   ├── bird.py             # Clase Bird con física de gravedad, salto, rotación y animación de alas
│   ├── pipe.py             # Clase PipePair con aperturas variables, render 3D y máscaras de colisión
│   ├── world.py            # Gradiente de cielo, nubes con paralaje y suelo animado retro
│   ├── ui.py               # Renderizado de HUD, texto con contorno, cartel de récord y medallas
│   └── game.py             # Bucle principal, máquina de estados (START, PLAYING, GAMEOVER, PAUSED)
├── tests/
│   └── test_game.py        # Pruebas unitarias y simulación headless de juego a 60 FPS
├── main.py                 # Punto de entrada ejecutable
├── requirements.txt        # Dependencias de pip (pygame-ce)
├── environment.yml         # Especificación del entorno conda
└── README.md               # Documentación completa
```

---

## ✨ Características Principales

- **Dificultad Dinámica Progresiva**:
  - Velocidad inicial más relajada y accesible (`1.9 px/frame`), permitiendo maniobrar y aprender el ritmo fácilmente.
  - Cada **5 puntos anotados**, el juego aumenta la velocidad (`+0.25 px/frame`), subiendo de nivel (`Nv. 1`, `Nv. 2`, etc.) con un aviso visual en pantalla.
  - Espaciado uniforme de tuberías basado en distancia (`215 px`), garantizando un reto justo y bien proporcionado a cualquier velocidad.
- **Física Fiel**: Curva de aceleración gravitatoria, salto suave y rotación suave del pájaro (inclinación hacia arriba al saltar y picada vertical en caída libre).
- **Colisiones Precisas**: Detección basada en `pygame.mask` (máscaras de píxeles) para evitar frustración con cajas cuadradas invisibles.
- **Gráficos Procedurales**: Creados con superficies vectoriales/pixeladas de Pygame con sombreado estilo arcade.
- **Audio Sintetizado**: Efectos de sonido generados matemáticamente mediante ondas (chirp de aleteo, campana de punto, ruido percusivo de golpe).
- **Sistema de Récords**: Persistencia local del puntaje más alto en `highscore.json`.
- **Premios y Medallas**: Medallas de Bronce (10+), Plata (20+), Oro (30+) y Platino (40+) en el panel de Game Over.
- **Efectos Jugosos (Juice)**: Screen shake (sacudida de pantalla) y flash blanco al chocar.

