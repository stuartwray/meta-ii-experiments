##################################################################
#
# Makefile for META-II experiments
#
##################################################################

OUTPUT=output.py

default: tmp.txt

tmp.txt: meta-ii-my-version.txt trial.py meta2defs.py
	./trial.py < meta-ii-my-version.txt > $(OUTPUT)
	chmod +x $(OUTPUT)

check: tmp.txt trial.py
	diff tmp.txt trial.py

clean:
	rm -f $(OUTPUT) *~

