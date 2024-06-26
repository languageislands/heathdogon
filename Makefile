# Makefile
.PHONY: download grouped ungrouped

download:
	git clone https://github.com/languageorphans/heathdogon.git
	cd heathdogon && git checkout new-profile

grouped:
	edictor wordlist --dataset="heathdogon/cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "grouped_segments": "tokens","grouped_plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-grouped"

ungrouped:
	edictor wordlist --dataset="heathdogon/cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "segments": "tokens","plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-ungrouped"
