#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABC to HTML book using abc2svg - Javascript ABC to SVG software
see http://moinejf.free.fr/

Revised indexing 9/12/2025
Fixed formatting - Dec 2025 and Jan 2026

@author: Bob Buckley

to do:
* title and front-matter files from command line so more generic templates can be provided
* meta tag follows last meta tag or preceeds title tag in template
* develop options for an optional *provenance* section at the end of the tune book 
* maybe have names for sets (maybe a separate data file ... with names for sets ... and full set playback)
* image file source from command line
* unify adding abc2svg.js source code 
* merge -r raw option?
* embed %%MIDI stuff - fix embedding MIDI.js and sound files
* local version  of javascript files (alternative to embedding)? Copy from URL to local location for local access during use?
"""

# This code embeds image files and other file types so that we end up with a single HTML file.
# -e option keeps remote URLs ... which means smaller file and playback (needs dynamic loading) works
# -p omits playback capability

import os
import re
import sys
import argparse
import datetime as dt
import base64
import urllib.request

import bs4

import ABClib

doc, body0, nblk = None, None, None
x2page = {}

def addindex(iname, items, sort=True, breakat=[], nochords=False):
    """
    insert an index into the document
    iname might be "Dance Index"
    items = ((category, 'title1', 'xid1'), (category, 'title2', 'xid2'), ...
    xid's are strings that can be interpreted as integers
    this routine sorts the index items when arg. sort is True.
    We should probably send the link ID rather than using the global x2page
    """
    global doc, body0, nblk, x2page
    didiv = doc.new_tag("div")
    didiv["class"] = "section index"
    didiv.append("\n    ")
    didiv.append(doc.new_tag("h1"))
    didiv.append("\n    ")
    didiv.append(doc.new_tag("div"))
    didiv.div.append("\n")
    didiv.div["class"] = ('colidx nochords' if nochords else 'colidx chords')

    xbreakat = [([y.strip() for y in x.split(".",1)]+[""])[:2] for x in breakat]

    idxname = iname.replace(' ', '').lower()
    didiv["id"] = idxname
    didiv.h1.string = iname
    body0.insert_before(didiv)
    if sort:
        idxs = sorted(items, key=lambda x:(x[0], x[1].lower() if type(x[1]) is str else x[1], int(x[2])))
    else:
        idxs = items
    print(" ... adding "+iname+".", len(idxs), 'items.')
    pcat = None
    for idx in idxs:
        cat, dn, xid, ktag = idx[0], idx[1], idx[2], idx[3] if len(idx)>3 else ''
        # some indices are too long ... so break them into sections to navigation at the top of the page does not overlap
        if any((xid==x[0] and dn.startswith(x[1])) for x in xbreakat): # add start of title check later
            print("in", iname, "break at", xid+". "+dn)
            didiv = doc.new_tag("div", attrs={'class': 'section index'})
            #didiv["class"] = "section index"
            didiv.append(doc.new_tag("h1"))
            didiv.h1.string = iname + (" (cont.)")  # index title cont. 
            didiv.append(doc.new_tag("div", attrs={'class': ('colidx nochords' if nochords else 'colidx chords')}))
            #didiv.div["class"] = "colidx"
            didiv.div.append("\n")
            body0.insert_before(didiv)

        didiv.div.append('\t')
        # idxitm = doc.new_tag('button', attrs={'class':'title'})
        idxitm = doc.new_tag('button')
        if cat!=pcat and cat:
            # new category - add <h2> and div to keep with the next button
            dx = doc.new_tag('div', attrs={'class':'ncb'}) # class=ncb means no-column-break
            h2 = doc.new_tag('h2')
            h2.string = cat
            dx.append(h2)
            dx.append('\n')
            dx.append(idxitm)
            if ktag: dx.append(ktag)
        else:
            didiv.div.append(idxitm)
            if ktag: didiv.div.append(ktag)
            dx = doc.new_tag('br')
        didiv.div.append(dx)
        didiv.div.append('\n')
        pcat = cat
        a = doc.new_tag("a", href='#'+x2page[xid])
        if type(dn) is str:
            xtag = doc.new_tag('div', attrs={'class': 'xid'})
            xtag.string = xid+'.'
            a.append(xtag)
            stag = doc.new_tag('div')
            stag.string = ABClib.fixtitle(dn)
            a.append(stag)
        else:
            dnstr = '<b>'+dn[0]+"</b><br/>\n"+", ".join(ABClib.fixtitle(t) for t in dn[1:])
            x = bs4.BeautifulSoup("<div>"+dnstr+"</div>", 'lxml') 
            a.append(x.body.div)
        idxitm.append(a) # as in template and its CSS

    if nblk:
        print(" ... adding", iname, "link to Nav Block.")
        bx = doc.new_tag("span")
        bx.append(doc.new_tag("a", href="#"+idxname))
        bx.a.string = iname
        nblk.append(bx)
        bx.insert_after("\n")
        bx.insert_before("  ")

    return

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
    input files x.abc and x.xhtml
    Add indices and abc2svg/txtmus Javascript ... if required
    Output to target
    """
    global doc, body0, nblk
    global x2page
    redigits = re.compile('\d+')
    def fnpage(s):
        fs = s.rsplit(' ', 2)
        return fs[0], ''.join(fs[1:])
    p = argparse.ArgumentParser(description="ABC XHTML indexer")
    p.add_argument("-e", '--embed', action='store_false', help="do not embed <link href...> and <script src=...> in a single file - used for quicker testing")
    p.add_argument("-p", "--playback", action="store_false", help="do not include snd-?.js for playback")
    p.add_argument("-c", '--contents', action='store_false', help="contents index (one page)")
    p.add_argument("-C", '--contentsx', help="break Contents index at 'X. title, X. title'")
    p.add_argument("-t", '--titles', action='store_false', help="Titles index (one page)")
    p.add_argument("-T", '--titlesx', help="Titles index with breaks at 'X. title, X. title'")
    p.add_argument("-b", '--byrhythm', action='store_false', help="index (one page)")
    p.add_argument("-B", '--byrhythmx', help="Tune by rhythm index with breaks at 'X. title, X. title'")
    p.add_argument("-r", '--rhythmsetindex', action='store_true', help="add index of sets by rhythm")
    p.add_argument("-g", '--singleindex', action='store_true', help="include single tune index (tunes that are not in sets) by rhythm")
    p.add_argument("-a", '--alphasetindex', action='store_true', help="set index sorted by name of first tune")
    p.add_argument('--all', action='store_true', help="index all titles")
    p.add_argument("-P", '--pavindex', action='store_true', help="index of singers (%p:v in ABC)")
    p.add_argument("-d", '--danceindex', action='store_true', help="include 'dance index' for set dance tunes")
    p.add_argument("-G", '--grid2', action='store_true', help="use %%grid2 1 to present chord charts, not music")
    p.add_argument('-o', '--output', help="output/target filename")
    xgrp = p.add_mutually_exclusive_group()
    xgrp.add_argument("-1", "--abc2svg", action='store_true', help="include abc2svg javascipt")
    xgrp.add_argument("-2", "--txtmus",  action='store_true', help="include txtmus javascipt")
    # p.add_argument("-s", '--style', type=argparse, help="CSS file to be included")
    p.add_argument("-f", "--template", default="abcsvg.htm", help="HTML template (default is abcsvg.htm)")
    p.add_argument('file', help="name of ABC file")
    args = p.parse_args(sys.argv[1:])
    
    # read an HTML file as the basis for the output
    print("Template from", args.template)
    with open(args.template, mode="rt") as tmplsrc:
        doc = bs4.BeautifulSoup(tmplsrc, 'lxml')
           
    # changes to body
    body = doc.body
    for body0 in body.children:
        pass
    # create <meta content-"abcsvg" name="generator"> tag for insertion
    nt = doc.new_tag("meta", content="abcsvg") # BS4 fails with name="xxx" argument
    nt["name"]="generator"

    # insert <meta> after last <meta>, before <title> ... or at the start of <head>
    for lastmetatag in doc.head.find_all("meta"):
        pass
    else:         
        lastmetatag = doc.head.title.previous_sibling if doc.head.title else doc.head.contents[0]
    
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
        x.string = mydate
    else:
        print("****** date not set ***********")
    nblk = body.find(id="nblist")

    print("reading", fnsrc)

    # read the ABC file into a Songsets class
    ss = ABClib.Songsets(fnsrc, midi=args.playback)
    # print(len(ss.sets), "sets found.")
    abcs = tuple(ss.abcs()) # songlist rather than list of sets
    print(len(abcs), "songs/tunes in", len(ss.sets), "sets.")
    print()
    
    print("Found", len(ss.sets), "sets in", fnsrc)
    # step through adding songsets ABC into HTML
    x2page =dict((x.xid, s[0].id()) for s in ss.sets for x in s)
    abcsect = body # could be different
    if ss.hdr:
        if args.grid2:
            ss.hdr.append("%%grid2 1")
        # we leave %%MIDI lines in the header/parameters block - they should be OK there - just keep it simple
        abcstr = "".join(t+"\n" for t in ss.hdr+[''])
        newtag = doc.new_tag("script", type="text/vnd.abc")
        newtag["class"] = "parm"
        newtag.string = abcstr
        hdrdiv = doc.new_tag("div", style="visibility: hidden; display:inline; height: 0px;")
        hdrdiv.append(newtag)
        hdrdiv.append("\n")
        abcsect.append(hdrdiv)
        abcsect.append("\n")

    tfix = re.compile(r'^T:\s*-') # titles starting with a minus sign (omitted from indices)
    for sset, nset in zip(ss.sets, ss.sets[1:]+[[]]):
        svgid = sset[0].id()

        newtag = doc.new_tag("div", id=svgid)
        newtag.append("\n  ")
        newtag["class"] = "abcdiv"+(' sp' if len(sset)>1 else '') # sets get sp class, os a separate page in CSS
        newtag.append(doc.new_tag("script", type="text/vnd.abc"))
        # remove - from T: lines when present (leading minus means omit title from index)
        # %%MIDI commands in songs screw up abc2svg playback
        xlines = '\n'.join('X: '+s.xid+"\n"+''.join(tfix.sub('T:', x)+"\n" for x in s.lines if not x.startswith('%%MIDI')) for s in sset)
        newtag.script.string =  xlines + ("\n%%sep\n\n" if len(sset)==1 and len(nset)==1 else "\n")
        newtag.append("\n")
        abcsect.append(newtag)
        abcsect.append("\n")
                                   
    # add tune index
    # omit titles with '-' at start
   
    if args.contents or args.contentsx:
        # add Table of Contents - only the first title of athe tune - in the order they appear
        cx = [('', x.title(fix=True), x.xid, x.key()) for x in abcs]
        # just does Xids for now - add title prefixes later
        breakat = [x.strip() for x in args.contentsx.split(',')] if args.contentsx else []
        # print("Contents breakat =", breakat)
        addindex("Contents", cx, sort=False, breakat=breakat)

    if args.titles or args.titlesx:
        # index all tune titles, not just the first title (unless dropped - start with minus) - in alphabetic order of titles
        tuneindex = [(t[0], t, x.xid, x.key()) for x in abcs if x.index for t in x.titles(drop=True)]
        breakat = [x.strip() for x in args.titlesx.split(',')] if args.titlesx else []
        addindex("Titles", tuneindex, breakat=breakat) 

    rgn = dict((g, n) for n, rg in enumerate(ABClib.ABCsong.rgroups) for g in rg)
    rgname = [', '.join(g) for g in ABClib.ABCsong.rgroups]
    if args.byrhythm or args.byrhythmx: 
        sx = [s for s in abcs if x.index]
        sx.sort(key=lambda s:(rgn[s.rhythmgroup()], s.title()))
        # should fix the breakat below to use command line argument
        breakat = [x.strip() for x in args.byrhythmx.split(',')] if args.byrhythmx else []
        addindex("By rhythm", [(rgname[rgn[x.rhythmgroup()]], x.title(), x.xid, x.key()) for x in sx], sort=False, breakat=breakat)
         
    if args.alphasetindex:
        # create a sorted list of sets
        sx = [s for s in ss.sets if len(s)>1]
        sx.sort(key=lambda s:s[0].title().upper())

        def setfmt1(ts):
            return ts[0].title()[0].upper(), '; '.join("{0} ({1})".format(t.title(fix=True), t.key()) for t in ts), ts[0].xid
        addindex("Sets (alphabetic)", [setfmt1(x) for x in sx], sort=False, nochords=True)
    
    if args.rhythmsetindex:
        # dts = tuple(x[0] for x in ABClib2.ABCsong.rgroups)
        sx = [s for s in ss.sets if len(s)>1]
        sx.sort(key=lambda s:(rgn[s[0].rhythmgroup()], s[0].title()))
        def setfmt2(ts):
            return rgname[rgn[ts[0].rhythmgroup()]], '; '.join(t.title(fix=True) for t in ts), ts[0].xid
        addindex("Sets by rhythm", [setfmt2(xs) for xs in sx], sort=False, nochords=True)


     # Paverty singer notation - for indexing
    if args.pavindex:
        singer = {'bb':'Bob Buckley', 'gc':'Graham Chalker', 'sd':'Simone Dawson', 
                  'br': 'Bryan Rae', 'rk':'Rick Kenyon', 'bp':'Bill Pitt'
                  }
        sditems = [(x.vocalist(), xt, x.xid, x.key()) for x in abcs if x.index for xt in x.titles() if not xt.startswith('-')]
        sditems = [(singer[s] if s in singer else s, t, x, k) for s,t,x,k in sditems if s!='-']
        addindex("Singers", sditems, sort=True)
        

    # add set dance index
    if args.danceindex:
        sditems = [('', z.strip(), x.xid) for x in abcs if x.index for tl in x.taglines('N') if tl.lower().strip().startswith('set dance:') for z in tl.split(':', 1)[-1].split(';')]
        if sditems:
            addindex("Dances", sditems)
    
    # finishing up
    d, fn = os.path.split(args.file)
    bn, ext = os.path.splitext(fn)
    target = args.output if args.output else os.path.join(d, bn+".htm")

    # check for ABC scripts ...
    ssrcs = [z for z in (x.rsplit('/',1)[-1] for x in doc.head.find_all("script") if x.has_attr("src")) if any(z.startswith(fns) for fns in ['abc2svg', 'abcweb', 'tmcore', 'tmweb'])]
    if ssrcs:
        if len(ssrcs)<2:
            print("incomplete abc2svg scripts:", ssrcs)
            exit(1)
        if args.abc2svg or args.txtmus:
            print("uses scripts:", ssrcs)
            print("-1 -2 --abc2svg, --txtmus are not allowed.")
            exit(1)
    
    jsdir = "http://moinejf.free.fr/js" # should be argument - not yet used
    if args.abc2svg:
        jslist = ["http://moinejf.free.fr/js/abc2svg-1.js", 
                  "http://moinejf.free.fr/js/abcweb-1.js"]
        if args.playback:
            jslist.append("http://moinejf.free.fr/js/snd-1.js")
    elif args.txtmus:
        jslist = ["http://moinejf.free.fr/js/tmcore-2.js",
                  "http://moinejf.free.fr/js/tmweb-2.js"]
        if args.playback:
            jslist.append("http://moinejf.free.fr/js/snd-2.js")
    else:
        jslist =[]
    
    if args.grid2:
        jslist.append("/home/bobb/mywin/OneDrive/Documents/GitHub/render-ABC/gchordfix.js")
    
    for js in jslist:
        print(" ... adding <script src={0}>".format(js))
        body.append(doc.new_tag("script", src=js, defer=""))
        body.append("\n")

    print("look for embedding files *********************************************")
    # embed image files before output is done.
    for img in (x for x in doc.body.find_all("img") if 'src' in x.attrs):
        if "src" in img.attrs:
            src = img.attrs['src']
            srcx = src.rsplit('.', 1) # could use os.basename maybe
            itype = srcx[1].lower() # image type (from file name)
            if len(srcx)!=2 or itype not in ["jpg", "png"]:
                print("  ", img, "not embedded!")
                continue
            em, imgdata = getsrc(src, args.embed, mode='rb')
            if em:
                print("  Embed img", src)
                img.attrs['src'] = "data:image/"+itype+";base64,"+base64.standard_b64encode(imgdata).decode()

    # there should be an option to embed <script src="filename" ...> and <link rel="stylesheet" href="filename"> files as well ...

    def embedlink(t):
        # note: t["rel"] returns a list
        return t.has_attr("href") and "stylesheet" in t.attrs.get("rel",[])
    txt = None
    for rtag in (x for x in doc.head.find_all("link") if embedlink(x)):
        em, txt = getsrc(rtag["href"], args.embed)
        if em:
            print("  Embed link ", rtag["href"])
            rtag.name = "style"
            rtag.append("\n"+txt)
            rtag["type"] = "text/css"
            del rtag["rel"]
            del rtag["href"]

    for rtag in (x for x in doc.find_all("script") if x.has_attr("src")):
        efn = rtag["src"].rsplit('/', 1)[-1]
        if efn.startswith('snd-'):
            if os.path.isfile(rtag["src"]):
                print("embedding snd-?.js does not work (without a local /js directory for all the abs2svg stuff.)")
            if args.playback and args.embed:
                print("removing", rtag)
                rtag.remove()
                continue
        # embed external content and remove src attribute
        em, txt = getsrc(rtag["src"], args.embed)
        if em:
            if any(efn.startswith(fn) for fn in ["abc2svg", "tmcore"]):
                txt = txt.replace("MIDI:{},", "") # fix loading of MIDI - doesn't work when embedded
                print("fixing MIDI call when emdedding ...")
            print("  Embed script ", rtag["src"])
            txt = "\n"+txt.replace("'</script>", "'<'+'/script>") # break the string up so HTML loading works
            rtag.append(txt)
            del rtag["src"]
    del txt

    print("Output sent to", target)
    with open(target, "w") as dst:
        print(doc, file=dst)    # doc is BeautifulSoup so that does all the work here.
    print("Done.")
    return

if __name__=="__main__":
    main()
