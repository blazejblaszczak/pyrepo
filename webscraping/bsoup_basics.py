from bs4 import BeautifulSoup
from bs4 import Tag, NavigableString
import requests
import re


# Learning basic BeautifulSoup functionality
html_doc = """<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>
"""
# Create our soup
# Note that we are not dealing with explicitly specifiying a parser in this series,
# the default parser should work fine.
soup = BeautifulSoup(html_doc)
# Let's get the lay of the land first.
# prettify() formats the HTML string in such a way that we can clearly
# see the nested structure. This can be very helpful when parsing more complex documents.
print(soup.prettify())
# An HTML document is fundamentally a nested, tree-like structure made up of elements defined by tags. 
# HTML tags have parents, children, and siblings.
# Almost everything we do with BeautifulSoup relies on this structure.
# Now we're ready to learn how to traverse this tree and extract the data that we want!
# The most basic operation we have in BeautifulSoup is getting a tag.
# We actually already tried this when we were testing our BeautifulSoup installation.
# For instance, if we want to get the content of the <title> HTML tag, we can call:
print(soup.title, "\n")
# Tags themselves can have contents. For instance, we can access the string contained in an tag (if it exists)
# with:
print(soup.title.string, "\n")
# Since HTML is a nested structure, tags can also contain other tags. We can use the syntax we just learned to parse the tree to an arbitrary
# depth by selecting tags.
print(soup.p.b, "\n")
# We can get attributes of an tag using Python dictionary syntax. For example:
print(soup.p['class'], "\n")
# Note that when we access elements like this, BeautifulSoup will return the first element of the specified type that it finds
# in the document, even if there are more such elements. For example, this document has three <a> tags. If we call:
print(soup.a, "\n") 
# BeautifulSoup will return the first such tag it encounters in the tree.
# We'll take a look at how to find multiple elements here shortly.
# SEARCHING IN THE TREE
# What we just did in that basic example is essentially *the* fundamental operation of web scraping: searching for content
# in the document tree. Most of what we will learn from here on out will consist of more complex, powerful, and convenient ways
# of searching for the exact information we need in an HTML page.
# Here are a few more ways to search in BeautifulSoup.
# We aren't limited to finding single HTML tags by type. There are quite a few different
# criteria we can search with in BeautifulSoup. For instance, we can also search by CSS class.
# To do this, we'll use a function called find().
print(soup.find(class_="story"), "\n")
print(soup.find(href="http://example.com/lacie"), "\n")
# Note that since 'class' is a Python keyword, BeautifulSoup requires an underscore.
# The find() function is great, but more commonly we'll want to find *all* of a certain category of tag.
print(soup.find_all("a"), "\n")
# Note that find_all() will return results as a list
# We can also pass in a list of tags or whatever category we'd like BeautifulSoup to find for us:
print(soup.find_all(["a", "title"]), "\n")
# There are many more ways to use find_all() than we'll go over here. It is a critical tool in the web scraping toolbox.
# TRAVERSING THE TREE RELATIVE TO A TAG
# When web scraping, it's a very common situation to find yourself in to need to access tags relative to other tags.
# For instance, we might know some content we need is contained in some child tag of a tag we have, but we can't say
# with certainty where in the tree this content is. Likewise, we might need to reference information that we know exists one tag
# above our current tag, but we don't have a reference to its specific location. What can we do in these situations?
# To address this, BeautifulSoup provides functionality to traverse the document tree relative to a starting location.
# To start off, let's take a look at how we move down the tree.
# Grab a tag as a starting point. Tags are a special object in BeautifulSoup that expose a lot of useful properties.
p = soup.find(class_="story") # Grab the 'story' <p> tag.
# If we take a look at the document structure, we can see that this <p> tag has three <a> child tags.
# Let's see how we can access them.
# .contents
print(p.contents, "\n")
# .children
for child in p.children:
    print(child)
print("\n")
# The .contents and .children attributes only provide access to a tag's direct children. For instance:
body = soup.find("body")
print(body.contents, "\n")
print(len(body.contents), "\n") # Even though we can see the <a> tags in the output, the list returned does not actually contain these as individual tags.
# To get all the tags underneath a particular tag recursively, we'll need to use .descendants.
# .descendants
print(list(body.descendants))
print(len(list(body.descendants)), "\n")
# Note that .descendants, like .children, is a generator object and so must be cast to a list before it can be used in that way.
# You may notice that there are some additional children compared with what we might expect just from
# looking at the HTML tags. For instance, ',\n' appears frequently, and the string content of tags is counted as well.
# This behavior is normal, but it is something to be aware of when traversing the tree. When web scraping, we must always
# be cognisant of this sort of noise and useless data cropping up. If we're not careful they can cause bugs in our code,
# especially when we are parsing more complex documents.
# Going up the tree.
# Just as we can traverse down the tree through a tag's siblings, we can also traverse
# up the tree to find a tag's parents.
# The simplest way to do this is to use the .parent attribute:
print(soup.a.parent, "\n")
# We can also iterate through a tag's parents until we reach the top of the
# document by using the .parents attribute.
for p in soup.a.parents:
    print(p.name) # n.b. we can use the .name attribute to just get the name of the tag. Useful for debugging and checking output like this.
print("\n")
# Going side to side in the tree.
# Finally, there are situations where the tag we need is not above or below a certain tag, but is on the same level of the tree.
# We call this a sibling relationship, and we can access these tags in BeautifulSoup like this:
a = soup.a
print(a.next_sibling)
print(a.next_sibling.next_sibling)
print(a.next_sibling.previous_sibling)
print()
# Note that, as we mentioned before, a lot of data other than the HTML tags we want will be present. This can be especially
# confusing when trying to find siblings, as it appears in the document that each of the <a> tags are direct siblings of one another,
# but in fact are not (according to BeautifulSoup).


# In the previous section, we went over some core functionality of BeautifulSoup in context of 
# a very simple example HTML document. Now we're ready to take our first step into real web scraping
# by requesting a live webpage, saving it to a file, and feeding it into BeautifulSoup.
# ETHICAL SCRAPING
# When deciding what content we'd like to scrape, we should be mindful of the 
# ethics involved. Every request we make to a web server is going to take up some of its
# bandwidth, and web scraping projects can involve a lot of requests. Web scraping also has the
# tendency, if we're not careful, to require a large volume of requests in very quick succession,
# which can overwhelm web servers. To address this, it is convention for websites to host
# a file called robots.txt which lays out the site's rules for scraping. Sites are not obligated
# to allow scraping, and many completely disallow it. If you scrape a site which has explicitly
# banned the practice, you risk getting your IP blocked, and it is generally not a very 
# nice thing to do for the health of the whole web scraping ecosystem. The less the desires of site
# hosts are respected, the less welcoming sites will be for future web scrapers.
# Going forward, we'll be using Wikipedia as our source for web content. Let's take a look at what 
# Wikipedia's robots.txt has to say. While Wikipedia does not explicitly ban web scraping in general,
# we can see here that it does ban specific (usually commercial) scrapers and crawlers which have been
# poorly behaved in the past. It also gives us the following warning:
# "Please note: There are a lot of pages on this site, and there are
# some misbehaved spiders out there that go _way_ too fast. If you're
# irresponsible, your access to the site may be blocked."
# So there we have it. As long as we keep our requests to a reasonable rate, we should be good to go.
# We'll go over some concrete ways to do this, such as rate limiting, as it comes up.
# REQUESTING A PAGE
# Now that we're aware of what we're getting ourselves into, let's use the Python requests library to 
# get an HTML page that we can load into BeautifulSoup. 
# As an example, we'll be using the Wikipedia page for the Bristlecone pine, a species of tree: https://en.wikipedia.org/wiki/Bristlecone_pine
# request = requests.get("https://en.wikipedia.org/wiki/Bristlecone_pine") # GET request
# print(request.text)
# A great way to lessen the load on web servers when scraping is to minimize the number of times we need to send requests.
# Rather than request the page each time we run the program, it will be best to save it to a local file.
# with open("./html_docs/bristlecone.html", "w", encoding="utf-8") as f:
#     f.write(request.text)
# Now we can comment out our GET request code and load in the HTML from our new file.
# GET request code
def get_html(url, path):
    request = requests.get(url) # GET request
    print(request.text)    
    with open(path, "w", encoding="utf-8") as f:
        f.write(request.text)
# Read from file.
with open("./html_docs/bristlecone.html", "r", encoding="utf-8") as f:
    html = f.read()
# print(html)
# And that's all! We're ready to load the raw HTML into BeautifulSoup.
soup = BeautifulSoup(html, "html.parser")
print(soup.title, "\n")
# Taking a look at this article's HTML, we can see that it is very complex and difficult to read manually.
# This is where another important web scraping tool comes in - our browser.
# When scraping from a real webpage, inspecting the HTML via browser tools allows us to get our bearings.
# I'll be using Chrome for this example, but other major browsers have their own equivalents of these tools.
# --- GET A LIST OF SECTION HEADINGS. ---
# Upon inspection, we realize the actual text is not contained in the <h2> tag but in a <span> tag that is a child of it.
print(soup.find_all("span"), "\n")
# We realize we need to specify class="mw-headline"
section_headings = soup.find_all("span", attrs={"class": "mw-headline"})
print(section_headings, "\n")
section_headings = [span.string for span in section_headings] # Clean up
print(section_headings, "\n")
# NavigableString type. These are not your normal strings!!
print(type(section_headings[0]))
# They are still bs4 objects. Check this out.
print(section_headings[0].parent, "\n")
# --- PARSE THE INFOBOX ---
#   - Create a dictionary out of the scientific classification section
# Upon inspection in the browser, we see that the article infobox is defined at the top level by a <table> tag with the class
# "infobox biota". Let's grab that to start with.
infobox = soup.find("table", attrs={"class": "infobox biota"})
print(infobox, "\n")
# Let's take a closer look at how the infobox is structured in the inspector.
# We have a <table> with a <tbody> directly beneath and many <tr> (table row) tags below that.
# Each table row has one or more <td> (table data) tags.
# When scraping, we're always on the lookout for formatting patterns that can help us naturally filter
# data we want. Let's say we want to create a data structure of the taxonomy categories. We can see there is
# actually a consistent "identifier" for what we want. Only the taxonomy labels contain a ":" character.
# Let's use that fact to filter out what we want.
taxonomy = {}
# We can define our own functions with which to filter tags with find_all()
def taxonomy_filter(tag): 
    return ":" in tag.text and tag.name == "td"
filtered = infobox.find_all(taxonomy_filter) 
print(filtered, "\n")
print([str(tag.text).strip().replace(":", "") for tag in filtered]) # Clean up
# What we wanted, though, was a dictionary, so let's go ahead and do that.
for tag in filtered:
    sibling = tag.next_sibling.next_sibling # Note we need to do two .next_sibling, the first one is just white space!
    print(sibling.text.strip())
    taxonomy[tag.text.strip().replace(":", "")] = sibling.text.strip()
print("\n", taxonomy) # Note that since there were multiple 'clade' entries, one was overwritten. Since this is just an example, we'll let it be.
print(taxonomy["Kingdom"], "\n")
# Note that there are usually many possible ways to get at the data we want, and there is no one "correct"
# answer, although certain solutions may be more efficient, save time, or be simpler to write. For instance,
# another way we could have done this is: 
# This method uses another property of the sections we want - the number of child elements == 4.
def another_taxonomy_filter(tag):
    return tag.name == "tr" and len(list(tag.children)) == 4
print("Second method: ", infobox.find_all(another_taxonomy_filter), "\n")
# Hopefully you're beginning to see how powerful this can be. Using the code we just wrote, we could potentially scrape
# taxonomy data from many different articles, not just this one. (Show example)
# Let's do a few more exercises.
# --- FIND ALL LINKS IN BODY TEXT ---
# While it would be easy enough to find all of the <a> tags in the document, this would leave us with a 
# huge number of links that aren't necessarily relevant to us - things like the Wikipedia nav bar and side bar,
# Wikimedia links, citations, etc.
# We can see that the body text is all contained in <p> tags, so let's narrow our search down to these first.
p_content = soup.find_all("p")
print(p_content, "\n")
# Now let's get all the links (anchor tags) in the body content.
# Note that we have to loop through the different <p> tags and then concatenate all of their
# <a> tags into a final list.
body_links = []
for p in p_content:
    body_links += p.find_all("a")
print(body_links, "\n")
# We need to filter out the in-text citation links (hrefs all contain "#cite")
# The filter() function is an extremely useful built in Python function that allows us to filter lists on a function.
# Since this is one off, inline function, we're using a lambda.
body_links = list(filter(lambda a: "#cite" not in a['href'] and "Citation needed" not in a['title'], body_links))
print(body_links, "\n")
# Let's put it into a usable dictionary format with the name of the link as the key and the link itself as the value.
links = {}
for a in body_links:
    links[a['title']] = 'https://en.wikipedia.org' + a['href']
print(links, "\n")
print("Species: ", links["Species"], "\n")
# And check it out, we can follow all these links directly from VSCode! In more advanced web scraping we can
# use links like this to traverse other pages and start to really aggregate data in a way that would take a very long time by hand.
# --- FIND ALL IMAGES ---
# Hopefully you're starting to get the hang of how this works. We start with an objective and progressively narrow down our
# searches. Let's see how images are handled on Wikipedia.
imgs = soup.find_all("img")
print(imgs, "\n")
# Some of these are, for instance, the Wikipedia logo. Let's try and get it a bit more specific.
for i in imgs:
    if 'class' in i.attrs:
        print(i['class'])
    else:
        print(i)
print()
# We can see we need those images with class 'mw-file-element'. There are also a couple images without a 'class' attribute
# which are causing trouble.
imgs = list(filter(lambda img: 'class' in img.attrs, imgs)) # Prevent key errors
imgs = list(filter(lambda img: img['class'][0] == 'mw-file-element', imgs)) # Important note! img['class'] returns a list!
print(imgs, '\n')
# Try downloading one.
def download_image(url, path):
    response = requests.get(url)
    with open(path, "wb") as f: # Note we have to specify write bytes
        f.write(response.content)
# download_image('https:' + imgs[0]['src'], './image.png')
# You may notice that the image we got was quite low res. Wikimedia is not terribly straightforward to grab images from,
# so we won't go into detail of how to access the higher resolution versions here.
# --- GENERATE LIST OF CITATIONS ---
# Let's say we wanted to collect a list of citations that are used in the article.
# Looking at the browser inspector we can see the citations are contained in an <ol> tag with the class "references"
citations = soup.find("ol", attrs={"class": "references"})
print(citations, '\n')
# We can see that a lot of the actual citation data is contained several tags down in a <cite> tag. So let's get all of those.
cite_tags = citations.find_all("cite")
print(cite_tags, '\n')
# Let's check out the text available in the cite tags.
print(cite_tags[0].text)
# Filter for only citations that list an ISBN or a DOI.
isbn_doi = [c.text for c in cite_tags if 'ISBN' in c.text or 'doi' in c.text]
print(isbn_doi)
