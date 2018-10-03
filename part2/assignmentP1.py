from bs4 import BeautifulSoup as bs
import re
from stemming.porter2 import stem
import getopt
import sys
import collections
import os
import csv
import urllib2
#import nltk
#from nltk.sentiment.vader import SentimentIntensityAnalyzer


document_frequency={}
frequency_doc_count={}
docsTable=[]


def generateDocsTable(filepath,filename,doc_no):

    positive_words=["best", "exciting", "outstanding"]
    negative_words=["dull","boring","disappointing","failure"]
            
    url="file://"+filepath
    page = urllib2.urlopen(url,"lxml")

    #print page
    soup = bs(page.read(),'lxml')

    ref_nodes_A_Tag = soup.find_all('a')
    
    #Get the title
    title=ref_nodes_A_Tag[0].text

    #Get the reviewer name
    reviewer=ref_nodes_A_Tag[1].text
    
    tempdict={}
    tempdict['Filename']=filename
    tempdict['Title']=title
    tempdict['Reviewer']=reviewer
   
    #Create a static snippet
    #In the some html static exists in the Pre tag. Capture those static snippet
    ref_nodes_PRE_Tag=soup.find_all('PRE')

    reviewdata_Capsule_PRE_flag=False
    reviewdata_Capsule_P_flag=False
 
    review=""
    remaining_words=0
 

    for ref_node in ref_nodes_PRE_Tag:
        #Get the text of the ref_node
        reviewdata=ref_node.text
        if "Capsule review" in reviewdata:
            reviewdata_Capsule_PRE_flag=True
            review=reviewdata
            count_of_review_words=len(review.split())

            if(count_of_review_words<50):
                remaining_words=50-count_of_review_words

            break
        else:
            continue    

                
            
    if(reviewdata_Capsule_PRE_flag==False):
        #Check within P tag data exists or not        
        ref_nodes_P_Tag_nodes = soup.find_all('p')
        for ref_node in ref_nodes_P_Tag_nodes:
            ref_nodes_P_Tag_data=ref_node.text
         
            if "Capsule review" in ref_nodes_P_Tag_data:
            #if str(ref_nodes_P_Tag_data).IndexOf("Capsule review", StringComparison.OrdinalIgnoreCase) >= 0:
                reviewdata_Capsule_P_flag=True
                review=ref_nodes_P_Tag_data
                count_of_review_words=len(review.split())        
                if(count_of_review_words<50):
                    remaining_words=50-count_of_review_words  
                    
            else:
                continue

    if(remaining_words>0 and len(review)>0 ):
       
        if(reviewdata_Capsule_P_flag == True):
            ref_nodes_P_Tag_data = soup.find_all('p')[1].text
            reviewlist=review.split()
            count=0
            for word in  ref_nodes_P_Tag_data.split():
                count=count+1
                if(count>remaining_words):
                    if (word == ".") or ("." in word):
                        reviewlist.append(word)
                        review=' '.join(reviewlist)
                        break
                    else:                           
                        review=' '.join(reviewlist)
                        continue
                else:    
                    reviewlist.append(word)

        elif(reviewdata_Capsule_PRE_flag ==True):            
            ref_nodes_P_Tag_data = soup.find_all('p')[0].text
            reviewlist=review.split()
            count=0
            for word in  ref_nodes_P_Tag_data.split():
                count=count+1
                if(count>remaining_words):
                    if (word == ".") or ("." in word):
                        reviewlist.append(word)
                        review=' '.join(reviewlist)
                        break                        
                    else:
                        reviewlist.append(word)
                        continue
                        

                else:    
                    reviewlist.append(word)
    
    else:
        
        ref_nodes_P_Tag_ref_nodes = soup.find_all('p')
        ref_nodes_P_Tag_data=""
        for ref_node in ref_nodes_P_Tag_ref_nodes:
            ref_nodes_P_Tag_data=ref_nodes_P_Tag_data+ref_node.text+" "

        reviewlist=[]
        count=0
        for word in  ref_nodes_P_Tag_data.split():
            count=count+1

            if(count>50):
                if (word == ".") or ("." in word):
                    reviewlist.append(word)
                    #review=' '.join(reviewlist)
                    break                        
                else:
                    reviewlist.append(word)
                    continue
                     
            else:    
                reviewlist.append(word)


    review=' '.join(reviewlist)            
    tempdict['Snippet']=' '.join(reviewlist)
    pagetext=""
    #Generate the Rate of the document
    try:
        pagetext=soup.get_text()
        if("\\xdft" in pagetext):
            pagetext=pagetext.replace("\xdft"," ")
    except Exception as e:
        print str(e.message)+"::"+str(e.args)
        pass

    #print pagetext        

    pagetextlowercase=pagetext.lower()
    #pagetext=pagetext.replace("","")
    #index=pagetextlowercase.find(pattern)
    pagetextList=pagetext.split()    
    text_fragment="-4 to +4 scale"
    
    if(text_fragment in pagetext):
        try:
            #pagetext=soup.get_text()
            #text_fragment="-4 to +4 scale"

            reversed_subtext = pagetext.split(text_fragment,4)[0][::-1]
            index_of_digit = re.search('\d', reversed_subtext).start()

            if reversed_subtext[index_of_digit+1] == "+":
                tempdict['Rate']='P'
                #rate = str(reversed_subtext[index_of_digit])
            elif reversed_subtext[index_of_digit+1] == "-":
                tempdict['Rate']='N'
            else:    
                tempdict['Rate']='NA'
    
        except Exception as e:
            print str(e.message)+"::"+str(e.args)
            tempdict['Rate']="NA"
                
    elif(reviewdata_Capsule_PRE_flag== True or reviewdata_Capsule_P_flag==True):
        
        try:   
            review=tempdict["Snippet"]
            count_of_review_words=len(review.split())
            
            review_word_items=review.split()
            positive_count=0
            negative_count=0

            for item in review_word_items:
                if item in positive_words:
                    positive_count=positive_count+1
                if item in negative_words:
                    negative_count=negative_count+1

            diff_count=positive_count-negative_count

            if (diff_count>=0):
                tempdict['Rate']='P'
            else:
                tempdict['Rate']='N'
        
        except Exception as e:
            print str(e.message)+"::"+str(e.args)
            tempdict['Rate']="NA"
                            
    elif ("rate" in pagetextList):
        try:
         
                #get the index of rate
                index=pagetextList.index("rate")
                patternlist=tempdict['Title'].lower().split()
                patternlistlen=len(patternlist)
                count=1
                movienamelist=[]
    
                positive_count=0
                negative_count=0
                while count<=patternlistlen:
                    movienamelist.append(pagetextList[index+count])
                    count=count+1
    
                if(movienamelist==patternlist):
                    item=pagetextList[count]
                    while("." not in item or "?" not in item or "!" not in item):
                        if(item in positive_words):
                            positive_count=positive_count+1
                        if(item in negative_words):
                            negative_count=negative_count+1
                        count=count+1    
                        item=pagetextList[count]    
                
                    diff_count=positive_count-negative_count
    
                    if (diff_count>=0):
                        tempdict['Rate']='P'
                    else:
                        tempdict['Rate']='N'
                else:                      
                    tempdict['Rate']="NA"          

        except Exception as e:
                print str(e.message)+"::"+e.args
                tempdict['Rate']="NA"
    
    else:
        ##Initialize the sentiment analyzer
        #sentiment_analyzer = SentimentIntensityAnalyzer()
        #positive_word_list=[]
        #neutral_word_list=[]
        #negative_word_list=[]  
        
        #for word in pagetextList:
            #if (sentiment_analyzer.polarity_scores(word)['compound']) >= 0.5:
                #positive_word_list.append(word)
            #elif (sentiment_analyzer.polarity_scores(word)['compound']) <= -0.5:
                #negative_word_list.append(word)
            #else:
                #neutral_word_list.append(word) 
            
        #countdiff=len(positive_word_list)- len(negative_word_list)    
        #if(countdiff>0):
            #tempdict['Rate']="P"
        #elif (countdiff<0):    
            #tempdict['Rate']="N"
        #else:
            #It is hard to rate
            tempdict['Rate']="NA"
            

    docsTable.append(tempdict)





def getIndexFrequencyList(input_file,doc_no):

    
    term_frequency={}
    useless_words = ["and", "a", "the", "an", "by", "from", "for", "hence", "of", "the", "with", "in", "within", "who", "when", "where", "why", "how", "whom", "have", "had", "has", "not", "for", "but", "do", "does", "done"]

    soup = bs(open(input_file), "html.parser")

    # Get the text on the html through BeautifulSoup
    text = str(soup.get_text())

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


        try:
            if (item.startswith('(') and item.endswith('(')) or (item.startswith('[') and item.endswith('[')) or (item.startswith('[') and item.endswith(']')) or (item.startswith('(') and item.endswith(')')):
                #test_file_write.write(str(item[1:-1])+"::"+item+"::\n")
                result1.append(item[1:-1])
            elif item.startswith('(') or item.startswith('[') or item.startswith(')') or item.startswith(']'):
                #test_file_write.write(str(item[1:])+"::"+item+"::\n")
                result1.append(item[1:])
            elif item.endswith('(') or item.endswith('[') or item.endswith(')') or item.endswith(']'):
                #test_file_write.write(str(item[:-1])+"::"+item+":: \n")
                result1.append(item[:-1]) 
            else:
                #test_file_write.write(str(item)+"\n")
                result1.append(item)
            #print item +"::\n"    

        except Exception as e:
            print str(e.message)+"::"+str(e.args)
            continue        
    

    #Remove all brackets and apostrophes, quotes etc
    newList = [item.replace('\'', '') for item in result1]
    newList = [item.replace('\"', '') for item in newList]
        
    #Split by "-"
    after_remove = ' '.join(newList)
    after_remove = after_remove.split("-")
    after_remove = ' '.join(after_remove)

    #Remove single special characters
    after_remove = re.sub(r'(?:^| )\W(?:$| )', ' ', after_remove) #\W = [^\w]
    
    #Split by "{"
    after_remove = after_remove.split("{")
    after_remove = ' '.join(after_remove)


    #Split by ","
    after_remove = after_remove.split(",")
    after_remove = ' '.join(after_remove)

    #Split by ")"
    after_remove = after_remove.split(")")
    after_remove = ' '.join(after_remove)
    
    after_remove = list(after_remove.split())

    #[\-!?:]+)}
    mustelimnated= ['?','!',':',';','-','+','[',']','{','}','(',')','*']
    after_remove_eliminated=[]
    tokenspecificlist=[]
    
    
    for token in after_remove:
        
        #Remove Special character from the begining of the file
        newtoken=re.sub(r'([^\w\s]|_)+(?=\s|$)', '', token)
        #Remove Special character from the end of the file
        newtoken1 = re.sub(r"^\W+", "", newtoken)        
        
        after_remove_eliminated.append(newtoken1)
                    
    
    #Stem the data
    documents = [stem(word) for word in after_remove_eliminated]    

    documents.sort()
    counter=collections.Counter(documents)
   
    term_frequency=dict(counter)
   
    for term in term_frequency:
        
        if term is None or len(term)<=1 or term ==" ":
            continue

        if term not in document_frequency:
            document_frequency[term]=1
            frequency_doc_count[term]=[]
            tempdict={}
            tempdict["Doc_No"]=doc_no
            tempdict["Doc_Name"]=input_file
            tempdict["term_freq"]=term_frequency[term]
            frequency_doc_count[term].append(tempdict)

        else:
            val=document_frequency[term]
            document_frequency[term]=val+1
            tempdict={}
            tempdict["Doc_No"]=doc_no
            tempdict["Doc_Name"]=input_file
            tempdict["term_freq"]=term_frequency[term]
            frequency_doc_count[term].append(tempdict)
            
    
    
def getdocno(file):
    docno=file.split(".")[0]
    return int(docno)




if __name__ == "__main__":

    
    if len(sys.argv) < 5:
        print("Input directory path is required")
        print("Execution format: python <program_name.py> <inputfile.rar> <Dictionary.csv> <Postings.csv> <DocsTable.txt>")
        sys.exit(1)

    else:
        input_dir = str(sys.argv[1])
        dictfile= str(sys.argv[2])
        postingfile=str(sys.argv[3])
        doctablefile=str(sys.argv[4])
        
    reload(sys)
    sys.setdefaultencoding("utf-8")    
    doc_no=0
    file_list=os.listdir(str(sys.argv[1]))
    file_list.sort()
    dirpath = os.getcwd()
    
    #Get the review documents
    for filename in file_list:
        
        filepath=os.path.join(input_dir, filename)
        doc_no=getdocno(filename)
        getIndexFrequencyList(filepath,doc_no)
        absfilepath=os.path.abspath(filepath)
        generateDocsTable(absfilepath,filename,doc_no)             
    
    
    output_file1=os.path.join(dirpath, dictfile)
    output_file2=os.path.join(dirpath, postingfile)
    output_file3=os.path.join(dirpath, doctablefile)
    
    dictionary_file = open(output_file1, 'w')
    posting_file= open(output_file2, 'w')
    doctable_file=open(output_file3,'w')

    dictionary_writer = csv.writer(dictionary_file, delimiter='\t',quotechar =',',quoting=csv.QUOTE_MINIMAL)
    posting_writer = csv.writer(posting_file, delimiter='\t',quotechar =',',quoting=csv.QUOTE_MINIMAL)
    #doctable_writer=csv.writer(doctable_file,delimiter='\t')

    
    #Mention the header for the Dictionary.csv File
    dictionary_header=['Term','df','offset']
    dictionary_writer.writerow(dictionary_header) 

    #Mention the header for the Postings.csv file
    posting_header=["DocI","tf"]
    posting_writer.writerow(posting_header)    
 

    #Mention the header for the DocsTable.csv file
    doctable_file.write("Filename \t Title \t Reviewer \t Snippet \t Rate")
    
    offsetinitialval=0
    prevfrequencyterm=0

    termlist=document_frequency.keys()
    termlist.sort()
    #print document_frequency
    
    
    
    for key in termlist:
        try:
            val=document_frequency[key]
            offsetinitialval=offsetinitialval+prevfrequencyterm     
            templist=[key,val,offsetinitialval]
            prevfrequencyterm=val
            
            dictionary_writer.writerow(templist)

            termspecificDocList=frequency_doc_count[key]
            
            doc_id_list=[]
            doc_id_dict={} 
            for item in termspecificDocList:

                #Item Dictionary
                doc_id=item["Doc_No"]
                term_freq=item["term_freq"]
                doc_id_dict[doc_id]=term_freq
                doc_id_list.append(doc_id)

            #Sort the document Id list
            doc_id_list.sort()
            for doc_id in doc_id_list:
                postinglist=[doc_id,doc_id_dict[doc_id]]
                posting_writer.writerow(postinglist)                        


        except Exception as e:
            
            print str(e.message) +"::"+ str(e.args)
            continue     

    

    for item in docsTable:
        
        try:
        
            docs_header=["Filename","Title","Reviewer","Snippet","Rate"]
            
            Filename=str(item['Filename'])
            try:
                Title=str(item['Title'])
            except Exception as e:
                if("\xdft" in Title):
                    Title=Title.replace("\xdf","")
                    print str(e.message) +"::"+ str(e.args)
            #print Title
            Reviewer=str(item['Reviewer'])
            Snippet=str(item['Snippet'])
            Rate=str(item['Rate'])
            doctablelist= "\n \n"+Filename+"\t"+Title+"\t"+Reviewer+"\t"+Snippet+"\t"+Rate+"\n \n"
            doctable_file.write(doctablelist)                
            

        except Exception as e:
            print str(e.message) +"::"+ str(e.args)
            continue     
            
        

    

