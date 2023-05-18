FROM public.ecr.aws/lambda/python:latest
WORKDIR ${LAMBDA_TASK_ROOT}
COPY install-browsers.sh .
RUN /usr/bin/bash ./install-browsers.sh
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["spotify_api.handler"]
