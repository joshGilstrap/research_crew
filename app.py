import streamlit as st
import os
import uuid
from typing import TypedDict
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

st.set_page_config("Research Crew", layout='wide')
st.title("Autonomous Research Crew")

os.environ['TAVILY_API_KEY'] = st.secrets["tavily_api_key"]

tool = TavilySearchResults(max_results=3)
model = ChatGroq(
    model='llama-3.1-8b-instant',
    temperature=0,
    api_key=st.secrets["groq_api_key"]
)
model_with_tools = model.bind_tools([tool])

memory = MemorySaver()

class AgentState(TypedDict):
    task: str
    research_data: str
    analysis_notes: str
    draft_report: str
    human_feedback: str
    final_report: str


def research_node(state: AgentState):
    user_task = state['task']
    response = tool.invoke(user_task)
    return {"research_data": str(response)}

def analyst_node(state: AgentState):
    prompt = f"""You are a Senior Analyst.
    Analyze the research in {state['research_data']} and identify key trends and patterns
    """
    response = model.invoke(prompt)
    return {'analysis_notes': response.content}

def writer_node(state: AgentState):
    prompt = f"""You are a Technical Writer.
    Analyze the notes in {state['analysis_notes']} and write a comprehensive blog post/report
    """
    response = model.invoke(prompt)
    return {'draft_report': response.content}

def review_node(state: AgentState):
    draft = state['draft_report']
    return {'final_report': "Reviewed by human: " + draft}

workflow = StateGraph(AgentState)
workflow.add_node("researcher", research_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("writer", writer_node)
workflow.add_node("reviewer", review_node)

workflow.add_edge(START, 'researcher')
workflow.add_edge('researcher', 'analyst')
workflow.add_edge('analyst', 'writer')
workflow.add_edge('writer', 'reviewer')
workflow.add_edge('reviewer', END)

if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()

app = workflow.compile(checkpointer=st.session_state.memory, interrupt_before=["reviewer"])

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

thread = {"configurable": {"thread_id": st.session_state.thread_id}}

if "logs" not in st.session_state:
    st.session_state.logs = []

def run_agent(input_data):
    for event in app.stream(input_data, thread):
        for node_name, node_output in event.items():
            st.session_state.logs.append(f"Thinking... ({node_name})")
            st.toast(f"Agent finished: {node_name}")

for log in st.session_state.logs:
    st.write(log)
    
try:
    current_state = app.get_state(thread)
    is_paused = len(current_state.next) > 0
except Exception:
    is_paused = False

user_text = st.text_input("Enter your research topic.", key="user_input")

if not is_paused:
    if st.button("Begin Research"):
        st.session_state.logs = []
        with st.spinner("Crew is working..."):
            run_agent({"task": user_text})
            st.rerun()
else:
    st.info("Paused for review.")
    draft = current_state.values.get('draft_report', "No draft found")
    
    st.subheader("Draft Report:")
    st.markdown(draft)
    
    st.write('---')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Approve & Publish"):
            with st.spinner("Publishing..."):
                run_agent(None)
            st.success("Process Complete")
            st.balloons()
            
            final_snapshot = app.get_state(thread)
            st.write(final_snapshot.values.get('final_report'))
            
            if st.button("Start Over"):
                st.session_state.logs = []
                st.rerun()
            
    with col2:
        if st.button("Reject & Reset"):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.logs = []
            st.warning("Resetting...")
            st.rerun()