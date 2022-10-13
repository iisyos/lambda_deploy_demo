FROM python:3.8-buster
ARG FUNCTION_DIR="/home/app/"

RUN pip install awslambdaric

COPY src/* ${FUNCTION_DIR}
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh /
COPY requirements.txt /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh
RUN pip install -r requirements.txt
ENTRYPOINT [ "/entry.sh" ]
CMD [ "app.handler" ]