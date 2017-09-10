#!/usr/bin/python
import re
from HTMLParser import HTMLParser

regex_for_finding_links = "^/fakebook/*[0-9]"

# HTML Data to analyse
HTMLdata = """<html><head><title>Fakebook</title><style TYPE="text/css"><!--\n#pagelist li { display: inline; padding-right: 10px; }\n--></style></head><body><h1>Fakebook</h1><p><a href="/fakebook/">Home</a></p><hr/>'
<h1>Welcome to Fakebook</h1><p>Get started by browsing some random people\'s profiles!</p>
<h2 class="secret_flag">sdkkfdskfkjsdhkjfhuehifwuehfiuhweuif</h2>
<ul><li><a href="/fakebook/246869555/">Boveli Xipott</a></li>
<li><a href="/fakebook/248039637/">Xac Proxik</a></li>
<li><a href="/fakebook/248670702/">Fatuciru Lolob</a></li>
<li><a href="/fakebook/248699766/">Colson Crijik</a></li>
<li><a href="/fakebook/249014933/">Nenababonu Justiss</a></li>
<li><a href="/fakebook/249659119/">Batisihuba Stovic</a></li>
<li><a href="/fakebook/250129083/">Jalujosi Jacobi</a></li>
<li><a href="/fakebook/250139692/">Darell Kammerzell</a></li>
<li><a href="/fakebook/250573573/">Lovonufe Troxip</a></li>
<h2 class="secret_flag">sdkkfdskfkjsdhkjfhuehifwuehfiuhweuif</h2>
<li><a href="/fakebook/250649500/">Waylon Mulvahill</a></li></ul>
<h6>Fakebook is run by <a href="http://www.ccs.neu.edu/home/choffnes/">
David Choffnes</a> at                        \n
<a href="http://www.northeastern.edu">NEU</a>.
For questions, contact <a href="mailto:choffnes@ccs.neu.edu">David Choffnes</a></h6></body></html>\n"""


# create a subclass and override the handler methods
class LinkParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs = dict(attrs)
            # print only those URLs that begin with
            # /fakebook/<somenumbers>
            if re.match(regex_for_finding_links,attrs['href']):
                print attrs['href']
    # def handle_endtag(self, tag):
    #     print "Encountered an end tag :", tag
    # def handle_data(self, data):
    #     if self.lasttag == 'h2':
    #         print "Encountered some data  :", data

    class SecretFlagParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.secret_data_found = 0
            self.flags = []
        def handle_starttag(self, tag, attrs):
            if tag == 'h2':
                attrs = dict(attrs)
                if ('class' in attrs) and ('style' in attrs):
                    if attrs['class'] == "secret_flag" and attrs['style'] == "color:red":
                        self.secret_data_found = 1
                    else:
                        self.secret_data_found = 0
                else:
                        self.secret_data_found = 0
            else:
                self.secret_data_found = 0
        def handle_data(self, data):
            # if self.lasttag == 'h2':
            if self.secret_data_found == 1:
                self.flags.append(data)
                # print repr(data)


# instantiate the links_parser and fed it some HTML
links_parser = LinkParser()
links_parser.feed(HTMLdata)

# instantiate the secret_flag_parser and fed it some HTML
secret_flag_parser = SecretFlagParser()
secret_flag_parser.feed('<html><head><title>Fakebook</title><style TYPE="text/css"><!--\n#pagelist li { display: inline; padding-right: 10px; }\n--></style></head><body><h1>Fakebook</h1><p><a href="/fakebook/">Home</a></p><hr/>'
'<h1>Welcome to Fakebook</h1><p>Get started by browsing some random people\'s profiles!</p>'
'<h2 class="secret_flag" style="color:red">kooroshmodibhakt</h2>'
'<h2 style="color:red">kooroshmodibhakt</h2>'
'<h2 class="kachda">kooroshnamobhakt</h2>'
'<ul><li><a href="/fakebook/246869555/">Boveli Xipott</a></li>'
'<li><a href="/fakebook/248039637/">Xac Proxik</a></li>'
'<li><a href="/fakebook/248670702/">Fatuciru Lolob</a></li>'
'<li><a href="/fakebook/248699766/">Colson Crijik</a></li>'
'<li><a href="/fakebook/249014933/">Nenababonu Justiss</a></li>'
'<li><a href="/fakebook/249659119/">Batisihuba Stovic</a></li>'
'<li><a href="/fakebook/250129083/">Jalujosi Jacobi</a></li>'
'<li><a href="/fakebook/250139692/">Darell Kammerzell</a></li>'
'<li><a href="/fakebook/250573573/">Lovonufe Troxip</a></li>'
'<h2 class="secret_flag">Chindichitranna</h2>'
'<li><a href="/fakebook/250649500/">Waylon Mulvahill</a></li></ul>'
'<h6>Fakebook is run by <a href="http://www.ccs.neu.edu/home/choffnes/">'
'David Choffnes</a> at                        \n'
'<a href="http://www.northeastern.edu">NEU</a>.'
'For questions, contact <a href="mailto:choffnes@ccs.neu.edu">David Choffnes</a></h6></body></html>')

print secret_flag_parser.flags