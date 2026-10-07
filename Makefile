.PHONY: env check fetch-inputs screen compile-screen

env:
	conda env create -f environment.yml

check:
	python -m compileall -q src analysis
	python -c "from pathlib import Path; import yaml; [yaml.safe_load(p.read_text()) for p in [Path('environment.yml'), *Path('configs').glob('*.yaml'), *Path('.github/workflows').glob('*.yml')]]"

fetch-inputs:
	python src/data/fetch_karnali_inputs.py

screen:
	PYTHONPATH=src python analysis/hazard_exposure/run_karnali_79.py $(SETTLEMENT_IDS)

compile-screen:
	python analysis/hazard_exposure/compile_karnali_79.py
