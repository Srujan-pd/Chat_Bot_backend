<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Chat
import os
import google.generativeai as genai
from pydantic import BaseModel

router = APIRouter(prefix="/chat")

=======
from datetime import datetime, timedelta
import os, uuid
from fastapi import APIRouter, Form, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Chat
from google import genai
from datetime import datetime, timedelta

router = APIRouter(prefix="/chat")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

>>>>>>> b72a9f6 (backend)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

<<<<<<< HEAD
# Get API key from environment
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    print("✅ Gemini API initialized")
else:
    model = None
    print("❌ GEMINI_API_KEY not found")

# Dictionary to store chat histories per user
chat_histories = {}

class ChatRequest(BaseModel):
    message: str
    user_id: int

# Inside chat.py
@router.post("/")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    if not model:
        raise HTTPException(status_code=500, detail="AI Configuration Error")
    
    # FIX: Ensure user_id is assigned from the request object immediately
    user_id = req.user_id 
    user_message = req.message

    try:
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        chat_session = model.start_chat(history=chat_histories[user_id])
        response = chat_session.send_message(user_message)
        bot_reply = response.text

        chat_histories[user_id] = chat_session.history

        # Save to database - Ensure 'owner_id' matches your models.py
        new_chat = Chat(user_id=user_id, question=user_message, answer=bot_reply)
        db.add(new_chat)
        db.commit()

        return {"reply": bot_reply}
        
    except Exception as e:
        db.rollback()
        # This will now print the specific error to your Cloud Run logs
        print(f"Chat Error: {str(e)}") 
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")

@router.get("/history/{user_id}")
def history(user_id: int, db: Session = Depends(get_db)):
    try:
        rows = db.query(Chat).filter(Chat.user_id == user_id).all()
        return {"history": [{"question": r.question, "answer": r.answer} for r in rows]}
    except Exception as e:
        print(f"Database Error: {e}")
        return {"history": []}
=======
# 🔹 SESSION HANDLER
def get_or_create_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age = 60 * 60 * 24 * 7,    # 7days
            samesite="lax"
        )
    return session_id

# 🔹 LOAD CHAT HISTORY FOR CONTEXT
def build_prompt(db, session_id, user_message, context_limit=50):
    """
    Build prompt with recent chat history for context.
    context_limit: Number of recent exchanges to include (default 10)
    """
    chats = (
        db.query(Chat)
        .filter(Chat.session_id == session_id)
        .order_by(Chat.created_at.desc())
        .limit(context_limit)
        .all()
    )
    
    # Reverse to get chronological order
    chats = list(reversed(chats))

    if chats:
        prompt = "You are a helpful support AI assistant. Previous conversation:\n\n"
        for chat in chats:
            prompt += f"User: {chat.question}\n"
            prompt += f"Assistant: {chat.answer}\n\n"
        prompt += f"User: {user_message}\nAssistant:"
    else:
        prompt = f"You are a helpful support AI assistant.\n\nUser: {user_message}\nAssistant:"

    return prompt

@router.post("/")
async def chat_main(
    request: Request,
    response: Response,
    text: str = Form(...),
    user_id: str = Form("default_user"),
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint - accepts form data
    """
    try:
        session_id = get_or_create_session(request, response)

        # Build prompt with chat history
        prompt = build_prompt(db, session_id, text)

        # Get AI response
        gemini_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        ai_text = gemini_response.text

        # Save to database
        new_chat = Chat(
            session_id=session_id,
            user_id=user_id,
            question=text,
            answer=ai_text
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return {
            "message": ai_text,
            "session_id": session_id,
            "status": "success"
        }

    except Exception as e:
        print("❌ Gemini Error:", str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.get("/history")
async def get_chat_history(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get chat history for current session
    Returns only the last {limit} messages (default: 10)
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        return []
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Get last N messages
    chats = (
        db.query(Chat)
        .filter(
            Chat.session_id == session_id,
            Chat.created_at >= seven_days_ago
        )
        .order_by(Chat.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Reverse to get chronological order (oldest to newest)
    return chats
>>>>>>> b72a9f6 (backend)
