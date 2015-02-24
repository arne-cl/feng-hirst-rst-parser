#!/local/all/perl -w
##!/usr/bin/perl -w 
#
# Sentence splitter
# By Marcia Munoz
#
# Modified by Ramya Nagarajan 6/19/01
#
# This program checks candidates to see if they are valid sentence boundaries.
# Its input is a text file, and its output is another text file where each text
# line corresponds to one sentence.

use Getopt::Std;

# Get the command-line arguments
getopt('hiod');

if (defined ($opt_h) || !defined ($opt_i) || !defined ($opt_d))
{
   $opt_h = 1;
   print "Usage: boundary.pl -d honorifics_file -i input_file\n";
   exit;
}

# Open the parameters file, and read its contents into the @honorifics array
open (HONORIFICS, $opt_d) || die "Couldn't open file $opt_d: !$\n";

while (<HONORIFICS>){
   chomp($_);
   push(@honorifics, $_);
}

# Open the corpus file
open(INPUT, $opt_i) || die "Cannot open $opt_i: $!";

# Check for an empty file
if (eof INPUT)
{
   print "$opt_i is an empty file!\n";
   exit;
}

$paragraph = "";

# Main loop
while (!eof INPUT)
{
   # Read a line
   $newline = <INPUT>;

   if ($newline =~ /^\s+$/)   # If next line is empty
   {
      Process($paragraph);
      $paragraph = "";
      print STDOUT "\n";
   }
   else                       # If next line is not empty
   {
      # Eliminate any leading whitespace
      while (substr($newline, 0, 1) =~ /\s+/)
      {
         $newline = substr($newline, 1);
      }

      # Take care of the hyphens
      chomp($paragraph);
      if (substr($paragraph, -1, 1) eq "-" && substr($paragraph, -2, 1) ne "-")
      {
         $paragraph = join '', substr($paragraph, 0, $#paragraph), $newline;
      }
      else
      {
         $paragraph = join ' ', $paragraph, $newline;
      }
   }
}
Process($paragraph);
         
sub Process
{
   my($paragraph) = @_;

   # Split the paragraph into words
   @words = split(" ", $paragraph);

   $sentence = "";

   for $i (0..$#words)
   {
      $newword = $words[$i];

      # Print the words
      #print "word is: ($newword)\n";


	  # Added by Ramya Nagarajan. 6/18/01.
	  # Deal with SGML tags in TREC text.
	  if($words[$i] =~ /<\/[A-Z]+>$/ or 
             $words[$i] eq "<TEXT>" or
             $words[$i] eq "<DOC>") {
		# print "word is $words[$i]\n";
		
		# Append the word to the sentence
		$sentence = join ' ', $sentence, $words[$i];
		
		# Eliminate any leading whitespace
		$sentence = substr($sentence, 1);
		
		print STDOUT $sentence, "\n";
		$sentence = "";
	  }
	  else {
		# Check the existence of a candidate
		$period_pos = rindex($newword, ".");
		$question_pos = rindex($newword, "?");
		$exclam_pos = rindex($newword, "!");
		
		# Determine the position of the rightmost candidate in the word
		$pos = $period_pos;
		$candidate = ".";
		if ($question_pos > $period_pos)
		  {
			$pos = $question_pos;
			$candidate = "?";
		  }
		if ($exclam_pos > $pos)
		  {
			$pos = $exclam_pos;
			$candidate = "!";
		  }

		# Do the following only if the word has a candidate
		if ($pos != -1)
		  {
			# Check the previous word
			if (!defined($words[$i - 1]))
			  {
				$wm1 = "NP";
				$wm1C = "NP";
				$wm2 = "NP";
				$wm2C = "NP";
			  }
			else
			  {
				$wm1 = $words[$i - 1];
				$wm1C = Capital($wm1);
				
				# Check the word before the previous one 
				if (!defined($words[$i - 2]))
				  {
					$wm2 = "NP";
					$wm2C = "NP";
				  }
				else
				  {
					$wm2 = $words[$i - 2];
					$wm2C = Capital($wm2);
				  }
			  }
			# Check the next word
			if (!defined($words[$i + 1]))
			  {
				$wp1 = "NP";
				$wp1C = "NP";
				$wp2 = "NP";
				$wp2C = "NP";
			  }
			else
			  {
				$wp1 = $words[$i + 1];
				$wp1C = Capital($wp1);
				
				# Check the word after the next one 
				if (!defined($words[$i + 2]))
				  {
					$wp2 = "NP";
					$wp2C = "NP";
				  }
				else
				  {
					$wp2 = $words[$i + 2];
					$wp2C = Capital($wp2);
				  }
			  }
			
			# Define the prefix
			if ($pos == 0)
			  {
				$prefix = "sp";
			  }
			else
			  {
				$prefix = substr($newword, 0, $pos);
			  }
			$prC = Capital($prefix);
			
			# Define the suffix
			if ($pos == length($newword) - 1)
			  {
				$suffix = "sp";
			  }
			else
			  {
				$suffix = substr($newword, $pos + 1, length($newword) - $pos);
			  }
			$suC = Capital($suffix);
			
			# Call the Sentence Boundary subroutine
			$prediction = Boundary($candidate, $wm2, $wm1, $prefix, $suffix, 
								   $wp1, $wp2, $wm2C, $wm1C, $prC, $suC, 
								   $wp1C, $wp2C);
			
			# Append the word to the sentence
			$sentence = join ' ', $sentence, $words[$i];
			if ($prediction eq "Y")
			  {
				# Eliminate any leading whitespace
				$sentence = substr($sentence, 1);
				
				print STDOUT $sentence, "\n";
				$sentence = "";
			  }
		  }
		else
		  { 
			# If the word doesn't have a candidate, then append the word to the sentence
			$sentence = join ' ', $sentence, $words[$i];
		  }
	  }
	}

   if ($sentence ne "")
   {
      # Eliminate any leading whitespace
      $sentence = substr($sentence, 1);

      print STDOUT $sentence, "\n";
      $sentence = "";
   }
}

# This subroutine returns "Y" if the argument starts with a capital letter.
sub Capital
{
   my ($substring);

   $substring = substr($_[0], 0, 1);
   if ($substring =~ /[A-Z]/)
   {
      return "Y";
   }
   else
   {
      return "N";
   }
}

# This subroutine does all the boundary determination stuff
# It returns "Y" if it determines the candidate to be a sentence boundary,
# "N" otherwise
sub Boundary
{
   # Declare local variables
   my($candidate, $wm2, $wm1, $prefix, $suffix, $wp1, $wp2, $wm2C, $wm1C, $prC, $suC, $wp1C, $wp2C) = @_;


   # Check if the candidate was a question mark or an exclamation mark
   if ($candidate eq "?" || $candidate eq "!")
   {
      # Check for the end of the file
      if ($wp1 eq "NP" && $wp2 eq "NP")
      {
         return "Y";
      }
      # Check for the case of a question mark followed by a capitalized word
      if ($suffix eq "sp" && $wp1C eq "Y")               
      {
         return "Y";
      }
      if ($suffix eq "sp" && StartsWithQuote($wp1))
      {
         return "Y";
      }
      if ($suffix eq "sp" && $wp1 eq "--" && $wp2C eq "Y") 
      {
         return "Y";
      }
      if ($suffix eq "sp" && $wp1 eq "-RBR-" && $wp2C eq "Y")
      {
         return "Y";
      }
      # This rule takes into account vertical ellipses, as shown in the
      # training corpus. We are assuming that horizontal ellipses are
      # represented by a continuous series of periods. If this is not a
      # vertical ellipsis, then it's a mistake in how the sentences were
      # separated.
      if ($suffix eq "sp" && $wp1 eq ".")
      {
         return "Y";
      }
      if (IsRightEnd($suffix) && IsLeftStart($wp1))
      {
         return "Y";
      }
      else 
      {
         return "N";
      }
   }
   else
   {
      # Check for the end of the file
      if ($wp1 eq "NP" && $wp2 eq "NP")
      {
         return "Y";
      }
      if ($suffix eq "sp" && StartsWithQuote($wp1))
      {
         return "Y";
      }
      if ($suffix eq "sp" && StartsWithLeftParen($wp1))
      {
         return "Y";
      }
      if ($suffix eq "sp" && $wp1 eq "-RBR-" && $wp2 eq "--")
      {
         return "N";
      }
      if ($suffix eq "sp" && IsRightParen($wp1))
      {
         return "Y";
      }
	  # Added by Ramya Nagarajan 6/19/01
	  # This takes account of the numbered lists seen in the TREC/TIPSTER_V3
	  # data files.
	  if ($candidate eq "." && $suffix eq "sp" && 
		  EndsWithRightParen($wp1) && $wp2C eq "Y")
		{
		  return "Y";
		}
      # This rule takes into account vertical ellipses, as shown in the
      # training corpus. We are assuming that horizontal ellipses are
      # represented by a continuous series of periods. If this is not a
      # vertical ellipsis, then it's a mistake in how the sentences were
      # separated.
      if ($prefix eq "sp" && $suffix eq "sp" && $wp1 eq ".")
      {
         return "N";
      }
      if ($suffix eq "sp" && $wp1 eq ".")
      {
         return "Y";
      }
      if ($suffix eq "sp" && $wp1 eq "--" && $wp2C eq "Y" 
            && EndsInQuote($prefix))
      {
         return "N";
      }
      if ($suffix eq "sp" && $wp1 eq "--" && ($wp2C eq "Y" || 
               StartsWithQuote($wp2)))
      {
         return "Y";
      }
      if ($suffix eq "sp" && $wp1C eq "Y" && 
           ($prefix eq "p.m" || $prefix eq "a.m") && IsTimeZone($wp1))
      {
         return "N";
      }
      # Check for the case when a capitalized word follows a period,
      # and the prefix is a honorific
      if ($suffix eq "sp" && $wp1C eq "Y" && IsHonorific($prefix."."))
      {
         return "N";
      }
      # Check for the case when a capitalized word follows a period,
      # and the prefix is a honorific
      if ($suffix eq "sp" && $wp1C eq "Y" && StartsWithQuote($prefix))
      {
         return "N";
      }
      # This rule checks for prefixes that are terminal abbreviations
      if ($suffix eq "sp" && $wp1C eq "Y" && IsTerminal($prefix))
      {
         return "Y";
      }
      # Check for the case when a capitalized word follows a period and the
      # prefix is a single capital letter
      if ($suffix eq "sp" && $wp1C eq "Y" && $prefix =~ /^([A-Z]\.)*[A-Z]$/)
      {
         return "N";
      }
      # Check for the case when a capitalized word follows a period
      if ($suffix eq "sp" && $wp1C eq "Y")               
      {
         return "Y";
      }
      if (IsRightEnd($suffix) && IsLeftStart($wp1))
      {
         return "Y";
      }
   }
   return "N";
}


# This subroutine checks to see if the input string is equal to an element
# of the @honorifics array.
sub IsHonorific
{
   my($word) = @_;
   my($newword);

   foreach $newword (@honorifics)
   {
      if ($newword eq $word)
      {
         return 1;      # 1 means true
      }
   }
   return 0;            # 0 means false
}

# This subroutine checks to see if the string is a terminal abbreviation.
sub IsTerminal
{
   my($word) = @_;
   my($newword);
   my(@terminals) = ("Esq", "Jr", "Sr", "M.D");

   foreach $newword (@terminals)
   {
      if ($newword eq $word)
      {
         return 1;      # 1 means true
      }
   }
   return 0;            # 0 means false
}

# This subroutine checks if the string is a standard representation of a U.S.
# timezone
sub IsTimeZone
{
   my($word) = @_;
   
   $word = substr($word,0,3);
   if ($word eq "EDT" || $word eq "CST" || $word eq "EST")
   {
      return 1;
   }
   else
   {
      return 0;
   }
}

# This subroutine checks to see if the input word ends in a closing double
# quote.
sub EndsInQuote 
{
   my($word) = @_;

   if (substr($word,-2,2) eq "''" || substr($word,-1,1) eq "'" || 
         substr($word, -3, 3) eq "'''" || substr($word,-1,1) eq "\""
         || substr($word, -2,2) eq "'\"")
   {
      return 1;         # 1 means true
   }
   else
   {
      return 0;         # 0 means false
   }
}

# This subroutine checks to see if a given word starts with one or more quotes
sub StartsWithQuote 
{
   my($word) = @_;

   if (substr($word,0,1) eq "'" ||  substr($word,0,1) eq "\"" || 
         substr($word, 0, 1) eq "`")
   {
      return 1;         # 1 means true
   }
   else
   {
      return 0;         # 0 means false
   }
}

# This subroutine checks to see if a word starts with a left parenthesis, be it
# {, ( or <
sub StartsWithLeftParen 
{
   my($word) = @_;

   if (substr($word,0,1) eq "{" || substr($word,0,1) eq "(" 
         || substr($word,0,5) eq "-LBR-")
   {
      return 1;         # 1 means true
   }
   else
   {
      return 0;         # 0 means false
   }
}

# Added by Ramya Nagarajan 6/19/01
# This subroutine checks to see if a word ends with a right parenthesis, be it
# }, ) or >
sub EndsWithRightParen 
{
   my($word) = @_;

   if (($word =~ /\}$/) or ($word =~ /\)$/) or ($word =~ /-LBR-$/))
   {
      return 1;         # 1 means true
   }
   else
   {
      return 0;         # 0 means false
   }
}


# This subroutine checks to see if a word starts with a left quote, be it
# `, ", "`, `` or ```
sub StartsWithLeftQuote 
{
   my($word) = @_;

   if (substr($word,0,1) eq "`" || substr($word,0,1) eq "\"" 
         || substr($word,0,2) eq "\"`")
   {
      return 1;         # 1 means true
   }
   else
   {
      return 0;         # 0 means false
   }
}


sub IsRightEnd
{
   my($word) = @_;
   
   if (IsRightParen($word) || IsRightQuote($word))
   {
      return 1;
   }
   else
   {
      return 0;
   }
}

# This subroutine detects if a word starts with a start mark.
sub IsLeftStart
{
   my($word) = @_;

   if(StartsWithLeftQuote($word) || StartsWithLeftParen($word) 
         || Capital($word) eq "Y")
   {
      return 1;
   }
   else
   {
      return 0;
   }
}

# This subroutine checks to see if a word is a right parenthesis, be it ), }
# or >
sub IsRightParen 
{
   my($word) = @_;

   if ($word eq "}" ||  $word eq ")" || $word eq "-RBR-")
   {
      return 1;         # 1 means true
   }
   else
   {
      return 0;         # 0 means false
   }
}

sub IsRightQuote
{
   my($word) = @_;

   if ($word eq "'" ||  $word eq "''" || $word eq "'''" || $word eq "\"" 
         || $word eq "'\"")
   {
      return 1;         # 1 means true
   }
   else
   {
      return 0;         # 0 means false
   }
}

# This subroutine prints out the elements of an array.
sub PrintArray
{
   my($word);

   foreach $word (@_)
   {
      print "Array Element = ($word)\n";
   }
}

# This subroutine reads a line from the input file. If the end of the input file
# is reached, it returns undef
sub ReadLine
{
   my($endoffile, $line, $startpos, $newline);

   # Get a non-blank sentence from the corpus file
   while ((($endoffile = eof INPUT) != 1) && (($line = <INPUT>) =~ /^\s+$/))
   {
      # Print a blank line
      print STDOUT "\n";
   }

   # Check for an empty file
   if ($endoffile == 1)
   {
      return undef;
   }

   # Eliminate the trailing carriage return
   chomp $line;

   # Eliminate any leading whitespace
   while(substr($line, 0, 1) =~ /\s+/)
   {
      $line = substr($line, 1);
   }

   return $line;
}
