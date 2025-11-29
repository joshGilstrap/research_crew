# Autonomous Research Crew (AI Agents)

A multi-agent system that autonomously conducts deep web research, synthesizes findings, and drafts reports—with Human-in-the-Loop (HITL) oversight.

## Live Demo

[Direct link](https://researchcrew.streamlit.app) or use it directly on my [portfolio website](joshgilstrap.com)
<img width="2524" height="1360" alt="Screenshot 2025-11-27 114410" src="https://github.com/user-attachments/assets/e1b3c372-e023-44c9-a68c-af870b705da3" />

## The Architecture

This application uses a Cyclic State Graph that schedules 3 AI personas that perform specialized tasks on a common state.

The Crew

- The Researcher: Uses Tavily API to scrape live web data based on the user's prompt.

- The Analyst: Reading the raw data, identifying trends, and structuring the information.

- The Writer: Compiling the analysis into a polished, professional blog post/report.

- The Manager (Human-in-the-Loop): The graph pauses execution before publishing. The user reviews the draft, approves it, or resets the cycle.

## Tech Stack & Engineering Decisions

| Component | Technology | Thought Process |
| :-------- | :--------- | :-------------- |
| Orchestration | LangGraph |Enables cyclic workflows and fine-grained state control (unlike standard DAGs). |
| LLM Engine | Groq (Llama 3.1) | Chosen for ultra-low latency inference (~300 tokens/s) to keep the UI snappy. |
| Frontend | Streamlit | Rapid prototyping with built-in session state management. |
| Search Tool | Tavily API | Optimized for LLM agents; returns clean context, not just HTML. |
| Persistence | MemorySaver | Maintains graph state across Streamlit re-runs (Session Persistence). |

## Key Features

1. Human-in-the-Loop (HITL)

  - The system effectively uses LangGraph's interrupt_before functionality.

    - The AI does the heavy lifting (Research -> Analyze -> Draft).

    - It hits a "breakpoint" and suspends execution.

    - The UI presents the draft to the user.

    - Upon approval, the graph resumes execution from the exact saved state to finalize the output.

2. State Management "The Amnesia Fix"

  - Streamlit apps re-run the entire script on every interaction. To prevent the AI from losing its memory or restarting from scratch:

    - I implemented a uuid based Session Threading system.
    - The LangGraph MemorySaver is cached in st.session_state.

    - "Resetting" the agent doesn't delete data; it dynamically generates a new thread_id, instantly giving the user a fresh workspace without server restart.

## Local Installation

Prerequisites: Python 3.10+

Clone the repository
```
git clone [https://github.com/joshgilstrap/research-crew.git](https://github.com/joshgilstrap/research-crew.git)
cd research-crew
```

Install dependencies
```
pip install -r requirements.txt
```

Configure Secrets
Create a folder .streamlit and a file secrets.toml:
```
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_..."
TAVILY_API_KEY = "tvly-..."
```

Run the App
```
streamlit run agent.py
```


Key Code Snippet: The Graph Definition

```
# Defining the cyclic workflow
workflow = StateGraph(AgentState)
workflow.add_node("researcher", research_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("writer", writer_node)
workflow.add_node("reviewer", review_node)

# The logic flow
workflow.add_edge(START, 'researcher')
workflow.add_edge('researcher', 'analyst')
workflow.add_edge('analyst', 'writer')
workflow.add_edge('writer', 'reviewer')
workflow.add_edge('reviewer', END)
```

🔮 Future Improvements

[ ] Multi-turn Research: Allow the Researcher to self-reflect and search again if data is insufficient.

[ ] Format Selection: Allow users to choose between "Blog Post", "Executive Brief", or "Social Media".

[ ] Export Options: Generate PDF/Markdown file downloads.

🤝 Connect

Built by Josh Gilstrap as a showcase of Agentic Workflows.

[LinkedIn](https://www.linkedin.com/in/josh-gilstrap-3b34b0126/)

[Portfolio](joshgilstrap.com)
