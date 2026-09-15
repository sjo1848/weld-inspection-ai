import pytest

from weldvision.data.mendeley import safe_filename


def test_safe_filename_accepts_plain_basename() -> None:
    assert safe_filename("dataset.zip") == "dataset.zip"


@pytest.mark.parametrize(
    "name",
    ["../dataset.zip", "folder/dataset.zip", r"folder\dataset.zip", "..", ""],
)
def test_safe_filename_rejects_paths(name: str) -> None:
    with pytest.raises(ValueError):
        safe_filename(name)
