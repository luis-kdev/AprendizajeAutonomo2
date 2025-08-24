"""
Ahorcado – Modo Consola 

"""

from __future__ import annotations
import os
import re
import random
import string
import time
from itertools import zip_longest
from typing import Dict, List, Set, Tuple, Callable, Any
from functools import reduce

# Asegurar que 'print' es el builtin (evita TypeError por sombreado)
import builtins as _builtins
print = _builtins.print  # garantiza soporte de 'end'


CSI = "\033["
RESET = f"{CSI}0m"
BOLD = f"{CSI}1m"
DIM = f"{CSI}2m"
FG = {
    "default": f"{CSI}39m",
    "red": f"{CSI}31m",
    "green": f"{CSI}32m",
    "yellow": f"{CSI}33m",
    "blue": f"{CSI}34m",
    "magenta": f"{CSI}35m",
    "cyan": f"{CSI}36m",
    "white": f"{CSI}97m",
    "gray": f"{CSI}90m",
}

USE_COLOR = os.environ.get("NO_COLOR", "0") != "1"


def _enable_vt_win() -> bool:
    """Intenta habilitar ANSI en Windows 10+ (VT). Degrada si no se puede."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        HANDLE_STDOUT = -11
        mode = ctypes.c_uint()
        h = kernel32.GetStdHandle(HANDLE_STDOUT)
        if h in (0, -1):
            return False
        if not kernel32.GetConsoleMode(h, ctypes.byref(mode)):
            return False
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        if not kernel32.SetConsoleMode(h, new_mode):
            return False
        return True
    except Exception:
        return False


if USE_COLOR and not _enable_vt_win():
    USE_COLOR = False


def c(text: str, *styles: str) -> str:
    if not USE_COLOR:
        return text
    return "".join(styles) + text + RESET



# Entrada segura / modo automático (no impone autoplay por defecto)

AUTO_MODE = os.environ.get("AUTO_MODE") == "1"


def safe_input(prompt: str, default: str = "") -> str:
    """`input()` tolerante: intenta leer; si falla o AUTO_MODE está activo, devuelve `default`."""
    if AUTO_MODE:
        return default
    try:
        return input(prompt)
    except (OSError, EOFError):
        return default



# Recursos del juego (banner y frames)

BANNER: tuple[str, ...] = (
    "  _   _                                          ",
    " | | | | __ _ _ __   __ _ _ __ ___   __ _ _ __   ",
    " | |_| |/ _` | '_ \\ / _` | '_ ` _ \\ / _` | '_ \\  ",
    " |  _  | (_| | | | | (_| | | | | | | (_| | | | | ",
    " |_| |_|\\__,_|_| |_|\\__, |_| |_| |_|\\__,_|_| |_| ",
    "                    |___/                        ",
)

HANGMAN_PICS: Tuple[str, ...] = (
    r"""
       +---+
       |   |
           |
           |
           |
           |
    =========
    """,
    r"""
       +---+
       |   |
       O   |
           |
           |
           |
    =========
    """,
    r"""
       +---+
       |   |
       O   |
       |   |
           |
           |
    =========
    """,
    r"""
       +---+
       |   |
       O   |
      /|   |
           |
           |
    =========
    """,
    r"""
       +---+
       |   |
       O   |
      /|\  |
           |
           |
    =========
    """,
    r"""
       +---+
       |   |
       O   |
      /|\  |
      /    |
           |
    =========
    """,
    r"""
       +---+
       |   |
       O   |
      /|\  |
      / \  |
           |
    =========
    """,
)

# Banco de palabras por categoría (diccionario con tuplas)
WORD_BANK: Dict[str, Tuple[str, ...]] = {
    "Tecnologia": (
        "python", "programacion", "computadora", "teclado",
        "mouse", "monitor", "algoritmo", "variable"
    ),
    "Ciencia": (
        "atomo", "molecula", "energia", "celula", "gravedad", "genetica"
    ),
    "Deportes": (
        "futbol", "basquet", "tenis", "natacion", "ciclismo"
    ),
}

# Dificultades
DIFFICULTY: Dict[str, Dict[str, int]] = {
    "facil":   {"max_intentos": 8},
    "media":   {"max_intentos": 6},
    "dificil": {"max_intentos": 5},
}



# Utilitarios de consola y helpers de "ventana"


def limpiar_consola() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner() -> None:
    print()
    for line in BANNER:
        print(c(line, FG["cyan"], BOLD))
    print()


def elegir_palabra(categoria: str | None = None) -> Tuple[str, str]:
    """Devuelve (categoria_elegida, palabra_aleatoria) desde WORD_BANK.
    Si `categoria` no es válida o es None, se elige una al azar.
    """
    if categoria and categoria in WORD_BANK:
        cat = categoria
    else:
        cat = random.choice(list(WORD_BANK.keys()))
    return cat, random.choice(WORD_BANK[cat])


# ---- helpers para "ventana" (box con bordes) ----
NO_UNICODE = os.environ.get("NO_UNICODE", "0") == "1"

# Definición de Box como tupla nombrada
Box = Tuple[str, str, str, str, str, str, str, str]

BOX_UNI: Box = ("╔", "╗", "╚", "╝", "═", "║", "╠", "╣")
BOX_ASC: Box = ("+", "+", "+", "+", "-", "|", "+", "+")
BOX: Box = BOX_ASC if NO_UNICODE else BOX_UNI

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


def vlen(s: str) -> int:
    return len(strip_ansi(s))


def pad_visible(s: str, width: int) -> str:
    pad = width - vlen(s)
    return s + (" " * max(0, pad))


def make_box(lines: List[str], title: str | None = None) -> str:
    tl, tr, bl, br, h, v, t_sep_l, t_sep_r = BOX
    width = max([vlen(ln) for ln in lines] + ([vlen(title)] if title else [0]))
    top = tl + (h * (width + 2)) + tr
    bot = bl + (h * (width + 2)) + br
    out: List[str] = [top]
    if title:
        t = pad_visible(f" {title} ", width + 2)
        out.append(f"{v}{t}{v}")
        out.append(t_sep_l + (h * (width + 2)) + t_sep_r)
    for ln in lines:
        out.append(f"{v} {pad_visible(ln, width)} {v}")
    out.append(bot)
    return "\n".join(out)


def compose_columns(left: List[str], right: List[str], gap: int = 3) -> List[str]:
    lw = max((vlen(ln) for ln in left), default=0)
    rw = max((vlen(ln) for ln in right), default=0)
    sep = " " * gap
    combo: List[str] = []
    for L, R in zip_longest(left, right, fillvalue=""):
        combo.append(pad_visible(L, lw) + sep + pad_visible(R, rw))
    return combo



# Lógica del juego (Programación Funcional)


# Definición de tipos para el estado del juego
GameState = Dict[str, Any]

def create_game_state(palabra: str, max_intentos: int = 6) -> GameState:
    """Crea el estado inicial del juego."""
    return {
        "palabra": palabra,
        "max_intentos": max_intentos,
        "letras_ok": set(),
        "letras_bad": set(),
        "palabras_bad": set()
    }


def intento_letra(game_state: GameState, letra: str) -> Tuple[GameState, bool]:
    """Intenta una letra y devuelve el nuevo estado y si fue acierto."""
    letra = (letra or "").strip().lower()
    if not (len(letra) == 1 and letra.isalpha() and letra in string.ascii_lowercase):
        raise ValueError("Ingresa una sola letra de la a a la z")
    if letra in game_state["letras_ok"] or letra in game_state["letras_bad"]:
        raise ValueError("Letra repetida")
    
    if letra in game_state["palabra"]:
        new_state = game_state.copy()
        new_state["letras_ok"] = game_state["letras_ok"] | {letra}
        return new_state, True
    else:
        new_state = game_state.copy()
        new_state["letras_bad"] = game_state["letras_bad"] | {letra}
        return new_state, False


def intento_palabra(game_state: GameState, candidata: str) -> Tuple[GameState, bool]:
    """Permite adivinar la palabra completa."""
    candidata = (candidata or "").strip().lower()
    if not candidata.isalpha():
        raise ValueError("La palabra debe contener solo letras")
    if candidata in game_state["palabras_bad"]:
        raise ValueError("Ya probaste esa palabra")
    
    if candidata == game_state["palabra"]:
        new_state = game_state.copy()
        new_state["letras_ok"] = set(game_state["palabra"])
        return new_state, True
    else:
        new_state = game_state.copy()
        new_state["palabras_bad"] = game_state["palabras_bad"] | {candidata}
        return new_state, False


def progreso(game_state: GameState) -> str:
    """Devuelve el progreso actual de la palabra."""
    return " ".join([ch if ch in game_state["letras_ok"] else "_" for ch in game_state["palabra"]])


def intentos_usados(game_state: GameState) -> int:
    """Calcula los intentos usados."""
    return len(game_state["letras_bad"]) + len(game_state["palabras_bad"])


def intentos_restantes(game_state: GameState) -> int:
    """Calcula los intentos restantes."""
    return game_state["max_intentos"] - intentos_usados(game_state)


def estado_ahorcado(game_state: GameState) -> str:
    """Devuelve el estado actual del ahorcado."""
    idx = min(intentos_usados(game_state), len(HANGMAN_PICS) - 1)
    color = FG["green"] if idx == 0 else (FG["yellow"] if idx < len(HANGMAN_PICS) - 1 else FG["red"])
    lines = [color + ln + (RESET if USE_COLOR else "") for ln in HANGMAN_PICS[idx].splitlines(True)]
    return "".join(lines)


def gano(game_state: GameState) -> bool:
    """Verifica si el jugador ganó."""
    return all(ch in game_state["letras_ok"] for ch in game_state["palabra"])


def perdio(game_state: GameState) -> bool:
    """Verifica si el jugador perdió."""
    return intentos_usados(game_state) >= game_state["max_intentos"]



# Modo automático (sin input) para sandbox / pruebas

LETTER_ORDER = tuple("etaoinshrdlucmfwypvbgkjqxz")


def next_auto_letter(game_state: GameState) -> str:
    """Selecciona la siguiente letra para el modo automático."""
    for ch in LETTER_ORDER:
        if ch not in game_state["letras_ok"] and ch not in game_state["letras_bad"]:
            return ch
    for ch in string.ascii_lowercase:
        if ch not in game_state["letras_ok"] and ch not in game_state["letras_bad"]:
            return ch
    return "a"



# UI de consola (con "ventana"/box)


def pintar_alfabeto(letras_ok: Set[str], letras_bad: Set[str]) -> str:
    """Pinta el alfabeto con colores según el estado."""
    partes: List[str] = []
    for ch in string.ascii_lowercase:
        if ch in letras_ok:
            partes.append(c(ch, FG["green"], BOLD))
        elif ch in letras_bad:
            partes.append(c(ch, FG["red"]))
        else:
            partes.append(c(ch, FG["gray"]))
    return " ".join(partes)


def pantalla_juego(cat: str, diff: str, game_state: GameState) -> None:
    """Muestra la pantalla del juego."""
    limpiar_consola()
    banner()

    # Izquierda: dibujo
    raw_left = estado_ahorcado(game_state)
    left = [ln for ln in raw_left.splitlines() if ln.strip()]

    # Derecha: estado
    prog = progreso(game_state)
    if USE_COLOR:
        prog = " ".join([p if p != "_" else c("_", FG["yellow"]) for p in prog.split(" ")])
    right: List[str] = [
        c("Estado", BOLD),
        f"Palabra: {prog}",
        f"Intentos: {intentos_usados(game_state)}/{game_state['max_intentos']}",
        f"Restantes: {intentos_restantes(game_state)}",
        "",
        c("Letras", BOLD),
        pintar_alfabeto(game_state["letras_ok"], game_state["letras_bad"]),
    ]
    if game_state["letras_bad"]:
        right.append(f"Incorrectas: {' '.join(sorted(game_state['letras_bad']))}")
    if game_state["palabras_bad"]:
        right.append(f"Palabras fallidas: {', '.join(sorted(game_state['palabras_bad']))}")

    # Componer columnas y encerrarlas en box
    cols = compose_columns(left, right, gap=4)
    title = f"Ahorcado — {cat} | {diff} | Intentos {intentos_usados(game_state)}/{game_state['max_intentos']}"
    ventana = make_box(cols, title=title)
    print(ventana)


def seleccionar_opcion(titulo: str, opciones: List[str]) -> str:
    """Permite al usuario seleccionar una opción del menú."""
    while True:
        limpiar_consola()
        banner()
        lines = [f"  {i}. {op}" for i, op in enumerate(opciones, 1)]
        caja = make_box([c(titulo, BOLD), "", *lines], title="Menu")
        print(caja)
        sel = safe_input(c("Selecciona una opcion: ", FG["yellow"]))
        if not sel:
            # Sin I/O o Enter vacío → elegir la primera opción para no bloquear
            return opciones[0]
        if sel.isdigit() and 1 <= int(sel) <= len(opciones):
            return opciones[int(sel) - 1]
        print(c("Opcion invalida. Intenta de nuevo.", FG["red"]))
        time.sleep(1)


def jugar_consola(categoria: str | None = None, dificultad: str = "media") -> None:
    """Función principal del juego."""
    if categoria is None:
        categoria = seleccionar_opcion("Elige una categoria", list(WORD_BANK.keys()))
    if dificultad not in DIFFICULTY:
        dificultad = seleccionar_opcion("Elige una dificultad", list(DIFFICULTY.keys()))

    cat, palabra = elegir_palabra(categoria)
    max_int = DIFFICULTY.get(dificultad, DIFFICULTY["media"])['max_intentos']
    game_state = create_game_state(palabra=palabra, max_intentos=max_int)

    # Función recursiva para el bucle del juego
    def game_loop(state: GameState) -> None:
        pantalla_juego(cat, dificultad, state)
        
        # Fin de juego
        if gano(state):
            msg = make_box([c("Ganaste.", FG["green"], BOLD), f"La palabra era: {state['palabra']}"], title="Resultado")
            print("\n" + msg)
            return
        if perdio(state):
            msg = make_box([c("Perdiste.", FG["red"], BOLD), f"La palabra era: {state['palabra']}"], title="Resultado")
            print("\n" + msg)
            return

        entrada = safe_input(c("Ingresa una letra o la palabra completa: ", FG["yellow"]))
        if AUTO_MODE or not entrada:
            entrada = next_auto_letter(state)

        try:
            if len(entrada.strip()) == 1:
                new_state, acierto = intento_letra(state, entrada)
                feedback = c("Acierto.", FG["green"]) if acierto else c("No esta en la palabra.", FG["red"])
            elif entrada.strip().isalpha() and len(entrada.strip()) == len(state["palabra"]):
                new_state, acierto = intento_palabra(state, entrada)
                feedback = c("¡Adivinaste la palabra completa!", FG["green"]) if acierto else c("No es la palabra.", FG["red"]) 
            else:
                raise ValueError("Escribe una sola letra o la palabra completa (solo letras)")
            print(make_box([f"Entrada: {entrada}", feedback], title="Movimiento"))
            time.sleep(0.2 if AUTO_MODE else 0.5)
            game_loop(new_state)  # Llamada recursiva
        except ValueError as e:
            print(make_box([f"Aviso: {e}"], title="Entrada invalida"))
            time.sleep(1)
            game_loop(state)  # Llamada recursiva con el mismo estado

    # Iniciar el bucle del juego
    game_loop(game_state)

    print()
    if not AUTO_MODE:
        safe_input(c("Presiona Enter para volver al menu... ", FG["gray"]))


def main() -> None:
    """Función principal del programa."""
    # Función recursiva para el menú principal
    def menu_loop() -> None:
        opcion = seleccionar_opcion(
            "Menu principal",
            ["Jugar", "Cambiar categoria", "Cambiar dificultad", "Salir"],
        )
        if opcion == "Jugar":
            jugar_consola()
            menu_loop()
        elif opcion == "Cambiar categoria":
            cat = seleccionar_opcion("Elige una categoria", list(WORD_BANK.keys()))
            jugar_consola(categoria=cat)
            menu_loop()
        elif opcion == "Cambiar dificultad":
            diff = seleccionar_opcion("Elige una dificultad", list(DIFFICULTY.keys()))
            jugar_consola(dificultad=diff)
            menu_loop()
        else:
            limpiar_consola()
            print(make_box([c("Hasta pronto.", FG["gray"])], title="Salir"))
    
    menu_loop()



# PRUEBAS (lógicas, sin I/O de consola)


def _run_tests() -> None:
    print("== Pruebas HangmanGame ==")
    # 1) progreso inicial
    g = create_game_state("abc", max_intentos=3)
    assert "_ _ _" in progreso(g), "Progreso inicial"
    # 2) acierto
    new_g, acierto = intento_letra(g, 'a')
    assert acierto is True
    assert 'a' in progreso(new_g)
    # 3) repetida
    try:
        intento_letra(new_g, 'a')
    except ValueError:
        pass
    else:
        raise AssertionError("Debe rechazar repetidas")
    # 4) fallo e incremento
    new_g2, acierto = intento_letra(g, 'x')
    assert acierto is False
    assert intentos_usados(new_g2) == 1
    # 5) ganar
    new_g3, _ = intento_letra(new_g, 'b')
    new_g4, _ = intento_letra(new_g3, 'c')
    assert gano(new_g4) and not perdio(new_g4)
    # 6) perder
    h = create_game_state("z", max_intentos=1)
    new_h, acierto = intento_letra(h, 'x')
    assert perdio(new_h) and not gano(new_h)
    # 7) validacion de entrada
    i = create_game_state("hola")
    for inval in ["", "ab", "ñ", "1", " "]:
        try:
            intento_letra(i, inval)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Entrada invalida: {inval!r}")
    # 8) saturacion de frame
    j = create_game_state("xyz", max_intentos=2)
    j["letras_bad"] = {'a', 'b', 'c'}
    assert isinstance(estado_ahorcado(j), str)
    # 9) dificultad media
    assert DIFFICULTY['media']['max_intentos'] == 6
    # 10) estrategia automática propone letras no repetidas
    t = create_game_state("python", max_intentos=8)
    seen: Set[str] = set()
    for _ in range(5):
        ch = next_auto_letter(t)
        assert ch not in seen, "next_auto_letter debe proponer letras nuevas"
        seen.add(ch)
        try:
            intento_letra(t, ch)
        except ValueError:
            pass
    # 11) demo automática termina en estado válido (gana o pierde)
    u = create_game_state("variable", max_intentos=8)
    steps = 0
    current_state = u
    while not (gano(current_state) or perdio(current_state)) and steps < 26:
        ch = next_auto_letter(current_state)
        try:
            new_state, _ = intento_letra(current_state, ch)
            current_state = new_state
        except ValueError:
            pass
        steps += 1
    assert gano(current_state) or perdio(current_state), "La demo automática debe finalizar"
    # 12) progreso() no debe contener códigos ANSI
    v = create_game_state("abc")
    assert "\033[" not in progreso(v), "progreso() debe ser texto plano"
    # 13) 'print' debe aceptar el argumento 'end' (no debe estar sombreado)
    try:
        print("", end="")
    except TypeError as e:
        raise AssertionError(f"El builtin print fue sombreado: {e}")
    # 14) intentos_restantes disminuye en fallos
    w = create_game_state("aa", max_intentos=3)
    antes = intentos_restantes(w)
    new_w, _ = intento_letra(w, 'z') if 'z' not in w["palabra"] else intento_letra(w, 'x')
    assert intentos_restantes(new_w) == antes - 1, "Debe descontar intento en fallo"
    # 15) elegir_palabra retorna categoria/word válidos
    cat, word = elegir_palabra(None)
    assert cat in WORD_BANK and word in WORD_BANK[cat] and isinstance(word, str), "elegir_palabra inválida"
    # 16) adivinar palabra completa (correcta) gana sin gastar intentos
    x = create_game_state("sol", max_intentos=6)
    new_x, acierto = intento_palabra(x, "sol")
    assert acierto is True
    assert gano(new_x) and intentos_usados(new_x) == 0
    # 17) adivinar palabra completa (incorrecta) consume 1 intento y se registra
    y = create_game_state("sol", max_intentos=2)
    usados_antes = intentos_usados(y)
    new_y, acierto = intento_palabra(y, "sal")
    assert acierto is False
    assert intentos_usados(new_y) == usados_antes + 1 and "sal" in new_y["palabras_bad"]
    # 18) palabra repetida debe lanzar error
    try:
        intento_palabra(new_y, "sal")
    except ValueError:
        pass
    else:
        raise AssertionError("Debe rechazar palabra completa repetida")

    print("Todas las pruebas pasaron")


if __name__ == "__main__":
    if os.environ.get("RUN_TESTS") == "1":
        _run_tests()
    else:
        main()

