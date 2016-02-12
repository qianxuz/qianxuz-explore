# Imports
import os
import jinja2
import webapp2
import logging
import json
import urllib
import httplib2

# this is used for constructing URLs to google's APIS
from googleapiclient.discovery import build

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# This uses discovery to create an object that can talk to the 
# fusion tables API using the developer key
API_KEY = 'AIzaSyA8SzD7eyY7A0Lls4B_LUoNuk8O4S8uLDk'

service = build('fusiontables', 'v1', developerKey=API_KEY)

TABLE_ID = '1xXFu8T2xycJprygAzGjhIjhMt9dKY-1Nacq2SjQ'

from flask import Flask, request
app = Flask(__name__)

def get_all_data(query):
    response = service.query().sql(sql=query).execute()
    logging.info(response['columns'])
    logging.info(response['rows']) 
    return response


@app.route('/')
def index():
    template = JINJA_ENVIRONMENT.get_template('templates/index.html')
    request = service.column().list(tableId=TABLE_ID)
    logging.info(request)
    #logging.info(get_all_data())
    query = "SELECT * FROM " + TABLE_ID + " WHERE  'Animal Type' = 'BIRD'"
    response = service.query().sql(sql=query).execute()
    return template.render(headers = response['columns'], content = response['rows'])

def make_query(cols):
    string_cols = ""
    if cols == []:
        cols = ['*']
    for col in cols:
        string_cols = string_cols + ", " + "'"+col+"'"
    string_cols = string_cols[2:len(string_cols)]
    query = "SELECT " + string_cols + " FROM " + TABLE_ID + " WHERE 'Animal Type' = 'BIRD'"
    return query

@app.route('/_update_table', methods=['POST']) 
def update_table():
    logging.info(request.get_json())
    cols = request.json['cols']
    result = get_all_data(make_query(cols))
    return json.dumps({'content' : result['rows'], 'headers' : result['columns']})



@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
