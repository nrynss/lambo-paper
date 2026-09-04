.PHONY: all extract figures verify pdf site clean

all: extract figures verify pdf site

extract:
	python3 scripts/extract_telemetry.py

figures:
	python3 scripts/plot_figures.py

verify:
	python3 scripts/verify_constraints.py

pdf:
	cd src && /tmp/tectonic main.tex
	cp src/main.pdf site/public/lambo-paper.pdf

site:
	cd site && npm run build

clean:
	rm -f src/*.aux src/*.bbl src/*.blg src/*.log src/*.out src/*.xdv
