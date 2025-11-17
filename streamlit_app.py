############################
# streamlit_app.py (FINAL FULL VERSION)
############################

import streamlit as st
import asyncio
import json

from google.adk.runners import InMemoryRunner
from agents.orchestrator import OrchestratorAgent


#############################################
# Async Helper
#############################################
def run_sync(awaitable):
    """Run async ADK coroutine inside Streamlit safely."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        new_loop = asyncio.new_event_loop()
        return new_loop.run_until_complete(awaitable)
    else:
        return loop.run_until_complete(awaitable)


#############################################
# Strip Markdown Fences (```)
#############################################
def strip_markdown_fences(txt: str) -> str:
    if not isinstance(txt, str):
        return txt

    s = txt.strip()

    if s.startswith("```") and s.endswith("```"):
        s = s.strip("`")
        if s.startswith("json"):
            s = s[4:].strip()

    return s


#############################################
# Remove ADK-reserved fields (tool, type)
#############################################
def sanitize_adk_json(txt: str):
    """Before feeding JSON to another agent, remove ADK-reserved fields."""
    cleaned = strip_markdown_fences(txt)

    try:
        data = json.loads(cleaned)

        if isinstance(data, dict):
            data.pop("tool", None)
            data.pop("type", None)
            return data

        return data

    except Exception:
        return txt


#############################################
# Pretty Planning Renderer
#############################################
def json_plan_to_markdown(parsed):
    md = []

    goal = parsed.get("goal", "")
    duration = parsed.get("duration", "")

    if goal:
        md.append(f"### 🎯 **Goal:** {goal}")
    if duration:
        md.append(f"### ⏳ **Duration:** {duration}")

    md.append("---")

    for week in parsed.get("plan", []):
        wk = week.get("week", "")
        focus = week.get("focus", "")
        tasks = week.get("tasks", [])

        md.append(f"## 🗓️ {wk} — **{focus}**")
        md.append("")

        if tasks:
            md.append("### ✓ Tasks:")
            for t in tasks:
                md.append(f"- {t}")

        md.append("")

    if "notes" in parsed:
        md.append("---")
        md.append(f"### 📝 Notes:\n{parsed['notes']}")

    return "\n".join(md)


#############################################
# Pretty Agenda Renderer
#############################################
def json_agenda_to_markdown(parsed):
    md = []

    md.append(f"### 📅 **Period:** {parsed.get('period', 'N/A')}")
    md.append(f"### 🌍 **Timezone:** {parsed.get('timezone', 'unknown')}")
    md.append("---")

    for day in parsed.get("days", []):
        week = day.get("week", "")
        day_name = day.get("day", "")
        focus = day.get("focus", "")

        md.append(f"## 🗓️ {week} — **{day_name}**")
        md.append(f"### 🎯 Focus: {focus}")
        md.append("")

        md.append("### 🧩 Blocks:")
        for b in day.get("blocks", []):
            md.append(f"- **{b['time']}** — {b['activity']} ({b['category']})")
        md.append("")

    if "notes" in parsed:
        md.append("---")
        md.append(f"### 📝 Notes:\n{parsed['notes']}")

    return "\n".join(md)


#############################################
# Pretty Guardrails Renderer (NEW)
#############################################
def json_guardrail_to_markdown(parsed):
    md = []
    category = parsed.get("category", "unknown")
    status = parsed.get("status", "")
    message = parsed.get("message", "")

    md.append(f"### 🚫 **Guardrail Triggered** ({category.capitalize()})")
    md.append(f"**Status:** {status}")
    md.append("")
    md.append(f"**Message:** {message}")

    return "\n".join(md)


#############################################
# Pretty Response Router
#############################################
def pretty_response(txt: str) -> str:
    """Route JSON → Markdown, or show readable text only."""
    if not isinstance(txt, str):
        txt = str(txt)

    cleaned = strip_markdown_fences(txt)

    try:
        parsed = json.loads(cleaned)

        # Planning agent output
        if isinstance(parsed, dict) and "plan" in parsed:
            return json_plan_to_markdown(parsed)

        # Agenda agent output
        if isinstance(parsed, dict) and "days" in parsed:
            return json_agenda_to_markdown(parsed)

        # Guardrail output
        if isinstance(parsed, dict) and parsed.get("type") == "guardrail":
            return json_guardrail_to_markdown(parsed)

        # Any other JSON → pretty-print
        formatted = json.dumps(parsed, indent=4, ensure_ascii=False)
        return f"```json\n{formatted}\n```"

    except Exception:
        return cleaned


#############################################
# Extract text from ADK events
#############################################
def extract_text_from_events(events):
    for ev in reversed(events):
        try:
            parts = getattr(ev.content, "parts", [])
            for p in parts:
                if hasattr(p, "text") and p.text:
                    return p.text
        except:
            continue
    return "No textual response found."


#############################################
# Initialize ADK + Streamlit
#############################################
st.set_page_config(page_title="ConciergeX Agentic AI", layout="wide")

orchestrator = OrchestratorAgent()
runner = InMemoryRunner(agent=orchestrator, app_name="conciergex")


#############################################
# UI Header
#############################################
st.title("🤖 ConciergeX Agentic AI")
st.caption("Multi-agent orchestration using Google ADK + Gemini 2.5 Flash Lite")



#############################################
# A2A Auto-Detection Helpers (FINAL VERSION)
#############################################
import requests

def check_a2a_server(base_url="http://localhost:8001"):
    """Detect A2A server and return the working POST execution endpoint."""
    agent_card_url = f"{base_url}/.well-known/agent.json"

    # Step 1 — Check if A2A server is alive
    try:
        r = requests.get(agent_card_url, timeout=1.5)
        if r.status_code != 200:
            return False, None
    except:
        return False, None

    # Step 2 — Known execution endpoints
    candidate_endpoints = [
        "/execute",           # ✔ Your ADK manual A2A endpoint
        "/",                  # Some ADK versions use root POST
        "/process",           # JSON-RPC style
        "/run"                # Rare but valid
    ]

    # Step 3 — Try each endpoint until one succeeds
    for ep in candidate_endpoints:
        try:
            url = f"{base_url}{ep}"
            test = requests.post(url, json={"input": "ping"}, timeout=1.5)

            # If endpoint exists, any of these are acceptable:
            if test.status_code in (200, 400, 422):
                return True, url
        except:
            continue

    # Agent card OK but no valid POST endpoint detected
    return True, None


#############################################
# Tabs
#############################################
tabs = st.tabs([
    "🧠 Orchestrator Chat",
    "📅 Planning",
    "🗓️ Agenda",
    "📋 Tasks",
    "🚨 Guardrails",
    "🔗 Pipeline",
    "🔌 A2A Agent"
])


#############################################
# TAB 1 — Orchestrator Chat
#############################################
with tabs[0]:
    st.subheader("🧠 Orchestrator Agent")
    msg = st.text_area("Enter message:", height=130)

    if st.button("Send to Orchestrator"):
        events = run_sync(runner.run_debug(msg))
        raw = extract_text_from_events(events)
        st.markdown(pretty_response(raw))


#############################################
# TAB 2 — Planning
#############################################
with tabs[1]:
    st.subheader("📅 Planning Agent")
    msg = st.text_area("Request a study plan:", height=130)

    if st.button("Generate Plan"):
        cmd = f"[force_planning]\n{msg}"
        events = run_sync(runner.run_debug(cmd))
        raw = extract_text_from_events(events)
        st.markdown(pretty_response(raw))


#############################################
# TAB 3 — Agenda
#############################################
with tabs[2]:
    st.subheader("🗓️ Agenda Agent")
    msg = st.text_area("Describe your plan to convert into agenda:", height=130)

    if st.button("Generate Agenda"):
        sanitized = sanitize_adk_json(msg)
        if isinstance(sanitized, dict):
            sanitized = json.dumps(sanitized, ensure_ascii=False)

        cmd = f"[force_agenda]\n{sanitized}"
        events = run_sync(runner.run_debug(cmd))
        raw = extract_text_from_events(events)
        st.markdown(pretty_response(raw))


#############################################
# TAB 4 — Tasks
#############################################
with tabs[3]:
    st.subheader("📋 Task Manager")
    msg = st.text_area("Enter task request:", height=130)

    if st.button("Run Task"):
        sanitized = sanitize_adk_json(msg)
        if isinstance(sanitized, dict):
            sanitized = json.dumps(sanitized, ensure_ascii=False)

        cmd = f"[force_tasks]\n{sanitized}"
        events = run_sync(runner.run_debug(cmd))
        raw = extract_text_from_events(events)
        st.markdown(pretty_response(raw))


#############################################
# TAB 5 — Guardrails
#############################################
with tabs[4]:
    st.subheader("🚨 Guardrails Test")
    msg = st.text_area("Enter dangerous request:", height=130)

    if st.button("Test Guardrails"):
        events = run_sync(runner.run_debug(msg))
        raw = extract_text_from_events(events)
        st.markdown(pretty_response(raw))


#############################################
# TAB 6 — Pipeline (Plan → Agenda)
#############################################
with tabs[5]:
    st.subheader("🔗 Full Pipeline")

    msg = st.text_area("Enter planning request:", height=130)

    if st.button("Run Full Pipeline"):
        # Step 1: Plan
        plan_cmd = f"[force_planning]\n{msg}"
        plan_events = run_sync(runner.run_debug(plan_cmd))
        plan_raw = extract_text_from_events(plan_events)

        st.info("Weekly Plan:")
        st.markdown(pretty_response(plan_raw))

        # Step 2: Clean plan for agenda
        cleaned = sanitize_adk_json(plan_raw)
        if isinstance(cleaned, dict):
            cleaned = json.dumps(cleaned, ensure_ascii=False)

        # Step 3: Agenda
        agenda_cmd = f"[force_agenda]\n{cleaned}"
        agenda_events = run_sync(runner.run_debug(agenda_cmd))
        agenda_raw = extract_text_from_events(agenda_events)

        st.success("Generated Agenda:")
        st.markdown(pretty_response(agenda_raw))


#############################################
# TAB 7 — A2A Agent (FINAL)
#############################################
with tabs[6]:
    st.subheader("🔌 A2A – Local ConciergeX A2A Endpoint")

    st.markdown("""
    This tab calls your **manual A2A server** running at port **8001**.

    Start the server in another terminal:
    ```
    uvicorn manual_a2a_agent:app --host 0.0.0.0 --port 8001
    ```
    """)

    import requests

    def detect_a2a():
        base = "http://localhost:8001"
        card = f"{base}/.well-known/agent.json"

        # Check if server is alive
        try:
            r = requests.get(card, timeout=2)
            if r.status_code != 200:
                st.warning("🟡 A2A server not responding to agent card.")
                return False, None
        except:
            st.warning("🟡 Unable to connect to A2A server.")
            return False, None

        # Check /execute only (since manual server uses ONLY this)
        exec_url = f"{base}/execute"

        try:
            test = requests.post(exec_url, json={"input": "ping"}, timeout=2)

            # Any response code means endpoint exists
            if test.status_code in (200, 400, 422):
                return True, exec_url

        except:
            pass

        return True, None

    alive, endpoint = detect_a2a()

    if not alive:
        st.error("🔴 A2A Server NOT Running.\nStart it with:\n`uvicorn manual_a2a_agent:app --port 8001`")
        st.stop()

    if endpoint is None:
        st.error("🟡 A2A server is running but no valid execution endpoint detected.")
        st.stop()

    st.success(f"🟢 A2A Server Running\nUsing endpoint: `{endpoint}`")

    st.markdown("---")

    query = st.text_area("Enter request for A2A agent:", height=120)

    if st.button("Send to A2A"):
        try:
            resp = requests.post(endpoint, json={"input": query}, timeout=20)
            output = resp.json().get("output", "")
            st.markdown(pretty_response(output))
        except Exception as e:
            st.error(f"Error contacting A2A server: {e}")

