##################################################################
#
# Makefile for META-II experiments
#
##################################################################

TMPne=./tmp-neighbors-meta-ii-compiler.py
TMPS=$(TMPne)

OUTPUTne=output-neighbors-meta-ii-reordered-object.txt
OUTPUTpy=output-meta-ii-python-object.py
OUTPUTS=$(OUTPUTne)

default: $(OUTPUTS)

$(OUTPUTne): neversion
neversion: neighbors-meta-ii-reordered-source.txt \
		   neighbors-meta-ii-reordered-object.txt\
           neighbors-meta-ii-runtime-header.py \
           neighbors-meta-ii-runtime-trailer.py
	cat neighbors-meta-ii-runtime-header.py > $(TMPne)
#	echo '"""' >> $(TMPne)
#	cat neighbors-meta-ii-reordered-object.txt >> $(TMPne)
#	echo '"""' >> $(TMPne)
#	cat neighbors-meta-ii-runtime-trailer.py >> $(TMPne)
	chmod +x  $(TMPne)
	$(TMPne) < neighbors-meta-ii-reordered-source.txt > $(OUTPUTne)

netest: neighbors-meta-ii-reordered-object.txt $(OUTPUTne)
	diff neighbors-meta-ii-reordered-object.txt $(OUTPUTne)

clean:
	rm -f $(OUTPUTS)  $(TMPS) *~

