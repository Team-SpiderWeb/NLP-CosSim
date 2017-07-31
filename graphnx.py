import networkx as nx
import matplotlib.pyplot as plt
import pymysql

G=nx.Graph()

db = pymysql.connect("localhost","root","belle","thsst_try" )

cursor = db.cursor()
cursor.execute("SELECT article_1 from old_links")
idpage1 = cursor.fetchall()
cursor.execute("SELECT article_2 from old_links")
idpage2 = cursor.fetchall()
cursor.execute("SELECT cos_sim from old_links")
scores = cursor.fetchall()
cursor.execute("SELECT idpage from page")
content = cursor.fetchall()


i = 1
for row in content:
	G.add_node(i)
	i+=1

j = 0
for row in idpage1:
	if(scores[j][0]!=0 or idpage1[j][0] != idpage2[j][0]):
		G.add_edge(idpage1[j][0], idpage2[j][0], weight = scores[j][0])
	j+=1


#G.add_node(2)
#G.add_node(5)
#G.add_node(3)
#G.add_edge(2,5, weight = 1.023)
#G.add_edge(2,3, weight = 2.031)
pos=nx.spring_layout(G)
labels = nx.get_edge_attributes(G,'weight')
nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

print(nx.info(G))

nx.draw_networkx(G)
plt.show()
db.close()