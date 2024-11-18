import re
import keyword
import tkinter as tk
from tkinter import messagebox, scrolledtext
from graphviz import Digraph

# Patrones de análisis léxico
TOKENS_PYTHON = [
    ('COMENTARIO_LINEA', r'#.*'),
    ('CADENA_MULTILINEA', r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\')'),
    ('CADENA', r'"[^"\n]*"|\'[^\']*\''),  
    ('OPERADOR_LOGICO', r'and|or|not|&&|\|\|'),  
    ('OPERADOR_COMPARACION', r'==|!=|<=|>=|<|>'),
    ('OPERADOR_ASIGNACION', r'[\+\-\*/]?='),
    ('OPERADOR_ARITMETICO', r'[+\-*/%]'),
    ('PUNTUACION', r'[;,\(\)\{\}\[\]\.:]'),
    ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('NUMERO', r'\d+(\.\d+)?'),  
    ('ESPACIO', r'\s+'),  
]

PALABRAS_CLAVE = keyword.kwlist

# Funciones del compilador
def es_palabra_clave(palabra):
    return palabra in PALABRAS_CLAVE

def analizador_lexico(codigo_fuente):
    tokens_encontrados = []
    lineas = codigo_fuente.splitlines()

    for num_linea, linea in enumerate(lineas, start=1):
        posicion = 0
        while posicion < len(linea):
            for token_tipo, patron in TOKENS_PYTHON:
                patron_compilado = re.compile(patron)
                coincidencia = patron_compilado.match(linea, posicion)
                if coincidencia:
                    texto = coincidencia.group(0)
                    if token_tipo != 'ESPACIO':  
                        if token_tipo == 'IDENTIFICADOR' and es_palabra_clave(texto):
                            tokens_encontrados.append((num_linea, 'PALABRA_CLAVE', texto))
                        else:
                            tokens_encontrados.append((num_linea, token_tipo, texto))
                    posicion = coincidencia.end(0)
                    break
    return tokens_encontrados

def construir_arbol_sintactico(tokens, nombre_programa):
    g = Digraph('G', format='png')
    g.attr(size='10,10')  # Tamaño en pulgadas
    g.attr(dpi='300')  # Establecer el DPI a 300 para mejor calidad
    nodo_id = 0
    pila_nodos = []  # Pila para manejar la jerarquía

    def nuevo_nodo(etiqueta):
        nonlocal nodo_id
        nodo_id += 1
        return f"nodo{nodo_id}", etiqueta

    # Crear el nodo raíz con el nombre del programa (no se agregará a la pila)
    raiz_id, raiz_etiqueta = nuevo_nodo(f"Programa: {nombre_programa}")
    g.node(raiz_id, raiz_etiqueta, shape='rect', style='filled', fillcolor='#A0D3E8')

    # Usar un nodo actual que parte desde la raíz
    nodo_actual = raiz_id

    for token in tokens:
        tipo, texto = token[1], token[2]

        # Crear nodos hijos según el tipo de token
        if tipo in ["PALABRA_CLAVE", "OPERADOR_ASIGNACION", "OPERADOR_COMPARACION", "OPERADOR_ARITMETICO"]:
            id_hijo, etiqueta_hijo = nuevo_nodo(texto)
            g.node(id_hijo, etiqueta_hijo)
            g.edge(nodo_actual, id_hijo)  # Conectar con el nodo actual
            pila_nodos.append(nodo_actual)  # Guardar el nodo actual en la pila
            nodo_actual = id_hijo  # Actualizar el nodo actual al hijo recién creado

        elif tipo in ["NUMERO", "IDENTIFICADOR"]:
            id_hijo, etiqueta_hijo = nuevo_nodo(texto)
            g.node(id_hijo, etiqueta_hijo)
            g.edge(nodo_actual, id_hijo)  # Conectar con el nodo actual

        # Si encontramos un punto y coma, volvemos al nodo padre
        elif tipo == "PUNTUACION" and texto == ';':
            if pila_nodos:
                nodo_actual = pila_nodos.pop()  # Volver al nodo padre

    # Guardar el archivo en formato PNG y visualizarlo
    g.render('arbol_sintactico', format='png', view=True)
    messagebox.showinfo("Árbol Sintáctico", "Se generó el árbol sintáctico. Verifica el archivo 'arbol_sintactico.png'.")



def analizador_semantico(tokens):
    tabla_simbolos = {}
    errores = []
    for token in tokens:
        tipo, valor = token[1], token[2]
        if tipo == "IDENTIFICADOR" and valor not in tabla_simbolos:
            errores.append(f"Error: Variable '{valor}' no definida.")
    return errores

def generar_codigo_intermedio(tokens):
    codigo_intermedio = []
    for token in tokens:
        tipo, valor = token[1], token[2]
        if tipo == "NUMERO" or tipo == "IDENTIFICADOR":
            codigo_intermedio.append(f"LOAD {valor}")
        elif tipo == "OPERADOR_ARITMETICO":
            codigo_intermedio.append(f"OPER {valor}")
    return codigo_intermedio

def optimizar_codigo(codigo_intermedio):
    optimizado = []
    for linea in codigo_intermedio:
        if "LOAD 0" not in linea:  # Ejemplo: eliminar cargas redundantes
            optimizado.append(linea)
    return optimizado

# Funciones de la interfaz gráfica
def mostrar_resultados_lexicos():
    tokens = analizador_lexico(codigo_fuente)
    resultado = "\n".join(f"Línea {t[0]}: {t[1]} -> {t[2]}" for t in tokens)
    messagebox.showinfo("Análisis Léxico", resultado)

def mostrar_arbol_sintactico():
    tokens = analizador_lexico(codigo_fuente)
    construir_arbol_sintactico(tokens, "MiPrograma")

def mostrar_errores_semanticos():
    tokens = analizador_lexico(codigo_fuente)
    errores = analizador_semantico(tokens)
    if errores:
        messagebox.showerror("Errores Semánticos", "\n".join(errores))
    else:
        messagebox.showinfo("Análisis Semántico", "No se encontraron errores semánticos.")

def mostrar_codigo_intermedio():
    tokens = analizador_lexico(codigo_fuente)
    codigo_intermedio = generar_codigo_intermedio(tokens)
    messagebox.showinfo("Código Intermedio", "\n".join(codigo_intermedio))

def mostrar_codigo_optimizado():
    tokens = analizador_lexico(codigo_fuente)
    codigo_intermedio = generar_codigo_intermedio(tokens)
    codigo_optimizado = optimizar_codigo(codigo_intermedio)
    messagebox.showinfo("Código Optimizado", "\n".join(codigo_optimizado))

# Ventana para ingresar código fuente
codigo_fuente = ""

def ventana_principal():
    def guardar_codigo():
        global codigo_fuente
        codigo_fuente = text_area.get("1.0", tk.END).strip()
        if not codigo_fuente:
            messagebox.showwarning("Advertencia", "El código fuente está vacío.")
        else:
            ventana.destroy()
            menu_compilador()

    ventana = tk.Tk()
    ventana.title("Entrada de Código Fuente")
    ventana.geometry("800x600")

    label_input = tk.Label(ventana, text="Escriba el código a analizar:", font=("Arial", 12))
    label_input.pack(pady=5)

    text_area = scrolledtext.ScrolledText(ventana, width=80, height=25, font=("Courier", 10))
    text_area.pack(padx=10, pady=10)

    btn_guardar = tk.Button(ventana, text="Continuar", command=guardar_codigo, width=25, height=2, bg="#32CD32", fg="white", font=("Arial", 10))
    btn_guardar.pack(pady=10)

    ventana.mainloop()

# Menú principal del compilador
def menu_compilador():
    ventana = tk.Tk()
    ventana.title("Compilador - Menú Principal")
    ventana.geometry("600x400")

    label_menu = tk.Label(ventana, text="Seleccione una función:", font=("Arial", 16))
    label_menu.pack(pady=20)

    tk.Button(ventana, text="Análisis Léxico", command=mostrar_resultados_lexicos, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Árbol Sintáctico", command=mostrar_arbol_sintactico, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Análisis Semántico", command=mostrar_errores_semanticos, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Código Intermedio", command=mostrar_codigo_intermedio, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Código Optimizado", command=mostrar_codigo_optimizado, width=30, height=2).pack(pady=5)

    tk.Button(ventana, text="Salir", command=ventana.quit, width=30, height=2, bg="#FF6347", fg="white").pack(pady=20)
    ventana.mainloop()

    # Continuación del código con función para corregir código y su integración en la interfaz gráfica

def corregir_codigo(codigo_fuente):
    correcciones = []
    lineas = codigo_fuente.splitlines()
    codigo_corregido = []

    for num_linea, linea in enumerate(lineas, start=1):
        linea_corregida = linea

        # Corregir paréntesis no cerrados
        if '(' in linea and ')' not in linea:
            linea_corregida += ')'
            correcciones.append(f"Línea {num_linea}: Se añadió un paréntesis de cierre.")
        
        # Corregir llaves no cerradas
        if '{' in linea and '}' not in linea:
            linea_corregida += '}'
            correcciones.append(f"Línea {num_linea}: Se añadió una llave de cierre.")
        
        # Corregir errores de sintaxis específicos
        linea_corregida = linea_corregida.replace("si ", "if ").replace("entonces", ":")  # Ejemplo de corrección

        # Asegurarse de que los comentarios no estén dentro de las cadenas
        if '#' in linea:
            indice_comentario = linea.index('#')
            parte_codigo = linea[:indice_comentario]
            parte_comentario = linea[indice_comentario:]
            linea_corregida = parte_codigo.strip() + ' ' + parte_comentario

        codigo_corregido.append(linea_corregida)

    return '\n'.join(codigo_corregido), correcciones

# Mostrar el código corregido en una ventana gráfica
def mostrar_codigo_corregido():
    global codigo_fuente
    codigo_corregido, correcciones = corregir_codigo(codigo_fuente)

    resultado_correcciones = "Correcciones realizadas:\n" + "\n".join(correcciones) if correcciones else "No se realizaron correcciones."
    messagebox.showinfo("Código Corregido", resultado_correcciones + "\n\nCódigo Corregido:\n" + codigo_corregido)

# Menú principal del compilador con opción de corregir código
def menu_compilador():
    ventana = tk.Tk()
    ventana.title("Compilador - Menú Principal")
    ventana.geometry("600x500")

    label_menu = tk.Label(ventana, text="Seleccione una función:", font=("Arial", 16))
    label_menu.pack(pady=20)

    tk.Button(ventana, text="Análisis Léxico", command=mostrar_resultados_lexicos, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Árbol Sintáctico", command=mostrar_arbol_sintactico, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Análisis Semántico", command=mostrar_errores_semanticos, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Código Intermedio", command=mostrar_codigo_intermedio, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Código Optimizado", command=mostrar_codigo_optimizado, width=30, height=2).pack(pady=5)
    tk.Button(ventana, text="Corregir Código", command=mostrar_codigo_corregido, width=30, height=2).pack(pady=5)

    tk.Button(ventana, text="Salir", command=ventana.quit, width=30, height=2, bg="#FF6347", fg="white").pack(pady=20)
    ventana.mainloop()

# Iniciar aplicación
ventana_principal()

