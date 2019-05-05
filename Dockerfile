FROM ubuntu:18.04
WORKDIR /usr/src/app

COPY . .

RUN apt update && \
    apt install -y make
RUN make

CMD ["./kompilator", "-h"]
