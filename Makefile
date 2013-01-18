##################################################################
#
# Makefile for META-II experiments
#
##################################################################

OUTPUT=output-meta-ii-python-object.py

default: $(OUTPUT)

$(OUTPUT): meta-ii-python-source.txt meta-ii-python-object.py meta2defs.py
	./meta-ii-python-object.py < meta-ii-python-source.txt > $(OUTPUT)
	chmod +x $(OUTPUT)

check: meta-ii-python-object.py $(OUTPUT)
	diff meta-ii-python-object.py $(OUTPUT)

clean:
	rm -f $(OUTPUT) *~

