ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.8"

FROM python:${RUNTIME_VERSION}-buster
RUN pip install awslambdaric

ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}
COPY . ${LAMBDA_TASK_ROOT}
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}

ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh /
COPY requirements.txt /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh
RUN pip install -r /requirements.txt
ENTRYPOINT [ "/entry.sh" ]
CMD [ "src/app.handler" ]