FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY cut_and_paste.py ${LAMBDA_TASK_ROOT}

CMD [ "copy_and_paste.handler"]