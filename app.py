import streamlit as st
import time
import os
from config import load_app_secrets

# ── Load Secrets Early ────────────────────────────────────────────────────────
load_app_secrets()

from pipeline import app_graph

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeepDive AI · Research Agent",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #E2E8F0;
}

.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {
    color: #CBD5E1 !important;
}

.stMarkdown a {
    color: #818CF8 !important;
    text-decoration: none;
    font-weight: 500;
}
.stMarkdown a:hover {
    text-decoration: underline;
    text-shadow: 0 0 8px rgba(129, 140, 248, 0.5);
}

.stApp {
    background-color: #0F172A;
    background-image: 
        radial-gradient(at 20% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 80% 100%, rgba(14, 165, 233, 0.15) 0px, transparent 50%);
    background-attachment: fixed;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.95) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
[data-testid="stSidebar"] * {
    color: #F8FAFC;
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { padding: 3rem 2rem 5rem; max-width: 1200px; }

/* ── Hero ── */
.hero { text-align: center; padding: 1rem 0 3rem; }
.hero-badge {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border-radius: 50px;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #818CF8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
}
.hero h1 {
    font-size: clamp(2.5rem, 5vw, 4.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 1rem;
    color: #F8FAFC;
    letter-spacing: -0.03em;
}
.hero h1 span {
    background: linear-gradient(135deg, #818CF8, #38BDF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(56, 189, 248, 0.3);
}
.hero p {
    color: #94A3B8 !important;
}

/* ── Cards (Glassmorphism) ── */
.clean-panel {
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    font-size: 1.05rem !important;
    padding: 0.9rem 1.2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
}
.stTextInput > div > div > input:focus {
    background: rgba(15, 23, 42, 0.8) !important;
    border-color: #818CF8 !important;
    box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2), inset 0 2px 4px rgba(0,0,0,0.2) !important;
}
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    color: #94A3B8 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #6366F1, #3B82F6) !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.02em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.9rem 2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100%;
    margin-top: 0.5rem;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
    background: linear-gradient(135deg, #4F46E5, #2563EB) !important;
}

/* ── Pipeline Steps ── */
.step-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.step-card:hover {
    transform: translateX(4px);
    border-color: rgba(255, 255, 255, 0.1);
}
.step-card.active {
    background: rgba(56, 189, 248, 0.05);
    border-color: rgba(56, 189, 248, 0.3);
    box-shadow: inset 4px 0 0 #38BDF8, 0 4px 20px rgba(56, 189, 248, 0.15);
}
.step-card.done {
    background: rgba(16, 185, 129, 0.05);
    border-color: rgba(16, 185, 129, 0.2);
    box-shadow: inset 4px 0 0 #10B981, 0 4px 6px rgba(0,0,0,0.1);
}
.step-icon {
    font-size: 2rem;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}
.step-details { flex-grow: 1; }
.step-title { font-weight: 600; color: #F1F5F9; font-size: 1.05rem; }
.step-desc { font-size: 0.85rem; color: #94A3B8; margin-top: 0.2rem; }
.step-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 0.4rem 0.8rem;
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.6);
    color: #64748B;
    font-weight: 600;
    letter-spacing: 0.05em;
    border: 1px solid rgba(255,255,255,0.05);
}
.step-card.active .step-status { background: rgba(56, 189, 248, 0.1); color: #38BDF8; border-color: rgba(56,189,248,0.2); }
.step-card.done .step-status { background: rgba(16, 185, 129, 0.1); color: #34D399; border-color: rgba(16,185,129,0.2); }

/* Pulse animation for running state */
@keyframes pulseGlow {
    0% { opacity: 1; filter: drop-shadow(0 0 5px rgba(56,189,248,0.5)); }
    50% { opacity: 0.7; filter: drop-shadow(0 0 2px rgba(56,189,248,0.2)); }
    100% { opacity: 1; filter: drop-shadow(0 0 5px rgba(56,189,248,0.5)); }
}
.step-card.active .step-icon { animation: pulseGlow 2s infinite; }

/* ── Result Panels ── */
.report-panel {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-top: 4px solid #6366F1;
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
    margin-bottom: 2rem;
}
.critic-panel {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(245, 158, 11, 0.2);
    border-top: 4px solid #F59E0B;
    border-radius: 20px;
    padding: 2.5rem;
    margin-top: 1.5rem;
    box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
}
.panel-tag {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.5rem 1.2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    letter-spacing: 0.05em;
}
.report-panel .panel-tag { background: rgba(99, 102, 241, 0.1); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.2); }
.critic-panel .panel-tag { background: rgba(245, 158, 11, 0.1); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.2); }

.report-panel h1, .report-panel h2, .report-panel h3 { color: #F8FAFC !important; font-weight: 700; }
.critic-panel h1, .critic-panel h2, .critic-panel h3 { color: #F8FAFC !important; font-weight: 700; }

/* ── Expanders ── */
.streamlit-expanderHeader {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    color: #94A3B8 !important;
    background: rgba(15, 23, 42, 0.6) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}

.stSpinner > div > div { border-color: #6366F1 !important; border-bottom-color: transparent !important; }

/* History Buttons */
.history-btn button {
    background: rgba(15, 23, 42, 0.4) !important;
    color: #94A3B8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    padding: 0.7rem 1rem !important;
    text-align: left !important;
    box-shadow: none !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.history-btn button:hover {
    background: rgba(30, 41, 59, 0.8) !important;
    color: #F1F5F9 !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(icon: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", ""),
        "running": ("RUNNING", "active"),
        "done":    ("DONE",    "done"),
    }
    label, cls = status_map.get(state, ("WAITING", ""))
    st.markdown(f"""
    <div class="step-card {cls}">
        <div class="step-icon">{icon}</div>
        <div class="step-details">
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        <div class="step-status">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done", "history", "current_view"):
    if key not in st.session_state:
        if key == "results":
            st.session_state[key] = {}
        elif key == "history":
            st.session_state[key] = []
        elif key == "current_view":
            st.session_state[key] = None
        else:
            st.session_state[key] = False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">V3.0 GROQ LLAMA-3.3 70B EDITION</div>


    <h1>DeepDive <span>AI</span></h1>
    <p style="color: #64748B; font-size: 1.1rem; max-width: 650px; margin: 0 auto; line-height: 1.6;">
        Experience the power of autonomous AI agents. They search the web, store facts in a vector database, draft comprehensive reports, and ruthlessly criticize their own work until perfect.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Layout ───────────────────────────────────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="clean-panel">', unsafe_allow_html=True)
    topic = st.text_input(
        "Mission Directive (Research Topic)",
        placeholder="e.g. Impact of Quantum Computing on Cryptography in 2025...",
        key="topic_input",
    )
    run_btn = st.button("Deploy Agents")
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.8rem;flex-wrap:wrap;margin-bottom:2.5rem; align-items:center;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#94A3B8;font-weight:600;letter-spacing:0.05em;">SUGGESTIONS:</span>
    """, unsafe_allow_html=True)
    examples = ["OpenAI Sora Architecture", "CRISPR-Cas9 Therapeutics", "Solid State Batteries"]
    for ex in examples:
        st.markdown(f"""
        <span style="
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 0.4rem 0.9rem;
            font-size: 0.8rem;
            color: #94A3B8;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            transition: all 0.2s;
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Sidebar History ──
with st.sidebar:
    # User Profile
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem; margin-bottom: 2.5rem; padding: 1.5rem; background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="background: linear-gradient(135deg, #818CF8, #38BDF8); width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: bold; color: white; margin: 0 auto 0.8rem auto; box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);">K</div>
        <div style="color: #F8FAFC; font-weight: 700; font-family: 'Inter', sans-serif; font-size: 1.1rem; letter-spacing: 0.02em;">Karun</div>
        <div style="color: #38BDF8; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; letter-spacing: 0.1em; margin-top: 0.2rem;">SYSTEM OPERATOR</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#F8FAFC; font-family:Inter; font-weight:700;'>📂 Mission History</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 0.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.markdown("<p style='font-size:0.9rem; color:#94A3B8;'>No past reports generated yet.</p>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="history-btn">', unsafe_allow_html=True)
        for idx, item in enumerate(reversed(st.session_state.history)):
            if st.button(f"📄 {item['topic'][:35]}...", key=f"hist_{idx}"):
                st.session_state.results = item['results']
                st.session_state.current_view = item['topic']
                st.session_state.done = True
                st.session_state.running = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with col_pipeline:
    r = st.session_state.results
    
    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        idx = steps.index(step)
        completed = list(r.keys())
        if step in r:
            return "done"
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    st.markdown('<div style="font-family:\'Fira Code\'; color:#00E5FF; font-size:0.8rem; margin-bottom:1rem; letter-spacing:0.1em;">LIVE PIPELINE STATUS</div>', unsafe_allow_html=True)
    
    step_card("🌐", "Search Agent",  s("search"), "Scours the internet for recent sources")
    step_card("🗄️", "Reader Agent",  s("reader"), "Scrapes URLs & populates FAISS Database")
    step_card("✍️", "Writer Agent",  s("writer"), "Drafts report using RAG Context")
    step_card("🧐", "Critic Agent",  s("critic"), "Reviews draft & enforces quality standard")

# ── System Diagnostics Dashboard (Dynamic) ──────────────────────────────────
import tools
import os

if not st.session_state.results and not st.session_state.running:
    st.markdown('<div style="margin: 4rem 0 2rem; height: 1px; background: rgba(255,255,255,0.05);"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#F8FAFC; font-family:Inter; font-weight:600; text-align:center; margin-bottom: 2.5rem;'>System Diagnostics</h3>", unsafe_allow_html=True)
    
    # 1. Active Agents (counting from pipeline graph)
    num_agents = 4 # Search, Reader, Writer, Critic
    try:
        if hasattr(app_graph, 'nodes'):
            # exclude internal nodes if present
            num_agents = len([n for n in app_graph.nodes if n not in ['__start__', '__end__']])
    except:
        pass
        
    # 2. Vector Memory (FAISS index size)
    if tools.global_vector_store is not None:
        try:
            num_vectors = tools.global_vector_store.index.ntotal
            memory_val = f"{num_vectors} Vectors"
        except:
            memory_val = "Active"
    else:
        memory_val = "0 Vectors"
        
    # 3. Last Run Latency
    last_run = st.session_state.get('last_run_time', 0)
    latency_val = f"{last_run:.1f} s" if last_run > 0 else "--"
    
    # 4. System Status (Checking API Keys)
    llm_key_ok = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("MISTRAL_API_KEY"))
    tavily_key_ok = bool(os.getenv("TAVILY_API_KEY"))
    keys_ok = llm_key_ok and tavily_key_ok
    sys_status = "OPTIMAL" if keys_ok else "NO KEYS"
    sys_color = "#A78BFA" if keys_ok else "#F87171"
    sys_glow = "rgba(139, 92, 246, 0.3)" if keys_ok else "rgba(248, 113, 113, 0.3)"

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown(f"""
        <div class="clean-panel" style="padding:1.5rem; text-align:center; margin-bottom:0; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <div style="font-size: 2rem; margin-bottom:0.8rem; filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.3));">🤖</div>
            <div style="color: #94A3B8; font-size: 0.75rem; font-weight:700; font-family:'JetBrains Mono', monospace; letter-spacing:0.05em; margin-bottom:0.3rem;">ACTIVE AGENTS</div>
            <div style="color: #38BDF8; font-size: 1.6rem; font-weight:800; font-family:'Inter', sans-serif;">{num_agents}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"""
        <div class="clean-panel" style="padding:1.5rem; text-align:center; margin-bottom:0; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <div style="font-size: 2rem; margin-bottom:0.8rem; filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.3));">🧠</div>
            <div style="color: #94A3B8; font-size: 0.75rem; font-weight:700; font-family:'JetBrains Mono', monospace; letter-spacing:0.05em; margin-bottom:0.3rem;">VECTOR MEMORY</div>
            <div style="color: #34D399; font-size: 1.6rem; font-weight:800; font-family:'Inter', sans-serif;">{memory_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f"""
        <div class="clean-panel" style="padding:1.5rem; text-align:center; margin-bottom:0; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <div style="font-size: 2rem; margin-bottom:0.8rem; filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.3));">⏱️</div>
            <div style="color: #94A3B8; font-size: 0.75rem; font-weight:700; font-family:'JetBrains Mono', monospace; letter-spacing:0.05em; margin-bottom:0.3rem;">LAST RUN TIME</div>
            <div style="color: #FBBF24; font-size: 1.6rem; font-weight:800; font-family:'Inter', sans-serif;">{latency_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat4:
        st.markdown(f"""
        <div class="clean-panel" style="padding:1.5rem; text-align:center; margin-bottom:0; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <div style="font-size: 2rem; margin-bottom:0.8rem; filter: drop-shadow(0 0 10px {sys_glow});">🛡️</div>
            <div style="color: #94A3B8; font-size: 0.75rem; font-weight:700; font-family:'JetBrains Mono', monospace; letter-spacing:0.05em; margin-bottom:0.3rem;">SYS STATUS</div>
            <div style="color: {sys_color}; font-size: 1.6rem; font-weight:800; font-family:'Inter', sans-serif;">{sys_status}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<br><br>', unsafe_allow_html=True)


# ── Run pipeline (KEEP LOGIC IDENTICAL) ──────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input
    
    start_time = time.time()

    try:
        with st.spinner("🧠 LangGraph Agentic Pipeline is executing..."):
            # We use app_graph.stream to watch the agents work step-by-step
            for event in app_graph.stream({"topic": topic_val}):
                for node, state in event.items():
                    if node == "Search":
                        results["search"] = state.get("search_results")
                        st.toast("🌐 Search Agent finished gathering info!")
                    elif node == "Scrape":
                        results["reader"] = state.get("scraped_content")
                        st.toast("🗄️ Reader Agent stored data in RAG Database!")
                    elif node == "Write":
                        results["writer"] = state.get("report")
                        st.toast("✍️ Writer Agent drafted a report!")
                    elif node == "Critic":
                        score = state.get("critic_score")
                        feedback = state.get("feedback")
                        results["critic"] = f"**Score: {score}/10**\n\n{feedback}"
                        if score < 7:
                            st.toast(f"🧐 Critic gave {score}/10. Sending back to Writer for rewrite!")
                        else:
                            st.toast(f"✅ Critic gave {score}/10. Report Approved!")
                    
                st.session_state.results = dict(results)

        st.session_state.last_run_time = time.time() - start_time
        st.session_state.running = False
        st.session_state.done = True
        st.session_state.current_view = topic_val
        
        # Save this run to the sidebar history
        st.session_state.history.append({
            "topic": topic_val,
            "results": dict(results)
        })
        st.rerun()

    except Exception as err:
        st.session_state.running = False
        st.session_state.done = False
        err_type = type(err).__name__
        err_str = str(err)
        
        st.error("❌ **Pipeline Execution Failed!**")
        
        if "GROQ_API_KEY" in err_str:
            st.error("🔑 **Groq API Key Error**: `GROQ_API_KEY` is missing or invalid. Get a free key at [console.groq.com](https://console.groq.com).")
        elif "GEMINI_API_KEY" in err_str or "GOOGLE_API_KEY" in err_str:
            st.error("🔑 **Gemini API Key Error**: `GEMINI_API_KEY` is missing or invalid. Get a free key at [aistudio.google.com](https://aistudio.google.com).")
        elif "HTTPStatusError" in err_type or "401" in err_str or "Unauthorized" in err_str:
            st.error("🔑 **401 Unauthorized Error**: Your LLM API key is invalid or expired. Check your Streamlit Secrets.")
        elif "429" in err_str or "Rate limit" in err_str or "Quota" in err_str:
            st.error("⏳ **429 Rate Limit Exceeded**: API rate limit reached.")
        elif "TAVILY_API_KEY" in err_str or "tavily" in err_str.lower():
            st.error("🔑 **Tavily API Key Error**: `TAVILY_API_KEY` is missing or invalid.")
        else:
            st.error(f"⚠️ **Error Details ({err_type})**: `{err_str}`")

        with st.expander("🛠️ How to set up Groq API Key on Streamlit Cloud"):
            st.markdown("""
            1. Get a **100% Free Groq API Key** from [console.groq.com/keys](https://console.groq.com/keys).
            2. Open your Streamlit Cloud app settings ⚙️ -> **Secrets**.
            3. Paste your secrets in TOML format:
               ```toml
               GROQ_API_KEY = "gsk_your_groq_api_key_here"
               TAVILY_API_KEY = "tvly-your_tavily_api_key_here"
               ```
            4. Click **Save** and re-run!
            """)





# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div style="margin: 3rem 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,229,255,0.3), transparent);"></div>', unsafe_allow_html=True)
    
    # Raw outputs in expanders
    col_raw1, col_raw2 = st.columns(2)
    if "search" in r:
        with col_raw1.expander("🌐 Raw Search Query Results"):
            st.markdown(f'<div style="font-size:0.85rem; color:#94A3B8;">{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with col_raw2.expander("🗄️ RAG Database Extractions"):
            st.markdown(f'<div style="font-size:0.85rem; color:#94A3B8;">{r["reader"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-tag">📝 FINAL INTELLIGENCE REPORT</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="critic-panel">
            <div class="panel-tag">🧠 CRITIC ANALYSIS & VERDICT</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:4rem; font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#64748B; letter-spacing:0.05em;">
    CRAFTED BY <span style="color: #818CF8; font-weight: 700;">KARUN</span> // POWERED BY LANGGRAPH & FAISS RAG
</div>
""", unsafe_allow_html=True)