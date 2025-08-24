# AprendizajeAutonomo2
Este repositorio contiene el desarrollo del clásico Juego del Ahorcado, implementado como parte del proyecto de Aprendizaje Autónomo 2. 
El objetivo es aplicar conceptos de programación, manejo de estructuras de datos y lógica para crear una versión funcional e interactiva del juego.
🎮 ¿Qué es este juego?
Este es una implementación clásica del Juego del Ahorcado ejecutándose en la terminal/consola. El objetivo es adivinar una palabra oculta letra por letra antes de que se complete el dibujo del ahorcado.

🕹 ¿Cómo se juega?
El programa selecciona aleatoriamente una palabra de la lista predefinida
Debes ingresar letras una por una para adivinar la palabra
Cada letra correcta se revela en su posición correspondiente
Cada letra incorrecta avanza el dibujo del ahorcado
Tienes 6 intentos antes de que el ahorcado se complete

¡Ganas si adivinas la palabra antes de quedarte sin intentos!

🗂 Estructura del repositorio
text
ahorcado-python/
├── README.md                           # Este archivo con las instrucciones
├── Autonomo2ProgramaElAhorcado.py      # Código fuente principal del juego
└── palabras.txt                        # Archivo opcional con palabras (no usado en esta versión básica)

💻 Tecnología utilizada
Lenguaje de programación: Python exclusivamente
Versión de Python: 3.11.12

🛠 Funcionalidades principales
- Interfaz tipo *ventana TUI* con bordes Unicode (╔═╗╚═╝) y fallback ASCII (+-|).  
- Colores ANSI (verde para aciertos, rojo para errores, amarillo para palabra oculta).  
- Selección de *categoría* y *dificultad*.  
- Opción de adivinar *letras* o la *palabra completa*.  
- Registro de *palabras fallidas* y conteo en intentos.  
- *Modo automático* (AUTO_MODE=1) para demos o cuando no hay entrada de teclado.  
- Validación robusta: solo letras, evita repetidas, manejo de errores amigable.  
- *18 pruebas automáticas* que garantizan la lógica del juego.  

📂 Estructura del código
- HangmanGame (dataclass): reglas del juego y estado.  
- *Estructuras de datos:*
  - Tuplas → HANGMAN_PICS, BANNER, LETTER_ORDER.  
  - Listas → alfabeto pintado, columnas en la interfaz.  
  - Diccionarios → WORD_BANK, DIFFICULTY, FG (colores).  
- Funciones principales:  
  - jugar_consola(categoria=None, dificultad="media")  
  - seleccionar_opcion(titulo, opciones)  
  - intento(letra), intento_palabra(candidata)  
  - make_box(lines, title)  

🚀 Cómo iniciar el juego
Clona el repositorio (o descarga el archivo):

bash
git clone 
Navega al directorio del proyecto:

bash
cd AprendizajeAutonomo2
Ejecuta el juego:

bash
python Autonomo2ProgramaElAhorcado.py
🎯 Características del juego
✅ Interfaz limpia en consola
✅ Dibujo ASCII progresivo del ahorcado
✅ Sistema de intentos limitados (6)
✅ Validación de entradas del usuario
✅ Lista de letras incorrectas
✅ Palabras relacionadas con programación

📝 Notas adicionales
No se requieren instalaciones adicionales ya que usa módulos estándar de Python
Las palabras están incluidas directamente en el código (lista predefinida)
El juego se ejecuta completamente en la terminal

¡Diviértete jugando! 🎲
