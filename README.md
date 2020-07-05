# searchpert-w2v
word2vec learns with korean government documents

### docker run
docker run --name visual-w2v -v ./learn-searchpert-w2v/:/searchpert-w2v -p 6006:6006 -it sehandev/django-tf  
docker run --name web-w2v -v ./learn-searchpert-w2v/:/searchpert-w2v -p 80:80 -it sehandev/django-tf  
