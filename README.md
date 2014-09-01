# Introduction
The program convert-gprof-to-gexf.py takes the output from the GNU Profiler
(gprof) and transforms it into a GEXF file which can be loaded into data
visualization and exploration programs such as [Gephi](https://gephi.github.io/).

# Usage
Instrument your code for use with gprof (outside the scope of this document).
After executing the program with profiling data and gathering the gmon.out
data, run gprof and redirect the output to a file, e.g., `gprof-report.txt`.
Convert the file using this script:
```
convert-gprof-to-gexf.py gprof-report.txt > gprof-report.gexf
```
