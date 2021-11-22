FROM python:3.8.0-slim
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

WORKDIR /CherryManagerBot
COPY . . 

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
# RUN git status
CMD [ "python3", "main.py"]
