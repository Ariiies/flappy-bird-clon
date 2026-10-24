"""
Punto de entrada principal para ejecutar el clon de Flappy Bird.
"""
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en el sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.game import FlappyBirdGame


def main():
    """Inicializa y arranca el juego."""
    print("Iniciando Flappy Bird Clon (MVP Python 3.14 + Pygame)...")
    game = FlappyBirdGame()
    game.run()
    print("Juego finalizado. ¡Gracias por jugar!")


if __name__ == "__main__":
    main()

