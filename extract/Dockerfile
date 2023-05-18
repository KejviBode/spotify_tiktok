FROM public.ecr.aws/lambda/python:latest
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY . ${LAMBDA_TASK_ROOT}
CMD ["spotify_api.handler"]