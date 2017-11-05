FROM python:2.7

ADD ./requirements.txt .
RUN pip install -r requirements.txt

# Install pymemcache from sources
RUN git clone https://github.com/pinterest/pymemcache.git
WORKDIR pymemcache/
RUN git config user.email "piotrbielak2@gmail.com" && \
    git config user.name "Piotr Bielak"
ADD Fixed-stats-whitespace-bug.patch .
RUN git am --signoff < Fixed-stats-whitespace-bug.patch
RUN python setup.py install

WORKDIR /
ADD ./app.py .

CMD ["python",  "app.py"]
