import re
import sys


def extraer_bloques(texto):
    # Generamos las tres comillas invertidas sin escribirlas literalmente,
    # así evitamos que se pierdan al copiar/pegar o que el editor las rompa.
    marca = chr(96) * 3
    patron = re.compile(marca + r"(\w*)[ \t]*\r?\n(.*?)" + marca, re.DOTALL)
    bloques = []
    for lenguaje, codigo in patron.findall(texto):
        if lenguaje.lower() in ("python", "py"):
            bloques.append(codigo.strip())  # .strip() limpia espacios vacíos
    return bloques


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 py_veritas.py ARCHIVO.md")
        return

    with open(sys.argv[1], encoding="utf-8") as f:
        texto = f.read()

    bloques = extraer_bloques(texto)

    print(f"Encontré {len(bloques)} bloque(s) de Python.")
    for i, codigo in enumerate(bloques, 1):
        print(f"--- Bloque {i} ---")
        print(codigo)
        print("-" * 16)


if __name__ == "__main__":
    main()
