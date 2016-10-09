#install redis and hiredis libraries for use with python
FROM python:2
RUN python -m easy_install redis hiredis
#set a shared volume that points to this directory
WORKDIR /src/app