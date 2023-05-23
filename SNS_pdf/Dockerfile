FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY report_pdf.py ${LAMBDA_TASK_ROOT}

CMD [ "report_pdf.handler"]