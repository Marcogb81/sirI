#!/usr/bin/env python
#_*_coding:utf-8_*_
#
#   s i r . p y
#
"""Implementation of Semantic Information Retrieval AI.
Based on the article from Open Book Project: http://www.openbookproject.net/py4fun/sir/sir.html

This is a simple artificial intelligence that takes as inputs strings
of information. You can then ask it questions and it will try to answer them
based on context of previous knowledge. The relations was translated to spanish.
the store information store in mongodb
Example from english structure:
? the cat owns a collar
  I understand
? fluff is a cat
  I understand
? does fluff own a collar
  Not sure
? every cat owns a collar
  I understand
? does fluff own a collar
  Yes
?
"""
import re, sys

debug = 0
facts = []
rules = (
 # ( "(every|any|an|a) (.*) is (a|an) (.*)",   lambda g: addFact(g,"1s3|3S1")),
 ("(cada|cualquier|un|uno|una|unos|unas) (.*) es (un|uno|una|unos|unas) (.*)", lambda g: addFact(g, "1s3|3S1")),
 ("(.*) es (un|uno|una|unos|unas) (.*)", lambda g: addFact(g, "0m2|2M0")),
 ("(.*) es (.*)", lambda g: addFact(g, "0e1|1e0")),
 # pendiente de introducir las premisas del TRF, esto es memoria semantica:
 # X es mayor que Y
 # Y es menor que X
 # X es igual que Y
 # X es igual que Y
 # X es distinto que Y
 # Y es distinto que Y
 # X es a favor de Y
 # Y es contrario a X
 # X es mas que Y
 # Y es menos que Y
 # si X entonces Y
 # si no X entonces no Y
 # Esto es memoria de trabajo:
 # meter razonamiento silogistico
 # meter lógica difusa verbal, escala: Imposible=0, poco probable =1/4, probable= 1/2, muy probable =3/4, inevitable = 1
 # memoria episodica: quien, cuando y donde : hora, geolocalización, usuario
 ("(cada|cualquier|un|uno|una|unos|unas) (.*) tiene (un|uno|una|unos|unas) (.*)", lambda g: addFact(g, "1p3|3P1")),
 ("(.*) tiene (un|uno|una|unos|unas) (.*)", lambda g: addFact(g, "0p2|2P0")),
 ("(.*) tiene (.*)", lambda g: addFact(g, "0p1|1P0")),
 
 ("es (cada|cualquier|un|uno|una|unos|unas) (.*) (un|uno|una|unos|unas) (.*)", lambda g: getPath(g, "1e*s*3")),
 ("es (.*) (un|uno|una|unos|unas) (.*)", lambda g: getPath(g, "0e*ms*2")),
 ("hace que (cada|cualquier|un|uno|una|unos|unas) (.*) tiene (un|uno|una|unos|unas) (.*)", lambda g: getPath(g ,"1e*ms*ps*3")),
 ("hace algun (.*) tener (un|uno|una|unos|unas) (.*)", lambda g: getPath(g, "0S*Me*ps*2")),
 ("hace que (.*) tenga (un|uno|una|unos|unas) (.*)", lambda g: getPath(g, "0e*ms*ps*2")),
 ("volcado", lambda g: dump()),
 ("depurar", lambda g: toggleDebug()),
 ("salir", lambda g: sys.exit()),
   )


def addFact(grp, phrases) :
    global facts
    for p in phrases.split("|") :
        f = (grp[int(p[0])], p[1], grp[int(p[2])])
        if debug : print "  adding fact", f
        facts.append(f)
    print "  Entendido"

def matchSent (sent) :
    sent = re.sub("  *"," ",sent.strip().lower())
    for pattern, action in rules :
        match = re.match(pattern, sent)
        if match :
            action(match.groups())
            return
            
def getPath (grp, rule) :
    pattern = rule[1:-1]; start=grp[int(rule[0])]; stop=grp[int(rule[-1])]
    ans = []
    p = path(pattern, start, stop, ans=ans)
    if debug : detail = "%s %s" % (pattern,ans)
    else     : detail = ""
    if ans : print "  Si", detail
    else   : print "  No estoy seguro", detail

def path (pat, start, end, before={}, ans=[], sofar="", indent=" ") :
    used = {}
    used.update(before)
    if debug : print indent,"ruta - ",start," a ",end
    if len(indent) > 20 : return
    for fact in facts :
        if used.get(fact) : continue
        a,rel,b = fact
        if  a != start : continue
        sts = okSoFar(pat, sofar+rel)
        if not sts : continue
        used[fact] = 1
        if b == end :
            if sts == 2 : ans.append(sofar+rel)
        else :
            # find inner solutions recursively
            path (pat, b, end, used, ans, sofar+rel, indent+"  ")

def okSoFar (a, b) :
    "return 1 for partial match, 2 for complete match"
    ans = 2
    while a :
        if re.match("^%s$"%a, b) : return ans
        if a[-1] == '*' : a = a[:-2]
        else            : a = a[:-1]
        ans = 1
    return 0

def toggleDebug () :
    global debug
    debug = not debug

def dump () :
    for p,rel,q in facts : print "  %-10s : %s : %s" % (p,rel,q)

def main () :
    sys.stderr = sys.stdout
    for file in sys.argv[1:] :
        if file == '.' : return
        lins = open(file).readlines()
        for lin in lins :
            print lin.strip()
            matchSent (lin)
    while 1 :
        sent = raw_input("? ").lower()
        matchSent(sent)
        
if __name__ == "__main__" : main()
