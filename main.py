import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser
import json
import os
import pyperclip
from datetime import datetime
import random

def generar_luhn(bin_prefix):
    # Completar el número con dígitos aleatorios
    numero = list(bin_prefix.replace('x', str(random.randint(0, 9))))
    # Calcular dígito de verificación Luhn
    suma = 0
    pos = len(numero) - 1
    while pos >= 0:
        digito = int(numero[pos])
        if pos % 2 == 0:  # posiciones pares
            temp = digito * 2
            if temp > 9:
                temp -= 9
            suma += temp
        else:  # posiciones impares
            suma += digito
        pos -= 1
    digito_verificacion = (10 - (suma % 10)) % 10
    numero.append(str(digito_verificacion))
    return ''.join(numero)

class BinGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Generador de BIN RS')
        self.root.geometry('800x600')
        self.root.configure(bg='#2c3e50')

        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=6, relief='flat', background='#3498db')
        style.configure('TLabel', background='#2c3e50', foreground='white')
        style.configure('TFrame', background='#2c3e50')
        style.configure('TEntry', padding=5)

        # Frame principal
        main_frame = ttk.Frame(root)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Título
        title_label = ttk.Label(main_frame, text='GENERADOR DE CC FRIENDS SCHOOL', font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=10)

        # Frame para entrada de datos
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', padx=20, pady=10)

        # Campo BIN
        bin_label = ttk.Label(input_frame, text='BIN (usa x para dígitos aleatorios):')
        bin_label.pack(anchor='w')
        self.bin_entry = ttk.Entry(input_frame)
        self.bin_entry.pack(fill='x', pady=5)
        self.bin_entry.insert(0, '453900xxxxxxxx')

        # Frame para mes y año
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill='x', pady=5)

        # Mes
        month_label = ttk.Label(date_frame, text='Mes:')
        month_label.pack(side='left')
        self.month_var = tk.StringVar(value='01')
        self.month_combo = ttk.Combobox(date_frame, width=3, textvariable=self.month_var, values=[str(i).zfill(2) for i in range(1, 13)])
        self.month_combo.pack(side='left', padx=5)

        # Año
        year_label = ttk.Label(date_frame, text='Año:')
        year_label.pack(side='left', padx=(20,0))
        self.year_var = tk.StringVar(value='24')
        self.year_combo = ttk.Combobox(date_frame, width=3, textvariable=self.year_var, values=[str(i).zfill(2) for i in range(23, 31)])
        self.year_combo.pack(side='left', padx=5)

        # Cantidad de tarjetas
        amount_label = ttk.Label(date_frame, text='Cantidad:')
        amount_label.pack(side='left', padx=(20,0))
        self.amount_var = tk.StringVar(value='10')
        self.amount_combo = ttk.Combobox(date_frame, width=5, textvariable=self.amount_var, values=['10', '15', '50', '100'])
        self.amount_combo.pack(side='left', padx=5)

        # Botón generar aleatorio
        random_date_btn = ttk.Button(date_frame, text='Fecha Aleatoria', command=self.generar_fecha_aleatoria)
        random_date_btn.pack(side='left', padx=20)

        # Botones principales
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', padx=20, pady=10)

        buttons = [
            ('Generar Tarjeta', self.generar_bin),
            ('Guardar Tarjeta', self.guardar_bin),
            ('Correo Temporal', self.correo_temporal),
            ('BIN Checker', self.bin_checker),
            ('Ver Tarjetas Guardadas', self.ver_bins),
            ('Créditos', self.mostrar_creditos),
            ('Información', self.mostrar_info)
        ]

        for text, command in buttons:
            btn = ttk.Button(buttons_frame, text=text, command=command)
            btn.pack(pady=5, fill='x')

        # Campo de resultado
        self.result_text = tk.Text(main_frame, height=10, width=60)
        self.result_text.pack(pady=10, padx=20)

    def generar_fecha_aleatoria(self):
        mes = str(random.randint(1, 12)).zfill(2)
        año = str(random.randint(23, 30)).zfill(2)
        self.month_var.set(mes)
        self.year_var.set(año)

    def generar_bin(self):
        bin_base = self.bin_entry.get()
        if not bin_base:
            messagebox.showerror("Error", "Ingrese un BIN")
            return

        # Completar con x si es menor a 16 dígitos
        if len(bin_base) < 16:
            bin_base = bin_base + 'x' * (15 - len(bin_base))

        mes = self.month_var.get()
        año = self.year_var.get()
        cantidad = int(self.amount_var.get())

        self.result_text.delete(1.0, tk.END)
        resultados = []

        for _ in range(cantidad):
            tarjeta = generar_luhn(bin_base)
            cvv = str(random.randint(100, 999))
            resultado = f"{tarjeta}|{mes}|{año}|{cvv}"
            resultados.append(resultado)
            self.result_text.insert(tk.END, resultado + '\n')

        # Copiar al portapapeles
        pyperclip.copy('\n'.join(resultados))
        messagebox.showinfo("Éxito", f"{cantidad} tarjetas generadas y copiadas al portapapeles")

    def guardar_bin(self):
        bin_actual = self.result_text.get(1.0, tk.END).strip()
        if bin_actual:
            with open('BinGuardados.txt', 'a') as f:
                f.write(f"\n{bin_actual} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            messagebox.showinfo("Éxito", "Tarjeta guardada correctamente")
        else:
            messagebox.showwarning("Advertencia", "No hay tarjeta para guardar")

    def correo_temporal(self):
        webbrowser.open('https://temp-mail.org/es/')

    def bin_checker(self):
        bin_num = self.bin_entry.get()[:6]  # Tomamos los primeros 6 dígitos
        if bin_num and len(bin_num) >= 6:
            try:
                response = requests.get(f"https://lookup.binlist.net/{bin_num}")
                if response.status_code == 200:
                    data = response.json()
                    info = f"Esquema: {data.get('scheme', 'N/A')}\n"
                    info += f"Tipo: {data.get('type', 'N/A')}\n"
                    info += f"Marca: {data.get('brand', 'N/A')}\n"
                    info += f"País: {data.get('country', {}).get('name', 'N/A')}\n"
                    info += f"Banco: {data.get('bank', {}).get('name', 'N/A')}"
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, info)
                else:
                    messagebox.showerror("Error", "BIN no válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error al verificar BIN: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Por favor ingrese un BIN válido (mínimo 6 dígitos)")

    def ver_bins(self):
        try:
            with open('BinGuardados.txt', 'r') as f:
                content = f.read()
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, content if content else "No hay tarjetas guardadas")
        except FileNotFoundError:
            messagebox.showinfo("Info", "No hay tarjetas guardadas todavía")

    def mostrar_creditos(self):
        credits = "Created by: Curso python Friends School\nVersion: cc-genpro1"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, credits)

    def mostrar_info(self):
        info = "Este es un generador de tarjetas con validación Luhn y verificador de BIN."
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, info)

if __name__ == '__main__':
    root = tk.Tk()
    app = BinGeneratorApp(root)
    root.mainloop()