# render-ABC

*Bob Buckley*

Software to render/merge ABC library files with HTML templates.

#abcsvg.py

This is a script for merging the contents of a ABC music notation file with a HTML template to create a HTML music book that can be used at a gig or for "printing" a PDF file or a paper copy.
The main feature is that it adds optional indices of the tunes that are click-able to go to the tunes. 

The HTML output relies on *[abc2svg](https://chiselapp.com/user/moinejf/repository/abc2svg/doc/trunk/README.md)* or *txtmus* software to render the music as the HTML loads into the browser. the *abc2svg* version allows dynamic playing of tunes when connected to the internet (it needs to load extra modules dynamically). 

Note: using *abc2svg* means that the book can provide chord charts instead of music notation.

The output HTML (tune or song books) can use links, which keeps the HTML file small but relies on having a network connection, or embed Javascript in the file so it can be used without a network connection.

This software has the notion of tune sets. Currently, sets are separated by %%newpage or %%sep directives (%%newpage after a set, %%sep after a single tune) in the ABC file (this may change - we may choose to use a separate set description file so ABC files are more standard).

The software can add (via command line options):
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

The software is written in Python 3 (about v3.12). This means it can be used on PCs, Macs or Linux/UNIX. You may needs to install some other modules (like bs4 and openpyxl). My python programs use Python's argparse module so you can get simple help using:
     python3 *prog*.py --help

#abcextract.py

The *abcextract.py* program extracts selected ABC tunes from an ABC library ... and create a new ABC library. This is meant to be used to created selected tunebooks from a larger ABC library.

Reads a MS Excel file. The first column is '-' separated Xids for the tunes you want in your tunebook. Outputs a new ABC file with %%newpage and %%sep separators inserted appropriately for use with *abcsvg.py* above.

#getlist.py

Create extract.csv list from an ABC library of the whole library. 

Note: load CSV files into MS Excel as separate data as just loading CSV can convert sets to dates (MS Excel converts set 5-6-7 to date 5-JUN-2007). In Excel use Data>Get Data>From File and choose Text/CSV import option. Do not use the "transform data" import option.

#To do

- maybe, detect some selected *abc2svg* modules and preload them? e.g. the MIDI module and selected sound modules.
- create examples with shell scripts (example templates, abc files (with ABC header)) in the examples folder/directory.
- *abcextract.py* should work from either CSV of XLSX file 
- embed HTML in ABC files - including image insertion - test does %%beginml work?
- consider a button to load snd-?.js dynamically into the HTML
- 'to do' in abcsvg.py
- figure out a good/easy way to let users choose music or *abc2svg* %%grid or %%grid2 charts.
- work out what MIDI playback works with *abc2svg* and *txtmus*
- convert songs from text with lines like "[G]I got the Blues [C]in the morning" to a chart with chords above the words.

