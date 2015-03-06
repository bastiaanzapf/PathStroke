
Explicit path stroking in python (via pyx)

Vector graphics software usually provides a "path stroking" function, that is, turning a line into a brush stroke. Since PostScript and other environments often support implicit path stroking, the results are not accessible for further processing, like in FontForge. Sometimes one subproblem of this is called "curve offset".

This is a library that implements basic path stroking via the pyx graphics package, which I plan to remove in the long term, so the resulting code could be transformed to another language more easily.

Missing Features are:

* caps 

Open paths are usually thought to end in a "cap" when stroked, this is plainly not implemented yet.

* rigorous treatment of self-intersections

Some cases of self-intersections might break the result

* other output formats

Once pyx is abstracted away, output could be directed to e.g. cairo as well.