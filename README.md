# render-ABC

*Bob Buckley*

Software to render/merge ABC library files with HTML templates.

This is a script for merging the contents of a ABC music notation file with a HTML template to create a HTML music book that can be used at a gig or for "printing" a PDF file or a paper copy.
The main feature is that it adds optional indices of the tunes that are click-able to go to the tunes. 

The HTML output relies on *[abc2svg](https://chiselapp.com/user/moinejf/repository/abc2svg/doc/trunk/README.md)* or *txtmus* software to render the music as the HTML loads into the browser. the *abc2svg* version allows dynamic playing of tunes when connected to the internet (it needs to load extra modules dynamically). 

The output HTML (tune or song books) can use links, which keeps the HTML file small but relies on having a network connection, or embed Javascript in the file so it can be used without a network connection.

The software can optionally add:
- Contents list
- title index
- tunes by rhythm type
- tune set (alphbetical by first tune name)
- tune set by rhythm type

This software was developed to maintain tune and song books for
- the [Canberra English session](https://www.facebook.com/canberra.english.session/)
- [Paverty Bush Band](http://paverty.com.au)
- [Blighty's Revenge](https://www.facebook.com/blightys.revenge/) - spin off band from the Canberra English session
- English sessions at the (Australian) [National Folk Festival](https://www.folkfestival.org.au/)

Information about ABC notation and *abc2svg* is available at:
- the [ABC standards v2.1 site](http://abcnotation.com/wiki/abc:standard:v2.1) (or the [v2.2 page](http://abcnotation.com/wiki/abc:standard:v2.2))
- abc rendering - see [txtmus / abc2svg / abcm2ps documentation](http://moinejf.free.fr/abcm2ps-doc/index.html)

The software is written in Python 3 (about v3.12). This means it can be used on PCs, Macs or Linux/UNIX. My python programs use Python's argparse module so you can get simple help using:
     python3 *prog*.py --help

#abcextract

The abcextract.py program extracts selected ABC tunes from an ABC library ... and create a new ABC library. This is meant to be used to created selected tunebooks from a larger ABC library.

Create a MS Excel file. The first column is '-' separated Xids for the tunes you want in your tunebook.