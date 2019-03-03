import _thread
import requests
import time

def request():
    response = requests.post('http://localhost:8081/search', json = {"keyword" : "spider"})
    
    
for i in range(10):
    for j in range(50):
        _thread.start_new_thread(request, ())
    time.sleep(10)