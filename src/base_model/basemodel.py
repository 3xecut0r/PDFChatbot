import os
from langchain_community.llms import HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from src.conf.config import settings

API_KEY = settings.hf_api_key
os.environ["HUGGINGFACEHUB_API_TOKEN"] = API_KEY


class BaseModel:
    def __init__(self):
        self.model = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                                    model_kwargs={"temperature": 0.5, "max_length": 6400})
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.prompt = ("Always check chat history before answer."
                       "Use no more than two sentences. Try to give the most accurate answer."
                       "\n\nChat history: {chat_history}"
                       "\n\nHuman: {user_input}\nAI:")

    def add_to_memory(self, userinput, model_answer):
        self.memory.save_context({"input": userinput}, {"output": model_answer})

    def drop_memory(self):
        self.memory.clear()

    async def answer(self, question):
        chat_memory = self.memory.buffer_as_str
        r = self.memory.buffer
        if len(r) > 30:
            self.drop_memory()
            return ("Free AI memory was was full. AI continue without previous messages. "
                    "For more memory select Premium version")
        if chat_memory:
            prompt = self.prompt.format(chat_history=chat_memory, user_input=question)
            answer = self.model(prompt)
            answer = answer.replace('\n\n', '')
            if '\nHuman Question' in answer:
                answer = answer.split('\nHuman Question')[0]
            self.add_to_memory(question, answer)
        else:
            prompt = self.prompt.format(chat_history='Without chat history', user_input=question)
            answer = self.model(prompt)
            self.add_to_memory(question, answer)

        return answer


BASEMODEL = BaseModel()

