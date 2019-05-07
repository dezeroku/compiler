FROM ubuntu:18.04
WORKDIR /usr/src/app

RUN apt update && \
    apt install -y python3-pip python3.7 libcln6 libcln-dev bison flex && \
    python3.7 -m pip install ply timeout_decorator pytest --user && \
    pip3 install ply --user  && \
    pip3 install timeout-decorator --user

COPY . .

RUN cd maszyna_rejestrowa && make

CMD ["./kompilator", "-h"]
