meta-ii-experiments
===================

Building on META-II by Schorre and further developments by Neighbors.

See "Meta-II: A Syntax-Oriented Compiler Writing Language" D. V. Schorre
and "Tutorial: Metacompilers Part 1" by James M. Neighbors.

The default 'make' target generates a new version of the python Meta-II
compiler, but rather than over-writing the current one, it puts the new
program in 'new-meta-ii-compiler.py'. So when you make a change to the
grammar file 'meta-ii-grammar.txt', you'll have to rename the newly 
created compiler by hand before you can use it to compile itself. The
compiler (rather too cleverly) uses its own text as the source for the
runtime of the new compiler, so any changes you make to the old compiler
(e.g. new operations) will just get copied over to the new one.

Running 'make test' just does a diff between the new and the old versions of
the compiler, to demonstrate that we have reached a fixed-point.

Running 'make test-aexp' uses the Meta-II complier to produce a compiler
for a simple language of arithmetic expressions and variable assignments. 
(This is very similar to and example in Neighbors' tutorial.) It then
runs *that* compiler on an example program 'axep-example.txt' to produce a
program 'aexp-example-object.py'. Then finally it runs *that* program and 
shows you can see the output.


