##################################################################
#
# Makefile for META-II experiments
#
##################################################################

default: meta-ii-object.txt

meta-ii-object.txt: meta-ii-compiler.py meta-ii-grammar.txt
	./meta-ii-compiler.py < meta-ii-grammar.txt > meta-ii-object.txt

test: meta-ii-object.txt
	diff meta-ii-object.txt meta-ii-object.txt.good 

clean:
	rm -f meta-ii-object.txt *~

