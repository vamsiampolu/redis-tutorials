I am using the official `redis` image [from dockerhub](https://hub.docker.com/_/redis/) like this:

```
docker run -ti --rm --name redis-server -p 6379:6379 --net=host redis
```

In order to run the `redis-cli`, I am using the `redis-cli` image created by prologic [from dockerhub](https://hub.docker.com/r/prologic/redis-cli/)

```
docker run --rm -ti --net=host --name=redis-client prologic/redis-cli
```

To run `python`, I have built an image from the Dockerfile in the repo. I build the Dockerfile and run it like this:

```
docker build .
docker tag containerId imageName:tag
```

and I run this container like this:

```
docker run --rm --net=host -ti --name python-box redisinaction:0.22 python posts.py
```

I build a new image every time I need to run my code and add the files to the container before I can run it.

I am using the `--net=host` property to let the containers communicate over the host's network instead of using a private network.

Also, when we use `time.time()` in the examples in the first chapter, make sure to:

```
import time
```

Also, when converting from `int` to `string`, use `str(integerValue)`.

This is the code to test that the posts functionality is working correctly:

```
conn = redis.Redis()
article_post(conn,'user1','Article1','http://user1/Article1')
article_post(conn,'user2','Article2','http://user2/Article2')
articles = get_articles(conn,1)
print articles
article_vote(conn,'user3','article:5')
article_vote(conn,'user3','article:5')
article_vote(conn,'user4','article:5')
articles2 = get_articles(conn,1)
print articles2
add_remove_groups(conn,5,[1,2])
add_remove_groups(conn,4,[2])
add_remove_groups(conn,5,[],[2])
articles_group2 = get_group_articles(conn,2,1,'score:')
print articles_group2
```

---