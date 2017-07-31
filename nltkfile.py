import  pymysql
import nltk, string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from nltk.stem import *
from nltk.stem.porter import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

db = pymysql.connect("localhost","root","belle","thsst_761" )

content = []

def normalize():
	cursor = db.cursor()
	cursor.execute("SELECT idpage, content FROM page")

	stop_words = set(stopwords.words('english'))

	for row in cursor.fetchall():
		idPageNum = row[0]
		data = row[1]

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
			cursor.execute ("""UPDATE page SET preprocessed=%s WHERE idpage=%s""", (fnl_text, idPageNum))
			db.commit()
		except MySQLError as e:
			print(e)
	
def get_preprocessed():
	cursor = db.cursor()
	cursor.execute("SELECT preprocessed FROM page")

	for row in cursor.fetchall():
		content.append(row[0])


def cosine_sim(text1, text2):
	vectorizer = TfidfVectorizer()
	print(text1)
	print(text2)
	tfidf = vectorizer.fit_transform([text1, text2])
	score = cosine_similarity(tfidf[0:1], tfidf)
	print(score[0][1])
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

			indexX = x+1
			indexY = y+1
			try:
				print(indexX,indexY,fnl_score)
				cursor.execute("""INSERT INTO score (article_1, article_2, cos_sim) VALUES ("%d","%d","%.13f")""" % (indexX, indexY, fnl_score))
				db.commit()
			except MySQLError as e:
				print(e)
	
	db.close()

def new_links510():
	cursor = db.cursor()
	#510
	# cursor.execute("select article_1, article_2, cos_sim, idscore from (select article_1, article_2, cos_sim, idscore, (@row:=if(@prev=article_1, @row +1, if(@prev:= s.article_1, 1, 1))) rn from ((select * from score) union all (select idscore, article_2, article_1, cos_sim from score as s2 where article_1<article_2)) as s, (select max(idpage) as maxid from link) maxpage inner join (select @row:=0, @prev:=null) c where  article_1 != article_2 and article_1 <= maxid order by article_1, cos_sim desc ) peritem where rn <= 4 order by article_1, cos_sim desc")
	#761
	cursor.execute("select article_1, article_2, cos_sim, idscore from (select article_1, article_2, cos_sim, idscore, (@row:=if(@prev=article_1, @row +1, if(@prev:= article_1, 1, 1))) rn from ((select * from score) union all (select idscore, article_2, article_1, cos_sim from score as s2 where article_1<article_2)) as s inner join (select @row:=0, @prev:=null) c where  article_1 != article_2 order by article_1, cos_sim desc) peritem where rn <= 4 order by article_1, cos_sim desc")
	article_1 = []
	article_2 = []
	cos_sim = []
	idscore = []

	for row in cursor.fetchall():
		article_1.append(row[0])
		article_2.append(row[1])
		cos_sim.append(row[2])
		idscore.append(row[3])

	count = len(article_1)
	for x in range(0, count):
		try:
			cursor.execute("""INSERT INTO new_links (article_1, article_2, cos_sim, idscore) VALUES ("%d","%d","%.13f", "%d")""" % (article_1[x], article_2[x], cos_sim[x], idscore[x]))
			db.commit()
			#print("Successfully added to database.")
		except MySQLError as e:
			print(e)

	db.close()

def old_links():
	cursor = db.cursor()
	# cursor1 = db.cursor()
	cursor.execute("CREATE TEMPORARY TABLE IF NOT EXISTS old_score AS (select * from score) union all (select idscore, article_2, article_1, cos_sim from score as s2 where article_1<article_2)")
	cursor.execute("select l.idpage as source, p.idpage as dest, s.cos_sim, s.idscore from page p, link l, old_score s where p.url = l.link and l.idpage=s.article_1 and p.idpage=s.article_2")

	article_1 = []
	article_2 = []
	cos_sim = []
	idscore = []

	for row in cursor.fetchall():
		article_1.append(row[0])
		article_2.append(row[1])
		cos_sim.append(row[2])
		idscore.append(row[3])


	count = len(article_1)
	for x in range(0, count):
		try:
			cursor.execute("""INSERT INTO old_links (article_1, article_2, cos_sim, idscore) VALUES ("%d","%d","%.13f","%d")""" % (article_1[x], article_2[x], cos_sim[x], idscore[x]))
			db.commit()
			#print("Successfully added to database.")
		except MySQLError as e:
			print(e)
	db.close()


#call functions
# normalize()
# get_preprocessed()
# cosine_sim(content[4], content[4])
# allCosine_sim()
# old_links()
new_links510()
