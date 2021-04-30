def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    assert len(list(cldf_dataset["FormTable"])) == 54073
    assert any(f["Form"] == "kidā́re" for f in cldf_dataset["FormTable"])
    assert any(f["Form"] == "yáhāre" for f in cldf_dataset["FormTable"])


def test_languages(cldf_dataset, cldf_logger):
    assert len(list(cldf_dataset["LanguageTable"])) == 159


def test_parameters(cldf_dataset, cldf_logger):
    assert len(list(cldf_dataset["ParameterTable"])) == 335


def test_sources(cldf_dataset, cldf_logger):
    assert len(cldf_dataset.sources) == 1
