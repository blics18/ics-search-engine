from elastic_web_interface import app
from flask import url_for, redirect, render_template, request, flash
from elasticsearch import Elasticsearch
from RegistrationForm import RegistrationForm
from SearchForm import SearchForm
from Pagination import Pagination
from ValidUrl import ValidUrl
from pprint import pprint
import json

app.secret_key = 'rly_scrt_4nd_harD_to_gu3$$'
PER_PAGE = 10
BOOKKEEPING = json.load(open("bookkeeping.json"))
checkUrl = ValidUrl()
es = Elasticsearch()

@app.route('/', methods=['GET', 'POST'])
def index():

    form = SearchForm(request.form)
    res = dict()
    n_hits = 0
    links = dict() 
    hits = []

    q = request.args.get('q', default='')
    page = request.args.get('page', type=int, default=1)

    if (request.method in ['POST'] and form.validate()):
        q = form.query.data
        json_query = queryBoost(q)
        res = es.search(index="zot-search", body=json_query, from_=0 ,size=PER_PAGE)
        json_res = json.dumps(res)
        hits = res['hits']['hits']
        n_hits = res['hits']['total']
        links = get_links_for_page(hits)

    if request.method in ['GET'] and page == 1 and (q != ''):
        json_query = queryBoost(q)
        res = es.search(index="zot-search", body=json_query, from_=(page-1)*PER_PAGE, size=10)
        json_res = json.dumps(res)
        hits = res['hits']['hits']
        n_hits = res['hits']['total']
        links = get_links_for_page(hits)

    if request.method in ['GET'] and page != 1:
        json_query = queryBoost(q)
        res = es.search(index="zot-search", body=json_query, from_=(page-1)*PER_PAGE, size=10)
        json_res = json.dumps(res)
        hits = res['hits']['hits']
        n_hits = res['hits']['total']
        links = get_links_for_page(hits)


    pagination = Pagination(page, PER_PAGE, n_hits, q)
    print("Query => {}, Total hits => {}".format(q, n_hits))
    return render_template('search.html', form=form, links=links, page=pagination)

def queryBoost(query):
     phrase_title = { "match": { "title": { "query": query, "operator": "and", "boost": 3} } }
     phrase_h1 = { "match": { "h1": { "query": query, "operator": "and", "boost": 2.5} } }
     phrase_h2 = { "match": { "h2": { "query": query, "operator": "and", "boost": 2.25} } }
     phrase_h3 = { "match": { "h3": { "query": query, "operator": "and", "boost": 2.15} } }
     phrase_bold = { "match": { "bold": { "query": query, "operator": "and", "boost": 2.15} } }
     phrase_content = { "match": { "content": { "query": query, "operator": "and"} } }

     title = { "match": { "title": { "query": query, "boost": 2 } } }
     h1 = { "match": { "h1": { "query": query, "boost": 1.5 } } }
     h2 = { "match": { "h2": { "query": query, "boost": 1.25 } } }
     h3 = { "match": { "h3": { "query": query, "boost": 1.15 } } }
     bold = { "match": { "bold": { "query": query, "boost": 1.15 } } }
     content = { "match": { "content": { "query": query} } }

     #dict_search = {"query": { "bool": { "must": [ phrase_content, phrase_title, phrase_h1, phrase_h2, phrase_h3, phrase_bold ], \
                                         #"should": [ content, title, h1, h2, h3, bold ] } } }

     dict_search = {"query": { "bool": { "should": [ phrase_content, phrase_title, phrase_h1, phrase_h2, phrase_h3, phrase_bold, content, title, h1, h2, h3, bold ] } } }

     j = json.dumps(dict_search)
     return j

def checkHttp(url):
    if ('http' not in url.lower()):
       url = ''.join(['http://', url])
    return url 

def get_links_for_page(hits):
    links = []
    ret = dict()
    for hit in hits:
       id_bookkeeping = hit['_id'].replace("_", "/")
       hit_content = hit['_source']['content'][:150]
       url = BOOKKEEPING[id_bookkeeping]
       url = checkHttp(url) 
       #if (checkUrl.is_valid(url)):
       ret[url] = hit_content
       links.append(url)

    return ret

def url_for_other_page(query, page):
   return url_for(request.endpoint, q=query, page=page)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
