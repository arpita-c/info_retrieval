#!/usr/bin/python

import sys
import csv
from stemming.porter2 import stem
from operator import or_
import os
import operator


term_dictionary={}
docstable_dict={}


def file_fetcher():
	if len(sys.argv) < 4:
		print("Usage: ./assignment_part_c.py <Dictionary_file_path> <Posting_file_path> <DocsTable_file_path>")
		sys.exit(1)
	else:
		fetch_files()



# Dictionary.csv DocsTable.txt Postings.csv
def getdocno(file):
	docno=file.split(".")[0]
	return int(docno)		



def fetch_files():

	dictionary_file = open(sys.argv[1], "rb")
	dictionary_reader = list(csv.reader(dictionary_file, delimiter='\t'))

	posting_file = open(sys.argv[2], "rb")
	posting_reader = list(csv.reader(posting_file, delimiter='\t'))

	
	with open(sys.argv[3]) as docstable_file:
		contents = docstable_file.read().splitlines()

	contents=contents[1:]
	
	for content in contents: 	
		if len(content.strip())<=1:
			continue
		content_split=content.split("\t")
		file_name=str(content_split[0])
		title=str(content_split[1])
		reviewer=str(content_split[2])
		snippet=str(content_split[3])
		rate=str(content_split[4])
		doc_no=getdocno(file_name)
		tempdict={"filename":file_name,"title":title,"reviewer":reviewer,"snippet":snippet,"rate":rate}
		docstable_dict[doc_no]=tempdict
	
	
	dictionary_reader=dictionary_reader[1:]
	posting_reader=posting_reader[1:]

	for item in dictionary_reader:

		
		term=item[0]
		df=item[1]
		offset=item[2]
		offset_start=int(offset)
		offset_end=int(offset)+int(df)-1
		doc_no=[]
		if(int(df)>1):
			posting_list_term=posting_reader[offset_start:offset_end]
			posting_list_term=list(posting_list_term)
			for doc_term in posting_list_term:
				doc_no.append(int(doc_term[0]))			
		else:
			posting_list_term=posting_reader[offset_start][0]
			doc_no.append(int(posting_list_term))
			
		term_dictionary[term]={}
		term_dictionary[term]["df"]=df
		term_dictionary[term]["offset"]=offset
		term_dictionary[term]["doc_no"]=doc_no





def stop_word_remover(query_sentence):
	useless_words = ["and", "a", "the", "an", "by", "from", "for", "hence", "of", "the", "with", "in", "within", "who", "when", "where", "why", "how", "whom", "have", "had", "has", "not", "for", "but", "do", "does", "done"]
	resultwords  = [word for word in query_sentence if word not in useless_words]
	return resultwords



def user_input():
	dirpath = os.getcwd()
	outputfilepath=os.path.join(dirpath, "output.txt")
	doctable_file=open(outputfilepath,'w')

	while True:
		user_input = raw_input("prompt>")
		if user_input.lower() == "exit":
			doctable_file.write("\n Query-> ")
			doctable_file.write(user_input+"\n ")			
			doctable_file.close()
			sys.exit(0)
	
		result_doc_id = []
		input_list = user_input.split()
		if(len(input_list)==0):
			continue
		
		if input_list[0] == 'AND':
			result_doc_id=and_parser(user_input)
				
		elif input_list[0] == 'OR':
			result_doc_id=or_parser(user_input)
			
		else:
			
			print("Invalid query! Support Query types: AND <query_words>, AND <query_words> AND NOT <query_words>, OR <query_words>")
			doctable_file.write("\n Query-> ")
			doctable_file.write(user_input+"\n ")
			doctable_file.write("\n Result:: \n ")
			doctable_file.write("Invalid query! Support Query types: AND <query_words>, AND <query_words> AND NOT <query_words>, OR <query_words>")			
			doctable_file.write("\n \n ")
			continue



		#create a output file
		
		doctable_file.write("\n Query-> ")
		doctable_file.write(user_input+"\n ")
		doctable_file.write("\n Result:: \n ")
		
		resultlist = []

		if result_doc_id!=[]:
			for doc_id in result_doc_id:
		
				resultlist.append(docstable_dict[int(doc_id)])

			#Sort the list per Rate and filename			
			resultlist=sorted(resultlist, key=operator.itemgetter('rate'), reverse=True)

			#Get the resultset based on rate
			positive_list=[]
			negative_list=[]
			na_list=[]

			for result in resultlist:
				if(result['rate']=='P'):
					positive_list.append(result)
				if(result['rate']=='N'):
					negative_list.append(result)
				if(result['rate']=='NA'):
					na_list.append(result)

			positive_list=sorted(positive_list, key=operator.itemgetter('filename'))	
			negative_list=sorted(negative_list, key=operator.itemgetter('filename'))		
			na_list=sorted(na_list, key=operator.itemgetter('filename'))		

			resultlist=positive_list+negative_list+na_list


			finalstr=""
			#Get the final output
			doctable_file.write("\n \n")
			print("Filename \t  title  \t  reviewer \t  snippet  \t  rate")
			doctable_file.write("Filename \t  title  \t  reviewer \t  snippet  \t  rate")
			for result in resultlist:

				finalstr=result["filename"]+"\t"+result["title"]+"\t"+result["reviewer"]+"\t"+result["snippet"]+"\t"+result["rate"]
				doctable_file.write(finalstr)
				doctable_file.write("\n \n")
				print finalstr
				print "\n"


		elif(result_doc_id == []):
			print "No Result"
			doctable_file.write("No Result")
			doctable_file.write("\n \n")


    

				
	
def process_and_query(result_and_query_stopword_removed):

	result_doc_list=[]
	for queryterm in result_and_query_stopword_removed:
		#print queryterm
		if queryterm in term_dictionary:
			#Get the document _number list
			result_doc_list.append(set(term_dictionary[queryterm]["doc_no"])) 
		else:
	    	#stem the word
			
			queryterm=stem(queryterm)
			if queryterm in term_dictionary:
				result_doc_list.append(set(term_dictionary[queryterm]["doc_no"]))
				
			else:
				print ("QueryTerm "+queryterm+ " not found")

	#Get the intersection of the list
	
	if result_doc_list!=[]:
		intersected_docid=reduce((lambda x,y : x&y),result_doc_list)
		return list(intersected_docid)
	else:
		return []	




def process_or_query(result_and_query_stopword_removed):

	result_doc_list=[]
	for queryterm in result_and_query_stopword_removed:
		#print queryterm
		if queryterm in term_dictionary:
			#Get the document _number list
			
			result_doc_list.append(set(term_dictionary[queryterm]["doc_no"]))
		else:
	    	#stem the word
			queryterm=stem(queryterm)
			if queryterm in term_dictionary:
				
				result_doc_list.append(set(term_dictionary[queryterm]["doc_no"]))
			else:
				print ("QueryTerm "+queryterm+ " not found")

	#Get the union of the list
	
	if result_doc_list!=[]:
		unionlist_docid=reduce(or_,result_doc_list)
		return list(unionlist_docid)
	else:	
		return []	






def and_parser(user_input):
	user_input = user_input.strip()
	result_and_query=[]
	result_and_not_query=[]
	result_doc_id=[]
	if "AND NOT" in user_input:
		and_not_index = user_input.index("AND NOT")

	
		result_and_query_processed1=[item.lower() for item in user_input[:and_not_index].split()[1:]]
		result_and_query_stopword_removed=stop_word_remover(result_and_query_processed1)
		#print result_and_query_stopword_removed
		doc_number_and_query=process_and_query(result_and_query_stopword_removed)

		#result_and_not_query = user_input[and_not_index:].split()
		result_and_not_query_processed1=[item.lower() for item in user_input[and_not_index:].split()[2:]]
		result_and_not_query_stopword_removed=stop_word_remover(result_and_not_query_processed1)
		doc_number_and_not_query=process_and_query(result_and_not_query_stopword_removed)
		#print doc_number_and_not_query
		result_doc_id=list(set(doc_number_and_query)-set(doc_number_and_not_query))
		#print result_doc_id
		return result_doc_id

	else:
		#result_and_query = user_input.split()[1:]
		result_and_query=[item.lower() for item in user_input.split()[1:]]
		result_and_query_stopword_removed=stop_word_remover(result_and_query)
		result_doc_id=process_and_query(result_and_query_stopword_removed)
		#print result_doc_id
		return result_doc_id
		
	
	
def or_parser(user_input):
	user_input = user_input.strip()
	#result_or_query = stop_word_remover(result_or_query[1:].lower().split())
	result_or_query=[item.lower() for item in user_input.split()[1:]]
	result_or_query_stopword_removed=stop_word_remover(result_or_query)
	result_doc_id=process_or_query(result_or_query_stopword_removed)
	#print result_doc_id
	return result_doc_id
	


if __name__ == '__main__':
	
	file_fetcher()
	user_input()