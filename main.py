import streamlit as st
import io
import base64
from openai import AzureOpenAI
from PIL import Image
from diagnostic_rules import diagnostic_rules
from dotenv import load_dotenv
import os
 
# Carica le variabili d'ambiente
load_dotenv()
 
# Configura Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
 
 
SYSTEM_MESSAGE_CONTEXT = """
 
Analizza l'immagine e restituisci il contesto appropriato tra i seguenti:
 
- misure
- componenti
- impianti
- strutture
- elettrici
- meccanica
 
Fai attenzione a scegliere correttamente il contesto appropriato.
!!! IMPORTANTE !!! Scrivi esclusivamente la parola, non aggiungere descrizioni o altro che non serva. Le parole tra cui scegliere sono quelle citate.
"""
 
 
client = AzureOpenAI(
  azure_endpoint = AZURE_OPENAI_ENDPOINT,
  api_key=AZURE_OPENAI_API_KEY,  
  api_version=AZURE_OPENAI_API_VERSION
)
 
 
def analyze_image_with_chatgpt(image_bytes):
    """Invia un disegno tecnico a GPT-4V per estrarre informazioni strutturate."""
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = (
        f"Questa è un'immagine di un disegno tecnico generato con CAD. Analizza lo schema e restituisci le seguenti informazioni in un elenco strutturato '{context}':\n"
        + "\n".join(diagnostic_rules.get(context))
        + "\nAnalizza l'immagine in base a queste regole."
    )
 
    try:
        # Richiesta ad Azure OpenAI
        response = client.chat.completions.create(
            model = AZURE_OPENAI_DEPLOYMENT_NAME,
            messages =[
                {"role": "system", "content": "L'immagine fornita è un disegno CAD 2D dettagliato. Analizza attentamente ogni elemento e fornisci informazioni tecniche approfondite.Identifica tutti gli elementi principali nel disegno (pareti, stanze, tubazioni, macchinari, impianti, strutture portanti, ecc.).Fornisci le dimensioni di ogni componente, comprese lunghezze, altezze e spessori.Analizza le tubazioni: percorso, diametro, lunghezza e materiale.Identifica i materiali delle strutture visibili e analizza eventuali indicazioni tecniche.Se richiesto, concentrati su un elemento specifico e descrivilo nei minimi dettagli.Interpreta eventuali simboli e annotazioni tecniche.Segnala incongruenze o errori presenti nel disegno.Fornisci una descrizione funzionale del sistema o dell'oggetto rappresentato.Rispondi in modo dettagliato, come farebbe un ingegnere esperto. Se necessario, fai ipotesi basate sulle informazioni disponibili." },
                {"role": "user", "content":[
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                    },
                    {
                    "type": "text",
                    "text": "Analizza questa immagine"
                    }
                ]
                },
               
            ],
        )
        return response.choices[0].message.content
 
 
    except Exception as e:
        return f"Errore durante la richiesta: {str(e)}"
   
 
def analyze_context(image_bytes):
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
   
    try:
        # Richiesta ad Azure OpenAI
        response = client.chat.completions.create(
            model = AZURE_OPENAI_DEPLOYMENT_NAME,
            messages =[
                {"role": "system", "content": SYSTEM_MESSAGE_CONTEXT},
                {"role": "user", "content":[
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                    },
                    {
                    "type": "text",
                    "text": "Descrivi questa immagine"
                    }
                ]
                },
               
            ],
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore durante la richiesta: {str(e)}"
 
def analyze_image_with_request(context, image_bytes, user_input):
        """Invia il contesto e l'immagine a GPT per l'analisi."""
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        prompt = (
            f"Sono un modello AI addestrato per analizzare immagini. Ecco le regole diagnostiche per il contesto '{context}':\n"
            + "\n".join(diagnostic_rules.get(context))
            + "\nAnalizza l'immagine in base a queste regole."
            + "\nConsidera anche le richieste specifiche."
        )
 
        try:
            # Richiesta ad Azure OpenAI
            response = client.chat.completions.create(
                model = AZURE_OPENAI_DEPLOYMENT_NAME,
                messages =[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content":[
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                        },
                        {
                        "type": "text",
                        "text": f"Analizza questa immagine. Per favore segui attentamente le seguenti richieste specifiche:\n{user_input}"
                        }
                    ]
                    },
                   
                ],
            )
            return response.choices[0].message.content
 
 
        except Exception as e:
            return f"Errore durante la richiesta: {str(e)}"
           
 
 
# Frontend con Streamlit
st.markdown(
    "<h1 style='text-align: center; color: purple; font-size: 36px;'>🖼️ Diagnostica Immagini</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .custom-file-uploader {
        background-color: #F3E5F5; /* Lilla */
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        color: purple;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Testo personalizzato dentro una barra colorata
st.markdown('<div class="custom-file-uploader">📂 <b>Carica un\'immagine</b></div>', unsafe_allow_html=True)

# Caricamento immagine
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])  # Lascia stringa vuota per evitare doppio testo

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="✅ Immagine caricata con successo!", use_container_width=True)

  


    # Converti immagine in byte stream
    buffered = io.BytesIO()
    image.save(buffered, format=image.format)
    image_bytes = buffered.getvalue()
   
    # with st.spinner("Analisi in corso..."):
    #     context = analyze_context(image_bytes)
    #     diagnosis = analyze_image_with_chatgpt(context, image_bytes)
    #     st.success(diagnosis)
 
 
# Sezione per richieste testuali ad Azure OpenAI
# Personalizzazione del testo con Markdown
st.markdown("<h2 style='font-size: 28px; font-weight: bold; color: purple;'>Richieste specifiche (facoltativo)</h2>", unsafe_allow_html=True)

# Personalizzazione con barra colorata
st.markdown("""
    <div style='background-color: #F3E5F5; padding: 10px; color: purple; font-size: 18px; font-weight: bold; border-radius: 5px;'>
        Inserisci la tua richiesta di testo:
    </div>
""", unsafe_allow_html=True)

# Text area per l'input dell'utente
user_input = st.text_area("", height=150)


 
if st.button("Invio"):
    if uploaded_file and user_input == "":
        
        #image = Image.open(uploaded_file)
        #st.image(image, caption="Immagine caricata", use_container_width=True)
 
        # Converti immagine in byte stream
        # buffered = io.BytesIO()
        # image.save(buffered, format=image.format)
        image_bytes = buffered.getvalue()
   
        with st.spinner("Analisi in corso..."):
            context = analyze_context(image_bytes)
            diagnosis = analyze_image_with_chatgpt(context, image_bytes)
            st.success(diagnosis)        
    elif uploaded_file and user_input != "":
        image_bytes = buffered.getvalue()
        with st.spinner("Analisi in corso..."):
            context = analyze_context(image_bytes)
            diagnosis = analyze_image_with_request(context, image_bytes, user_input)
            st.success(diagnosis)   


 