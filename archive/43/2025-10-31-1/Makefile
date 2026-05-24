# Use ?= to set a default that can be overridden from the command line
# Example: make PAPER_DIR=vol44is1
PAPER_DIR ?= vol43is1

GENERATOR = generate_newspaper.py
BLURB_GENERATOR = generate_json.py
ARTICLES_GENERATOR = generate_articles.py

CONTENT_DIR = $(PAPER_DIR)/content
MAIN_TEX = $(PAPER_DIR)/main.tex
MAIN_PDF = $(PAPER_DIR)/main.pdf
PRINT_PDF = $(PAPER_DIR)/main-print.pdf

# Source files
ARTICLES = $(wildcard $(PAPER_DIR)/articles/*.yaml)
BLURBS = $(wildcard $(PAPER_DIR)/blurb/jsons/*.json)
CONFIG = $(PAPER_DIR)/config.yaml
EVENTS = $(PAPER_DIR)/events.yaml

# Generated files
GENERATED = $(CONTENT_DIR)/toc.tex $(CONTENT_DIR)/events.tex \
			$(CONTENT_DIR)/letter.tex $(CONTENT_DIR)/articles.tex \
			$(CONTENT_DIR)/directory.tex

.PHONY: all generate compile clean help view online print view-print

# Default target - online version
all: online

# Generate LaTeX content from YAML/JSON (online mode - default)
generate: $(GENERATED)

$(GENERATED): $(ARTICLES) $(BLURBS) $(CONFIG) $(EVENTS) $(GENERATOR)
	@echo "Generating articles for $(PAPER_DIR)..."
	@python3 $(ARTICLES_GENERATOR) ./$(PAPER_DIR)
	@echo "Generating blurbs for $(PAPER_DIR)..."
	@python3 $(BLURB_GENERATOR) ./$(PAPER_DIR)
	@echo "Generating LaTeX files for $(PAPER_DIR) (online mode)..."
	@python3 $(GENERATOR) ./$(PAPER_DIR)
	@echo "✓ LaTeX files generated (clickable blue links)"

# Generate LaTeX content for print version
generate-print:
	@echo "Generating articles for $(PAPER_DIR)..."
	@python3 $(ARTICLES_GENERATOR) ./$(PAPER_DIR)
	@echo "Generating blurbs for $(PAPER_DIR)..."
	@python3 $(BLURB_GENERATOR) ./$(PAPER_DIR)
	@echo "Generating LaTeX files for $(PAPER_DIR) (print mode)..."
	@python3 $(GENERATOR) ./$(PAPER_DIR) --print-mode
	@echo "✓ LaTeX files generated (black non-clickable links)"

# Compile online version (blue clickable links)
online: generate
	@echo "Compiling online PDF for $(PAPER_DIR) (pass 1)..."
	@cd $(PAPER_DIR) && pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
	@echo "Compiling online PDF for $(PAPER_DIR) (pass 2)..."
	@cd $(PAPER_DIR) && pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
	@if [ -f $(MAIN_PDF) ]; then \
		echo "✓ Online PDF compiled successfully: $(MAIN_PDF)"; \
		cd $(PAPER_DIR) && rm -f *.aux *.log *.out *.toc; \
		echo "✓ Cleaned up auxiliary files"; \
	else \
		echo "✗ PDF compilation failed for $(PAPER_DIR)"; \
		exit 1; \
	fi

# Compile print version (black non-clickable links)
print: generate-print
	@echo "Compiling print PDF for $(PAPER_DIR) (pass 1)..."
	@cd $(PAPER_DIR) && pdflatex -interaction=nonstopmode -jobname=main-print main.tex > /dev/null 2>&1 || true
	@echo "Compiling print PDF for $(PAPER_DIR) (pass 2)..."
	@cd $(PAPER_DIR) && pdflatex -interaction=nonstopmode -jobname=main-print main.tex > /dev/null 2>&1 || true
	@if [ -f $(PRINT_PDF) ]; then \
		echo "✓ Print PDF compiled successfully: $(PRINT_PDF)"; \
		cd $(PAPER_DIR) && rm -f *.aux *.log *.out *.toc; \
		echo "✓ Cleaned up auxiliary files"; \
	else \
		echo "✗ PDF compilation failed for $(PAPER_DIR)"; \
		exit 1; \
	fi

# Compile both versions
both: online print
	@echo ""
	@echo "✓ Both versions compiled successfully for $(PAPER_DIR)"
	@echo "  - Online version: $(MAIN_PDF)"
	@echo "  - Print version:  $(PRINT_PDF)"

# Legacy compile target (uses online mode)
compile: online

# Clean generated files
clean:
	@echo "Cleaning generated files for $(PAPER_DIR)..."
	@rm -f $(GENERATED)
	@rm -f $(PAPER_DIR)/*.aux $(PAPER_DIR)/*.log $(PAPER_DIR)/*.out $(PAPER_DIR)/*.toc
	@rm -f $(MAIN_PDF) $(PRINT_PDF)
	@echo "✓ Clean complete"

# Clean only auxiliary LaTeX files (keep PDF and generated content)
clean-aux:
	@echo "Cleaning auxiliary files for $(PAPER_DIR)..."
	@rm -f $(PAPER_DIR)/*.aux $(PAPER_DIR)/*.log $(PAPER_DIR)/*.out $(PAPER_DIR)/*.toc
	@echo "✓ Auxiliary files removed"

# View the online PDF
view: $(MAIN_PDF)
	@if command -v open >/dev/null 2>&1; then \
		open $(MAIN_PDF); \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open $(MAIN_PDF); \
	elif command -v start >/dev/null 2>&1; then \
		start $(MAIN_PDF); \
	else \
		echo "Please open $(MAIN_PDF) manually"; \
	fi

# View the print PDF
view-print: $(PRINT_PDF)
	@if command -v open >/dev/null 2>&1; then \
		open $(PRINT_PDF); \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open $(PRINT_PDF); \
	elif command -v start >/dev/null 2>&1; then \
		start $(PRINT_PDF); \
	else \
		echo "Please open $(PRINT_PDF) manually"; \
	fi

# Quick rebuild (clean and build online version)
rebuild: clean online

# Quick rebuild both versions
rebuild-both: clean both

# Help target
help:
	@echo "Banks of the Boneyard - Newspaper Generation System"
	@echo ""
	@echo "Usage: make [target] [PAPER_DIR=issue_directory]"
	@echo ""
	@echo "Current Default Issue: $(PAPER_DIR)"
	@echo ""
	@echo "Main Targets:"
	@echo "  all          - Generate and compile online version (default)"
	@echo "  online       - Generate and compile online version (blue clickable links)"
	@echo "  print        - Generate and compile print version (black non-clickable links)"
	@echo "  both         - Compile both online and print versions"
	@echo ""
	@echo "Generation Targets:"
	@echo "  generate       - Generate LaTeX files for online version"
	@echo "  generate-print - Generate LaTeX files for print version"
	@echo ""
	@echo "Utility Targets:"
	@echo "  view         - Open the online PDF"
	@echo "  view-print   - Open the print PDF"
	@echo "  clean        - Remove all generated files"
	@echo "  clean-aux    - Remove only auxiliary LaTeX files"
	@echo "  rebuild      - Clean and rebuild online version"
	@echo "  rebuild-both - Clean and rebuild both versions"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make               # Compile default issue ($(PAPER_DIR))"
	@echo "  make print         # Compile print version of default issue"
	@echo "  make PAPER_DIR=vol44is1  # Compile online version of 'vol44is1'"
	@echo "  make both PAPER_DIR=vol44is2 # Compile both versions of 'vol44is2'"
	@echo "  make view-print    # Open print PDF of default issue"
	@echo "  make clean PAPER_DIR=vol44is1  # Clean files for 'vol44is1'"
	@echo ""
	@echo "Output files for $(PAPER_DIR):"
	@echo "  Online: $(MAIN_PDF) (blue clickable links)"
	@echo "  Print:  $(PRINT_PDF) (black text links)"