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
import re
import sqlite3

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
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        #Generate metrics
        if self.headers['Content-Type'] != 'application/json':
            self.send_response(415)
            self.send_header('Content-type','application/json')
            self.end_headers()
        elif re.match("/autori$", self.path):
            try:
                v = []
                conn = sqlite3.connect('autori.db')
                c = conn.cursor()
                for row in c.execute('SELECT * FROM AUTORI'):
                    v.append({'Id' : row[0], 'Nume' : row[1], 'Data Nasterii' : row[2], 'Tara' : row[3]})
                conn.close()
                
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write(json.dumps(v).encode())    
            except Exception:
                self.send_response(500)
                self.send_header('Content-type','application/json')
                self.end_headers()

        elif re.match("/autori/(\d+)$", self.path ):
            try:
                conn = sqlite3.connect('autori.db')
                c = conn.cursor()
                id = self.path.split('/')[-1]
                c.execute('SELECT * FROM AUTORI WHERE id = ?', (id))
                row = c.fetchone()
                
                if row is None:
                    self.send_response(404)
                    self.send_header('Content-type','application/json')
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header('Content-type','application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'Nume' : row[1], 'Data Nasterii' : row[2], 'Tara' : row[3]}).encode())    
            except Exception:
                self.send_response(500)
                self.send_header('Content-type','application/json')
                self.end_headers()

        else:
            self.send_response(404)
            self.send_header('Content-type','application/json')
            self.end_headers()

        
    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Make the APIs request
        if self.headers['Content-Type'] != 'application/json':
            self.send_response(415)
            self.send_header('Content-type','application/json')
            self.end_headers()
        elif re.match("/autori$", self.path):
            
            
            try:
                conn = sqlite3.connect('autori.db')
                c = conn.cursor()

                post_body = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))).decode())
                values = []
                for autor in post_body:
                    values.append( (autor['nume'], autor['data nasterii'], autor['tara']) )

                c.executemany('INSERT INTO AUTORI(Nume, Data_nasterii, Tara) VALUES (?, ?, ?)', values)
                conn.commit()
                conn.close()
    
            except (json.decoder.JSONDecodeError, TypeError):
                self.send_response(400)
                self.send_header('Content-type','application/json')
                self.end_headers()
            except Exception:
                self.send_response(500)
                self.send_header('Content-type','application/json')
                self.end_headers()
            else:                
                self.send_response(201)
                self.send_header('Content-type','application/json')
                self.end_headers()
                
        elif re.match("/autori/(\d+)$", self.path):
            self.send_response(405)
            self.send_header('Content-type','application/json')
            self.end_headers()
        
        else:
            self.send_response(404)
            self.send_header('Content-type','application/json')
            self.end_headers()
            
    def do_DELETE(self):
        if self.headers['Content-Type'] != 'application/json':
            self.send_response(415)
            self.send_header('Content-type','application/json')
            self.end_headers()
        elif re.match("/autori$", self.path):
            conn = sqlite3.connect('autori.db')
            c = conn.cursor()
            c.execute(' DELETE FROM AUTORI')
            c.execute('DELETE FROM sqlite_sequence WHERE name=\'AUTORI\';')
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()

        elif re.match("/autori/(\d+)$", self.path):
            
            id = self.path.split('/')[-1]
            conn = sqlite3.connect('autori.db')
            c = conn.cursor()
            c.execute(' DELETE FROM AUTORI WHERE id = ?', id)
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
        
        else:
            self.send_response(404)
            self.send_header('Content-type','application/json')
            self.end_headers()

    def do_PUT(self):
        if self.headers['Content-Type'] != 'application/json':
            self.send_response(415)
            self.send_header('Content-type','application/json')
            self.end_headers()
        elif re.match("/autori$", self.path):
            try:
                conn = sqlite3.connect('autori.db')
                c = conn.cursor()
                c.execute(' DELETE FROM AUTORI')
                c.execute('DELETE FROM sqlite_sequence WHERE name=\'AUTORI\';')
            
                post_body = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))).decode())
                values = []
                for autor in post_body:
                    values.append( (autor['nume'], autor['data nasterii'], autor['tara']) )

                c.executemany('INSERT INTO AUTORI(Nume, Data_nasterii, Tara) VALUES (?, ?, ?)', values)
                conn.commit()
                conn.close()
            
            except (json.decoder.JSONDecodeError, TypeError):
                self.send_response(400)
                self.send_header('Content-type','application/json')
                self.end_headers()
            except Exception:
                self.send_response(500)
                self.send_header('Content-type','application/json')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                
        elif re.match("/autori/(\d+)$", self.path):
            try:
                conn = sqlite3.connect('autori.db')
                c = conn.cursor()
                
                id = self.path.split('/')[-1]
                post_body = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))).decode())
                values = [post_body['nume'], post_body['data nasterii'], post_body['tara'], id]
                
                c.execute('SELECT * FROM AUTORI WHERE id = ?', (id))
                row = c.fetchone()
                
                if row is None:
                    self.send_response(404)
                    self.send_header('Content-type','application/json')
                    self.end_headers()
                    return
                else:
                    c.execute('UPDATE AUTORI SET  Nume = ?, Data_nasterii =  ?, Tara = ? WHERE id = ?', values)
                    conn.commit()
                    conn.close()
            
            except (json.decoder.JSONDecodeError, TypeError):
                self.send_response(400)
                self.send_header('Content-type','application/json')
                self.end_headers()
            except Exception:
                self.send_response(500)
                self.send_header('Content-type','application/json')
                self.end_headers()
            
            else:
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
            
        else:
            self.send_response(404)
            self.send_header('Content-type','application/json')
            self.end_headers()

    def do_PATCH(self):
        self.send_response(405)
        self.send_header('Content-type','application/json')
        self.end_headers()
            

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

    