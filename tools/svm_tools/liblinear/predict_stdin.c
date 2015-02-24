#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include "linear.h"

char* line;
int max_line_len = 1024;
struct feature_node *x;
int max_nr_attr = 64;

struct model* model_;
int flag_predict_probability=0;

void do_predict_stdin(struct model* model_)
{
	int correct = 0;
	int total = 0;

	int nr_class=get_nr_class(model_);
	double *prob_estimates=NULL;
	int n;
	int nr_feature=get_nr_feature(model_);
	if(model_->bias>=0)
		n=nr_feature+1;
	else
		n=nr_feature;

	if(flag_predict_probability)
	{
		int *labels;

		if(model_->param.solver_type!=L2_LR)
		{
			fprintf(stderr, "probability output is only supported for logistic regression\n");
			return;
		}

		labels=(int *) malloc(nr_class*sizeof(int));
		get_labels(model_,labels);
		prob_estimates = (double *) malloc(nr_class*sizeof(double));
		//printf("labels");		
		//for(j=0;j<nr_class;j++)
		//	printf(" %d",labels[j]);
		//printf("\n");
		free(labels);
	}
	printf("Ready for input:\n");
	fflush(stdout);
	
	while(1)
	{
		int i = 0;
		int c;
		double target;
		int target_label, predict_label;
		
		c = getc(stdin);
		if (c == '\n')
			break;
		else
		{
			//printf("# %c", c);
			ungetc(c, stdin);
		}	
		scanf("%lf", &target);
		//printf("* %f | %c *", target, target);
		
		target_label=(int)target;

		while(1)
		{
			if(i>=max_nr_attr-2)	// need one more for index = -1
			{
				max_nr_attr *= 2;
				x = (struct feature_node *) realloc(x,max_nr_attr*sizeof(struct feature_node));
			}

			do {
				c = getc(stdin);
				if(c=='\n' || c==EOF) goto out2;
			} while(isspace(c));
			ungetc(c, stdin);
			if (fscanf(stdin,"%d:%lf",&x[i].index,&x[i].value) < 2)
			{
				fprintf(stderr,"Wrong input format at line %d\n", total+1);
				exit(1);
			}
			// feature indices larger than those in training are not used
			if(x[i].index<=nr_feature)
				++i;
		}

out2:
		if(model_->bias>=0)
		{
			x[i].index = n;
			x[i].value = model_->bias;
			i++;
		}
		x[i].index = -1;

		if(flag_predict_probability)
		{
			int j;
			predict_label = predict_probability(model_, x, prob_estimates);
			printf("%d ", predict_label);
			for(j=0;j<model_->nr_class;j++)
				printf("%g ",prob_estimates[j]);
			printf("\n");
		}
		else
		{
			predict_label = predict(model_,x);
			printf("%d\n",predict_label);
		}
		fflush(stdout);

		if(predict_label == target_label)
			++correct;
		++total;
	}
	
	printf("Accuracy = %g%% (%d/%d)\n", (double)correct/total*100,correct,total);
	if(flag_predict_probability)
		free(prob_estimates);
}

void exit_with_help()
{
	printf(
	"Usage: predict [options] test_file model_file output_file\n"
	"options:\n"
	"-b probability_estimates: whether to output probability estimates, 0 or 1 (default 0)\n"
	);
	exit(1);
}

int main(int argc, char **argv)
{
	int i;

	// parse options
	for(i=1;i<argc;i++)
	{
		if(argv[i][0] != '-') break;
		++i;
		switch(argv[i-1][1])
		{
			case 'b':
				flag_predict_probability = atoi(argv[i]);
				break;

			default:
				fprintf(stderr,"unknown option\n");
				exit_with_help();
				break;
		}
	}
	if(i>=argc)
		exit_with_help();

	if((model_=load_model(argv[i]))==0)
	{
		fprintf(stderr,"can't open model file %s (argc: %d, i:%d)\n",argv[i], argc, i);
		exit(1);
	}

	line = (char *) malloc(max_line_len*sizeof(char));
	x = (struct feature_node *) malloc(max_nr_attr*sizeof(struct feature_node));
	do_predict_stdin(model_);
	destroy_model(model_);
	free(line);
	free(x);
	return 0;
}

