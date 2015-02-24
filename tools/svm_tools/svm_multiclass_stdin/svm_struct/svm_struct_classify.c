/***********************************************************************/
/*                                                                     */
/*   svm_struct_classify.c                                             */
/*                                                                     */
/*   Classification module of SVM-struct.                              */
/*                                                                     */
/*   Author: Thorsten Joachims                                         */
/*   Date: 03.07.04                                                    */
/*                                                                     */
/*   Copyright (c) 2004  Thorsten Joachims - All rights reserved       */
/*                                                                     */
/*   This software is available for non-commercial use only. It must   */
/*   not be modified and distributed without prior permission of the   */
/*   author. The author is not responsible for implications from the   */
/*   use of this software.                                             */
/*                                                                     */
/************************************************************************/

#include <stdio.h>
#ifdef __cplusplus
extern "C" {
#endif
#include "../svm_light/svm_common.h"
#ifdef __cplusplus
}
#endif
#include "../svm_struct_api.h"
#include "svm_struct_common.h"

char modelfile[200];

void read_input_parameters(int, char **, char *, 
			   STRUCT_LEARN_PARM *, long*, long *);
void print_help(void);


int main (int argc, char* argv[])
{
  long correct=0,incorrect=0,no_accuracy=0;
  long i;
  double t1,runtime=0;
  double avgloss=0,l;
  STRUCTMODEL model; 
  STRUCT_LEARN_PARM sparm;
  STRUCT_TEST_STATS teststats;
  SAMPLE testsample;
  LABEL y;

  char *line = NULL;
  size_t size = 1024;

  svm_struct_classify_api_init(argc,argv);

  read_input_parameters(argc,argv,modelfile,&sparm,
			&verbosity,&struct_verbosity);

  model=read_struct_model(modelfile,&sparm);
  printf("Reading model done\n"); fflush(stdout);

  if(model.svm_model->kernel_parm.kernel_type == LINEAR) { /* linear kernel */
    /* compute weight vector */
    add_weight_vector_to_linear_model(model.svm_model);
    model.w=model.svm_model->lin_weights;
  }
  
  while (1) {
	  getline(&line, &size, stdin);

	  if (line[0] == '\n')
	  {
		  break;
	  }

    testsample=read_struct_examples(line,&sparm);
    t1=get_runtime();
    y=classify_struct_example(testsample.examples[0].x,&model,&sparm);
    runtime+=(get_runtime()-t1);

    //write_label(predfl,y);
	fprintf(stdout,"%d",y.class); 
	if(y.scores) 
    for(i=1;i<=y.num_classes;i++)
      fprintf(stdout," %f",y.scores[i]);
	fprintf(stdout, "\n");
	fflush(stdout);

    free_label(y);
	free_struct_sample(testsample);
  
  }  
  avgloss/=testsample.n;
  
  free(line);

  free_struct_model(model);

  svm_struct_classify_api_exit();

  return(0);
}

void read_input_parameters(int argc,char *argv[],
			   char *modelfile,
			   STRUCT_LEARN_PARM *struct_parm,
			   long *verbosity,long *struct_verbosity)
{
  long i;
  
  /* set default */
  strcpy (modelfile, "svm_model");
  (*verbosity)=0;/*verbosity for svm_light*/
  (*struct_verbosity)=1; /*verbosity for struct learning portion*/
  struct_parm->custom_argc=0;

  for(i=1;(i<argc) && ((argv[i])[0] == '-');i++) {
    switch ((argv[i])[1]) 
      { 
      case 'h': print_help(); exit(0);
      case '?': print_help(); exit(0);
      case '-': strcpy(struct_parm->custom_argv[struct_parm->custom_argc++],argv[i]);i++; strcpy(struct_parm->custom_argv[struct_parm->custom_argc++],argv[i]);break; 
      case 'v': i++; (*struct_verbosity)=atol(argv[i]); break;
      case 'y': i++; (*verbosity)=atol(argv[i]); break;
      default: printf("\nUnrecognized option %s!\n\n",argv[i]);
	       print_help();
	       exit(0);
      }
  }

  strcpy (modelfile, argv[i]);
 
  parse_struct_parameters_classify(struct_parm);
}

void print_help(void)
{
  printf("\nSVM-struct classification module: %s, %s, %s\n",INST_NAME,INST_VERSION,INST_VERSION_DATE);
  printf("   includes SVM-struct %s for learning complex outputs, %s\n",STRUCT_VERSION,STRUCT_VERSION_DATE);
  printf("   includes SVM-light %s quadratic optimizer, %s\n",VERSION,VERSION_DATE);
  copyright_notice();
  printf("   usage: svm_struct_classify [options] example_file model_file output_file\n\n");
  printf("options: -h         -> this help\n");
  printf("         -v [0..3]  -> verbosity level (default 2)\n\n");

  print_struct_help_classify();
}




