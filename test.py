src= "test-yamc.py"

for line in open(src):
    if len(line)>1:
        r= exec line
        print line,"->",r
