% This make.m is used under Windows

mex -O -c ..\blas\*.c -outdir ..\blas
mex -O -c ..\linear.cpp
mex -O -c ..\tron.cpp
mex -O -c linear_model_matlab.c -I..\
mex -O train.c -I..\ tron.obj linear.obj linear_model_matlab.obj ..\blas\*.obj
mex -O predict.c -I..\ tron.obj linear.obj linear_model_matlab.obj ..\blas\*.obj
mex -O read_sparse.c

