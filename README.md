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

---