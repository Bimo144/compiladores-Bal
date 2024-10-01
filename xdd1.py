import re
import keyword
import tkinter as tk
from tkinter import messagebox, scrolledtext
from graphviz import Digraph

# Definir patrones generales y ampliados para Python
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

def es_palabra_clave(palabra):
    return palabra in PALABRAS_CLAVE

# Analizador léxico
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

# Analizador sintáctico para construir el árbol (sintaxis simple)
def construir_arbol_sintactico(tokens, nombre_programa):
    g = Digraph('G', format='png')
    g.attr(size='6,6')
    nodo_id = 0
    pila_nodos = []  # Pila para manejar la jerarquía

    def nuevo_nodo(etiqueta):
        nonlocal nodo_id
        nodo_id += 1
        return f"nodo{nodo_id}", etiqueta

    # Crear el nodo raíz con el nombre del programa
    raiz_id, raiz_etiqueta = nuevo_nodo(f"Programa: {nombre_programa}")
    g.node(raiz_id, raiz_etiqueta, shape='rect', style='filled', fillcolor='#A0D3E8')
    pila_nodos.append(raiz_id)

    for token in tokens:
        tipo, texto = token[1], token[2]
        
        # Manejar palabras clave y operadores como nodos hijos
        if tipo in ["PALABRA_CLAVE", "OPERADOR_ASIGNACION", "OPERADOR_COMPARACION", "OPERADOR_ARITMETICO"]:
            id_hijo, etiqueta_hijo = nuevo_nodo(texto)
            g.node(id_hijo, etiqueta_hijo)
            g.edge(pila_nodos[-1], id_hijo)  # Conectar al nodo raíz
            pila_nodos.append(id_hijo)  # Agregar nuevo nodo a la pila

        elif tipo in ["NUMERO", "IDENTIFICADOR"]:
            id_hijo, etiqueta_hijo = nuevo_nodo(texto)
            g.node(id_hijo, etiqueta_hijo)
            g.edge(pila_nodos[-1], id_hijo)  # Conectar al nodo actual

        # Si encontramos un punto y coma, volvemos al nodo padre
        elif tipo == "PUNTUACION" and texto == ';':
            pila_nodos.pop()  # Volver al padre

    # Guardar el archivo en formato PNG y visualizarlo
    g.render('arbol_sintactico', format='png', view=True)
    messagebox.showinfo("Árbol Sintáctico", "Se generó el árbol sintáctico. Verifica el archivo 'arbol_sintactico.png'.")

# Función para analizar el código y mostrar los resultados
def analizar_codigo():
    codigo_fuente = text_area.get("1.0", tk.END)
    if not codigo_fuente.strip():
        messagebox.showwarning("Advertencia", "El código fuente está vacío.")
        return

    # Pedir al usuario el nombre del programa
    nombre_programa = "MiPrograma"  # Puedes reemplazarlo por una entrada de usuario si deseas

    tokens = analizador_lexico(codigo_fuente)

    # Mostrar los tokens en una ventana emergente
    resultado_tokens = "Tokens encontrados:\n" + "\n".join(f"Línea {token[0]}: {token[1]} -> {token[2]}" for token in tokens)
    messagebox.showinfo("Resultados de Análisis Léxico", resultado_tokens)

    # Construir y mostrar el árbol sintáctico
    construir_arbol_sintactico(tokens, nombre_programa)

# Crear la ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Analizador Léxico y Sintáctico")
ventana_principal.geometry("800x600")

# Añadir un área de texto para ingresar código fuente
label_input = tk.Label(ventana_principal, text="Escriba el código a analizar:", font=("Arial", 12))
label_input.pack(pady=5)

text_area = scrolledtext.ScrolledText(ventana_principal, width=80, height=25, font=("Courier", 10))
text_area.pack(padx=10, pady=10)

# Botón para analizar el código
btn_analizar = tk.Button(ventana_principal, text="Analizar Código", command=analizar_codigo, width=25, height=2, bg="#D2691E", fg="white", font=("Arial", 10))
btn_analizar.pack(pady=10)

# Ejecutar la ventana principal
ventana_principal.mainloop()
