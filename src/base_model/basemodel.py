import os
from langchain_community.llms import HuggingFaceHub
from langchain.memory import ConversationBufferMemory

os.environ["HUGGINGFACEHUB_API_TOKEN"] = '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'


class BaseModel:
    def __init__(self):
        self.model = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                                    model_kwargs={"temperature": 0.5, "max_length": 6400})
        self.memory = ConversationBufferMemory(memory_key="chat_history",  return_messages=True)

    def add_to_memory(self, userinput, model_answer):
        self.memory.save_context({"input": userinput}, {"output": model_answer})

    def drop_memory(self):
        self.memory.clear()

    async def answer(self, question):
        chat_history = self.memory
        print(chat_history)
        if chat_history:
            answer = self.model(f'{chat_history} New question:{question}')
            answer = answer.replace('\n\n', '')
            self.add_to_memory(question, answer)
        else:
            answer = self.model(question)                # Vazhnoee
            answer = answer.replace('\n\n', '')         # Vazhnoee
            self.add_to_memory(question, answer)

        if answer == '':
            self.drop_memory()
        print(self.memory)
        return answer


BASEMODEL = BaseModel()

