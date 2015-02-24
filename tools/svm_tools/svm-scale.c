/*
	scale attributes to [lower,upper]
	usage: scale [-l lower] [-u upper] [-y y_lower y_upper] 
		     [-s filename] [-r filename] filename
*/
#include <float.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

char *line;
int max_line_len = 1024*1024;
double lower=-1.0,upper=1.0,y_lower,y_upper;
int y_scaling = 0;
double *feature_max;
double *feature_min;
double y_max = -DBL_MAX;
double y_min = DBL_MAX;
int max_index;

#define max(x,y) ((x>y)?x:y)
#define min(x,y) ((x<y)?x:y)

void output_target(double value);
void output(int index, double value);
char* readline(FILE *input);

int main(int argc,char **argv)
{
	int i,index;
	FILE *fp;
	char *save_filename = NULL;
	char *restore_filename = NULL;

	for(i=1;i<argc;i++)
	{
		if(argv[i][0] != '-') break;
		++i;
		switch(argv[i-1][1])
		{
			case 'r': restore_filename = argv[i]; break;
			default:
				fprintf(stderr,"unknown option\n");
				exit(1);
		}
	}

	line = (char *) malloc(max_line_len*sizeof(char));

	
	if(restore_filename)
	{
		FILE *fp = fopen(restore_filename, "r");
		int idx, c;
		double fmin, fmax;
		
		if(fp==NULL)
		{
			fprintf(stderr,"can't open file %s\n", restore_filename);
			exit(1);
		}
		
		if((c = fgetc(fp)) == 'y')
		{
			fscanf(fp, "%lf %lf\n", &y_lower, &y_upper);
			fscanf(fp, "%lf %lf\n", &y_min, &y_max);
			y_scaling = 1;
		}
		else
			ungetc(c, fp);

		if (fgetc(fp) == 'x')
		{
			fscanf(fp, "%lf %lf\n", &lower, &upper);
			max_index = 0;
			while(fscanf(fp,"%d %lf %lf\n",&idx,&fmin,&fmax)==3)
			{
				max_index = max(max_index, idx);
			}
			
			feature_max = (double *)malloc((max_index+1)* sizeof(double));
			feature_min = (double *)malloc((max_index+1)* sizeof(double));
			
			if(feature_max == NULL || feature_min == NULL)
			{
				fprintf(stderr,"can't allocate enough memory\n");
				exit(1);
			}

			rewind(fp);
			fgetc(fp); // dirty
			fscanf(fp, "%lf %lf\n", &lower, &upper); // dirty
			
			while(fscanf(fp,"%d %lf %lf\n",&idx,&fmin,&fmax)==3)
			{
				if(idx<=max_index)
				{
					feature_min[idx] = fmin;
					feature_max[idx] = fmax;
				}
			}
		}
			
		fclose(fp);
	}
	else
	{
		printf("Need a scale file\n");
		exit(-1);
	}


#define SKIP_TARGET\
	while(isspace(*p)) ++p;\
	while(!isspace(*p)) ++p;

#define SKIP_ELEMENT\
	while(*p!=':') ++p;\
	++p;\
	while(isspace(*p)) ++p;\
	while(*p && !isspace(*p)) ++p;
	
	char *p;
	int next_index=1;
	double target;
	double value;
	printf("Ready:\n");
	fflush(stdout);
	
	while(1)
	{
		
	// read from stdin
		fgets(line, max_line_len, stdin);
		if(line[0] == '\n')
			break;
		if(line[0] == '#')
			continue;
			
		//printf("\n** %d **\n", strlen(line));
		p = line;
				
		sscanf(p,"%lf",&target);
		output_target(target);

		SKIP_TARGET

		while(sscanf(p, "%d:%lf", &index, &value)==2)
		{
			for(i=next_index; i<index; i++)
				output(i, 0);
			
			output(index,value);

			SKIP_ELEMENT
			next_index=index+1;
		}
		
		for(i=next_index;i<=max_index;i++)
			output(i,0);
			
		printf("\n");
		fflush(stdout);
	}

	free(line);
	return 0;
}

char* readline(FILE *input)
{
	int len;
	
	if(fgets(line,max_line_len,input) == NULL)
		return NULL;

	while(strrchr(line,'\n') == NULL)
	{
		max_line_len *= 2;
		line = (char *) realloc(line, max_line_len);
		len = strlen(line);
		if(fgets(line+len,max_line_len-len,input) == NULL)
			break;
	}
	return line;
}

void output_target(double value)
{
	if(y_scaling)
	{
		if(value == y_min)
			value = y_lower;
		else if(value == y_max)
			value = y_upper;
		else value = y_lower + (y_upper-y_lower) *
			     (value - y_min)/(y_max-y_min);
	}
	printf("%g ",value);
}

void output(int index, double value)
{
	/* skip single-valued attribute */
	if(feature_max[index] == feature_min[index])
		return;

	if(value == feature_min[index])
		value = lower;
	else if(value == feature_max[index])
		value = upper;
	else
		value = lower + (upper-lower) * 
			(value-feature_min[index])/
			(feature_max[index]-feature_min[index]);

	if(value != 0)
		printf("%d:%g ",index, value);
}

