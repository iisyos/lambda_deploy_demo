import argparse
import logging
import sys
import subprocess
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from mangum import Mangum
import turicreate as tc
import boto3

logger = logging.getLogger(__name__)


class Envs(BaseModel):
    key: Optional[str] = None
    val: Optional[str] = None


class HealthCheck(BaseModel):
    message: Optional[str] = 'OK'


class Command(BaseModel):
    command: str = 'ls'


class ImageOutput(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None


class PredictRequest(BaseModel):
    url: Optional[str] = None


class PredictResponse(BaseModel):
    predictions: Optional[str] = None
    ok: Optional[bool] = None
    message: Optional[str] = None


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

class ImageNotDownloadedException(Exception):
    pass


@app.exception_handler(Exception)
async def unknown_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={'message': 'Internal error.'})


@app.exception_handler(ImageNotDownloadedException)
async def client_exception_handler(request: Request, exc: ImageNotDownloadedException):
    return JSONResponse(status_code=400, content={'message': 'One or more images could not be downloaded.'})


@app.on_event('startup')
def load_model():
    print('ok')
    tc.config.set_runtime_config('TURI_CACHE_FILE_LOCATIONS', '/tmp')


def configure_logging(logging_level=logging.INFO):
    root = logging.getLogger()
    root.handlers.clear()
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    root.setLevel(logging_level)
    root.addHandler(stream_handler)


def predict_images(url):
    loaded_model = tc.load_model('src/z-fighters.model')
    data = tc.image_analysis.load_images(url)
    return loaded_model.predict(data)[0]


@app.post('/v1/predict', response_model=PredictResponse)
async def process(req: PredictRequest):
    tc.config.set_runtime_config('TURI_CACHE_FILE_LOCATIONS', '/tmp')
    logger.info('Processing request.')
    logger.debug(req.json())
    logger.info('Downloading images.')
    try:
        result = predict_images(req.url)
        ok = True
        message = 'success'
    except Exception as e:
        result = None
        message = repr(e)
        ok = False

    logger.info('Transaction complete.')
    return PredictResponse(predictions=result, ok=ok, message=message)


@app.get('/health')
def test():
    return HealthCheck()


handler = Mangum(app)

if __name__ == '__main__':

    import uvicorn

    parser = argparse.ArgumentParser(description='Runs the API locally.')
    parser.add_argument('--port',
                        help='The port to listen for requests on.',
                        type=int,
                        default=8081)
    args = parser.parse_args()
    configure_logging()
    uvicorn.run(app, host='0.0.0.0', port=args.port)
