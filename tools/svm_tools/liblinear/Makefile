CXX ?= g++
CC ?= gcc
CFLAGS ?= -Wall -O3 -fPIC
LIBS ?= blas/blas.a
#LIBS ?= -lblas

all: train predict predict_stdin

train: tron.o linear.o train.c blas/blas.a
	$(CXX) $(CFLAGS) -o train train.c tron.o linear.o $(LIBS)

predict: tron.o linear.o predict.c blas/blas.a
	$(CXX) $(CFLAGS) -o predict predict.c tron.o linear.o $(LIBS)

predict_stdin: tron.o linear.o predict_stdin.c blas/blas.a
	$(CXX) $(CFLAGS) -o predict_stdin predict_stdin.c tron.o linear.o $(LIBS)

tron.o: tron.cpp tron.h
	$(CXX) $(CFLAGS) -c -o tron.o tron.cpp

linear.o: linear.cpp linear.h
	$(CXX) $(CFLAGS) -c -o linear.o linear.cpp

blas/blas.a:
	cd blas; make OPTFLAGS='$(CFLAGS)' CC='$(CC)';

clean:
	cd blas;	make clean
	rm -f *~ tron.o linear.o train predict predict_stdin
