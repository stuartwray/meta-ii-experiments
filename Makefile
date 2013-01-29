##################################################################
#
# Makefile for META-II experiments
#
##################################################################

default: new-meta-ii-compiler.py

new-meta-ii-compiler.py: meta-ii-compiler.py meta-ii-grammar.txt
	./meta-ii-compiler.py meta-ii-grammar.txt 

test: new-meta-ii-compiler.py
	diff new-meta-ii-compiler.py  meta-ii-compiler.py 

# Example compiler using the AEXP grammar & runtime

aexp-compiler.py: aexp-grammar.txt meta-ii-compiler.py
	./meta-ii-compiler.py aexp-grammar.txt 

aexp-example-object.py: aexp-compiler.py aexp-example.txt aexp-runtime.py
	./aexp-compiler.py aexp-example.txt

test-aexp: aexp-example-object.py
	./aexp-example-object.py

clean:
	rm -f new-meta-ii-compiler.py aexp-compiler.py aexp-example-object.py *~ 

