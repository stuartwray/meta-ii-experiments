##################################################################
#
# Makefile for META-II experiments
#
##################################################################

TMPne=./tmp-neighbors-meta-ii-compiler.py
TMPS=$(TMPne)

OUTPUTne=output-neighbors-meta-ii-reordered-object.txt
OUTPUTpy=output-meta-ii-python-object.py
OUTPUTS=$(OUTPUTpy) $(OUTPUTne)

default: $(OUTPUTS)

$(OUTPUTne): neversion
neversion: neighbors-meta-ii-reordered-source.txt \
		   neighbors-meta-ii-reordered-object.txt\
           neighbors-meta-ii-runtime-header.py \
           neighbors-meta-ii-runtime-trailer.py \
	cp neighbors-meta-ii-runtime-header.py > $(TMPne)
	echo '"""' >> $(TMPne)
	cat neighbors-meta-ii-reordered-object.txt >> $(TMPne)
	echo '"""' >> $(TMPne)
	cat neighbors-meta-ii-runtime-trailer.py >> $(TMPne)
	chmod +x  $(TMPne)
	$(TMPne) < neighbors-meta-ii-reordered-source.txt > $(OUTPUTne)

netest: neighbors-meta-ii-reordered-object.txt $(OUTPUTne)
	diff neighbors-meta-ii-reordered-source.txt $(OUTPUTne)

$(OUTPUTpy): pyversion
pyversion: meta-ii-python-source.txt meta-ii-python-object.py meta2defs.py
	./meta-ii-python-object.py < meta-ii-python-source.txt > $(OUTPUTpy)
	chmod +x $(OUTPUTpy)

pytest: meta-ii-python-object.py $(OUTPUTpy)
	diff meta-ii-python-object.py $(OUTPUTpy)

clean:
	rm -f $(OUTPUT) $(TMPS) *~

