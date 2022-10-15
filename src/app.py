import argparse
import base64
import io
import os
import logging
import sys

from urllib.parse import urlparse

from aiohttp.client import ClientSession
from asyncio import wait_for, gather, Semaphore

from typing import Optional, List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel, validator

import numpy as np

from PIL import Image

from mangum import Mangum
import turicreate as tc



logger = logging.getLogger(__name__)


class HealthCheck(BaseModel):
    """
    Represents an image to be predicted.
    """
    message: Optional[str] = 'OK'



class ImageOutput(BaseModel):
    """
    Represents the result of a prediction
    """
    category: Optional[str] = None
    name: Optional[str] = None


class PredictRequest(BaseModel):
    """
    Represents a request to process
    """
    url: Optional[str] = None


class PredictResponse(BaseModel):
    """
    Represents a request to process
    """
    predictions: Optional[str] = None


app = FastAPI()


class ImageNotDownloadedException(Exception):
    pass


@app.exception_handler(Exception)
async def unknown_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for all other errors.
    """
    return JSONResponse(status_code=500, content={'message': 'Internal error.'})


@app.exception_handler(ImageNotDownloadedException)
async def client_exception_handler(request: Request, exc: ImageNotDownloadedException):
    """
    Called when the image could not be downloaded.
    """
    return JSONResponse(status_code=400, content={'message': 'One or more images could not be downloaded.'})


# @app.on_event('startup')
# def load_model():
#     print('start')
    # # Load images (Note:'Not a JPEG file' errors are warnings, meaning those files will be skipped)
    # data = tc.image_analysis.load_images('PetImages', with_path=True)

    # # From the path-name, create a label column
    # data['label'] = data['path'].apply(lambda file_name: 'dog' if 'dog' in file_name else 'cat')
    
    # data.print_rows(num_rows=60)
    # # Save the data for future use
    # data.save('cats-dogs.sframe')
    
    # model = tc.image_classifier.create(data, target='label')
    # model.save('cats-dogs.model')



def configure_logging(logging_level=logging.INFO):
    """
    Configures logging for the application.
    """
    root = logging.getLogger()
    root.handlers.clear()
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    root.setLevel(logging_level)
    root.addHandler(stream_handler)

# def get_url_scheme(url, default_scheme='unknown'):
#     """
#     Returns the scheme of the specified URL or 'unknown' if it could not be determined.
#     """
#     result = urlparse(url, scheme=default_scheme)
#     return result.scheme


# async def retrieve_content(url, sess):
#     """
#     Retrieves the image content for the specified entry.
#     """
#     logger.info('retrieve_content.')
#     if url is not None:
#         scheme = get_url_scheme(url)
#         if scheme in ('http', 'https'):
#             raw_data = await download(url, sess)
#         else:
#             raise ValueError('Invalid scheme: %s' % scheme)
#         if raw_data is not None:
#             image = Image.open(io.BytesIO(raw_data))
#             image = image.convert('RGB')
#             return image
#     return None

# async def retrieve_image(url):
#     """
#     Retrieves the images for processing.

#     :param entries: The entries to process.

#     :return: The retrieved data.
#     """
#     logger.info('ClientSession.')
#     async with ClientSession() as sess:
#         print('ClientSession')
            
#         return await retrieve_content(url, sess),
            

# async def download(url, sess):
#     """
#     Downloads an image from the specified URL.

#     :param url: The URL to download the image from.
#     :param sess: The session to use to retrieve the data.
#     :param sem: Used to limit concurrency.

#     :return: The file's data.
#     """
#     async with sess.get(url) as res:
#         logger.info('Downloading %s' % url)
#         content = await res.read()
#         logger.info('Finished downloading %s' % url)
#     if res.status != 200:
#         raise ImageNotDownloadedException('Could not download image.')
#     return content


def predict_images(url):
    """
    Predicts the image's category and transforms the results into the output format.

    :param images: The Pillow Images to predict.

    :return: The prediction results.
    """
    loaded_model = tc.load_model('cats-dogs.model')
    data = tc.image_analysis.load_images(url)
    return loaded_model.predict(data)[0]



@app.post('/v1/predict', response_model=PredictResponse)
async def process(req: PredictRequest):
    """
    Predicts the category of the images contained in the request.

    :param req: The request object containing the image data to predict.

    :return: The prediction results.
    """
    logger.info('Processing request.')
    logger.debug(req.json())
    logger.info('Downloading images.')
    result = predict_images(req.url)
    logger.info('Transaction complete.')
    return PredictResponse(predictions = result)


@app.get('/health')
def test():
    """
    Can be called by load balancers as a health check.
    """
    return HealthCheck()


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
