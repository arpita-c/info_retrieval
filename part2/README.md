
Run the following command 
----------------------------
---------------------------------------------------------------- 
Package to install(before executing the python script):: 
---------------------------------------------------------------
pip install stemming

------------------------
How to execute::
------------------------
python assignmentP1.py  ./Reviews/  Dictionary.csv Postings.csv DocsTable.txt

arg1=folder path where all review html files are stored
arg2=Dictionary.csv
arg3=Postings.csv
arg4=DocsTable.txt


-----------------------------
Libraries used::
-----------------------------

a>stemming.porter package (Purpose:: stemming the token)
b>BeautifulSoup package ((Purpose: traversing the html node and access the node data)

c>nltk package 
d>nltk.sentiment.vader package
e>twython 2.7.0
--Purpose:: Package c,d,e have been used as a heuristic approach for performing RATE calculation from the movie review
(The portion of the code has been commented out,as it has a dependencies and require installing few packages in the remote machine.Feel free to ask me if you wanna know what approach I have taken for rate calculation in a heuristic approach) 

f>csv package [Purpose::Handling csv package]
g>urllib2 package[Purpose:For accessing html files as an URL to extract the node]


 
 
