import re
import keyword
import tkinter as tk
from tkinter import messagebox, scrolledtext
from graphviz import Digraph

# === Patrones de análisis léxico ===
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

# === Funciones del compilador ===

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
            else:
                # Error léxico
                tokens_encontrados.append((num_linea, 'ERROR_LEXICO', linea[posicion]))
                posicion += 1
    return tokens_encontrados

def analizador_semantico(tokens):
    tabla_simbolos = {}
    errores = []
    for token in tokens:
        tipo, valor = token[1], token[2]
        if tipo == "IDENTIFICADOR" and valor not in tabla_simbolos:
            errores.append(f"Error: Variable '{valor}' no definida.")
    return errores

def construir_arbol_sintactico(tokens, nombre_programa):
    g = Digraph('G', format='png')
    g.attr(size='10,10', dpi='300')  # Tamaño y DPI
    nodo_id = 0
    pila_nodos = []

    def nuevo_nodo(etiqueta):
        nonlocal nodo_id
        nodo_id += 1
        return f"nodo{nodo_id}", etiqueta

    raiz_id, raiz_etiqueta = nuevo_nodo(f"Programa: {nombre_programa}")
    g.node(raiz_id, raiz_etiqueta, shape='rect', style='filled', fillcolor='#A0D3E8')
    nodo_actual = raiz_id

    for token in tokens:
        tipo, texto = token[1], token[2]
        if tipo in ["PALABRA_CLAVE", "OPERADOR_ASIGNACION", "OPERADOR_COMPARACION", "OPERADOR_ARITMETICO"]:
            id_hijo, etiqueta_hijo = nuevo_nodo(texto)
            g.node(id_hijo, etiqueta_hijo)
            g.edge(nodo_actual, id_hijo)
            pila_nodos.append(nodo_actual)
            nodo_actual = id_hijo
        elif tipo in ["NUMERO", "IDENTIFICADOR"]:
            id_hijo, etiqueta_hijo = nuevo_nodo(texto)
            g.node(id_hijo, etiqueta_hijo)
            g.edge(nodo_actual, id_hijo)
        elif tipo == "PUNTUACION" and texto == ';':
            if pila_nodos:
                nodo_actual = pila_nodos.pop()

    g.render('arbol_sintactico', format='png', view=True)
    messagebox.showinfo("Árbol Sintáctico", "Se generó el árbol sintáctico. Verifica 'arbol_sintactico.png'.")

def generar_codigo_intermedio(tokens):
    codigo_intermedio = []
    for token in tokens:
        tipo, valor = token[1], token[2]
        if tipo == "NUMERO":
            codigo_intermedio.append(f"LOAD {valor}")
        elif tipo == "IDENTIFICADOR":
            codigo_intermedio.append(f"STORE {valor}")
        elif tipo == "OPERADOR_ARITMETICO":
            codigo_intermedio.append(f"OPER {valor}")
        elif tipo == "OPERADOR_ASIGNACION":
            codigo_intermedio.append(f"ASSIGN {valor}")
        elif tipo == "OPERADOR_COMPARACION":
            codigo_intermedio.append(f"COMPARE {valor}")
    return codigo_intermedio

def optimizar_codigo(codigo_intermedio):
    optimizado = []
    for linea in codigo_intermedio:
        if "LOAD 0" not in linea:
            optimizado.append(linea)
    return optimizado

def corregir_codigo(codigo_fuente):
    lineas = codigo_fuente.splitlines()
    codigo_corregido = []
    correcciones = []

    for num_linea, linea in enumerate(lineas, start=1):
        if '(' in linea and ')' not in linea:
            linea = linea + ')'
            correcciones.append(f"Línea {num_linea}: Añadido paréntesis de cierre.")
        if '{' in linea and '}' not in linea:
            linea = linea + '}'
            correcciones.append(f"Línea {num_linea}: Añadida llave de cierre.")
        codigo_corregido.append(linea)

    return '\n'.join(codigo_corregido), correcciones

def ejecutar_codigo():
    global codigo_fuente
    try:
        # Capturar salida estándar y errores
        import io
        import sys

        buffer_salida = io.StringIO()
        sys.stdout = buffer_salida
        sys.stderr = buffer_salida

        # Ejecutar el código fuente
        exec(codigo_fuente)

        # Restaurar la salida estándar
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Mostrar el resultado
        salida = buffer_salida.getvalue()
        messagebox.showinfo("Resultado del Código", salida if salida else "Código ejecutado sin salida.")
    except Exception as e:
        # Restaurar la salida estándar en caso de error
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        messagebox.showerror("Error en el Código", f"Error: {str(e)}")

# === Funciones de interfaz gráfica ===

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

def mostrar_codigo_corregido():
    global codigo_fuente
    codigo_corregido, correcciones = corregir_codigo(codigo_fuente)
    resultado_correcciones = "Correcciones:\n" + "\n".join(correcciones) if correcciones else "No se realizaron correcciones."
    messagebox.showinfo("Código Corregido", resultado_correcciones + "\n\n" + codigo_corregido)

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
    tk.Label(ventana, text="Escriba el código a analizar:", font=("Arial", 14)).pack(pady=10)
    text_area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=90, height=25, font=("Consolas", 12))
    text_area.pack(pady=20)
    tk.Button(ventana, text="Guardar y Continuar", command=guardar_codigo, width=20, height=2, bg="#4CAF50", fg="white").pack(pady=10)
    ventana.mainloop()

def menu_compilador():
    ventana = tk.Tk()
    ventana.title("Menú Compilador")
    ventana.geometry("400x350")
    opciones = [
        ("Análisis Léxico", mostrar_resultados_lexicos),
        ("Árbol Sintáctico", mostrar_arbol_sintactico),
        ("Errores Semánticos", mostrar_errores_semanticos),
        ("Código Intermedio", mostrar_codigo_intermedio),
        ("Código Optimizado", mostrar_codigo_optimizado),
        ("Código Corregido", mostrar_codigo_corregido),
        ("Ejecutar Código", ejecutar_codigo),
    ]
    for texto, funcion in opciones:
        tk.Button(ventana, text=texto, command=funcion, width=30, height=2, bg="#4CAF50", fg="white").pack(pady=5)
    ventana.mainloop()

codigo_fuente = ""
ventana_principal()
