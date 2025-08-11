
"""
Juego del Ahorcado - Versión Básica en Consola
Este es un juego clásico donde debes adivinar una palabra letra por letra
antes de que se complete el dibujo del ahorcado.
"""

import random
import os

def limpiar_consola():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_ahorcado(intentos):
    """Muestra el dibujo del ahorcado según los intentos fallidos"""
    etapas = [
        """
           +---+
           |   |
               |
               |
               |
               |
        =========
        """,
        """
           +---+
           |   |
           O   |
               |
               |
               |
        =========
        """,
        """
           +---+
           |   |
           O   |
           |   |
               |
               |
        =========
        """,
        """
           +---+
           |   |
           O   |
          /|   |
               |
               |
        =========
        """,
        """
           +---+
           |   |
           O   |
          /|\  |
               |
               |
        =========
        """,
        """
           +---+
           |   |
           O   |
          /|\  |
          /    |
               |
        =========
        """,
        """
           +---+
           |   |
           O   |
          /|\  |
          / \  |
               |
        =========
        """
    ]
    print(etapas[intentos])

def seleccionar_palabra():
    """Selecciona una palabra aleatoria de la lista"""
    palabras = ["python", "programacion", "computadora", "teclado", 
                "mouse", "monitor", "algoritmo", "variable"]
    return random.choice(palabras)

def jugar_ahorcado():
    """Función principal que maneja la lógica del juego"""
    palabra = seleccionar_palabra()
    palabra_oculta = ["_"] * len(palabra)
    intentos = 0
    max_intentos = 6
    letras_adivinadas = []
    letras_incorrectas = []
    
    print("¡Bienvenido al juego del Ahorcado!")
    print("Adivina la palabra letra por letra.")
    
    while True:
        limpiar_consola()
        mostrar_ahorcado(intentos)
        print("\nPalabra: " + " ".join(palabra_oculta))
        print("\nLetras incorrectas: " + " ".join(letras_incorrectas))
        
        # Verificar si ganó
        if "_" not in palabra_oculta:
            print("\n¡Felicidades! ¡Ganaste!")
            print(f"La palabra era: {palabra}")
            break
            
        # Verificar si perdió
        if intentos >= max_intentos:
            print("\n¡Perdiste! Se completó el ahorcado.")
            print(f"La palabra era: {palabra}")
            break
            
        # Pedir letra al jugador
        letra = input("\nIngresa una letra: ").lower()
        
        # Validar entrada
        if len(letra) != 1 or not letra.isalpha():
            print("Por favor ingresa una sola letra válida.")
            time.sleep(1)
            continue
            
        if letra in letras_adivinadas or letra in letras_incorrectas:
            print("Ya has intentado con esa letra. Prueba con otra.")
            time.sleep(1)
            continue
            
        # Verificar si la letra está en la palabra
        if letra in palabra:
            letras_adivinadas.append(letra)
            # Revelar la letra en la palabra oculta
            for i in range(len(palabra)):
                if palabra[i] == letra:
                    palabra_oculta[i] = letra
        else:
            letras_incorrectas.append(letra)
            intentos += 1
            print(f"La letra '{letra}' no está en la palabra.")
            time.sleep(1)

if __name__ == "__main__":
    import time
    jugar_ahorcado()