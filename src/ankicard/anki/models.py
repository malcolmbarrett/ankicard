import genanki

# Define the Anki Model (Note Type) to match "Immersion Kit" structure
IMMERSION_KIT_MODEL = genanki.Model(
    1239585222,  # Official Immersion Kit model ID (must match for card compatibility)
    "Immersion Kit Sentence",
    fields=[
        {"name": "Expression"},
        {"name": "English"},
        {"name": "Reading"},
        {"name": "Screenshot"},
        {"name": "Audio Sentence"},
        {"name": "ID"},
    ],
    templates=[
        {
            "name": "Sentence",
            "qfmt": '<div style="font-size: 30px;">{{Expression}}</div><br>{{Screenshot}}',
            "afmt": '{{FrontSide}}<hr id="answer"><div style="font-size: 20px;">{{English}}</div><br><div style="font-size: 20px;">{{furigana:Reading}}</div><br>{{Audio Sentence}}',
        },
    ],
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } img { max-width: 400px; }",
)
