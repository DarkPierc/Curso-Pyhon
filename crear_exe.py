import os
import sys
import subprocess

def crear_exe(script_path):
    if not os.path.isfile(script_path):
        print(f"[❌] El archivo {script_path} no existe.")
        return

    base_name = os.path.splitext(os.path.basename(script_path))[0]
    icon_path = f"{base_name}.ico"

    cmd = [
        "pyinstaller",
        "--onefile",                 # Generar un solo archivo .exe
        "--clean",                   # Limpiar caché de PyInstaller
        "--noconsole",               # Ocultar consola al ejecutar .exe
        "--name", "GEN_CC",          # Nombre del ejecutable
        "--hidden-import", "requests", # Incluir módulo requests
        "--hidden-import", "pyperclip", # Incluir módulo pyperclip
        "--hidden-import", "urllib3", # Incluir módulo urllib3
        f"{script_path}"             # Ruta del script .py
    ]

    # Si el icono existe en el mismo directorio, lo añadimos
    if os.path.isfile(icon_path):
        cmd.insert(-1, "--icon")
        cmd.insert(-1, icon_path)
        print(f"[🧩] Icono detectado: {icon_path}")
    else:
        # Buscar icono.ico en el directorio actual
        if os.path.isfile("icono.ico"):
            cmd.insert(-1, "--icon")
            cmd.insert(-1, "icono.ico")
            print(f"[🧩] Icono detectado: icono.ico")
        else:
            print("[ℹ️] No se encontró icono .ico. Se usará el icono por defecto.")

    # Comando visible al usuario
    print("\n[⚙️] Ejecutando PyInstaller con el siguiente comando:\n")
    print(" ".join(cmd), "\n")

    # Ejecutar PyInstaller
    subprocess.run(cmd)

    print(f"\n[✅] Proceso completado. El ejecutable se encuentra en la carpeta 'dist/'")

if __name__ == "__main__":
    #Ejecuacion del script python crear_exe.py main.py
    if len(sys.argv) < 2:
        print("Uso: python crear_exe.py <archivo_script.py>")
    else:
        crear_exe(sys.argv[1])
