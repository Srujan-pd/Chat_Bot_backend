<<<<<<< HEAD
from google.cloud import speech, texttospeech
import google.generativeai as genai
import uuid, os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.0-flash")

speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

chat_history = []

def voice_to_text(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        audio = speech.RecognitionAudio(content=f.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US"
    )

    response = speech_client.recognize(config=config, audio=audio)
    if not response.results:
        return "Sorry, I could not understand."
    return response.results[0].alternatives[0].transcript

def get_ai_response(text: str) -> str:
    chat_history.append({"role": "user", "parts": [text]})
    response = model.generate_content(chat_history)
    chat_history.append({"role": "model", "parts": [response.text]})
    return response.text

def text_to_voice(text: str) -> str:
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    os.makedirs("/tmp/audio", exist_ok=True)
    filename = f"/tmp/audio/{uuid.uuid4()}.mp3"

    with open(filename, "wb") as out:
        out.write(response.audio_content)

    return filename
=======
import os, uuid, base64
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Chat
import google.genai as genai
from google.genai import types
from google.cloud import texttospeech

router = APIRouter(prefix="/voice")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
tts_client = None

def get_tts_client():
    global tts_client
    if tts_client is None:
        try:
            tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS client initialization failed: {str(e)}")

@router.post("/")
async def voice_chat(
    file: UploadFile = File(...),
    user_id: str = Form("default_user"),
    db: Session = Depends(get_db)
):
    audio_bytes = await file.read()
    
    # Check if audio file is too small (likely silence)
    if len(audio_bytes) < 1000:  # Less than 1KB is likely just silence
        return {
            "user_said": "",
            "message": "No speech detected. Please speak clearly.",
            "audio": None,
            "status": "no_speech"
        }
    
    try:
        # Step 1: Use Gemini to transcribe and detect if there's actual speech
        model_res = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=file.content_type)
            ]
        )

        full_text = model_res.text.strip()
        
        # Step 2: Check for silence detection
        if "SILENCE_DETECTED" in full_text or full_text.upper() == "SILENCE_DETECTED":
            return {
                "user_said": "",
                "message": "I couldn't hear you clearly. Please try again.",
                "audio": None,
                "status": "no_speech"
            }
        
        # Step 3: Parse the response for actual speech
        if "USER_SAID:" in full_text and "AI_RESPONSE:" in full_text:
            user_text = full_text.split("USER_SAID:")[1].split("AI_RESPONSE:")[0].strip()
            ai_text = full_text.split("AI_RESPONSE:")[1].strip()
            
            # Additional check: if transcription is too short or contains markers of uncertainty
            if len(user_text) < 3 or user_text.upper() in ["EMPTY", "UNCLEAR", "NOISE", "..."]:
                return {
                    "user_said": "",
                    "message": "I couldn't understand what you said. Please speak clearly.",
                    "audio": None,
                    "status": "unclear_speech"
                }
        else:
            # If format is wrong, treat as unclear
            return {
                "user_said": "",
                "message": "I couldn't process your audio. Please try again.",
                "audio": None,
                "status": "processing_error"
            }

        # Step 4: Generate TTS only for valid responses
        synthesis_input = texttospeech.SynthesisInput(text=ai_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", 
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        tts_client_instance = get_tts_client()
        tts_res = tts_client_instance.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )
        audio_base64 = base64.b64encode(tts_res.audio_content).decode('utf-8')

        # Step 5: Save to DB only for successful conversations
        db.add(Chat(
            user_id=user_id, 
            session_id="voice_session", 
            question=user_text, 
            answer=ai_text
        ))
        db.commit()

        return {
            "user_said": user_text,
            "message": ai_text,
            "audio": audio_base64,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")


>>>>>>> b72a9f6 (backend)
