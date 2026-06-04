"""Tests for recipe validation and the scaffold/validate CLI."""

from xmldiffreport.core import load_recipe, validate_recipe
from xmldiffreport.scaffold import PLACEHOLDER, _prompt_text, main


def test_builtin_recipes_are_valid():
    for name in ("controlm", "maven-pom", "junit", "sitemap", "generic"):
        assert validate_recipe(load_recipe(name)) == []


def test_validate_catches_problems():
    bad = {"defaults": {"unite": "X"}, "elements": {"JOB": {"key": ["JOBNAME"]}}}
    problems = validate_recipe(bad)
    assert any("unite" in p for p in problems)  # unknown defaults key
    assert any("JOB" in p and "key token" in p for p in problems)  # missing "@"


def test_prompt_loads_and_has_placeholder():
    p = _prompt_text()
    assert "key mini-language" in p.lower()
    assert PLACEHOLDER in p


def test_scaffold_embeds_xml(tmp_path, capsys):
    xml = tmp_path / "s.xml"
    xml.write_text("<root><item id='1'/></root>", encoding="utf-8")
    assert main(["scaffold", str(xml)]) == 0
    out = capsys.readouterr().out
    assert "<item id='1'/>" in out
    assert PLACEHOLDER not in out  # placeholder was replaced by the XML


def test_scaffold_without_file_keeps_placeholder(capsys):
    assert main(["scaffold"]) == 0
    assert PLACEHOLDER in capsys.readouterr().out


def test_list_builtin_recipes(capsys):
    assert main(["list"]) == 0
    out = capsys.readouterr().out.split()
    assert {"controlm", "maven-pom", "junit", "sitemap", "generic"} <= set(out)


def test_schema_cli(capsys):
    assert main(["schema"]) == 0
    assert '"title": "xmldiffreport recipe"' in capsys.readouterr().out
    assert main(["schema", "--path"]) == 0
    assert capsys.readouterr().out.strip().endswith("recipe.schema.json")


def test_validate_cli(tmp_path, capsys):
    good = tmp_path / "good.toml"
    good.write_text('name = "x"\n[elements.A]\nkey = ["@id"]\n', encoding="utf-8")
    assert main(["validate", str(good)]) == 0

    bad = tmp_path / "bad.toml"
    bad.write_text('[elements.A]\nkey = ["id"]\n', encoding="utf-8")
    assert main(["validate", str(bad)]) == 1


def test_show_cli(capsys, tmp_path):
    # A built-in name prints its TOML, header comment and all.
    assert main(["show", "controlm"]) == 0
    out = capsys.readouterr().out
    assert 'name = "controlm"' in out
    assert "SMART_FOLDER" in out

    # A path to a .toml is printed verbatim.
    mine = tmp_path / "mine.toml"
    mine.write_text('name = "mine"\n[elements.A]\nkey = ["@id"]\n', encoding="utf-8")
    assert main(["show", str(mine)]) == 0
    assert 'name = "mine"' in capsys.readouterr().out

    # An unknown name errors (non-zero) and hints at what is available.
    assert main(["show", "does-not-exist"]) == 2
    assert "recipe not found" in capsys.readouterr().err
