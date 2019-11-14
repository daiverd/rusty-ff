from flask import Flask, session, redirect, url_for, escape, request, flash, render_template, Markup, jsonify
from datetime import datetime
import sys, requests
from bs4 import BeautifulSoup

def download(url):
 headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url,headers=headers)
    if r.history and ('Location' in r.history[-1].headers):
        url = r.history[-1].headers['Location']
    return parse(url, r.content)

def parse(url, page):
    soup = BeautifulSoup(page)
    return soup

app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'k7\xa0\r\xa1{\xd7\x87=\xae\x9a\x95ng\xbb\xd1'

@app.route('/ff')
def index():
 soup = download("https://www.fanfiction.net/book/Harry-Potter/")
 stories = parse_stories(soup)
 return render_template("index.html", stories=stories)

def parse_stories(soup):
 stories = soup.find_all("div", class_="z-list")
 for i in stories:
  i.a.img.extract()
  i.a.wrap(soup.new_tag("h2"))
  i.find_all("a")[1].extract()
  i.div.find(text=True).wrap(soup.new_tag("blockquote"))
  for link in i.find_all("a"):
   link["href"] = "https://www.fanfiction.net" + link["href"]
 return stories

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['server'] = request.form['server']
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        flash(validate.login(session['username'], session['password'], session['server']))
        return redirect(url_for('index'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/i/<id>', methods=['GET', 'POST'])
def issue(id):
 issue = jira.issue(id)
 if request.method == 'POST':
  return do_comment(issue.key)
 fields = issue.raw['fields']
 if issue.fields.issuetype.name == "Epic":
  stories = jira.search_issues("cf[10006]=" + issue.key)
 else:
  stories = None
 return render_template("issue.html", issue=issue, fields=fields, jlink=render_jlink, jira_fields=jira_fields, stories=stories)

@app.route('/create', methods=['GET', 'POST'])
def create():
 if request.method == 'POST':
  return do_create()
 issue_types = jira.issue_types()
 projects = jira.projects()
 p = []
 for i in projects:
  if "do not use" in i.name.lower():
   continue
  p.append(i)
 projects = p
 return render_template("create.html", issue_types=issue_types, projects=projects)

@app.route('/e/<id>', methods=['GET', 'POST'])
def edit(id):
 issue = jira.issue(id)
 meta = jira.editmeta(issue)
 f = form.form(meta, jira_fields)(request.form, data=issue.raw['fields'])
 return render_template("edit.html", form=f)


def do_create():
 issue = {
 'project': {'key': request.form['project']},
 'summary': request.form['summary'],
 'description': request.form['description'],
 'issuetype': {'name': request.form['issuetype']},
 'components': [{'name': request.form['component_list']}],
 }
 new_issue = jira.create_issue(fields=issue)
 return redirect("/i/" + new_issue.key)
 
def do_comment(issue_key):
 comment = request.form['comment']
 if comment:
  jira.add_comment(issue_key, comment)
 return redirect("/i/" + issue_key)
 
@app.route('/components')
def components():
 text = request.args.get('project')
 components = jira.project_components(text)

 return render_template("components.html", components=components)

@app.route('/fields')
def fields():
 project = request.args.get('project')
 issuetype = request.args.get('issuetype')
 q = jira.createmeta(projectKeys=project, issuetypeNames=issuetype, expand="projects.issuetypes.fields")
 fields = q['projects'][0]['issuetypes'][0]['fields']
 return render_template("fields.html", fields=fields)

@app.route('/users')
def users():
 q = request.args.get('q')
 results = jira.search_users(q, maxResults=15)
 r = []
 for i in results:
  r.append(i.raw)
 return jsonify(r)

@app.route('/search')
def search():
 q = request.args.get('q')
 issues = jira.search_issues(q)
 return render_template("search.html", q=q, issues=issues)
 
@app.template_filter('date')
def render_time(s):
 return datetime.strptime(s.split(".")[0], '%Y-%m-%dT%H:%M:%S').strftime("%B %d, %Y at %H:%M")
 
def render_jlink(link):
 links = []
 if hasattr(link, "inwardIssue"):
  links.append(link.inwardIssue)
 if hasattr(link, "outwardIssue"):
  links.append(link.outwardIssue)
 text = ""
 for i in links:
  text += "<a href='/i/"
  text += i.key
  text += "'>"
  text += link.type.name
  text += " "
  text += i.fields.summary
  text += "</a>"
 return text
