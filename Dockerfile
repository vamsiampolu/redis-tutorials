#install redis and hiredis libraries for use with python
FROM python:2
RUN python -m easy_install redis hiredis
#set a shared volume that points to this directory
VOLUME ["C:\Users\vamsi\Do\redis-tutorials","/usr/src/app"]
WORKDIR /usr/src/app