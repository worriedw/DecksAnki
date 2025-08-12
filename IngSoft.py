import genanki
import re

# Mantén el mismo deck y model ID
deck_id = 8545543847  
model_id = 7897556211  
name = "IngSoft"

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
            'afmt': '''
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh;">
            <div style="text-align:left; font-size:16px; margin-top:10px;">
            {{Pregunta}}<p><hr>
              <ul>
                {{#Respuesta}}
                  {{Respuesta}}
                {{/Respuesta}}
              </ul>
            </div>
            </div>
            ''',
        },
        {
            'name': 'Tarjeta 2 (Reversa)',
            'qfmt': """
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh;">
            <div style="text-align:center; font-size:20px;">{{Respuesta}}</div>
            </div>
            """,
            'afmt': '''
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh;">
            <div style="text-align:left; font-size:16px; margin-top:10px;">
            {{Respuesta}}<p><hr>
              <ul>
                {{#Pregunta}}
                  {{Pregunta}}
                {{/Pregunta}}
              </ul>
            </div>
            </div>
            ''',
        },
    ]
)

# Crear el deck reutilizando el mismo deck_id
deck = genanki.Deck(deck_id, name)

# Función para extraer preguntas y respuestas del archivo de texto
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

# Función para agregar cartas al deck
def agregar_carta(pregunta, respuesta):
    carta = genanki.Note(
        model=model,
        fields=[pregunta, respuesta.replace('\n', '<br>')]  # Reemplazar saltos de línea por <br> para HTML
    )
    deck.add_note(carta)

# Extraer las cartas del archivo
cartas = extraer_cartas(name + '.txt')

# Añadir cada carta extraída al deck
for pregunta, respuesta in cartas:
    agregar_carta(pregunta, respuesta)

# Guardar las nuevas cartas en un archivo .apkg
def guardar_deck(nombre_archivo):
    paquete = genanki.Package(deck)
    paquete.write_to_file(nombre_archivo)

# Guardar el deck con las nuevas cartas
guardar_deck(name + '.apkg')
