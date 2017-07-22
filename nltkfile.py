import  pymysql
import nltk, string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from nltk.stem import *
from nltk.stem.porter import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

db = pymysql.connect("localhost","root","belle","thsst" )

content = []

def normalize():
	cursor = db.cursor()
	cursor.execute("SELECT content FROM page")

	stop_words = set(stopwords.words('english'))

	for row in cursor.fetchall():
		data = row

		#remove special char, tokenize & change to lowercase, remove stop words
		data = re.sub('[^A-Za-z0-9]+', ' ', data)
		word_tokens = word_tokenize(str(data).lower())
		filtered_sentence = [w for w in word_tokens if not w in stop_words]

		#stemming
		stemmer = PorterStemmer()
		stem = [stemmer.stem(word) for word in filtered_sentence]

		fnl_text = ' '.join(stem)

		#insert to db
		try:
			cursor.execute("""INSERT INTO preprocessed (content) VALUES ("%s")""" % (fnl_text))
			db.commit()
		except:
			pass

	db.close()
	print("Successfully added to database.")


def get_preprocessed():
	cursor = db.cursor()
	cursor.execute("SELECT content FROM preprocessed")

	for row in cursor.fetchall():
		content.append(row)

	print(content)
	db.close()


def cosine_sim(text1, text2):
	vectorizer = TfidfVectorizer()
	tfidf = vectorizer.fit_transform([text1, text2])
	score = cosine_similarity(tfidf[0:1], tfidf)
	# print(score)
	return score[0][1]


def allCosine_sim():
	#loop content
	contentCount = len(content)

	cursor = db.cursor()
	for x in range(0, contentCount):
		for y in range(x, contentCount):
			firstDoc = content[x]
			secondDoc = content[y]
			fnl_score = cosine_sim(firstDoc, secondDoc) 
			print(x,y,fnl_score)

			indexX = x+1
			indexY = y+1
			try:
				cursor.execute("""INSERT INTO score (article_1, article_2, cos_sim) VALUES ("%d","%d","%f")""" % (indexX, indexY, fnl_score))

				db.commit()

				# print(x,fnl_score)
			except MySQLError as e:
				print(e)
	db.close()

# def old_link_table():
	#loop content
	# contentCount = len(content)

	# cursor = db.cursor()
	# for x in range(0, contentCount):
	# 	for y in range(x, contentCount):
	# 		firstDoc = content[x]
	# 		secondDoc = content[y]
	# 		fnl_score = cosine_sim(firstDoc, secondDoc) 
	# 		print(x,y,fnl_score)

	# 		indexX = x+1
	# 		indexY = y+1
	# 		try:
	# 			cursor.execute("""INSERT INTO score (article_1, article_2, cos_sim) VALUES ("%d","%d","%f")""" % (indexX, indexY, fnl_score))

	# 			db.commit()

	# 			# print(x,fnl_score)
	# 		except MySQLError as e:
	# 			print(e)
	# db.close()

	# #get id page of link from link table
	# "SELECT "

	# id_score = 
	# src_page = 
	# desti_page =
	# score =  




#call functions

get_preprocessed()
# cosine_sim(content[4], content[34])
# allCosine_sim()