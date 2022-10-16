import argparse
import base64
import io
import os
import logging
import sys
import subprocess
from urllib.parse import urlparse

from aiohttp.client import ClientSession
from asyncio import wait_for, gather, Semaphore

from typing import Optional, List

from click import command

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel, validator

import numpy as np

from PIL import Image

from mangum import Mangum
from sympy import content
import turicreate as tc

import boto3
import joblib

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
    code: Optional[str] = None
    message: Optional[str] = None


app = FastAPI()


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
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    root.setLevel(logging_level)
    root.addHandler(stream_handler)

def predict_images(url):
    loaded_model = tc.load_model('src/cats-dogs.model')
    data = tc.image_analysis.load_images(url)
    return loaded_model.predict(data)[0]

@app.post('/v1/predict', response_model=PredictResponse)
async def process(req: PredictRequest):
    tc.config.set_runtime_config('TURI_CACHE_FILE_LOCATIONS', '/tmp')
    logger.info('Processing request.')
    logger.debug(req.json())
    logger.info('Downloading images.')
    result = ""
    code = ""
    message = ""
    try:
        result = predict_images(req.url)
        code = 'ok'
    except Exception as e:
        message = repr(e)
        code = 'fail'

    logger.info('Transaction complete.')
    return PredictResponse(predictions = result, code=code,message=message)


@app.get('/health')
def test():
    cp = subprocess.run('ls', shell=True, text=True)
    print(tc.config.get_runtime_config()['TURI_CACHE_FILE_LOCATIONS'])
    return HealthCheck(message=str(cp.stdout))

@app.post('/hoge')
def hoge(req: Command):

    cp = subprocess.run(req.command, shell=True, text=True, stdout=subprocess.PIPE)
    print(tc.config.get_runtime_config()['TURI_CACHE_FILE_LOCATIONS'])
    return Command(command=str(cp.stdout))

handler = Mangum(app)

if __name__ == '__main__':

    import uvicorn

    parser = argparse.ArgumentParser(description='Runs the API locally.')
    parser.add_argument('--port',
                        help='The port to listen for requests on.',
                        type=int,
                        default=8080)
    args = parser.parse_args()
    configure_logging()
    uvicorn.run(app, host='0.0.0.0', port=args.port)
