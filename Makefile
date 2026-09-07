.PHONY: all extract figures verify test pdf site tectonic clean

# Kept in lockstep with .github/workflows/deploy.yml. If you bump the version
# here, bump it there too, or local and CI builds stop being the same build.
TECTONIC ?= tectonic
TECTONIC_VERSION := 0.17.0
TECTONIC_SHA256 := 8533d07f9ccbd7a65824b9e0459041bca34af1eb33daba48f59215593753a3b7
TECTONIC_URL := https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40$(TECTONIC_VERSION)/tectonic-$(TECTONIC_VERSION)-x86_64-unknown-linux-musl.tar.gz
TECTONIC_INSTALL_DIR ?= $(HOME)/.local/bin

all: figures verify pdf site

extract:
	python3 scripts/extract_telemetry.py

figures:
	python3 scripts/plot_figures.py

verify:
	python3 scripts/verify_constraints.py

test:
	python3 -m unittest discover -s tests -p 'test_compare_memory.py'

pdf:
	@command -v $(TECTONIC) >/dev/null 2>&1 || { \
		echo "error: '$(TECTONIC)' not found on PATH."; \
		echo "  Run 'make tectonic' to install the pinned $(TECTONIC_VERSION) build to $(TECTONIC_INSTALL_DIR),"; \
		echo "  or point at an existing one with 'make pdf TECTONIC=/path/to/tectonic'."; \
		exit 1; }
	cd src && $(TECTONIC) main.tex
	cp src/main.pdf site/public/lambo-paper.pdf

# Same pinned artifact and checksum as CI, installed somewhere that survives a
# reboot. Never install the compiler into /tmp.
tectonic:
	@set -eu; \
	mkdir -p "$(TECTONIC_INSTALL_DIR)"; \
	tmpdir="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmpdir"' EXIT INT TERM; \
	echo "Downloading tectonic $(TECTONIC_VERSION) ..."; \
	curl -fsSL -o "$$tmpdir/tectonic.tar.gz" "$(TECTONIC_URL)"; \
	echo "$(TECTONIC_SHA256)  $$tmpdir/tectonic.tar.gz" | sha256sum -c -; \
	tar -xzf "$$tmpdir/tectonic.tar.gz" -C "$$tmpdir"; \
	install -Dm755 "$$tmpdir/tectonic" "$(TECTONIC_INSTALL_DIR)/tectonic"; \
	"$(TECTONIC_INSTALL_DIR)/tectonic" -V; \
	echo "Installed to $(TECTONIC_INSTALL_DIR)/tectonic"

site:
	cd site && npm run build

clean:
	rm -f src/*.aux src/*.bbl src/*.blg src/*.log src/*.out src/*.xdv
