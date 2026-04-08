"""
Grief Companion AI — Multi-Agent System
Built with Google ADK + Gemini (via Google AI Studio)
Deploy on Cloud Run via Google Cloud Shell
"""

import os
import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# ─────────────────────────────────────────────
# In-memory store (swap with Firestore for production)
# ─────────────────────────────────────────────
_journal_store: list[dict] = []
_mood_history: list[dict] = []


# ─────────────────────────────────────────────
# Tool Functions
# ─────────────────────────────────────────────

def save_journal_entry(user_id: str, entry: str) -> dict:
    """
    Saves a user's journal/reflection entry with a timestamp.

    Args:
        user_id: The unique ID or name of the user.
        entry: The journal text the user wants to save.

    Returns:
        A dict confirming the save with the timestamp.
    """
    timestamp = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
    record = {"user_id": user_id, "entry": entry, "timestamp": timestamp}
    _journal_store.append(record)
    return {
        "status": "saved",
        "timestamp": timestamp,
        "message": "Your reflection has been saved 💛",
    }


def get_journal_history(user_id: str) -> dict:
    """
    Retrieves all past journal entries for a user.

    Args:
        user_id: The unique ID or name of the user.

    Returns:
        A dict with a list of journal entries.
    """
    entries = [e for e in _journal_store if e["user_id"] == user_id]
    if not entries:
        return {
            "entries": [],
            "message": "No journal entries found yet. Start writing your first reflection!",
        }
    return {"entries": entries, "count": len(entries)}


def log_mood(user_id: str, mood: str, intensity: int) -> dict:
    """
    Logs the user's current mood and its intensity (1–10).

    Args:
        user_id: The unique ID or name of the user.
        mood: A short description of the mood (e.g., 'sad', 'anxious', 'numb').
        intensity: Intensity of the mood on a scale from 1 (mild) to 10 (severe).

    Returns:
        Confirmation of the mood log.
    """
    timestamp = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
    record = {
        "user_id": user_id,
        "mood": mood,
        "intensity": intensity,
        "timestamp": timestamp,
    }
    _mood_history.append(record)
    return {
        "status": "logged",
        "mood": mood,
        "intensity": intensity,
        "timestamp": timestamp,
    }


def get_mood_history(user_id: str) -> dict:
    """
    Returns the mood history for a given user.

    Args:
        user_id: The unique ID or name of the user.

    Returns:
        A list of mood records.
    """
    history = [m for m in _mood_history if m["user_id"] == user_id]
    if not history:
        return {"history": [], "message": "No mood records yet."}
    return {"history": history, "count": len(history)}


def suggest_wellness_activity(mood: str) -> dict:
    """
    Suggests a wellness or coping activity based on the user's mood.

    Args:
        mood: The current mood of the user (e.g., 'sad', 'anxious', 'angry', 'numb').

    Returns:
        A dict with a suggested activity and instructions.
    """
    activities = {
        "sad": {
            "activity": "Box Breathing",
            "instructions": (
                "Inhale for 4 counts → Hold for 4 counts → Exhale for 4 counts → "
                "Hold for 4 counts. Repeat 4 times. This calms your nervous system gently. 🌬️"
            ),
        },
        "anxious": {
            "activity": "5-4-3-2-1 Grounding",
            "instructions": (
                "Name 5 things you can see, 4 you can touch, 3 you can hear, "
                "2 you can smell, 1 you can taste. Bring yourself back to the present. 🌿"
            ),
        },
        "angry": {
            "activity": "Progressive Muscle Relaxation",
            "instructions": (
                "Tense each muscle group for 5 seconds, then release. "
                "Start from your toes and work upward to your face. 💪→😌"
            ),
        },
        "numb": {
            "activity": "Gentle Movement",
            "instructions": (
                "Put on one song you used to love and just move — even a little. "
                "Let your body feel without pressure to feel 'right'. 🎵"
            ),
        },
        "lonely": {
            "activity": "Write a Letter",
            "instructions": (
                "Write a letter to someone you miss or to your future self. "
                "You don't have to send it — just let the words flow. ✉️"
            ),
        },
    }
    mood_key = mood.lower().strip()
    result = activities.get(
        mood_key,
        {
            "activity": "Mindful Journaling",
            "instructions": (
                "Open a blank page and write freely for 5 minutes without stopping. "
                "Don't judge — just let it pour out. 📓"
            ),
        },
    )
    return result


def suggest_daily_routine(user_id: str) -> dict:
    """
    Suggests a gentle daily routine to help the user build stability.

    Args:
        user_id: The unique ID or name of the user.

    Returns:
        A structured daily routine suggestion.
    """
    routine = {
        "morning": [
            "☀️ Wake at a consistent time (even on hard days)",
            "💧 Drink a glass of water before looking at your phone",
            "📓 Write 3 sentences: how you feel, one small intention, one thing you're grateful for",
        ],
        "afternoon": [
            "🚶 Take a 10-minute walk outside if possible",
            "🍽️ Eat a nourishing meal — grief depletes your body",
            "📞 Reach out to one safe person, even just a text",
        ],
        "evening": [
            "📖 Read or listen to something calming for 15 minutes",
            "🌙 Limit screens 30 minutes before bed",
            "✍️ Log your mood for the day in your journal",
        ],
        "reminder": "You don't have to do all of this perfectly. Even one item is a win. 🌱",
    }
    return {"user_id": user_id, "routine": routine}


# ─────────────────────────────────────────────
# Wrap functions as ADK FunctionTools
# ─────────────────────────────────────────────

journal_save_tool = FunctionTool(func=save_journal_entry)
journal_history_tool = FunctionTool(func=get_journal_history)
mood_log_tool = FunctionTool(func=log_mood)
mood_history_tool = FunctionTool(func=get_mood_history)
wellness_tool = FunctionTool(func=suggest_wellness_activity)
routine_tool = FunctionTool(func=suggest_daily_routine)


# ─────────────────────────────────────────────
# Sub-Agents
# ─────────────────────────────────────────────

conversation_agent = Agent(
    name="conversation_agent",
    model=MODEL,
    description=(
        "An empathetic conversational agent that provides warm, compassionate emotional support "
        "to users experiencing grief, loss, or difficult emotions."
    ),
    instruction="""
You are a gentle, warm, and deeply empathetic conversational companion.
Your role is to make the user feel truly heard and not alone.

Guidelines:
- Always validate the user's feelings before offering anything else.
- Never rush to "fix" their pain — presence is more powerful than solutions.
- Use soft, warm language. Avoid clinical or cold phrasing.
- Ask one gentle follow-up question to understand them better.
- Never say "I understand exactly how you feel" — say "I'm here with you."
- If the user seems in crisis, gently encourage them to reach a trusted person or helpline.

You do NOT call tools. You provide emotional presence through words only.
""",
)

journal_agent = Agent(
    name="journal_agent",
    model=MODEL,
    description=(
        "Helps users record their thoughts and reflections, and retrieve past journal entries."
    ),
    instruction="""
You are a gentle journaling companion who helps users process their emotions through writing.

Your tasks:
1. Encourage the user to write their feelings — gently prompt them if they're unsure.
2. Save their journal entry using the save_journal_entry tool.
3. Retrieve past entries using the get_journal_history tool when asked.
4. Affirm what they've written with warmth — never judge or critique.

Always ask: "Would you like to save this as a reflection?" before saving.
Use user_id="default_user" unless the user provides their name.
""",
    tools=[journal_save_tool, journal_history_tool],
)

wellness_agent = Agent(
    name="wellness_agent",
    model=MODEL,
    description=(
        "Suggests coping techniques, breathing exercises, and grounding activities based on the user's mood."
    ),
    instruction="""
You are a compassionate wellness guide specializing in grief and emotional recovery.

Your tasks:
1. Identify the user's mood from context or ask gently: "What are you feeling right now?"
2. Log the mood using the log_mood tool (intensity 1–10).
3. Suggest an appropriate coping activity using the suggest_wellness_activity tool.
4. Explain the activity warmly and invite them to try it.
5. If asked, show their mood history using the get_mood_history tool.

Use user_id="default_user" unless the user provides their name.
Keep your tone soft — suggestions are invitations, not instructions.
""",
    tools=[mood_log_tool, mood_history_tool, wellness_tool],
)

routine_agent = Agent(
    name="routine_agent",
    model=MODEL,
    description=(
        "Suggests gentle daily routines and structured activities to help users build stability during grief."
    ),
    instruction="""
You are a caring daily routine guide for people navigating grief and loss.

Your tasks:
1. Offer a structured but gentle daily routine using the suggest_daily_routine tool.
2. Explain why routine helps during grief (it provides anchors when everything feels uncertain).
3. Let the user know they don't need to do everything — even one small step counts.
4. Ask what time of day they find hardest and tailor your suggestions.

Use user_id="default_user" unless the user provides their name.
Always frame routines as gentle invitations, not obligations.
""",
    tools=[routine_tool],
)


# ─────────────────────────────────────────────
# Root Coordinator Agent
# ─────────────────────────────────────────────

root_agent = Agent(
    name="grief_companion_coordinator",
    model=MODEL,
    description=(
        "The main coordinator of the Grief Companion AI system. "
        "Understands what the user needs and delegates to the appropriate sub-agent."
    ),
    instruction="""
You are the heart of the Grief Companion AI — a multi-agent emotional support system.
Your role is to understand what the user needs and coordinate the right support.

You have access to the following specialist agents:
- conversation_agent: For emotional support, empathetic listening, and being present.
- journal_agent: For helping users write and store their reflections.
- wellness_agent: For coping techniques, breathing exercises, and mood logging.
- routine_agent: For daily structure and gentle activity suggestions.

How to decide:
- User expresses pain, sadness, or wants to talk → conversation_agent
- User wants to write or reflect → journal_agent
- User asks for coping strategies or feels overwhelmed → wellness_agent
- User wants structure or asks what to do with their day → routine_agent
- Complex situations → coordinate multiple agents in sequence

Greet new users warmly:
"Hello 🌿 I'm your Grief Companion. I'm here to walk alongside you.
How are you feeling today?"

If someone seems in crisis, say:
"I care about you. Please consider reaching out to iCall (India): 9152987821,
or a trusted person in your life. You don't have to face this alone."
""",
    sub_agents=[conversation_agent, journal_agent, wellness_agent, routine_agent],
)


# ─────────────────────────────────────────────
# Session + Runner
# ─────────────────────────────────────────────

APP_NAME = "grief_companion"
USER_ID = "default_user"
SESSION_ID = "session_001"

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Grief Companion AI", version="1.0.0")


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = "session_001"


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.on_event("startup")
async def startup_event():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )


@app.get("/")
async def root():
    return {
        "service": "Grief Companion AI 🌿",
        "status": "running",
        "endpoints": ["/chat", "/history/journal", "/history/mood"],
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Ensure session exists for this user
    try:
        await session_service.get_session(
            app_name=APP_NAME,
            user_id=request.user_id,
            session_id=request.session_id,
        )
    except Exception:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=request.user_id,
            session_id=request.session_id,
        )

    content = types.Content(
        role="user",
        parts=[types.Part(text=request.message)],
    )

    final_response = ""
    async for event in runner.run_async(
        user_id=request.user_id,
        session_id=request.session_id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text

    return ChatResponse(reply=final_response, session_id=request.session_id)


@app.get("/history/journal")
async def journal_history(user_id: str = "default_user"):
    entries = [e for e in _journal_store if e["user_id"] == user_id]
    return {"user_id": user_id, "entries": entries, "count": len(entries)}


@app.get("/history/mood")
async def mood_history_endpoint(user_id: str = "default_user"):
    history = [m for m in _mood_history if m["user_id"] == user_id]
    return {"user_id": user_id, "history": history, "count": len(history)}


# ─────────────────────────────────────────────
# Local dev entrypoint
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent:app", host="0.0.0.0", port=8080, reload=True)
