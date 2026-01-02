# render-ABC

*Bob Buckley*

Software to render/merge ABC library files with HTML templates.

This is a script for merging the contents of a ABC music notation file with a HTML template to create a HTML music book that can be used at a gig or for "printing" a PDF file or a paper copy.
The main feature is that it adds optional indices of the tunes that are click-able to go to the tunes. 

The HTML output relies on [abc2svg](https://chiselapp.com/user/moinejf/repository/abc2svg/doc/trunk/README.md) software to render the music as the HTML loads into the browser. 

The output HTML can use links, which keeps the HTML file small but relies on having a network connection, or embed Javascript in the file so it can be used without a network connection.

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

The software is written in Python 3.
