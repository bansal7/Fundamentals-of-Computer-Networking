#!/usr/bin/python
import sys
import re
import time
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

# Override the username and password for testing, comment this out later
# MY NUID
# USERNAME = "001611108"
# PASSWORD = "49BMMFF5"

# Bansal
# USERNAME = "001617243"
# PASSWORD = "X9FSRB70"

start_time = time.time()
visited_links = []
links_to_visit = []
secret_flags  = []
amount_of_data_received = 0

# Populate this once and use it till connection termination
# Only the session ID changes for a login logout
# Also, CSRF token will be given only once during login
# Store it and love it
CSRF_TOKEN = ""

# Initial Session ID
INITIAL_SESSION_ID = ""
# Session ID changes once you login, this session id can be used to fetch all internal pages
# Hence a handy constant for all future GET requests
USER_SESSION_ID = ""


def get_login_page():
	global amount_of_data_received
	global CSRF_TOKEN
	global INITIAL_SESSION_ID
	stream_socket = socket_handler.create_socket()
	stream_socket = socket_handler.connect_socket_to_host(stream_socket)

	# Navigate to the home page
	print "GET "+LOGIN_PAGE+" ...",
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
		if 'Content-Length' in dictionary_of_headers:
			amount_of_data_received+=int(dictionary_of_headers['Content-Length'])
	elif response_status_code == HTTP_NOT_FOUND:
		print "Unable to GET the homepage of fakebook, please try some time later"
		print "OR"
		print "Try to connect from NEU-Wave"
		sys.exit()
	elif response_status_code == HTTP_SERVER_ERROR_RETRY:
		get_login_page()
	print "DONE"


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
print "POST /accounts/login/?next=/fakebook/ ...",
stream_socket = socket_handler.create_socket()
stream_socket = socket_handler.connect_socket_to_host(stream_socket)
stream_socket.send(post_query)
post_response_container = extractors.fetch_server_response(stream_socket)
stream_socket.close()
print "DONE"

post_response_headers      = extractors.get_header_with_status(post_response_container)
post_response_status_code  = extractors.get_status_code(post_response_headers)
post_dictionary_of_cookies = extractors.get_dictionary_of_cookies(post_response_headers)
post_dictionary_of_headers = extractors.get_dictionary_of_headers(post_response_headers)

if 'Content-Length' in post_dictionary_of_headers:
	amount_of_data_received+=int(post_dictionary_of_headers['Content-Length'])

NEXT_PATH = ""
if post_response_status_code == HTTP_MOVED_TEMPORARILY:
	# This means the server is redirecting to another location
	# Just fetch the path, Host remains the same
	NEXT_PATH = extractors.get_path_of_redirect_location(post_dictionary_of_headers)
elif post_response_status_code ==  HTTP_STATUS_OK:
	# It means, we were not redirected to logged in page, we are still in same page
	# to which we submitted
	# Possible reason: Wrong username/password
	# Display error and exit
	print "ERROR: Please enter a correct username and password. Note that both fields are case-sensitive."
	sys.exit()

links_to_visit.append(NEXT_PATH)
# Logged in users session id : Fetch the SESSION ID
USER_SESSION_ID = post_dictionary_of_cookies['sessionid']

# NEXT_PATH = /fakebook/
# Enter the user home page
# stream_socket = socket_handler.create_socket()
# stream_socket = socket_handler.connect_socket_to_host(stream_socket)
#
# # Navigate to user home page
# client_request_message = "GET "+NEXT_PATH+" "+HTTP_PROTOCOL+CRLF+\
# "Host: "+REMOTE_HOST+CRLF+\
# "Cookie: csrftoken=" + CSRF_TOKEN + "; sessionid="+ USER_SESSION_ID+CRLF+\
# PERSISTENT_CONNECTION_HEADER+CRLF+CRLF
#
# print "GET "+NEXT_PATH+"...",
# stream_socket.send(client_request_message)
# response_message_for_get = extractors.fetch_server_response(stream_socket)
# response_headers = extractors.get_header_with_status(response_message_for_get)
# response_body	 = extractors.get_body(response_message_for_get)
#
# dictionary_of_headers = extractors.get_dictionary_of_headers(response_headers)
# if 'Content-Length' in dictionary_of_headers:
# 	amount_of_data_received+=int(dictionary_of_headers['Content-Length'])
#
# stream_socket.close()
# print "DONE\n"
#
# links_parser = LinkParser()
# links_parser.feed(response_body)
#
# # Fetched the URLs in the home page of user
# homepage_urls = links_parser.links
# links_to_visit += homepage_urls


# current_url_to_visit = "/fakebook/473929244/friends/2/"

print "INITIAL LINKSTOVISIT ARRAY: "+str(links_to_visit)

# exit_counter = 0
track_of_flag_pages = []
number_of_pages_visited = 0
number_of_301_302_http_codes = 0
number_of_500_http_codes = 0
number_of_200_http_codes = 0
# FOR_LOOP_BREAK_COUNTER = 5000
for current_url_to_visit in links_to_visit:
	# if(exit_counter == FOR_LOOP_BREAK_COUNTER ): break
	if (current_url_to_visit not in visited_links) and (len(secret_flags) < FLAG_COUNT):
		# Steps:
		# 1. Construct the GET request message and Append the required Cookies
		# 2. create a socket connection and send the GET request
		# 3. Receive the response
		# 4. Parse the response header for HTTP_STATUS_OK, if it is 500, retry
		# 5. If it is 200 OK, parse the body of response for more links and secret flag
		# 6. add whatever you get out of secret flags to array
		request_message = "GET " + current_url_to_visit + " " + HTTP_PROTOCOL + CRLF + "Host: " + REMOTE_HOST + CRLF +\
		"Cookie: csrftoken=" + CSRF_TOKEN + "; sessionid="+ USER_SESSION_ID+CRLF+\
		PERSISTENT_CONNECTION_HEADER+CRLF+CRLF

		stream_socket = socket_handler.create_socket()
		stream_socket = socket_handler.connect_socket_to_host(stream_socket)
		print "GET " + current_url_to_visit + " "+HTTP_PROTOCOL+" - ",
		stream_socket.send(request_message)
		response_message = extractors.fetch_server_response(stream_socket)
		response_headers = extractors.get_header_with_status(response_message)
		response_status_code  = extractors.get_status_code(response_headers)

		dictionary_of_headers = extractors.get_dictionary_of_headers(response_headers)
		if 'Content-Length' in dictionary_of_headers:
			amount_of_data_received+=int(dictionary_of_headers['Content-Length'])

		visited_links.append(current_url_to_visit)
		stream_socket.close()
		print response_status_code

		if response_status_code == HTTP_STATUS_OK:
			number_of_200_http_codes+=1
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
			if flags_found:
				track_of_flag_pages.append(number_of_pages_visited)
			secret_flags = secret_flags + flags_found

		elif response_status_code == HTTP_MOVED_PERMANENTLY or response_status_code == HTTP_MOVED_TEMPORARILY:
			number_of_301_302_http_codes+=1
			if 'Location' in dictionary_of_headers:
				new_url = dictionary_of_headers['Location']
				if new_url not in visited_links and new_url not in links_to_visit:
					links_to_visit.append(new_url)
		# I don't think, we need to handle 403 and 404.
		# Reason: We have already visited this link and we have already added
		# this link to the list of visited links.
		# In any case, the program will never visit these links

		# elif response_status_code == HTTP_FORBIDDEN:
		# 	"nothing"
		# elif response_status_code == HTTP_NOT_FOUND:
		# 	"nothing"
		elif response_status_code == HTTP_SERVER_ERROR_RETRY:
			number_of_500_http_codes+=1
			links_to_visit.append(current_url_to_visit)
			visited_links.remove(current_url_to_visit)
		number_of_pages_visited+=1

# Show what you did
print "Visited links: " + str(visited_links) +"\n"
print "Links to visit: "+ str(links_to_visit) +"\n"
print "Collected secret flags: "+str(secret_flags)+"\n"
print "Number of pages visited to find the secret flag : " + str(number_of_pages_visited)
print "Amount of data received: "+str(round (amount_of_data_received/float(1024*1024),2))+"MB"
print ("Time taken to search : %s minutes " % str(round((time.time() - start_time)/60,2)))
print "Extra information: "
print "Number of times 301/302 HTTP status codes were obtained: "+str(number_of_301_302_http_codes)
print "Number of times 500 HTTP status codes were obtained: "+str(number_of_500_http_codes)
print "Number of times 200 HTTP status codes were obtained: "+str(number_of_200_http_codes)
print "Pages where flags were found: " + str(track_of_flag_pages)

# Clean up the flags_found array to have required content
# for flag in secret_flags:
# 	print flag.split(": ")[1]
