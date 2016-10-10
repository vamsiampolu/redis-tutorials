import time
import redis

ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432
ARTICLES_PER_PAGE = 25

#user can vote on an article
def article_vote(conn,user,article):
	#article is a string that looks like `article:id`
	cutoff = time.time() - ONE_WEEK_IN_SECONDS
	#cutoff is a timestamp, we return if the timestamp on the article
	#is smaller than the timestamp one week ago
	if conn.zscore('time:',article) < cutoff:
		return
	article_id = article.partition(':')[-1]
	#add user to the voted SET for the article
	#if the user could be added successfully
	#increment the score of the article
	#increment the votes of the article
	if conn.sadd('voted:' + article_id,user):
		conn.zincrby('score:',article,VOTE_SCORE)
		conn.hincrby(article,'votes',1)

#user can post a new article
def article_post(conn,user,title,link):
	#increment the article key to generate a new article_id
	article_id = conn.incr('article:')
	#create a voted set and add the user to it
	#expire: the voted set must only remain in memory until a week
	#article_id has to be converted to string
	voted = 'voted:' + str(article_id)
	conn.sadd(voted,user)
	conn.expire(voted,ONE_WEEK_IN_SECONDS)
	now = time.time()
	article = 'article:' + str(article_id)
	#adding a hash to represent the article
	conn.hmset(article,{
		'title': title,
		'link': link,
		'poster': user,
		'time': now,
		'votes': 1
	})
	#add the score for the article
	#add the time for the article
	conn.zadd('score:',article,now + VOTE_SCORE)
	conn.zadd('time:',article,now)
	return article_id

#get the most voted articles from this week
def get_articles(conn,page,order='score:'):
	start = (page - 1) * ARTICLES_PER_PAGE
	end = start + ARTICLES_PER_PAGE - 1
	#retrieve the articles by their score in descending order
	ids = conn.zrevrange(order,start,end)
	articles = []
	#get each article by id and add it list
	for id in ids:
		article_data = conn.hgetall(id)
		article_data['id'] = id
		articles.append(article_data)
	return articles

#add article to groups and remove article from groups in to_add and to_remove respectively
#an article can be part of multiple groups
def add_remove_groups(conn,article_id,to_add=[],to_remove=[]):
	article = 'article:'+ article_id
	for group in to_add:
		conn.sadd('group:' + group,article)
	for group in to_remove:
		conn.srem('group:' + group,article)

def get_group_articles(conn,group,page,order='score:'):
	key = order + group
	if not conn.exists(key):
		conn.zinterstore(key,
			['group:' + group, order ],
			aggregate='max',
		)
		conn.expire(key,60)
		return get_articles(conn,page,key)

conn = redis.Redis()
article_post(conn,'user1','Article1','http://user1/Article1')
article_post(conn,'user2','Article2','http://user2/Article2')