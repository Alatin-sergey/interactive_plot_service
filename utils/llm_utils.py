from abc import ABC
from tools import tools
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent

load_dotenv()


class BaseClass(ABC):
    pass


class AgentLLM(BaseClass):
    def __init__(self):
        self.model = ChatOllama(
            model=os.getenv("MODEL", "mistral"),
            verbose=True,
            base_url=f"http://{os.getenv('LLM_SERVICE', 'localhost')}:{os.getenv('LLM_PORT', '11434')}",
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        with open("utils/prompts/base_prompt.txt", "r", encoding="utf-8") as f:
            self.prompt = ChatPromptTemplate.from_template(f.read())
        self.agent = initialize_agent(
            tools,
            self.model,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
        )

    def ask_question(self, query):
        """Задает вопрос агенту и возвращает ответ."""
        response = self.agent.run(query)
        return response
