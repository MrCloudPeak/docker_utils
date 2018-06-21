# docker_utils
useful utils for docker

dependence:
- python2.7
- root user

## 1.find unused images
exec 
```
python find_unused_images.py
````
then you can get unused docker images,including their id,name and size
```
unused images
id:e111a70eee6a name:celery size:216MB
```
