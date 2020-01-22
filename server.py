#  coding: utf-8 
import socketserver
from os import path
from email.utils import formatdate

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def getHTTPVersion(self):
        '''
            a method to get HTTP Version from the user's request
                parameter: None
                return: a string of HTTP version
        '''
        return self.data.split()[2]
    def getRequestedURL(self):
        '''
            a method to get URL from the user's request
                parameter: None
                return: a string of url
        '''
        return self.data.split()[1][1:]
    def getRequestMethod(self):
        '''
            a method to get requested method
                parameter: None 
                return: a string of method name
        '''
        return self.data.split()[0]
    
    def findFilePath(self):
        '''
            a method to decide the status code and return the file path
            parameter: None
            return: a path to the certain html file. 
        '''
        url =''
        if 'www' not in self.url:
            url = 'www/'+self.url
        current_path = path.curdir+'/'+url
        if path.isdir(current_path):
            if self.url == '':
                self.status_code = 200
            elif self.url[-1] == '/':
                self.status_code = 200
            else:
                self.url += '/'
                current_path += '/'
                self.status_code = 301
            current_path +='index.html'
            self.filetype = 'html'  #Since we redirect to the index.html, the filetype is html
        elif path.isfile(current_path):
            self.status_code = 200
            self.filetype = current_path.split('.')[-1]
        else:
            self.status_code = 404
        #For example, UNIX, Microsoft Windows, and other operating systems use ".." as a '
        #path component to indicate a directory level above the current one.'
        if '..' in self.url:
            self.status_code = 404
        #Check given method if valid or not.
        if self.method in ['POST','DELETE','PUT']:
            self.status_code = 405
        return current_path
    def handleStatusCode(self,path_to_file):
        '''
            a method to handle cases with different status code 
                parameter: 
                    path_to_file, a string of file path
                return:
                    a string format of http response
        '''
        headers = '''{} {}\r\nContent-Type: {};\r\nContent-Length: {}\r\nConnection: Closed\r\n'''
        content = '''<html>\r\n<head>\r\n<title>{}</title>\r\n</head>\r\n<body>\r\n<h1>{}</h1>\r\n<p>{}</p>\r\n</body>\r\n</html>\r\n''' 
        filetype = 'text/{}'.format(str(self.filetype))
        if self.status_code == 404: 
            comment = 'The requested URL .{} was not found on this server.'
            comment = comment.format(self.url)
            content = content.format(str(404)+' NOT FOUND','Not Found',comment)
            headers = headers.format(self.version,'404 NOTFOUND',filetype,str(len(content)))
            return headers+'\r\n'+content
        
        if self.status_code == 405:
            comment = 'The requested Method {} was NOT Allowed'
            comment = comment.format(self.method)
            content = content.format(str(405)+' Method Not Allowed','Method Not Allowed',comment)
            headers = headers.format(self.version,'405 Method Not Allowed',filetype,str(len(content)))
            return headers+'\r\n'+content
        
        if self.status_code == 200:
            with open(path.curdir+'/'+path_to_file,'r') as f:
                content = f.read()    
            headers = headers.format(self.version,'200 OK',filetype,str(len(content)))
            return headers+'\r\n'+content
        
        if self.status_code == 301:
            with open(path.curdir+'/'+path_to_file,'r') as f:
                content = f.read()
            location = 'Location: {}\r\n'.format(self.url)
            content = content
            headers = headers.format(self.version,'301 Moved Permanently',filetype,str(len(content)))
            headers = headers + location
            return headers+'\r\n'+content
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        self.method = self.getRequestMethod()
        self.url = self.getRequestedURL()
        self.version = self.getHTTPVersion()
        self.status_code = 200
        self.filetype = None
        self.request_url = None
        path_to_file = self.findFilePath()
        self.repose_content = self.handleStatusCode(path_to_file)
        self.request.sendall(bytearray(str(self.repose_content),'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
