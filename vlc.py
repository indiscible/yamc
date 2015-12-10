import requests
import json

root= "http://:vlc@127.0.0.1:8080/requests/status.json"
cmd="?command=in_play&input="
def play(f):
    return requests.get(root + cmd + f).json()
def pause():
    return requests.get(root + "?command=pl_pause").json()
def status():
    return requests.get(root).json()
def shuffle():
    return requests.get(root + "?command=pl_random").json()
def repeat():
    return requests.get(root + "?command=pl_repeat").json()
