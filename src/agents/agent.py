from langchain.agents import create_agent

def create_rag_agent(model, tools, prompt=None):
    agent = create_agent(model, tools, system_prompt=prompt)
    return agent