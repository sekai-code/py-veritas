import os
import re
import subprocess
import sys
import tempfile


def extraer_bloques(texto):
    marca = chr(96) * 3
    patron = re.compile(marca + r"(\w*)[ \t]*\r?\n(.*?)" + marca, re.DOTALL)
    bloques = []
    for lenguaje, codigo in patron.findall(texto):
        if lenguaje.lower() in ("python", "py"):
            bloques.append(codigo.strip())
    return bloques


def ejecutar_bloque(codigo, limite=10):
    # Nos aseguramos de que el archivo termine en salto de línea
    if not codigo.endswith("\n"):
        codigo += "\n"

    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "bloque.py")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(codigo)

        try:
            r = subprocess.run(
                [sys.executable, "bloque.py"],
                cwd=carpeta,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=limite,
                stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            return "timeout", f"Pasó del límite de {limite} segundos"
        except (OSError, FileNotFoundError) as e:
            return "error_entorno", f"No se pudo ejecutar: {e}"

        if r.returncode == 0:
            return "funciona", r.stdout

        # Distinguimos sintaxis de ejecución
        stderr = r.stderr or ""
        if "SyntaxError" in stderr or "IndentationError" in stderr:
            return "error_sintaxis", stderr
        return "falla", stderr


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 py_veritas.py ARCHIVO.md")
        return

    with open(sys.argv[1], encoding="utf-8") as f:
        texto = f.read()

    bloques = extraer_bloques(texto)
    print(f"Encontré {len(bloques)} bloque(s) de Python.\n")

    resumen = {}
    for i, bloque in enumerate(bloques, 1):
        estado, salida = ejecutar_bloque(bloque)
        resumen[estado] = resumen.get(estado, 0) + 1
        print(f"--- Bloque {i}: {estado} ---")
        if salida.strip():
            print(salida.rstrip())
        print("-" * 16)

    # Resumen final
    print("\n=== Resumen ===")
    for estado, cuenta in sorted(resumen.items()):
        print(f"  {estado}: {cuenta}")


if __name__ == "__main__":
    main()
