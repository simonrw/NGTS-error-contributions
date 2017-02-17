PDFS := ~/Desktop/theory_noise_10s_3600s-total_osborn.pdf ~/Desktop/theory_noise_10s_3600s-total_young.pdf

all: $(PDFS)

~/Desktop/theory_noise_10s_3600s-total_osborn.pdf: /tmp/dark_osborn.csv /tmp/bright_osborn.csv ./plot_rendered_theory_noise.py
	python ./plot_rendered_theory_noise.py --dark /tmp/dark_osborn.csv --bright /tmp/bright_osborn.csv --output $@

~/Desktop/theory_noise_10s_3600s-total_young.pdf: /tmp/dark_young.csv /tmp/bright_young.csv ./plot_rendered_theory_noise.py
	python ./plot_rendered_theory_noise.py --dark /tmp/dark_young.csv --bright /tmp/bright_young.csv --output $@

/tmp/dark_osborn.csv: TheoryNoiseWithBinning.py
	python ./TheoryNoiseWithBinning.py -t 3600 --scintillation-method osborn -e 10 -s dark -ST -o /tmp/out.$$$$.png -r $@

/tmp/bright_osborn.csv: TheoryNoiseWithBinning.py
	python ./TheoryNoiseWithBinning.py -t 3600 --scintillation-method osborn -e 10 -s bright -ST -o /tmp/out.$$$$.png -r $@

/tmp/dark_young.csv: TheoryNoiseWithBinning.py
	python ./TheoryNoiseWithBinning.py -t 3600 --scintillation-method young -e 10 -s dark -ST -o /tmp/out.$$$$.png -r $@

/tmp/bright_young.csv: TheoryNoiseWithBinning.py
	python ./TheoryNoiseWithBinning.py -t 3600 --scintillation-method young -e 10 -s bright -ST -o /tmp/out.$$$$.png -r $@

clean:
	rm -f ~/Desktop/*.pdf 2>/dev/null

clobber:
	$(MAKE) clean
	rm -f /tmp/{dark,bright}_{young,osborn}.csv 2>/dev/null

view:
	open $(PDFS)

.PHONY: clean clobber view
