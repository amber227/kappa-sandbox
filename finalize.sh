#!/usr/bin/env bash
# Regenerate every derived artefact from results/ and build the PDF.
set -e
cd "$(dirname "$0")"
uv run python kpr/assets.py
uv run python kpr/macros.py
uv run python kpr/figures.py
cd report && tectonic -X compile report.tex
cp report.pdf ../kinetic_proofreading_kappa.pdf
echo "wrote kinetic_proofreading_kappa.pdf"
