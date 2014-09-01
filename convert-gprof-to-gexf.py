#!/usr/bin/python

# convert-gprof-to-gexf.py
#   by Mike Melanson (mike -at- multimedia.cx)
# A tool for converting the output of the GNU profiler to GEXF, a file
# format that can be fed into data analysis tools like Gephi.

import sys

def get_id_and_name(s):
    if '[' not in s:
        return (-1, s.strip())
    parts = s.split('[')
    function_id = int(parts[1].rstrip(']'))
    function_name = parts[0].strip()
    return (function_id, function_name)

if len(sys.argv) < 2:
    print "USAGE: convert-gprof-to-gexf.py <gprof report>"
    sys.exit(1)

# open file and search for signature line where call stacks begin
signature = "index % time    self  children    called     name"
f = open(sys.argv[1], 'r')
while True:
    line = f.readline()
    if not line:
        print "no call stacks found"
        sys.exit(1)
    if line.startswith(signature):
        break

# parse the call stacks
focus_id = None
focus_name = None
callers = {}
callees = {}
graph_nodes = {}
graph_edges = {}
while True:
    line = f.readline()
    line = line.rstrip()
    if not line:
        # a blank line indicates the end of the call stack section
        break
    elif line.startswith('-'):
        # end of the call stack; process it
        #print "processing call stack %d: %s" % (function_id, function_name)
        for caller_id in callers:
            node_id = "%d-%d" % (caller_id, focus_id)
            graph_edges[node_id] = [caller_id, focus_id, callers[caller_id]]
        for callee_id in callees:
            node_id = "%d-%d" % (focus_id, callee_id)
            graph_edges[node_id] = [focus_id, callee_id, callees[callee_id]]

        # reset the call stack state variables
        focus_id = None
        focus_name = None
        callers = {}
        callees = {}
    elif line.startswith('['):
        # parse the focus of this call stack
        parts = line[:45].split()
        (focus_id, focus_name) = get_id_and_name(line[45:])
        graph_nodes[focus_id] = focus_name
    else:
        (function_id, function_name) = get_id_and_name(line[45:])
        if function_name == "<spontaneous>":
            continue
        parts = line[:45].split()
        call_count = parts[-1]
        if '/' in call_count:
            (num, den) = call_count.split('/')
            #edge_weight = float(num) / float(den)
            edge_weight = int(num)
        else:
            edge_weight = 1.0

        # if the function_name as not been set, this is a caller;
        # else, it's a callee
        graph_nodes[function_id] = function_name
        if not focus_name:
            callers[function_id] = edge_weight
        else:
            callees[function_id] = edge_weight

# generate the GEXF file
print """<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
    <graph mode="static" defaultedgetype="directed">"""

# nodes
print '        <nodes count="%d">' % (len(graph_nodes))
for function_id in graph_nodes:
    # substitute "<>" with "[]"
    function_name = graph_nodes[function_id].replace('<', '[').replace('>', ']')
    print " " * 12,
    print '<node id="%d" label="%s" />' % (function_id, function_name)
print "        </nodes>"

# edges
print '        <edges count="%d">' % (len(graph_edges))
counter = 0
for edge_id in graph_edges:
    edge = graph_edges[edge_id]
    print " " * 12,
    print '<edge id="%d" source="%d" target="%d" weight="%f" />' % \
        (counter, edge[0], edge[1], edge[2])
    counter += 1
print "        </edges>"

print """    </graph>
</gexf>"""
