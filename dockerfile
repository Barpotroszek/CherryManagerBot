FROM python:3.9-slim-buster

WORKDIR /CherryManagerBot
COPY . . 

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
# RUN git status
CMD [ "python3", "main.py"]
