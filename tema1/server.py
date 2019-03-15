from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from os import curdir, sep
import socketserver
import os, sys
import logging
import cgi
import requests
import json
import time



def log(type, duration):
        dic = {"type" : type , "time" : time.ctime(), "response time" : duration}        
        with open("logs.txt", "a") as myfile:
                    myfile.write(json.dumps(dic) + "\n")

def request(url, params = {}):
    start = time.time()
    if len(params) == 0:
        response = requests.get(url).json()
    else:
        response = requests.get(url, params = params).json()
    log(url, time.time()-start)
    return response
               
class S(BaseHTTPRequestHandler):
       
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path=="/":
            self.path = "/index.html"
        try:
            #Check the file extension required and
            #set the right mime type

            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True
            
            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read().encode())
                f.close()
            
            #Generate metrics
            if self.path == "/metrics":
                total1 = 0
                nr1 = 0
                total2 = 0
                nr2 = 0
                for line in open("logs.txt"):
                    js = json.loads(line.replace("\'", "\""))
                    if js["type"] == "search":
                        total1 = total1 + float(js["response time"])
                        nr1 = nr1 + 1
                    else:
                        total2 = total2 + float(js["response time"])
                        nr2 = nr2 +1
                    
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write("<!DOCTYPE html><html><head><link rel=\"stylesheet\" href=\"index.css\"></head><body><h1>Average server response time: {}</h1><h1>Average API response time: {}</h1></body></html>".format(str(total1/nr1),str(total2/nr2)).encode())    

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Make the APIs request
        if self.path == "/search":
                print(self.headers)
                start = time.time()
                post_body = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))).decode())
                #First API
                response1 = request(url = 'https://api.adviceslip.com/advice/search/' + post_body["keyword"])
                if("slips" not in response1):
                    response1["slips"] = [{"advice" : "No advice found using keyword " +  post_body["keyword"]}]
                #Second API
                response2 = request(url = 'https://favqs.com/api/qotd', params = {"apiKey" : open("config.txt", "rt").read()})
                #Third API
                response3 = request(url = 'https://api.chucknorris.io/jokes/random')
                
                
                
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write("<!DOCTYPE html><html><head><link rel=\"stylesheet\" href=\"index.css\"></head><body><h2>Advice:</h2><p>{}</p><h2>Bonus Free Quote:</h2><p>{}</p><h2>Bonus Free Chuck Norris Joke:</h2><p>{}</p></body></html>".format(response1['slips'][0]['advice'], response2["quote"]["body"],  response3["value"]).encode())
                log("search", start)
       
class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass        
        
def run(server_class=ThreadingSimpleServer, handler_class=S, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

    