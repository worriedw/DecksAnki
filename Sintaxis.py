import genanki
import html
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# Mantén el mismo deck y model ID
deck_id = 8547623847  
model_id = 7889056211  
name = "Sintaxis"

# Crear el modelo de la tarjeta con reverso
model = genanki.Model(
    model_id,
    'Modelo Doble Cara',
    fields=[
        {'name': 'Pregunta'},
        {'name': 'Respuesta'},
    ],
    templates=[
        {
            'name': 'Tarjeta 1 (Normal)',
            'qfmt': """
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh;">
            <div style="text-align:center; font-size:20px;">{{Pregunta}}</div>
            </div>
            """,
            'afmt': """
            <div style="text-align:center; font-size:16px; margin-top:10px;">
             {{Pregunta}}<p>
             </div>
           
            <hr id="answer">
            <div style="text-align: left; font-size: 16px; padding: 20px;">
            {{Respuesta}}
            </div>
            """
        },
        {
            'name': 'Tarjeta 2 (Reversa)',
            'qfmt': """
            <div style="text-align: center; font-size: 20px; padding: 20px;">
            {{Respuesta}}
            </div>
            """,
            'afmt': """
             <div style="text-align:center; font-size:16px; margin-top:10px;">
            {{Respuesta}}<p>
             </div>
            <hr id="answer">
            <div style="text-align: left; font-size: 16px; padding: 20px;">
            {{Pregunta}}
            </div>
            """
        },
    ],
    css='''
    .card {
        font-family: Arial, sans-serif;
        text-align: left;
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 10px;
    }
    
    hr#answer {
        border: 1px solid #444;
        margin: 15px 0;
    }
    
    .hljs-code {
        background: #1e1e1e;
        padding: 10px;
        border-radius: 6px;
        overflow-x: auto;
        font-family: "Fira Code", monospace;
        font-size: 15px;
    }
    
    .hljs-code pre {
        margin: 0;
    }
    
    /* Estilos específicos para el tema VS */
    .hljs-code .hljs-keyword { color: #569CD6; }
    .hljs-code .hljs-built_in { color: #4EC9B0; }
    .hljs-code .hljs-type { color: #4EC9B0; }
    .hljs-code .hljs-literal { color: #569CD6; }
    .hljs-code .hljs-number { color: #B5CEA8; }
    .hljs-code .hljs-string { color: #CE9178; }
    .hljs-code .hljs-comment { color: #6A9955; }
    .hljs-code .hljs-title { color: #DCDCAA; }
    .hljs-code .hljs-params { color: #9CDCFE; }
    .hljs-code .hljs-function { color: #DCDCAA; }
    .hljs-code .hljs-class { color: #4EC9B0; }
    
    b {
        color: #ffffff;
        font-weight: bold;
    }
    '''
)

# Crear el deck reutilizando el mismo deck_id
deck = genanki.Deck(deck_id, name)

def aplicar_highlighting(texto):
    """
    Encuentra bloques de código en el texto y aplica highlighting de sintaxis
    """
    # Patrón para encontrar bloques de código con lenguaje especificado
    pattern = r'<pre><code class="language-([^"]+)">(.*?)</code></pre>'
    
    def highlight_match(match):
        lang = match.group(1)
        code_content = match.group(2)
        
        try:
            # Limpiar el código (eliminar entidades HTML)
            clean_code = html.unescape(code_content)
            clean_code = clean_code.replace('<br>', '\n')
            
            # Obtener el lexer y formateador
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = HtmlFormatter(
                style='vs',
                cssclass='hljs-code',
                noclasses=False,
                prestyles='margin: 0; padding: 0;'
            )
            
            # Aplicar highlighting
            highlighted_code = highlight(clean_code, lexer, formatter)
            return highlighted_code
            
        except Exception as e:
            print(f"Error aplicando highlighting para lenguaje {lang}: {e}")
            # Si falla, devolver el código original con escape HTML
            return f'<pre><code class="language-{lang}">{html.escape(code_content)}</code></pre>'
    
    # Aplicar highlighting a todos los bloques de código encontrados
    return re.sub(pattern, highlight_match, texto, flags=re.DOTALL)

def extraer_cartas(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    pattern = r'\d+\.\s\*\*(.*?)\*\*\s*(.*?)(?=\n\d+\.\s\*\*|\Z)'
    matches = re.findall(pattern, contenido, re.DOTALL)
    
    cartas_limpias = []
    for pregunta, respuesta in matches:
        # Convertir **texto** a <b>texto</b>
        pregunta = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', pregunta.strip())
        respuesta = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', respuesta.strip())

        # Eliminar líneas con solo "---"
        respuesta = re.sub(r'\n\s*---\s*\n?', '', respuesta)

        cartas_limpias.append((pregunta, respuesta))

    return cartas_limpias

def agregar_carta(pregunta, respuesta):
    # Aplicar highlighting a la respuesta
    respuesta_con_highlight = aplicar_highlighting(respuesta)
    
    carta = genanki.Note(
        model=model,
        fields=[
            html.escape(pregunta).replace('\n', '<br>'),
            respuesta_con_highlight
        ]
    )
    deck.add_note(carta)

def main():
    # Extraer las cartas del archivo
    cartas = extraer_cartas(name + '.txt')
    
    # Añadir cada carta extraída al deck
    for i, (pregunta, respuesta) in enumerate(cartas):
        print(f"Procesando carta {i+1}/{len(cartas)}")
        agregar_carta(pregunta, respuesta)
    
    # Guardar el deck
    paquete = genanki.Package(deck)
    paquete.write_to_file(name + '.apkg')
    print(f"Deck guardado como '{name}.apkg' con {len(cartas)} cartas")

if __name__ == "__main__":
    main()