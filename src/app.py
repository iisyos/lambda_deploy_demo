from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

app = FastAPI()


class HelloParam(BaseModel):
    name: str


@app.get("/hello")
def get_hello(name: str = None):
    """
    getで返事する
    """
    if name:
        message = f"[GET]hello, {name}!"
    else:
        message = f"[GET]hello, visitor!"

    return {"message": message}


@app.post("/hello_post")
def post_hello(param: HelloParam):
    """
    postで返事する
    """
    if param.name:
        message = f"[POST]hello, {param.name}!"
    else:
        message = f"[POST]hello, visitor!"

    return {"message": message}


handler = Mangum(app)