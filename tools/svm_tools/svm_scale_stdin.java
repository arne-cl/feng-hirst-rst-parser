import libsvm.*;
import java.io.*;
import java.util.*;
import java.text.DecimalFormat;

class svm_scale_stdin
{
	private String line = null;
	private double lower = -1.0;
	private double upper = 1.0;
	private double y_lower;
	private double y_upper;
	private boolean y_scaling = false;
	private double[] feature_max;
	private double[] feature_min;
	private double y_max = -Double.MAX_VALUE;
	private double y_min = Double.MAX_VALUE;
	private int max_index;

	private static void exit_with_help()
	{
		System.out.print(
		 "Usage: svm-scale restore_fname\n"
		);
		System.exit(1);
	}

	private BufferedReader rewind(BufferedReader fp, String filename) throws IOException
	{
		fp.close();
		return new BufferedReader(new FileReader(filename));
	}

	private void output_target(double value)
	{
		if(y_scaling)
		{
			if(value == y_min)
				value = y_lower;
			else if(value == y_max)
				value = y_upper;
			else
				value = y_lower + (y_upper-y_lower) *
				(value-y_min) / (y_max-y_min);
		}

		System.out.print(value + " ");
	}

	private void output(int index, double value)
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
			System.out.print(index + ":" + value + " ");
	}

	private String readline(BufferedReader fp) throws IOException
	{
		line = fp.readLine();
		return line;
	}

	private void run(String []argv) throws IOException
	{
		int i,index;
		if(argv.length != 1)
			exit_with_help();
		
		String restore_filename = argv[0];
		
		/* pass 2.5: save/restore feature_min/feature_max */
		if(restore_filename != null)
		{
			BufferedReader fp_restore = null;
			try {
				fp_restore = new BufferedReader(new FileReader(restore_filename));
			}
			catch (Exception e) {
				System.err.println("can't open file " + restore_filename);
				System.exit(1);
			}

			int idx, c;
			double fmin, fmax;

			fp_restore.mark(2);				// for reset
			if((c = fp_restore.read()) == 'y')
			{
				fp_restore.readLine();		// pass the '\n' after 'y'
				StringTokenizer st = new StringTokenizer(fp_restore.readLine());
				y_lower = Double.parseDouble(st.nextToken());
				y_upper = Double.parseDouble(st.nextToken());
				st = new StringTokenizer(fp_restore.readLine());
				y_min = Double.parseDouble(st.nextToken());
				y_max = Double.parseDouble(st.nextToken());
				y_scaling = true;
			}
			else
				fp_restore.reset();

			if(fp_restore.read() == 'x') {
				fp_restore.readLine();		// pass the '\n' after 'x'
				StringTokenizer st = new StringTokenizer(fp_restore.readLine());
				lower = Double.parseDouble(st.nextToken());
				upper = Double.parseDouble(st.nextToken());
				String restore_line = null;
				while((restore_line = fp_restore.readLine())!=null)
				{
					StringTokenizer st2 = new StringTokenizer(restore_line);
					idx = Integer.parseInt(st2.nextToken());
					max_index = Math.max(max_index, idx);
				}
			}

			feature_max = new double[(max_index+1)];
			feature_min = new double[(max_index+1)];

			fp_restore = rewind(fp_restore, restore_filename);
			if(fp_restore.read() == 'x') {
				fp_restore.readLine();		// pass the '\n' after 'x'
				StringTokenizer st = new StringTokenizer(fp_restore.readLine());
				lower = Double.parseDouble(st.nextToken());
				upper = Double.parseDouble(st.nextToken());
				String restore_line = null;
				while((restore_line = fp_restore.readLine())!=null)
				{
					StringTokenizer st2 = new StringTokenizer(restore_line);
					idx = Integer.parseInt(st2.nextToken());
					fmin = Double.parseDouble(st2.nextToken());
					fmax = Double.parseDouble(st2.nextToken());
					//System.out.println(idx + " " + fmin + " " + fmax);
					if (idx <= max_index)
					{
						feature_min[idx] = fmin;
						feature_max[idx] = fmax;
					}
				}
			}
			fp_restore.close();
		}

		System.out.println("Loading restored file successfully!");
		/* pass 3: scale */
		BufferedReader input = new BufferedReader(new InputStreamReader(System.in));
		String line;
		while((line = input.readLine()) != null)
		{
			int next_index = 1;
			double target;
			double value;

			if (line.trim().equals(""))
				break;
			
			max_index = 0;
			StringTokenizer st = new StringTokenizer(line," \t\n\r\f:");
			/*st.nextToken();
			while(st.hasMoreElements())
			{
				index = Integer.parseInt(st.nextToken());
				max_index = Math.max(max_index, index);
				//System.out.println(index + " : " + max_index);
				st.nextToken();
			}

			try {
				feature_max = new double[(max_index+1)];
				feature_min = new double[(max_index+1)];
			} catch(OutOfMemoryError e) {
				System.err.println("can't allocate enough memory");
				System.exit(1);
			}

			for(i=0;i<=max_index;i++)
			{
				feature_max[i] = -Double.MAX_VALUE;
				feature_min[i] = Double.MAX_VALUE;
			}

			st = new StringTokenizer(line," \t\n\r\f:");*/
			target = Double.parseDouble(st.nextToken());
			output_target(target);
			while(st.hasMoreElements())
			{
				index = Integer.parseInt(st.nextToken());
				value = Double.parseDouble(st.nextToken());
				//System.out.println(index + ":" + value);
				for (i = next_index; i<index; i++)
					output(i, 0);
				output(index, value);
				next_index = index + 1;
			}

			for(i=next_index;i<= max_index;i++)
				output(i, 0);
			System.out.print("\n");
		}
	}

	public static void main(String argv[]) throws IOException
	{
		svm_scale_stdin s = new svm_scale_stdin();
		s.run(argv);
	}
}
