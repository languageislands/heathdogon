.PHONY: all manual_data install bench grouped ungrouped coverage cognates

all: manual_data install bench grouped ungrouped coverage cognates

manual_data:
	python prepare_manual_data.py
install:
	pip install -e .
bench:
	cldfbench lexibank.makecldf --glottolog="C:/Users/Promise Dodzi Kpoglu/glottolog" --concepticon="C:/Users/Promise Dodzi Kpoglu/concepticon-data" --clts="C:/Users/Promise Dodzi Kpoglu/clts" --glottolog-version=v5.0 --concepticon-version=v3.2.0 --clts-version=v2.3.0 heathdogon

grouped:
	edictor wordlist --dataset="cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "grouped_segments": "tokens","grouped_plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-grouped"

ungrouped:
	edictor wordlist --dataset="cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "segments": "tokens","plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-ungrouped"

coverage:
	python coverage.py

cognates:
	python cognates.py



