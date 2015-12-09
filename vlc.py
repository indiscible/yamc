import requests
import json

root= "http://:vlc@127.0.0.1:8080/requests/status.json"

def play(f):
    url= root + "?command=in_play&input=" + f
    return requests.get(url).json()

def status():
    return requests.get(root).json()
    
