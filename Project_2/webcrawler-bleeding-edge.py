#!/usr/bin/python
import sys
import re
import socket
import argparse
import urlparse
import constants
import socket_handler
import extractors
from constants import *
from HTMLParser import HTMLParser
from parser_classes import *

parser = argparse.ArgumentParser()
parser.add_argument("username", type=str, help="Please provide your username")
parser.add_argument("password", type=str, help="Please enter your password")
args = parser.parse_args()
USERNAME = args.username
PASSWORD = args.password

visited_links = []
links_to_visit = []
secret_flags  = []

CSRF_TOKEN = ""
INITIAL_SESSION_ID = ""
USER_SESSION_ID = ""

def get_login_page():
	global CSRF_TOKEN
	global INITIAL_SESSION_ID
	stream_socket = socket_handler.create_socket()
	stream_socket = socket_handler.connect_socket_to_host(stream_socket)

	# Navigate to the home page
	# print "GET "+LOGIN_PAGE+" ...",
	client_request_message = GET_LOGIN_PAGE
	stream_socket.send(client_request_message)
	get_response_container = extractors.fetch_server_response(stream_socket)
	response_headers      = extractors.get_header_with_status(get_response_container)
	response_status_code  = extractors.get_status_code(response_headers)
	stream_socket.close()
	if response_status_code == HTTP_STATUS_OK:
		dictionary_of_cookies = extractors.get_dictionary_of_cookies(response_headers)
		dictionary_of_headers = extractors.get_dictionary_of_headers(response_headers)
		CSRF_TOKEN = dictionary_of_cookies['csrftoken']
		INITIAL_SESSION_ID = dictionary_of_cookies['sessionid']
	elif response_status_code == HTTP_NOT_FOUND:
		print "Unable to GET the homepage of fakebook, please try some time later"
		print "OR"
		print "Try to connect from NEU-Wave"
		sys.exit()
	elif response_status_code == HTTP_SERVER_ERROR_RETRY:
		get_login_page()
	# print "DONE"


# Get the login page
get_login_page()

post_query = "POST "+FORM_ACTION+" "+HTTP_PROTOCOL+CRLF+\
"Host: fring.ccs.neu.edu"+CRLF+\
"Cookie: csrftoken=" + CSRF_TOKEN + "; sessionid=" + INITIAL_SESSION_ID +CRLF+\
PERSISTENT_CONNECTION_HEADER+CRLF+\
"Content-Type: application/x-www-form-urlencoded"+CRLF+\
"Content-Length: 109"+CRLF+CRLF+\
"csrfmiddlewaretoken=" + CSRF_TOKEN + "&username=" + USERNAME + "&password=" + PASSWORD + "&next=%2Ffakebook%2F"+CRLF+CRLF

# Create a new connection for logging into fakebook
# print "POST /accounts/login/?next=/fakebook/ ...",
stream_socket = socket_handler.create_socket()
stream_socket = socket_handler.connect_socket_to_host(stream_socket)
stream_socket.send(post_query)
post_response_container = extractors.fetch_server_response(stream_socket)
stream_socket.close()
# print "DONE"

post_response_headers      = extractors.get_header_with_status(post_response_container)
post_response_status_code  = extractors.get_status_code(post_response_headers)
post_dictionary_of_cookies = extractors.get_dictionary_of_cookies(post_response_headers)
post_dictionary_of_headers = extractors.get_dictionary_of_headers(post_response_headers)

NEXT_PATH = ""
if post_response_status_code == HTTP_MOVED_TEMPORARILY:
	NEXT_PATH = extractors.get_path_of_redirect_location(post_dictionary_of_headers)
elif post_response_status_code ==  HTTP_STATUS_OK:
	print "ERROR: Please enter a correct username and password. Note that both fields are case-sensitive."
	sys.exit()

links_to_visit.append(NEXT_PATH)
USER_SESSION_ID = post_dictionary_of_cookies['sessionid']

for current_url_to_visit in links_to_visit:
	if (current_url_to_visit not in visited_links) and (len(secret_flags) < FLAG_COUNT):
		request_message = "GET " + current_url_to_visit + " " + HTTP_PROTOCOL + CRLF + "Host: " + REMOTE_HOST + CRLF +\
		"Cookie: csrftoken=" + CSRF_TOKEN + "; sessionid="+ USER_SESSION_ID+CRLF+\
		PERSISTENT_CONNECTION_HEADER+CRLF+CRLF

		stream_socket = socket_handler.create_socket()
		stream_socket = socket_handler.connect_socket_to_host(stream_socket)
		# print "GET " + current_url_to_visit + " "+HTTP_PROTOCOL+" - ",
		stream_socket.send(request_message)
		response_message = extractors.fetch_server_response(stream_socket)
		response_headers = extractors.get_header_with_status(response_message)
		response_status_code  = extractors.get_status_code(response_headers)

		dictionary_of_headers = extractors.get_dictionary_of_headers(response_headers)
		visited_links.append(current_url_to_visit)
		stream_socket.close()
		# print response_status_code

		if response_status_code == HTTP_STATUS_OK:
			response_body = extractors.get_body(response_message)
			links_parser  = LinkParser()
			links_parser.feed(response_body)
			urls_found = links_parser.links
			for url in urls_found:
				if url not in visited_links and url not in links_to_visit:
					links_to_visit.append(url)

			secret_flag_parser = SecretFlagParser()
			secret_flag_parser.feed(response_body)
			flags_found = secret_flag_parser.flags
			secret_flags = secret_flags + flags_found

		elif response_status_code == HTTP_MOVED_PERMANENTLY or response_status_code == HTTP_MOVED_TEMPORARILY:
			if 'Location' in dictionary_of_headers:
				new_url = dictionary_of_headers['Location']
				if new_url not in visited_links and new_url not in links_to_visit:
					links_to_visit.append(new_url)
		elif response_status_code == HTTP_SERVER_ERROR_RETRY:
			links_to_visit.append(current_url_to_visit)
			visited_links.remove(current_url_to_visit)

# Clean up the flags_found array to have required content
for flag in secret_flags:
	print flag.split(": ")[1]