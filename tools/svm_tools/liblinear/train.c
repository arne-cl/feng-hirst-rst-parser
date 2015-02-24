#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "linear.h"
#define Malloc(type,n) (type *)malloc((n)*sizeof(type))
#define INF HUGE_VAL

void exit_with_help()
{
	printf(
	"Usage: train [options] training_set_file [model_file]\n"
	"options:\n"
	"-s type : set type of solver (default 1)\n"
	"	0 -- L2-regularized logistic regression\n"
	"	1 -- L2-loss support vector machines (dual)\n"	
	"	2 -- L2-loss support vector machines (primal)\n"
	"	3 -- L1-loss support vector machines (dual)\n"
	"	4 -- multi-class support vector machines by Crammer and Singer\n"
	"-c cost : set the parameter C (default 1)\n"
	"-e epsilon : set tolerance of termination criterion\n"
	"	-s 0 and 2\n" 
	"		|f'(w)|_2 <= eps*min(pos,neg)/l*|f'(w0)|_2,\n" 
	"		where f is the primal function, (default 0.01)\n"
	"	-s 1, 3, and 4\n"
	"		Dual maximal violation <= eps; similar to libsvm (default 0.1)\n"
	"-B bias : if bias >= 0, instance x becomes [x; bias]; if < 0, no bias term added (default 1)\n"
	"-wi weight: weights adjust the parameter C of different classes (see README for details)\n"
	"-v n: n-fold cross validation mode\n"
	);
	exit(1);
}

void parse_command_line(int argc, char **argv, char *input_file_name, char *model_file_name);
void read_problem(const char *filename);
void do_cross_validation();

struct feature_node *x_space;
struct parameter param;
struct problem prob;
struct model* model_;
int flag_cross_validation;
int nr_fold;
double bias;

int main(int argc, char **argv)
{
	char input_file_name[1024];
	char model_file_name[1024];
	const char *error_msg;

	parse_command_line(argc, argv, input_file_name, model_file_name);
	read_problem(input_file_name);
	error_msg = check_parameter(&prob,&param);

	if(error_msg)
	{
		fprintf(stderr,"Error: %s\n",error_msg);
		exit(1);
	}

	if(flag_cross_validation)
	{
		do_cross_validation();
	}
	else
	{
		model_=train(&prob, &param);
		save_model(model_file_name, model_);
		destroy_model(model_);
	}
	destroy_param(&param);
	free(prob.y);
	free(prob.x);
	free(x_space);

	return 0;
}

void do_cross_validation()
{
	int i;
	int total_correct = 0;
	int *target = Malloc(int, prob.l);

	cross_validation(&prob,&param,nr_fold,target);

	for(i=0;i<prob.l;i++)
		if(target[i] == prob.y[i])
			++total_correct;
	printf("Cross Validation Accuracy = %g%%\n",100.0*total_correct/prob.l);

	free(target);
}

void parse_command_line(int argc, char **argv, char *input_file_name, char *model_file_name)
{
	int i;

	// default values
	param.solver_type = L2LOSS_SVM_DUAL;
	param.C = 1;
	param.eps = INF; // see setting below
	param.nr_weight = 0;
	param.weight_label = NULL;
	param.weight = NULL;
	flag_cross_validation = 0;
	bias = 1;

	// parse options
	for(i=1;i<argc;i++)
	{
		if(argv[i][0] != '-') break;
		if(++i>=argc)
			exit_with_help();
		switch(argv[i-1][1])
		{
			case 's':
				param.solver_type = atoi(argv[i]);
				break;

			case 'c':
				param.C = atof(argv[i]);
				break;

			case 'e':
				param.eps = atof(argv[i]);
				break;

			case 'B':
				bias = atof(argv[i]);
				break;

			case 'w':
				++param.nr_weight;
				param.weight_label = (int *)realloc(param.weight_label,sizeof(int)*param.nr_weight);
				param.weight = (double *)realloc(param.weight,sizeof(double)*param.nr_weight);
				param.weight_label[param.nr_weight-1] = atoi(&argv[i-1][2]);
				param.weight[param.nr_weight-1] = atof(argv[i]);
				break;

			case 'v':
				flag_cross_validation = 1;
				nr_fold = atoi(argv[i]);
				if(nr_fold < 2)
				{
					fprintf(stderr,"n-fold cross validation: n must >= 2\n");
					exit_with_help();
				}
				break;

			default:
				fprintf(stderr,"unknown option\n");
				exit_with_help();
				break;
		}
	}

	// determine filenames
	if(i>=argc)
		exit_with_help();

	strcpy(input_file_name, argv[i]);

	if(i<argc-1)
		strcpy(model_file_name,argv[i+1]);
	else
	{
		char *p = strrchr(argv[i],'/');
		if(p==NULL)
			p = argv[i];
		else
			++p;
		sprintf(model_file_name,"%s.model",p);
	}

	if(param.eps == INF)
	{
		if(param.solver_type == L2_LR || param.solver_type == L2LOSS_SVM)
			param.eps = 0.01;
		else if(param.solver_type == L2LOSS_SVM_DUAL || param.solver_type == L1LOSS_SVM_DUAL || param.solver_type == MCSVM_CS)
			param.eps = 0.1;
	}
}

// read in a problem (in libsvm format)
void read_problem(const char *filename)
{
	int elements, max_index, i, j;
	FILE *fp = fopen(filename,"r");

	if(fp == NULL)
	{
		fprintf(stderr,"can't open input file %s\n",filename);
		exit(1);
	}

	prob.l = 0;
	elements = 0;
	while(1)
	{
		int c = fgetc(fp);
		switch(c)
		{
			case '\n':
				++prob.l;
				// fall through,
				// count the '-1' element
			case ':':
				++elements;
				break;
			case EOF:
				goto out;
			default:
				;
		}
	}
out:
	rewind(fp);

	prob.bias=bias;

	prob.y = Malloc(int,prob.l);
	prob.x = Malloc(struct feature_node *, prob.l);
	x_space = Malloc(struct feature_node, elements+prob.l);

	max_index = 0;
	j=0;
	for(i=0;i<prob.l;i++)
	{
		double label;
		prob.x[i] = &x_space[j];
		fscanf(fp,"%lf",&label);
		prob.y[i] = (int)label;

		while(1)
		{
			int c;
			do {
				c = getc(fp);
				if(c=='\n') goto out2;
			} while(isspace(c));
			ungetc(c,fp);
			if (fscanf(fp,"%d:%lf",&(x_space[j].index),&(x_space[j].value)) < 2)
			{
				fprintf(stderr,"Wrong input format at line %d\n", i+1);
				exit(1);
			}
			if (x_space[j].index<=0)
			{
				fprintf(stderr,"Error: index <=0\n");
				exit(1);
			}
			++j;
		}
out2:
		if(j>=1 && x_space[j-1].index > max_index)
			max_index = x_space[j-1].index;

		if(prob.bias>=0)
			x_space[j++].value = prob.bias;

		x_space[j++].index = -1;
	}

	if(prob.bias>=0)
	{
		prob.n=max_index+1;
		for(i=1;i<prob.l;i++)
			(prob.x[i]-2)->index = prob.n; 
		x_space[j-2].index = prob.n;
	}
	else
		prob.n=max_index;

	fclose(fp);
}
