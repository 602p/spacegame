from pycallgraph import PyCallGraph
from pycallgraph.output import GephiOutput

with PyCallGraph(output=GephiOutput()):
    execfile('test_state.py')