import time
import redis

ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432
ARTICLES_PER_PAGE = 25
UPVOTE = 'UPVOTE'
DOWNVOTE = 'DOWNVOTE'

#a user who has already voted can change their vote
def change_vote(conn,article,user,from_type,to_type):
	article_id = article.partition(':')[-1]
	upvoted = 'upvoted:' + article_id
	downvoted = 'downvoted:' + article_id
	if from_type == to_type:
		return
	elif from_type == UPVOTE and to_type == DOWNVOTE:
		conn.srem(upvoted,user)
		conn.sadd(downvoted,user)
		conn.zincrby('score:',article, -2 * VOTE_SCORE)
		conn.hincrby(article,'votes',-2)
	elif from_type == DOWNVOTE and to_type == UPVOTE:
		conn.srem(downvoted,user)
		conn.sadd(upvoted,user)
		conn.zincrby('score:',2 * VOTE_SCORE)
		conn.hincrby(article,'votes',2)

#user can vote on an article
def article_vote(conn,user,type,article):
	cutoff = time.time() - ONE_WEEK_IN_SECONDS
	if conn.zscore('time:',article) < cutoff:
		return
	article_id = article.partition(':')[-1]
	upvoted = 'upvoted:' + article_id
	downvoted = 'downvoted:' + article_id
	if conn.sadd('voted:' + article_id,user):
		if type == UPVOTE:
			conn.zincrby('score:',article,VOTE_SCORE)
			conn.hincrby(article,'votes',1)
			conn.sadd(upvoted,user)
		elif type == DOWNVOTE:
			conn.zincrby('score:',article,-VOTE_SCORE)
			conn.hincrby(article,'votes',-1)
			conn.sadd(downvoted,user)
	else:
		from_type = ''
		if conn.sismember(upvoted,user):
			from_type = UPVOTE
		elif conn.sismember(downvoted,user):
			from_type = DOWNVOTE
		if(from_type != type):
			change_vote(conn,article,user,from_type,type)


#user can post a new article
def article_post(conn,user,title,link):
	article_id = conn.incr('article:')
	voted = 'voted:' + str(article_id)
	upvoted = 'upvoted:' + str(article_id)
	downvoted = 'downvoted:' + str(article_id)
	conn.sadd(voted,user)
	conn.expire(voted,ONE_WEEK_IN_SECONDS)
	conn.sadd(upvoted,user)
	conn.expire(upvoted,ONE_WEEK_IN_SECONDS)
	conn.expire(downvoted,ONE_WEEK_IN_SECONDS)
	now = time.time()
	article = 'article:' + str(article_id)
	conn.hmset(article,{
		'title': title,
		'link': link,
		'poster': user,
		'time': now,
		'votes': 1
	})
	conn.zadd('score:',article,now + VOTE_SCORE)
	conn.zadd('time:',article,now)
	return article_id

def get_articles(conn,page,order='score:'):
	start = (page - 1) * ARTICLES_PER_PAGE
	end = start + ARTICLES_PER_PAGE - 1
	ids = conn.zrevrange(order,start,end)
	articles = []
	for id in ids:
		article_data = conn.hgetall(id)
		article_data['id'] = id
		articles.append(article_data)
	return articles

def add_remove_groups(conn,article_id,to_add=[],to_remove=[]):
	article = 'article:'+ str(article_id)
	for group in to_add:
		conn.sadd('group:' + str(group),article)
	for group in to_remove:
		conn.srem('group:' + str(group),article)

def get_group_articles(conn,group,page,order='score:'):
	key = order + str(group)
	if not conn.exists(key):
		conn.zinterstore(key,
			['group:' + str(group), order ],
			aggregate='max',
		)
		conn.expire(key,60)
		return get_articles(conn,page,key)