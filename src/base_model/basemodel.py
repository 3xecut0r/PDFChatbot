import os
from langchain_community.llms import HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import UnstructuredFileLoader
from tempfile import NamedTemporaryFile

from src.conf.config import settings
from src.utils.get_mongo import get_mongodb_chat_history

API_KEY = settings.hf_api_key
os.environ["HUGGINGFACEHUB_API_TOKEN"] = API_KEY

async def save_message(question, answer, chat_id):
    db = await get_mongodb_chat_history()
    collection_msg = db['messages']
    message = {'chat_id': chat_id, 'question': question, 'answer': answer}
    await collection_msg.insert_one(message)


class BaseModel:
    def __init__(self):
        self.model = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                                    model_kwargs={"temperature": 0.5, "max_length": 6400})
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.prompt = ("Always check chat history before answer."
                       "Use no more than two sentences. Try to give the most accurate answer."
                       "\n\nChat history: {chat_history}"
                       "\n\nHuman: {user_input}\nAI:")
        self.document = None
        self.prompt2 = ("Always check chat history before answer."
                       "Use no more than two sentences. Try to give the most accurate answer."
                       "\n\nThis is user document, read it: {document}"
                       "\n\nChat history: {chat_history}"
                       "\n\nHuman: {user_input}\nAI:")

    def add_to_memory(self, userinput, model_answer):
        self.memory.save_context({"input": userinput}, {"output": model_answer})

    def drop_memory(self):
        self.memory.clear()

    def upload_pdf(self, file_name, content):
        with NamedTemporaryFile(delete=False, suffix=file_name) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        loader = UnstructuredFileLoader(temp_file_path, strategy="fast", mode="single")
        docs = loader.load()
        text = docs[0].page_content if docs else ""
        self.document = text
        return text

    async def answer(self, question):
        chat_memory = self.memory.buffer_as_str
        r = self.memory.buffer
        if len(r) > 30:
            self.drop_memory()
            return ("Free AI memory was was full. AI continue without previous messages. "
                    "For more memory select Premium version")
        if chat_memory:
            if self.document:
                prompt = self.prompt2.format(chat_history=chat_memory, user_input=question, document=self.document)
            else:
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

