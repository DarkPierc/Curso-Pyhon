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
    # Reemplazar cada 'x' con un dígito aleatorio
    numero_sin_verificar = ''
    for digito in bin_prefix:
        if digito.lower() == 'x':
            numero_sin_verificar += str(random.randint(0, 9))
        else:
            numero_sin_verificar += digito
    
    # Verificar que todos sean dígitos
    if not numero_sin_verificar.isdigit():
        raise ValueError("El BIN debe contener solo dígitos o 'x'")
    
    # Aseguramos que tengamos 15 dígitos (para luego agregar el dígito de verificación)
    if len(numero_sin_verificar) > 15:
        numero_sin_verificar = numero_sin_verificar[:15]
    
    # Calculamos el dígito de verificación usando el algoritmo de Luhn
    suma = 0
    for i, digito in enumerate(reversed(numero_sin_verificar)):
        n = int(digito)
        if i % 2 == 1:  # Posiciones impares (desde el final)
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    
    digito_verificacion = (10 - (suma % 10)) % 10
    
    # Devolvemos el número completo con el dígito de verificación
    return numero_sin_verificar + str(digito_verificacion)

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
        bin_base = self.bin_entry.get().strip()
        if not bin_base:
            messagebox.showerror("Error", "Ingrese un BIN")
            return

        # Completar con x si es menor a 15 dígitos (para luego agregar el dígito de verificación)
        if len(bin_base) < 15:
            bin_base = bin_base + 'x' * (15 - len(bin_base))
        elif len(bin_base) > 15:
            bin_base = bin_base[:15]  # Truncar si es más largo

        mes = self.month_var.get()
        año = self.year_var.get()
        cantidad_solicitada = int(self.amount_var.get())

        self.result_text.delete(1.0, tk.END)
        resultados = []

        try:
            # Generamos tarjetas hasta obtener la cantidad solicitada de tarjetas válidas
            tarjetas_generadas = 0
            intentos_maximos = cantidad_solicitada * 10  # Límite para evitar bucles infinitos
            intentos = 0
            
            while tarjetas_generadas < cantidad_solicitada and intentos < intentos_maximos:
                intentos += 1
                try:
                    # Generar tarjeta con algoritmo Luhn
                    tarjeta = generar_luhn(bin_base)
                    
                    # Verificar que la tarjeta sea válida según Luhn
                    if self.verificar_luhn(tarjeta):
                        cvv = str(random.randint(100, 999))
                        resultado = f"{tarjeta}|{mes}|{año}|{cvv}"
                        resultados.append(resultado)
                        self.result_text.insert(tk.END, resultado + '\n')
                        tarjetas_generadas += 1
                except Exception as e:
                    # No mostramos errores, solo continuamos intentando
                    pass

            # Copiar al portapapeles si hay resultados
            if resultados:
                pyperclip.copy('\n'.join(resultados))
                messagebox.showinfo("Éxito", f"{len(resultados)} tarjetas válidas generadas y copiadas al portapapeles")
            else:
                messagebox.showwarning("Advertencia", "No se pudo generar ninguna tarjeta válida")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la generación: {str(e)}")
            self.result_text.insert(tk.END, f"Error: {str(e)}\n")
            
    def verificar_luhn(self, numero):
        """Verifica si un número de tarjeta cumple con el algoritmo de Luhn"""
        if not numero.isdigit():
            return False
            
        # Calculamos la suma según el algoritmo de Luhn
        suma = 0
        for i, digito in enumerate(reversed(numero)):
            n = int(digito)
            if i % 2 == 1:  # Posiciones impares (desde el final)
                n *= 2
                if n > 9:
                    n -= 9
            suma += n
                
        # La suma debe ser divisible por 10
        return suma % 10 == 0

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
        bin_number = self.bin_entry.get()[:8]  # Get first 8 digits of BIN
        if len(bin_number) >= 6:
            try:
                # Make API request to binlist.net
                headers = {'Accept-Version': '3'}
                response = requests.get(f'https://lookup.binlist.net/{bin_number}', headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Format the response data
                    result = f"BIN Information:\n"
                    result += f"Scheme: {data.get('scheme', 'N/A')}\n"
                    result += f"Type: {data.get('type', 'N/A')}\n"
                    result += f"Brand: {data.get('brand', 'N/A')}\n"
                    
                    if 'country' in data:
                        result += f"Country: {data['country'].get('name', 'N/A')} {data['country'].get('emoji', '')}\n"
                        result += f"Currency: {data['country'].get('currency', 'N/A')}\n"
                    
                    if 'bank' in data:
                        result += f"Bank: {data['bank'].get('name', 'N/A')}\n"
                        result += f"Bank URL: {data['bank'].get('url', 'N/A')}\n"
                        result += f"Bank Phone: {data['bank'].get('phone', 'N/A')}\n"
                    
                    # Display results
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, result)
                else:
                    messagebox.showerror("Error", f"API request failed with status code: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to connect to BIN lookup service: {str(e)}")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to parse API response")
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