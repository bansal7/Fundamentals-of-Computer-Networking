#!/usr/bin/python
import re
from HTMLParser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs = dict(attrs)
            regex_for_finding_links = "^/fakebook/*[0-9]"
            # print only those URLs that begin with
            # /fakebook/<somenumbers>
            if re.match(regex_for_finding_links,attrs['href']):
                self.links.append(attrs['href'])
                # print attrs['href']

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
        if self.secret_data_found == 1:
            self.flags.append(data)
