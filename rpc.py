
class RPC(object):
    @classmethod
    def Get(c,ps):
        r={}
        for p in ps:
            name= "".join( p.split(".") )
            if hasattr(c, name ):
                r[p]= getattr(c,name)
        return r
            
    @classmethod
    def GetProperties(c,properties,**o):
        return c.Get(properties)

    @classmethod
    def GetInfoBooleans(c,booleans):
        return c.Get(booleans)
        
    @classmethod
    def GetInfoLabels(c,labels):
        return c.Get(labels)

    @classmethod
    def GetList(c,k,p,l):
        v= getattr(c,k)
        r= v[ l["start"]:l["end"] ]
        if p:
            r=[]
            for e in v[ l["start"]:l["end"] ]:
                r.append( { k:e[k] for k in p if e.has_key(k)} )
        return { k: r,
                 "limits":
                 { "start": 0, "end":len(r), "total":len(v) } }

