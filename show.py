import json

with open("introspect.json", "r") as infile:
   reply= json.load(infile)


sigs= []
keys= []

def signature(obj):
    if hasattr(obj,"keys"):
        sigs.append("-".join(obj.keys()) )
        keys.extend (obj.keys())
    if hasattr(obj,"items"):
        for item in obj.items():
            signature(item[1])

signature(reply)
uniq= sorted(set(sigs))
for s in uniq:
    print s,sigs.count(s), s.count("-")

    
