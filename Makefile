##################################################################
#
# Makefile for META-II experiments
#
##################################################################

default: new-meta-ii-compiler.py

new-meta-ii-compiler.py: meta-ii-compiler.py meta-ii-grammar.txt
	./meta-ii-compiler.py meta-ii-grammar.txt 
	chmod +x new-meta-ii-compiler.py

test: new-meta-ii-compiler.py
	diff new-meta-ii-compiler.py  meta-ii-compiler.py 

clean:
	rm -f new-meta-ii-compiler.py *~

