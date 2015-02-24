CXX? = g++
CFLAGS = -Wall -O3 

all: svm-train svm-predict svm-scale svm-predict-stdin

svm-predict: svm-predict.c svm.o
	$(CXX) $(CFLAGS) svm-predict.c svm.o -o svm-predict -lm
svm-predict-stdin: svm-predict-stdin.c svm.o
	$(CXX) $(CFLAGS) svm-predict-stdin.c svm.o -o svm-predict-stdin -lm
svm-train: svm-train.c svm.o
	$(CXX) $(CFLAGS) svm-train.c svm.o -o svm-train -lm
svm-scale: svm-scale.c
	$(CXX) $(CFLAGS) svm-scale.c -o svm-scale
svm.o: svm.cpp svm.h
	$(CXX) $(CFLAGS) -c svm.cpp
clean:
	rm -f *~ svm.o svm-train svm-predict svm-scale svm-predict-stdin
