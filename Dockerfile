FROM alpine:3.8

RUN apk update && \
    apk add git py2-setuptools py2-pip build-base openjdk8-jre perl && \
    pip install nltk==3.4

# The README claims that liblbfgs is included, but it's not
WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite
RUN wget https://github.com/downloads/chokkan/liblbfgs/liblbfgs-1.10.tar.gz && \
    tar xfvz liblbfgs-1.10.tar.gz && \
    rm liblbfgs-1.10.tar.gz

WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite/liblbfgs-1.10
RUN ./configure --prefix=$HOME/local && \
    make && \
    make install

# FIXME: get code from github
# RUN git clone https://github.com/arne-cl/rst_discourse_parser

COPY texts /opt/feng-hirst-rst-parser/texts
COPY tools /opt/feng-hirst-rst-parser/tools
COPY model /opt/feng-hirst-rst-parser/model
COPY src /opt/feng-hirst-rst-parser/src


WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-0.12
# Can't put chmod and ./configure in the same layer (to avoid "is busy" error)
RUN chmod +x configure install-sh
RUN ./configure --prefix=$HOME/local --with-liblbfgs=$HOME/local && \
    make && \
    make install && \
    cp /root/local/bin/crfsuite /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-stdin && \
    chmod +x /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-stdin

WORKDIR /opt/feng-hirst-rst-parser/src

ENTRYPOINT ["/opt/feng-hirst-rst-parser/src/parser_wrapper.py"]
CMD ["../texts/input_long.txt"]
