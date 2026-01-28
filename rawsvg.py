#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embed ABC in a raw HTML file usingng abc2svg or txtmux

@author: Bob Buckley

"""

# -p omits playback capability

import os
import re
import sys
import argparse
import datetime as dt
import base64
import urllib.request

import bs4

def getsrc(src, embed, mode="rt"):
    "get external src contents - filename or URL"
    # always embed files - HTML may get moved and filenames won't work
    if os.path.isfile(src): # should use URL
        with open(src, mode=mode) as imgx:
            data = imgx.read()
        return True, data
    elif embed and any(src.startswith(s) for s in ["http://", "https://"]):
        # url = urllib.request.urlopen(src)
        with urllib.request.urlopen(src) as urlsrc:
            data = urlsrc.read().decode()
        return True, data
    return False, None
       
def main():
    """
    input file x.abc
    """
    p = argparse.ArgumentParser(description="Embed ABC file is abc2scg/txtmus template")
    p.add_argument("-e", '--embed', action='store_false', help="do not embed <link href...> and <script src=...> in a single file - used for quicker testing")
    p.add_argument("-p", "--playback", action="store_false", help="do not include snd-?.js for playback")
    # p.add_argument("-c", '--contents', action='store_false', help="contents index (one page)")
    # p.add_argument("-C", '--contentsx', help="break Contents index at 'X. title, X. title'")
    # p.add_argument("-t", '--titles', action='store_false', help="Titles index (one page)")
    # p.add_argument("-T", '--titlesx', help="Titles index with breaks at 'X. title, X. title'")
    # p.add_argument("-b", '--byrhythm', action='store_false', help="index (one page)")
    # p.add_argument("-B", '--byrhythmx', help="Tune by rhythm index with breaks at 'X. title, X. title'")
    # p.add_argument("-r", '--rhythmsetindex', action='store_true', help="add index of sets by rhythm")
    # p.add_argument("-g", '--singleindex', action='store_true', help="include single tune index (tunes that are not in sets) by rhythm")
    # p.add_argument("-a", '--alphasetindex', action='store_true', help="set index sorted by name of first tune")
    # p.add_argument('--all', action='store_true', help="index all titles")
    # p.add_argument("-P", '--pavindex', action='store_true', help="index of singers (%p:v in ABC)")
    # p.add_argument("-d", '--danceindex', action='store_true', help="include 'dance index' for set dance tunes")
    p.add_argument('-o', '--output', help="output/target filename")
    xgrp = p.add_mutually_exclusive_group()
    xgrp.add_argument("-1", "--abc2svg", action='store_true', help="include abc2svg javascipt")
    xgrp.add_argument("-2", "--txtmus",  action='store_true', help="include txtmus javascipt")
    # # p.add_argument("-s", '--style', type=argparse, help="CSS file to be included")
    # p.add_argument("-f", "--template", default="abcsvg.htm", help="HTML template")
    p.add_argument('file', help="name of ABC file")
    args = p.parse_args(sys.argv[1:])
    if not args.txtmus: # args.abc2svg is true is args.txtmus is not true - no option
        args.abc2svg = True
    
    tmplsrc = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
<title>CBR English Session Tunebook - raw </title>
</head>
<body> 
  <p id="abcdate"></p>
<div>
        <script type="text/vnd.abc">
        </script>
</div> </body>
</html>
"""
    doc = bs4.BeautifulSoup(tmplsrc, 'lxml')
    body = doc.body
           
    # find last <meta> tag
    lastmeta = None
    for lastmetatag in doc.head.find_all("meta"):
        pass
    if not lastmeta:
        if doc.head.title:
            # insert <meta> before <title> ... if title is present
            lastmetatag = doc.head.title.previous_sibling
        else: 
            lastmetatag = doc.head.contents[0] # if no <meta> tags

    nt = doc.new_tag("meta", content="abcsvg") # BS4 fails with name="xxx" argument
    nt["name"]="generator"
    lastmetatag.insert_after("\n") # add linebreak after new tag
    lastmetatag.insert_after(nt)

    fnsrc = args.file
    print("ABC file:", fnsrc)
    abcstat = os.stat(fnsrc)
    mydate =  dt.datetime.fromtimestamp(abcstat.st_mtime).strftime("%d-%b-%Y").upper()
    if mydate.startswith('0'):
        mydate = mydate[1:] # get rid of ugly leading zeroes in date numbers
    print("Date:", mydate)
    
    x = body.find("p", id="abcdate")
    if x:
        x.string = args.file + " at " + mydate
        print("date string:", x.string)

    print("reading", fnsrc)
    with open(fnsrc, "rt") as src:
        abc = src.read()
    
    # fix ABC here
    # remove %%newpage, %%sep, empty X:s. T:-
    abc = re.sub(r'[\t ]+$', '', abc, flags=re.M) # remove ALL trailing spaces in lines
    oldabc = abc
    abc = re.sub(r'^\s*%%(newpage|sep)\b.*\n', '\n', abc, flags=re.M)
    if oldabc==abc:
        print("Remove %%sep and %%newpage failed!!!!!!!!!!!!!!!!!!!!!!!!!")
    abc = re.sub(r'^X:\s*\d+\n$', '\n\n', abc, flags=re.M)
    abc = re.sub(r'^T:\s*-', 'T:', abc, flags=re.M)
    abc = re.sub(r'\n\n+', '\n\n', abc)

    body.div.script.string = abc

    if args.abc2svg:
        jslist = ["http://moinejf.free.fr/js/abc2svg-1.js", 
                  "http://moinejf.free.fr/js/abcweb1-1.js"]
        if args.playback:
            jslist.append("http://moinejf.free.fr/js/snd-1.js")
    elif args.txtmus:
        jslist = ["http://moinejf.free.fr/js/tmcore-2.js",
                  "http://moinejf.free.fr/js/tmweb1-2.js"]
        if args.playback:
            jslist.append("http://moinejf.free.fr/js/snd-2.js")
    else:
        jslist =[]
    
    for js in jslist:
        print(" ... adding <script src={0}>".format(js))
        body.append(doc.new_tag("script", src=js, defer=""))
        body.append("\n")

    # if args.abc2svg:
    #     print(" ... adding abc2svg Javascript.")
    #     body.append(doc.new_tag("script", src="http://moinejf.free.fr/js/abc2svg-1.js", defer=""))
    #     body.append("\n")
    #     body.append(doc.new_tag("script", src="http://moinejf.free.fr/js/abcweb1-1.js", defer=""))
    #     body.append("\n")
    #     if args.playback:
    #         print(" ... and snd-1.js playback.")
    #         body.append(doc.new_tag("script", src="http://moinejf.free.fr/js/snd-1.js", defer=""))
    #         body.append("\n")
    # elif args.txtmus:
    #     print(" ... adding txtmus Javascript.")
    #     body.append(doc.new_tag("script", src="http://moinejf.free.fr/js/tmcore-2.js", defer=""))
    #     body.append("\n")
    #     body.append(doc.new_tag("script", src="http://moinejf.free.fr/js/tmweb1-2.js", defer=""))
    #     body.append("\n")
    #     if args.playback:
    #         print(" ... and snd-2.js playback.")
    #         body.append(doc.new_tag("script", src="http://moinejf.free.fr/js/snd-2.js", defer=""))
    #         body.append("\n")
    # else:
    #     print("Bad abc2svg or txtmus - js scripts:", [z for z in (x.rsplit('/',1)[-1] for x in doc.head.find_all("script") if x.has_attr("src"))])
    #     exit(1)

    for rtag in (x for x in doc.find_all("script") if x.has_attr("src")):
        efn = rtag["src"].rsplit('/', 1)[-1]
        if efn.startswith('snd-'):
            if os.path.isfile(rtag["src"]):
                print("embedding snd-?.js does not work (without a local /js directory for all the abs2svg stuff.)")
            if args.playback and args.embed:
                print("removing", rtag)
                if rtag: 
                    rtag.remove()
                continue
        # embed external content and remove src attribute
        em, txt = getsrc(rtag["src"], args.embed)
        if em:
            if any(efn.startswith(fn) for fn in ["abc2svg", "tmcore"]):
                txt = txt.replace("MIDI:{},", "") # fix loading of MIDI 
                print("fixing MIDI call when emdedding ...")
            print("  Embed script ", rtag["src"])
            txt = "\n"+txt.replace("'</script>", "'<'+'/script>") # break the string up so HTML loading works
            rtag.append(txt)
            del rtag["src"]
    del txt

    # finishing up
    d, fn = os.path.split(args.file)
    bn, ext = os.path.splitext(fn)
    target = args.output if args.output else os.path.join(d, bn+".htm")
    print("<script> length =", len(body.div.script.string))
 
    print("Output sent to", target)
    with open(target, "w") as dst:
        print(doc, file=dst)    # doc is BeautifulSoup so that does all the work here.
    print("Done.")
    return

if __name__=="__main__":
    main()
