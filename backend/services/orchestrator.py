import json
import re
from typing import AsyncGenerator, Dict, Any

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from services.api_key_pool import (
    get_next_key,
    mark_key_quota_exceeded,
)
from services.agents import symptom_agent
from services.history_store import save_history
from services.memory import get_shared_memory, reset_memory
from config.settings import GROQ_MODEL_NAME, GROQ_REQUEST_TIMEOUT_SECONDS


# ---------------------------------------------------------------------
# Synthesizer / Wellness Agent LLM helper
# ---------------------------------------------------------------------
def _make_synth_llm_with_key():
    """Create the synthesizer LLM using the next available Groq API key."""
    key = get_next_key()
    llm = ChatOpenAI(
        model=GROQ_MODEL_NAME,
        api_key=key,
        base_url="https://api.groq.com/openai/v1",
        temperature=0.0,
        max_tokens=450,
        timeout=GROQ_REQUEST_TIMEOUT_SECONDS,
    )
    return llm, key


def _build_markdown_table(output: dict) -> str:
    """Build a markdown-style block summarizing each agent."""
    parts: list[str] = []

    def add_block(title: str, text: str | None):
        if not text:
            return
        if parts:
            parts.append("")
        parts.append(f"**{title}**")
        parts.append(text.strip())

    add_block("Symptom & Triage Agent", output.get("symptom_analysis", ""))
    add_block("Wellness Guidance (Diet, Fitness & Lifestyle)", output.get("synthesized_guidance", ""))

    return "\n".join(parts)


# ---------------------------------------------------------------------
# Main orchestration (non-streaming, used by /health-assist)
# ---------------------------------------------------------------------
async def orchestrate(
    symptoms: str, medical_report: str, user_id: str
) -> Dict[str, Any]:
    """Run the streamlined 2-agent pipeline and return structured JSON."""

    reset_memory()
    agent_flow = []

    # 1. Symptom & Triage Agent (LLM Call 1)
    symptom_result = await symptom_agent(symptoms)
    agent_flow.append(
        {
            "agent": "Symptom & Triage Agent",
            "output": symptom_result,
        }
    )

    # 2. Wellness Guidance Agent (LLM Call 2)
    synth_llm, synth_key = _make_synth_llm_with_key()

    synth_messages = [
        SystemMessage(
            content=(
                "You are an expert health and wellness assistant.\n"
                "Review the user symptoms, medical report, and clinical triage notes below.\n\n"
                "Write a concise, reassuring, non-diagnostic wellness plan in markdown with these sections:\n"
                "1. Overview - Brief summary of the situation.\n"
                "2. When to See a Doctor - 2-3 key red-flag symptoms.\n"
                "3. Lifestyle & Rest - 2-3 gentle daily habits, sleep, or stress tips.\n"
                "4. Diet & Hydration - 2-3 simple, safe food and fluid guidance points.\n"
                "5. Movement & Activity - 2 safe, low-intensity options with a STOP warning if pain occurs.\n"
                "6. Final Note - 1 sentence reminding that this does not replace a doctor's advice.\n\n"
                "Tone: calm, reassuring, strictly non-diagnostic. Never prescribe medications.\n\n"
                "Return ONLY valid JSON with keys:\n"
                "  - synthesized_guidance: the markdown text described above\n"
                "  - recommendations: array of 3-4 short recommendation strings\n"
                "Do not wrap JSON in code fences or add extra text."
            )
        ),
        HumanMessage(
            content=(
                f"User Symptoms: {symptoms}\n"
                f"Medical Report: {medical_report or 'None'}\n"
                f"Symptom Analysis: {symptom_result}\n\n"
                "Generate the JSON response now."
            )
        ),
    ]

    try:
        final_answer = await synth_llm.ainvoke(synth_messages)
    except Exception:
        mark_key_quota_exceeded(synth_key)
        synth_llm, synth_key = _make_synth_llm_with_key()
        final_answer = await synth_llm.ainvoke(synth_messages)

    raw = final_answer.content.strip()

    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"synthesized_guidance": raw, "recommendations": []}

    guidance = data.get("synthesized_guidance", "")
    recommendations = data.get("recommendations", [])

    agent_flow.append(
        {
            "agent": "Wellness & Lifestyle Agent",
            "output": guidance[:200] + "...",
        }
    )

    output = {
        "user_id": user_id,
        "query": symptoms,
        "symptom_analysis": symptom_result,
        "lifestyle": "Rest, hydration, and stress reduction outlined in the wellness plan.",
        "diet": "Balanced hydration and nutrition guidance included in the plan.",
        "fitness": "Low-intensity safe movement included in the plan.",
        "synthesized_guidance": guidance,
        "recommendations": recommendations,
        "agent_flow": agent_flow,
    }

    output["table_markdown"] = _build_markdown_table(output)
    save_history(user_id, output)
    return output


# ---------------------------------------------------------------------
# Streaming helper - agent communication for UI (used by /chat_stream)
# ---------------------------------------------------------------------
async def stream_agent_updates(symptoms: str, medical_report: str) -> AsyncGenerator[Dict[str, str], None]:
    """
    Stream agent collaboration thought events and answer tokens for the UI.
    Streamlined 2-agent design:
    1. Symptom & Triage Agent -> assesses urgency & clinical severity.
    2. Wellness & Lifestyle Agent -> streams full personalized plan (Diet + Fitness + Routine).
    """

    reset_memory()

    # Step 1: Notify UI of incoming query
    yield {
        "type": "thought",
        "content": "User → Orchestrator: new wellness query received.",
    }
    yield {
        "type": "thought",
        "content": "Orchestrator → SymptomAgent: analyzing primary symptoms and severity.",
    }

    # Step 2: Run Symptom & Triage Agent (LLM Call 1)
    symptom_result = await symptom_agent(symptoms)

    yield {
        "type": "thought",
        "content": (
            f"SymptomAgent → Orchestrator: clinical profile ready ({symptom_result[:130]}...)"
        ),
    }

    yield {
        "type": "thought",
        "content": "SymptomAgent → WellnessAgent: passing symptom profile for diet, fitness & lifestyle planning.",
    }

    yield {
        "type": "thought",
        "content": "WellnessAgent: formulating holistic nutrition, safe movement, and daily routine plan...",
    }

    # Step 3: Stream Wellness Plan tokens (LLM Call 2)
    synth_llm, synth_key = _make_synth_llm_with_key()

    synth_messages = [
        SystemMessage(
            content=(
                "You are an expert wellness and lifestyle coach.\n"
                "Review the user symptoms, optional medical report, and clinical triage analysis.\n\n"
                "Produce a structured wellness plan in clean markdown with these sections:\n"
                "## 1. Overview\n"
                "Brief 2-3 sentence overview of the concern.\n\n"
                "## 2. When to See a Doctor\n"
                "2-3 clear bullet points on red-flag symptoms.\n\n"
                "## 3. Lifestyle & Rest\n"
                "3 simple daily tips (sleep hygiene, stress management, hydration).\n\n"
                "## 4. Diet & Nutrition\n"
                "3 gentle food and hydration recommendations (foods to favor/avoid).\n\n"
                "## 5. Movement & Physical Activity\n"
                "2 light, safe activity ideas with an explicit warning to stop if discomfort occurs.\n\n"
                "## 6. Medical Disclaimer\n"
                "Reminder that this is non-diagnostic wellness guidance and does not replace professional medical care.\n\n"
                "Tone: calm, reassuring, strictly non-diagnostic. Never prescribe medications."
            )
        ),
        HumanMessage(
            content=(
                f"User Symptoms: {symptoms}\n"
                f"Medical Report: {medical_report or 'None'}\n"
                f"Symptom Triage Analysis: {symptom_result}\n\n"
                "Generate the complete markdown wellness plan now."
            )
        ),
    ]

    try:
        async for chunk in synth_llm.astream(synth_messages):
            text = getattr(chunk, "content", "") or ""
            if text:
                yield {"type": "answer", "content": text}
    except Exception:
        mark_key_quota_exceeded(synth_key)
        synth_llm, synth_key = _make_synth_llm_with_key()
        async for chunk in synth_llm.astream(synth_messages):
            text = getattr(chunk, "content", "") or ""
            if text:
                yield {"type": "answer", "content": text}

    yield {
        "type": "thought",
        "content": "WellnessAgent → Orchestrator → User: personalized wellness plan delivered successfully.",
    }
