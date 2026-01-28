# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:26:27 2017

@author: bobbuckley

A library of code for ABC files.
The ABC files can be augmented for Paverty
A line that is "%p: v BB" means BB is the vocalist
"""
#import itertools
import re
import sys
            
def abcdict(ssx):
    "convert a list of songs to a header and a dictionary of songs lines"
    # should be like songdict() below

    sdict = dict((s.xid, s.lines) for s in ssx)
    return sdict
    
def songdict(ssx):
    "convert a list of songs to a header and a dictionary of Songs"
    assert ssx, "expects at least one song"       
    hdr, ss = ([], ssx) if ssx[0][0].startswith('X:') else (ssx[0], ssx[1:])

    # should check hdr[0] (if it exists) starts with "%abc" 
    
    badsongs = [n for n, s in enumerate(ss) if not s[0].startswith('X:')]
    
    if badsongs:
        print("badsongs=", badsongs)
        for n in badsongs[:4]:
            print(ss[n-1][:3])
            print(ss[n][:3])
        
    assert all(s[0].startswith('X:') for s in ss), "malformed song - first line is not X:"
    
    sdict = dict((s[0][2:].strip(), ABCsong(s[1:])) for s in ss)
    return hdr, sdict

# retitlefix = re.compile(r'^(.*), (an?|the|l[ae]|en)$', flags=re.IGNORECASE)    
retitlenorm = re.compile(r'^(an?|the|l[ae]|en)\s+', flags=re.IGNORECASE)    # article (A|The) at start of title - normalise (for sorting)
    
def sorttitle(title):
    "transform a title for sorting"
    return retitlenorm.sub('', title.lower()) # remove the article if it is there

def fixtitle(title):
    ps = [p.strip() for p in title.rsplit(',', 1)] # only for a single word following ',' - should be like retitle pattern above
    if len(ps)>1 and len(ps[1].split())==1:
        ps.reverse()
    return ' '.join(ps)

class Song:
    pass

oldplines =[]
class ABCsong(Song):
    """
    class for storing and accessing ABC song/tune notation
    Note: the X: lines was trimmed from the front.
    No blank line at the end.
    Also, set index value for each ABC item - True unless %%index 0 is present
    """
    patnoindex = re.compile(r'^\s*%%\s*index\s+[0NnFf]') # Allow 0, No or False
    def __init__(self, plines, attrs=None):
        global oldplines
        # song/tunes must start with an X: line
        if not plines[0].startswith('X:'):
            print('bad ABC song/tune ...')
            print('plines =', ''.join(x+'\n' for x in plines))
            print()
            if oldplines:
                print("previous ...")
                print(''.join(x+'\n' for x in oldplines))
            sys.exit(1)
            assert False
        # dispose of any initial blank words lines ... they break things
        oldplines = plines
        wpos = 0
        for i, l in enumerate(plines):
            if l.startswith('W:'):
                wpos = i
                wend = wpos
                while wend<len(plines) and plines[wend]=='W:':
                    wend+=1
                break
        lines = [x for x in (plines[:wpos]+plines[wend:] if wpos else plines)]
        self.index = not any(ABCsong.patnoindex.match(x) for x in plines)
        self.xid = lines[0][2:].strip()
        self.lines = lines[1:] if lines[0].startswith('X:') else lines 
        self.attr = attrs
        return
        
    def clean(self):
        self.lines = [l for l in self.lines if not l.startswith('%%newpage')]
        return self
    
    def id(self):
        return "x"+self.xid
        
    def taglines(self, tag):
        "all the lines that start with tag"
        tagx = tag.strip()+':'
        return (l.removeprefix(tagx).strip() for l in self.lines if l.startswith(tagx))
    
    def tagline(self, tag):
        "the first lines that start with tag - otherwise None"
        for l in self.taglines(tag):   
            return l
        return None

    
    def titles(self, all=False, fix=False, drop=False):
        "title lines - lines that start with T: up to first K: line (if not all)"
        for line in self.lines:
            if line.startswith('T:'):
                t = line[2:].strip()
                if drop and t.startswith('-'): # ignore titles that start with '-'
                    continue
                yield fixtitle(t) if fix else t.strip()
                # yield retitlefix.sub(r'\2 \1', t) if fix else t
            if not all and line.startswith('K:'):
                break
        return
    
    def alltitles(self, fix=False, drop=False):
        "title lines - lines that start with T: up to first K: line"
        return self.titles(all=True, fix=fix, drop=drop)
    
    def title(self, fix=False):
        "main title of song/tune - the first title line"
        for t in self.titles(fix=fix):
            return t
        return None
        
    def sorttitles(self, all=False, fix=False, drop=False):
        "titles used for sorting - all lowercase and remove leading article"
        return map(sorttitle, self.titles(all=all, fix=fix, drop=drop))
        
    def words(self):
        "words or lyrics - lines starting with W:"
        # maybe should include w: as well
        return self.taglines('W')
    
    def key(self):
        "get the first key - first K: tag"
        trim = (('maj', ''), ('major', ''), ('minor', 'm'), ('min', 'm'), ('dorian', 'dor'))
        for ll in self.taglines('K'):
            if not ll:
                return ll
            l = ll.split()[0] # strip off any extra stuff like clef= ...
            for x, z in trim:
                if l.endswith(x):
                    l = l[:-len(x)]+z
            return l
        return None
    
    def mbody(self):
        "True if anything follows K: ... this is more than a place holder"
        kno = next(i for i, lx in enumerate(self.lines) if lx.startswith('K:'))
        return kno+1<len(self.lines)
    
    def linesstr(self):
        "the lines of the song - as a string"
        return ''.join(map(lambda x:x+"\n", self.lines))
        
    def vocalist(self):
        "%p: v BB style lines in Paverty ABC files"
        for l in self.taglines('%p'):
            if l.startswith('v '):
                return l[2:].lstrip().lower()
        return '-'
    
    # first is list is key name for group
    rgroups = [['reel'], ['polka'], ['hornpipe', 'schottische', 'barndance'], ['march'], 
               ['jig', 'single jig', 'double jig'], ['slip jig'], ['slide'],               
               ['waltz'], ['varsovienna', 'varsoviana'],
               ['maggot', 'minuet', 'triple hornpipe'],
               ]
    
    rd = dict((r, rz[0]) for rz in rgroups for r in rz) # dictionary to translate rhythm to rhythm group
    
    # used to guess rhythm group from M: line if no R: tagline
    mtrans = dict(x for x in [('C|', 'polka'), ('2/4', 'polka'), 
                  ('C', 'reel'), ('4/4', 'reel'), ('2/2', 'hornpipe'),
                  ('6/8', 'jig'), ('9/8', 'slip jig'),
                  ('12/8', 'slide'),
                  ('3/2', 'maggot'),
                  ('3/4', 'waltz')]
                  )
    
    def rhythmgroup(self):
        "define a rhythm group for each song - derived from R: or M: tag"
        rs = self.tagline('R')
        if rs:
            rs = re.sub(r'\s*\d+[ -]bars*\s*', '', rs)   # ignore bar count
        else:
            mx = self.tagline('M')
            assert mx, "song {xid} missing both R: and M: lines".format(xid=self.xid)
            assert mx in ABCsong.mtrans, "song {xid} with no R: and unrecognised M: field {mx}".format(xid=self.xid, mx=mx)
            rs = ABCsong.mtrans[mx]
        rs = rs.lower()
        assert rs in ABCsong.rd, "song {xid} has unrecognised rhythm group {rs}".format(xid=self.xid, rs=rs)

        return ABCsong.rd[rs]

class Songsets:

    def __init__(self, fn, midi=True):
        """
        Read an ABC file whose name is fn
        
        Split file into songs/tunesets. These are separated by "\n%%newpage\n" or %%sep
        File is split into self.hdr and self.sets

        It attempts to manage %%begintext to %%endtext that may contain blank lines.
        The ABC file may contain isolated X: lines (as placeholders for new tunes)
        """
        
        with open(fn, 'rt') as src:
            orig = src.read()+'\n' # extra newline fixes final %%newpage
            if not midi:
                orig = re.sub("\n%%MIDI.*\n", "\n", orig) # remove all MIDI lines - not able to play
            orig = re.sub(r'[ \t]+\n', '\n', orig) # remove trailing space in all lines
            txtpat = re.compile(r'%%begintext(([^%]|%(?!%end))*)', flags=re.MULTILINE)
            txtblks = txtpat.findall(orig)                  # find and remember all %%(begin|end)text blocks
            lines = txtpat.subn('%%begintextx', orig)[0]    # replace all text blocks
            subpat = re.compile(r'%%begintextx')
            def songfix(s):
                "put text-blocks back into songs - must be called in order"
                while(subpat.match(s)):
                    s=subpat.sub(txtblks.pop(0)[0], s)
                return s
            setpat = re.compile(r'\n%%\s*(newpage|sep)\s*\n', flags=re.IGNORECASE|re.UNICODE|re.MULTILINE)
            settmp = setpat.split(lines)[0::2]
            inp = [z for z in map(lambda x: x.strip(), settmp) if z]

        if inp and inp[0].startswith("%abc"): # deal with ABC header if there is one
            hdr, inp[0] = inp[0].split("\n\n", 1)
            self.hdr = hdr.splitlines()
        else:
            self.hdr = "%abc-2.1" # an assumption!
        sss = ([songfix(x).strip().splitlines() for x in xs.strip().split('\n\n')] for xs in inp if xs)
        # fails with multiple blank lines between songs - should use groupby()
        # drop empty X: songs - they are fillers for later use
        self.sets = [[ABCsong(x) for x in ss if len(x)>1] for ss in sss if len(ss)] # drop empty sets and tunes
        
        return
    
    def abcs(self):
        "flatten the sets to a list of abcs"
        return [s for ss in self.sets for s in ss]
