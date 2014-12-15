from flask import Flask, render_template, request
import pymongo
import json, pyelasticsearch
import re
import config
import mrjob
from mrjob.job import MRJob
import re

EMAIL_RE = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

# Setup Flask
app = Flask(__name__)

# Setup Mongo
conn = pymongo.Connection() # defaults to localhost
db = conn.agile_data
emails = db['full_inbox']

# Setup ElasticSearch
elastic = pyelasticsearch.ElasticSearch(config.ELASTIC_URL)
# Controller: Fetch an email and display 

class MRTopTenEmailers(MRJob):

    def mapper_get_emails(self, _, line):
        # yield each email in the line
      for email in EMAIL_RE.findall(line):
        yield email,1

    def combiner_count_emails(self, email, counts):
        # optimization: sum the emails we've seen so far
        yield (email, sum(counts))

    def reducer_count_emails(self, emails, counts):
        # send all (num_occurrences, emails) pairs to the same reducer.
        # num_occurrences is so we can easily use Python's max() function.
        yield None, (emails,sum(counts))

    # discard the key; it is just None
    def reducer_find_top_ten(self, _, email_count_pairs):
        # each item of email_count_pairs is (count, email),
        # so yielding one results in key=counts, value=email
        sort_list = sorted(email_count_pairs, key=lambda x:x[1], reverse=True)
        for d in sort_list[:10]:
          yield (d)

    def steps(self):
        return [
            self.mr(mapper=self.mapper_get_emails,
        combiner=self.combiner_count_emails,
                    reducer=self.reducer_count_emails),
            self.mr(reducer=self.reducer_find_top_ten)
        ]


def get_navigation_offsets(offset1, offset2, increment):
  offsets = {}
  offsets['Next'] = {'top_offset': offset2 + increment, 'bottom_offset': offset1 + increment}
  offsets['Previous'] = {'top_offset': max(offset2 - increment, 0), 'bottom_offset': max(offset1 - increment, 0)} # Don't go < 0
  return offsets

# Process elasticsearch hits and return email records
def process_search(results):
  emails = []
  if results['hits'] and results['hits']['hits']:
    hits = results['hits']['hits']
    for hit in hits:
      email = hit['_source']
      emails.append(hit['_source'])
  return emails


@app.route("/landing", methods=['POST'])
#@app.route("/landing/<int:offset1>/<int:offset2>")
def dummmy(offset1 = 0, offset2 = config.EMAILS_PER_PAGE, query=None):
  name = request.form.get('name')
  print "Name :", name
  email = request.form.get('email')
  print "Email :", email
  email_list = list()
  x = offset2 - offset1
  if name == '' and email == '':
    query = request.args.get('search')
    if query == None:
      email_list = emails.find()[offset1:offset2]
      print "11111111111111111111111111"
    # else:
    #   results = elastic.search({'query': {'match': { '_all': query}}, 'sort': {'date': {'order': 'desc'}}, 'from': offset1, 'size':x},index="fullinbox") #config.EMAILS_PER_PAGE}, index="fullinbox")
    #   print results
    #   email_list = process_search(results)
    # nav_offsets = get_navigation_offsets(offset1, offset2, x)#config.EMAILS_PER_PAGE)
    # return render_template('partials/emails.html', emails=email_list, nav_offsets=nav_offsets, nav_path='/emails/', query=query)
  elif email == '' and name != '':
    email_list = emails.find({"from.real_name":name})[offset1:offset2]
    print "2222222222222222222222"
  elif name == '' and email != '':
    email_list = emails.find({"from.address":email})[offset1:offset2]
    print "3333333333333333333333333"
  elif email != '' and name != '':
    email_list = emails.find({"from.real_name":name})[offset1:offset2]
    print "4444444444444444444444"
  nav_offsets = get_navigation_offsets(offset1, offset2, x)#config.EMAILS_PER_PAGE)
  return render_template('partials/emails.html', emails=email_list, nav_offsets=nav_offsets, nav_path='/landing/', name=name, email=email, query=query)

@app.route("/landing/<int:offset1>/<int:offset2>/a/")
@app.route("/landing/<int:offset1>/<int:offset2>/<name>/a/")
@app.route("/landing/<int:offset1>/<int:offset2>/a/<email>/")
@app.route("/landing/<int:offset1>/<int:offset2>/<name>/<email>/")
@app.route("/landing/<int:offset1>/<int:offset2>/<name>/a/<email>/<query>")
def dummmy2(offset1, offset2, name='', email='', query=None):
  name = name
  print "Name :", name
  email = email
  print "Email :", email
  email_list = list()
  x = offset2 - offset1
  if name == '' and email == '':
    query = request.args.get('search')
    if query == None:
      email_list = emails.find()[offset1:offset2]
      print "11111111111111111111111111"
    # else:
    #   results = elastic.search({'query': {'match': { '_all': query}}, 'sort': {'date': {'order': 'desc'}}, 'from': offset1, 'size':x},index="fullinbox") #config.EMAILS_PER_PAGE}, index="fullinbox")
    #   print results
    #   email_list = process_search(results)
    # nav_offsets = get_navigation_offsets(offset1, offset2, x)#config.EMAILS_PER_PAGE)
    # return render_template('partials/emails.html', emails=email_list, nav_offsets=nav_offsets, nav_path='/emails/', query=query)
  elif email == '' and name != '':
    email_list = emails.find({"from.real_name":name})[offset1:offset2]
    print "2222222222222222222222"
  elif name == '' and email != '':
    email_list = emails.find({"from.address":email})[offset1:offset2]
    print "3333333333333333333333333"
  elif email != '' and name != '':
    email_list = emails.find({"from.real_name":name})[offset1:offset2]
    print "4444444444444444444444"
  nav_offsets = get_navigation_offsets(offset1, offset2, x)#config.EMAILS_PER_PAGE)
  return render_template('partials/emails.html', emails=email_list, nav_offsets=nav_offsets, nav_path='/landing/', name=name, email=email, query=query)

@app.route("/email/<message_id>")
def sent_counts(message_id):
  email = emails.find_one({'message_id': message_id})
  return render_template('partials/email.html', email=email)
  
# Calculate email offsets for fetchig lists of emails from MongoDB
def get_navigation_offsets(offset1, offset2, increment):
  offsets = {}
  offsets['Next'] = {'top_offset': offset2 + increment, 'bottom_offset': offset1 + increment}
  offsets['Previous'] = {'top_offset': max(offset2 - increment, 0), 'bottom_offset': max(offset1 - increment, 0)} # Don't go < 0
  return offsets

# Process elasticsearch hits and return email records
def process_search(results):
  emails = []
  if results['hits'] and results['hits']['hits']:
    hits = results['hits']['hits']
    for hit in hits:
      email = hit['_source']
      emails.append(hit['_source'])
  return emails

# Controller: Fetch a list of emails and display them
@app.route('/')
def dummy():
  return render_template('partials/landing.html')

@app.route('/emails/')
@app.route("/emails/<int:offset1>/<int:offset2>/")
def list_emails(offset1 = 0, offset2 = config.EMAILS_PER_PAGE, query=None):
  query = request.args.get('search')
  x = offset2 - offset1
  if query==None:
    email_list = emails.find()[offset1:offset2]
  else:
    results = elastic.search({'query': {'match': { '_all': query}}, 'sort': {'date': {'order': 'desc'}}, 'from': offset1, 'size':x},index="fullinbox") #config.EMAILS_PER_PAGE}, index="fullinbox")
    print results
    email_list = process_search(results)
  nav_offsets = get_navigation_offsets(offset1, offset2, x)#config.EMAILS_PER_PAGE)
  return render_template('partials/emails.html', emails=email_list, nav_offsets=nav_offsets, nav_path='/emails/', query=query)

@app.route('/diagnostics')
def top_senders():
  top_emails =list()
  count=list()
  time_top =list()
  count_top =list()
  f = open('sample.txt', 'w')
  for email in emails.find():
    #print email['from']['address']
    f.write(str(email['from']['address']))
    f.write('\n')
  f.close()
  #MRTopTenEmailers.run() sample.txt > sample.out
  f=open('sample.out', 'r')
  lines = f.readlines()
  for line in lines:

    top_emails.append(re.sub('"','', line.split('\t')[0]))
    count.append(line.split('\t')[1].strip())
  f.close()
  f = open('sample_top.txt', 'w')
  for top in emails.find({"from.address": top_emails[0]}):
    print top['date'].split('-')[0]
    f.write(top['date'].split('-')[0])
    f.write('\n')
  f.close()

  f=open('sample_top.out', 'r')
  lines = f.readlines()
  for line in lines:
    time_top.append(re.sub('"','', line.split('\t')[0]))
    count_top.append(line.split('\t')[1].strip())
  top_sender = top_emails[0]
  return render_template('partials/diagnostics.html', top_emails=top_emails, count=count, time_top=time_top, count_top=count_top, top_sender=top_sender)

if __name__ == "__main__":
  app.run(debug=True)
