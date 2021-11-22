FROM debian:bullseye

RUN apt update && apt install -y build-essential gcc clang clang-tools cmake python3 cppcheck valgrind afl gcc-multilib && rm -rf /var/lib/apt/lists/*

WORKDIR /CherryManagerBot
COPY . . 

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
# RUN git status
CMD [ "python3", "main.py"]
