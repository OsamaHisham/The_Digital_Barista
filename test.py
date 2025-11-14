from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tools = []  # no tools for now
prompt = "You are an assistant. Answer the user."

agent = create_react_agent(model=model, tools=tools, prompt=prompt)

result = agent.invoke({"input": "What is 5 + 7?"})
print(result)
