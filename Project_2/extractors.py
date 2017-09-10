#!/usr/bin/python
import urlparse

def get_header_with_status(response_container):
    response_header = response_container.split("\r\n\r\n")[0]
    return response_header

def get_body(response_container):
    response_body   = response_container.split("\r\n\r\n")[1]
    return response_body

def get_status_code(response_header):
    header_parts = response_header.split("\r\n")
    status_line = header_parts[0]
    status_code = status_line.split(" ")[1]
    return status_code

def get_dictionary_of_cookies(response_header):
    dictionary_of_cookies = {}
    response_header_parts = response_header.split("\r\n")[1:]
    for item in response_header_parts:
        header_key = item.split(": ")[0]
        header_value = item.split(": ")[1]
        if header_key == "Set-Cookie":
            temp=header_value.split(";")[0]
            cookie_name  = temp.split("=")[0]
            cookie_value = temp.split("=")[1]
            dictionary_of_cookies[cookie_name] = cookie_value
    return dictionary_of_cookies

def get_dictionary_of_headers(response_header):
    dictionary_of_headers = {}
    response_header_parts = response_header.split("\r\n")[1:]
    for item in response_header_parts:
        header_key = item.split(": ")[0]
        header_value = item.split(": ")[1]
        dictionary_of_headers[header_key] = header_value
    return dictionary_of_headers

def get_path_of_redirect_location(dictionary_of_headers):
    navigate_to = dictionary_of_headers['Location']
    return urlparse.urlsplit(navigate_to).path

def fetch_server_response(stream_socket):
    # Just make sure you are starting with blank containers
    response_container      = ""
    server_response_message = ""
    while True:
        server_response_message = stream_socket.recv(1024)
        if server_response_message == "": break
        response_container += server_response_message
    return response_container
