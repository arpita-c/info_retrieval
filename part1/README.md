Information Retreival
---------------------

Project Part 1
--------------

This project implements a HTML document indexer which parses a HTML document,
extracts all text from it and generates its index and stores the same into a file.

The program accepts 2 parameteres, input file and the output file.
The input file is the HTML file which has to be parsed and indexed.
The output file is the file to which the indeces are stored to.

The program implements the following functionalities:

1. Extracts all text between HTML tags.
2. Converts all text to lower case.
3. Removes the list of words from the text. The word list is
   "and, a, the, an, by, from, for, hence, of, the, with, in, within, who,
   when, where, why, how, whom, have, had, has, not, for, but, do, does, done"
4. Removes single charecters.
5. Seperates hyphenated charecters into 2 words.
6. Removes leading brackets ('(', '[') and quotes ('\'', '\"')
7. Removes trailing brackets ('(', '[') and quotes ('\'', '\"')
8. Removes charecters if they are only special characters.
9. Indexes everything else including numbers.
10. Deletes all apostrophes.
11. performs stemming.
12. Handles extra spaces, newlines, etc.
13. Sorts the indeces before writing them to the file.


To run the program, use the following command:

$python <program_name.py> <input_file_path> <output_file_path>

Example: $python assignmentP1.py /home/user/0002.html dictionary.txt
