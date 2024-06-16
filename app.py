from fastapi import FastAPI
import uvicorn

from src.base_model.routers import base
from src.routers.routers import files
from src.routers.routers import users, chats, main, payment
from starlette.staticfiles import StaticFiles

app = FastAPI()

origins = ["http://localhost:8000"]

app.mount("/static", StaticFiles(directory="static"), name="static")

# commandline_args = os.environ.get('COMMANDLINE_ARGS', "--skip-torch-cuda-test --no-half")

app.include_router(main)
app.include_router(users)
app.include_router(chats)
app.include_router(payment)
app.include_router(files)
app.include_router(base)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
