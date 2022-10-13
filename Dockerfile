ARG FUNCTION_DIR="/home/app/"

FROM python:3.8-buster
RUN pip install awslambdaric


ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh /
COPY requirements.txt /
COPY src/* ${FUNCTION_DIR}
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh
RUN pip install -r /requirements.txt
ENTRYPOINT [ "/entry.sh" ]
CMD [ "src/app.handler" ]