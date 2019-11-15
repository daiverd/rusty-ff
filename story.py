import re

class Story(object):
 def __init__(self, soup):
  self.soup = soup

 @property
 def title(self):
  return self._url.find(text=True)

 @property
 def _url(self):
  return self.soup.find("a", class_="stitle")

 @property
 def url(self):
  return self._url["href"]

 @property
 def story_id(self):
  return re.search(r"/(\d*)/", self.url).group(1)

 @property
 def _author(self):
  return self.soup.find("a", {"href": re.compile(r"/u/")})

 @property
 def author(self):
  return self._author.find(text=True)

 @property
 def author_url(self):
  return self._author["href"]

 @property
 def author_id(self):
  return re.search(r"/(\d*)/", self.author_url).group(1)

 @property
 def _description(self):
  return self.soup.find("div", class_="z-indent")

 @property
 def description(self):
  return self._description.find(text=True)

 @property
 def _meta(self):
  return self._description.div

 @property
 def meta(self):
  return self._meta.text

 @property
 def words(self):
  return re.search(r"Words: (\S*) ", self.meta).group(1)

 @property
 def rating(self):
  return re.search(r"Rated: (\S*) ", self.meta).group(1)

 @property
 def chapters(self):
  return re.search(r"Chapters: (\S*) ", self.meta).group(1)

 @property
 def lang(self):
  return re.search(r"- (\S*) -", self.meta).group(1)

 @property
 def genre(self):
  return re.search(r"(\S*) - Chapters:", self.meta).group(1)

 @property
 def characters(self):
  c = re.search(r"Published: \S* - (.*)", self.meta)
  if c:
   return c.group(1)
  else:
   return ""
 
 @property
 def published(self):
  return re.search(r"Published: (\S*)", self.meta).group(1)

 @property
 def updated(self):
  c = re.search(r"Updated: (\S*)", self.meta)
  if c:
   return c.group(1)
  else:
   return ""

 @property
 def reviews(self):
  c = re.search(r"Reviews: (\S*)", self.meta)
  if c:
   return c.group(1)
  else:
   return ""

 @property
 def favs(self):
  c = re.search(r"Favs: (\S*)", self.meta)
  if c:
   return c.group(1)
  else:
   return ""

 @property
 def follows(self):
  c = re.search(r"Follows: (\S*)", self.meta)
  if c:
   return c.group(1)
  else:
   return ""

 @property
 def _updated(self):
  s = self._meta.find_all("span")
  if len(s) == 2:
   return s[0]
  else:
   return ""

 @property
 def _published(self):
  s = self._meta.find_all("span")
  if len(s) == 2:
   return s[1]
  else:
   return s[0]
 
 @property
 def publish_time(self):
  return self._published["data-xutime"]

 @property
 def update_time(self):
  t = self._updated
  if t:
   return t["data-xutime"]
  else:
   return ""