from vladiate import Vlad
from vladiate.inputs import LocalFile
from vladiate.validators import RegexValidator, SetValidator, UniqueValidator


class Validator(Vlad):
    source = LocalFile("repos.csv")
    validators = {
        "contact": [
            RegexValidator(r"[\w\-' ]+ <[\w\-.]+@[\w\-.]+>", full=True, empty_ok=True)
        ],
        "doi": [RegexValidator(r"[\w\-./]+", full=True, empty_ok=True)],
        "funders": [RegexValidator(r"(\d+;?)+", full=True, empty_ok=True)],
        "homepage_url": [RegexValidator(r"https?://.+", full=True, empty_ok=True)],
        "licence": [SetValidator(["MIT", "GPL-2.0", "Artistic-2.0", "BSD-3-Clause"], empty_ok=True)],
        "organisations": [SetValidator(["grid.457348.9"], empty_ok=True)],
        "rsotm": [RegexValidator(r"\d{4}-\d{2}", full=True, empty_ok=True)],
        "url": [UniqueValidator()],
    }
