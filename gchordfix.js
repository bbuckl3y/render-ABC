gchordFix = function (e) {
    // the %%gchord2 1 version leaves some extra junk lying around - this removes it
    var f6 = document.querySelectorAll("svg g text.f6")
    // console.log(f6.length+" triple marks to remove.")
    for (var i=f6.length; i--; ) f6[i].remove()
    var sgp = document.querySelectorAll("svg g path"), cnt=0
    for (var i=sgp.length; i--; ) if (!sgp[i].hasAttribute("class")) { cnt++; sgp[i].remove() }
    // console.log(cnt+" slurs removed from chord charts.")
    // console.log("did gchordFix()")
}
