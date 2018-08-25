from bs4 import BeautifulSoup as bs
import re
from stemming.porter2 import stem
import getopt
import sys

if len(sys.argv) < 3:
	print("Input and output path required!")
	print("Execution format: python <program_name.py> <input_file_path> <output_file_path>")
	sys.exit(2)
else:
	input_file = str(sys.argv[1])
	output_file = str(sys.argv[2])


useless_words = ["and", "a", "the", "an", "by", "from", "for", "hence", "of", "the", "with", "in", "within", "who", "when", "where", "why", "how", "whom", "have", "had", "has", "not", "for", "but", "do", "does", "done"]

soup = bs(open(input_file), "html.parser")

# Get the text on the html through BeautifulSoup
text = soup.get_text()

#Lowercase all text
new_text = text.lower()
word_list = list(new_text.split())

#Chuck out all words in the list of non-required words
resultwords  = [word for word in word_list if word not in useless_words]
result = ' '.join(resultwords)

#Remove single charecters
result = re.sub(r'(?:^| )\w(?:$| )', ' ', result).strip()
result = list(result.split())

#Check for special charecters only! => (start(, (start, start(, [start, start[, [start[
result1 = list()
for item in result:
	if item.startswith('(') or item.startswith('['):
		result1.append(item[1:])
	elif item.endswith('(') or item.endswith('['):
		result1.append(item[:-1])
	elif (item.startswith('(') and item.endswith('(')) or (item.startswith('[') and item.endswith('[')):
		result1.append(item[1:-1])
	else:
		result1.append(item)

#print result1

#Remove all brackets and apostrophes, quotes etc
newList = [item.replace('\'', '') for item in result1]
newList = [item.replace('\"', '') for item in newList]

#Split by "-"
after_remove = ' '.join(newList)
after_remove = after_remove.split("-")
after_remove = ' '.join(after_remove)

#Remove single special characters
after_remove = re.sub(r'(?:^| )\W(?:$| )', ' ', after_remove) #\W = [^\w]

after_remove = list(after_remove.split())


#Stem the data
documents = [stem(word) for word in after_remove]

#Keep unique words only - Remove repeated words
#documents = set(documents)
#duplicate = set()
#result = []
#for item in documents:
#    if item not in duplicate:
#        duplicate.add(item)
#        result.append(item)

#Sort this list
#result.sort()
documents.sort()

file_to_write = open(output_file, 'w')

#for item in result:
for item in documents:
	file_to_write.write("%s\n" % item)

