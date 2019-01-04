FROM alpine:3.8 as builder

RUN apk update && \
    apk add git py2-setuptools py2-pip build-base openjdk8-jre perl && \
    pip install nltk==3.4 pytest

WORKDIR /opt
RUN git clone https://github.com/arne-cl/feng-hirst-rst-parser.git

# The Feng's original README claims that liblbfgs is included, but it's not
WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite
RUN wget https://github.com/downloads/chokkan/liblbfgs/liblbfgs-1.10.tar.gz && \
    tar xfvz liblbfgs-1.10.tar.gz && \
    rm liblbfgs-1.10.tar.gz

WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite/liblbfgs-1.10
RUN ./configure --prefix=$HOME/local && \
    make && \
    make install

WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-0.12
# Can't put chmod and ./configure in the same layer (to avoid "is busy" error)
RUN chmod +x configure install-sh
RUN ./configure --prefix=$HOME/local --with-liblbfgs=$HOME/local && \
    make && \
    make install && \
    cp /root/local/bin/crfsuite /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-stdin && \
    chmod +x /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-stdin


FROM alpine:3.8

RUN apk update && \
    apk add py2-pip openjdk8-jre-base perl && \
    pip install nltk==3.4 pytest

WORKDIR /opt/feng-hirst-rst-parser
COPY --from=builder /opt/feng-hirst-rst-parser .

WORKDIR /root/local
COPY --from=builder /root/local .

WORKDIR /opt/feng-hirst-rst-parser/src

ENTRYPOINT ["/opt/feng-hirst-rst-parser/src/parser_wrapper.py"]
CMD ["../texts/input_long.txt"]
