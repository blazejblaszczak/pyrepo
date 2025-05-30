from bs4 import BeautifulSoup
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
