"""N-way, recursive, recipe-driven structural diff engine.

Model
-----
- Every XML element is a node with attributes, optional text, and children.
- A recipe declares, per tag: the ``key`` (natural identity), whether the tag is
  ``inline`` (its children become pseudo-attributes instead of opening a new
  level), and which attributes to ignore.
- N sources are compared at once, matching nodes by identity (order-independent).
  Only differences end up in the result.

Performance
-----------
Each file is parsed once into an in-memory tree (ElementTree); the diff cost is
roughly linear in the number of nodes. For typical Control-M exports (a few MB)
it is instant, and it is fine up to the order of tens of MB. It is not designed
for gigabyte-scale files — we deliberately favour simple, maintainable code over
incremental/streaming parsing.
"""

from __future__ import annotations

import tomllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path

ABSENT = "−"


# ---------------------------------------------------------------------------
# recipe
# ---------------------------------------------------------------------------
def load_recipe(name_or_path: str) -> dict:
    """Load a built-in TOML recipe (by name) or one from a path."""
    p = Path(name_or_path)
    if p.is_file():
        data = tomllib.loads(p.read_text(encoding="utf-8"))
    else:
        res = files("xmldiffreport").joinpath("recipes", f"{name_or_path}.toml")
        if not res.is_file():
            raise FileNotFoundError(f"recipe not found: {name_or_path}")
        data = tomllib.loads(res.read_text(encoding="utf-8"))
    data.setdefault("defaults", {})
    data["defaults"].setdefault("ignore_attrs", [])
    data.setdefault("elements", {})
    return data


def _cfg(recipe: dict, tag: str) -> dict:
    return recipe["elements"].get(tag, {})


def is_inline(recipe: dict, tag: str) -> bool:
    return bool(_cfg(recipe, tag).get("inline"))


def key_attrs(recipe: dict, tag: str) -> set[str]:
    spec = _cfg(recipe, tag).get("key")
    if not spec:
        return {"NAME"}
    return {t[1:] for t in spec if isinstance(t, str) and t.startswith("@")}


# ---------------------------------------------------------------------------
# parsing (with namespace normalization)
# ---------------------------------------------------------------------------
def parse_xml(path, strip_ns: bool = True) -> ET.Element:
    root = ET.parse(path).getroot()
    if strip_ns:
        for el in root.iter():
            if isinstance(el.tag, str) and "}" in el.tag:
                el.tag = el.tag.split("}", 1)[1]
            for k in list(el.attrib):
                if "}" in k:
                    el.set(k.split("}", 1)[1], el.attrib.pop(k))
    return root


# ---------------------------------------------------------------------------
# element identity and comparable values
# ---------------------------------------------------------------------------
def identity(recipe: dict, tag: str, el: ET.Element) -> str:
    """Identity key of an element among its siblings, per the recipe (with fallbacks)."""
    spec = _cfg(recipe, tag).get("key")
    if not spec:
        name = el.get("NAME")
        if name is not None:
            return name
        text = (el.text or "").strip()
        if text:
            return text
        return "|".join(f"{k}={v}" for k, v in sorted(el.attrib.items())) or tag

    parts: list[str] = []
    for tok in spec:
        if tok == "*kinds":  # summary of children (e.g. ON → actions)
            kinds = [c.get("ACTION", "") if c.tag == "DOACTION" else c.tag for c in el]
            parts.append("+".join(k for k in kinds if k))
        elif tok == "*tag":  # singleton: identity is the tag itself
            parts.append(el.tag)
        elif tok == "#text":
            parts.append((el.text or "").strip())
        elif tok.startswith("@"):
            parts.append(el.get(tok[1:], "") or "")
        elif tok.startswith("child:"):
            rest = tok[6:]
            if "@" in rest:
                ct, at = rest.split("@", 1)
                c = el.find(ct)
                parts.append(c.get(at, "") if c is not None else "")
            elif rest.endswith("#text"):
                c = el.find(rest[:-5])
                parts.append((c.text or "").strip() if c is not None else "")
    return "|".join(p for p in parts if p) or tag


def is_container(recipe: dict, el: ET.Element) -> bool:
    return len(list(el)) > 0 and not is_inline(recipe, el.tag)


def value_attrs(recipe: dict, tag: str, el: ET.Element, ignore: set[str]) -> dict[str, str]:
    """Comparable attributes of a leaf/inline node (excludes identity and volatile)."""
    skip = ignore | key_attrs(recipe, tag)
    out = {k: v for k, v in el.attrib.items() if k not in skip}
    if is_inline(recipe, tag):
        for c in el:
            k = f"{c.tag}:{c.get('ACTION')}" if c.tag == "DOACTION" else c.tag
            out[k] = "; ".join(f"{a}={b}" for a, b in c.attrib.items()) or "(present)"
    elif len(list(el)) == 0:
        text = (el.text or "").strip()
        if text:
            out["#text"] = text
    return out


# ---------------------------------------------------------------------------
# result
# ---------------------------------------------------------------------------
@dataclass
class NodeDiff:
    tag: str
    ident: str
    sources: list[str]
    rows: list = field(default_factory=list)  # (label, {src: value})
    presence_children: list = field(default_factory=list)  # (tag, ident, {src: bool})
    child_diffs: list = field(default_factory=list)  # NodeDiff
    identical: int = 0

    def changed(self) -> bool:
        return bool(self.rows or self.presence_children or self.child_diffs)


def _differ(vals: dict) -> bool:
    return len(set(vals.values())) > 1


def _attr_rows(maps: dict, srcs: list[str]) -> list:
    rows = []
    keys = set().union(*maps.values()) if maps else set()
    for a in sorted(keys):
        vals = {s: maps[s].get(a, ABSENT) for s in srcs}
        if _differ(vals):
            label = "(text)" if a == "#text" else f"`{a}`"
            rows.append((label, vals))
    return rows


def _leaf_children(recipe: dict, el: ET.Element, ignore: set[str]) -> dict:
    out: dict = {}
    for c in el:
        if is_container(recipe, c):
            continue
        ident = identity(recipe, c.tag, c)
        key = (c.tag, ident)
        n = 2
        while key in out:
            key = (c.tag, f"{ident}#{n}")
            n += 1
        out[key] = value_attrs(recipe, c.tag, c, ignore)
    return out


def _leaf_rows(maps: dict, srcs: list[str]) -> list:
    rows = []
    keys = set().union(*maps.values()) if maps else set()
    for tag, ident in sorted(keys):
        base = f"`{tag}`" if ident == tag else f"{tag} `{ident}`"  # singleton vs keyed
        present = {s: (tag, ident) in maps[s] for s in srcs}
        if not all(present.values()):
            rows.append((base, {s: ("present" if present[s] else ABSENT) for s in srcs}))
            continue
        akeys = set().union(*(maps[s][(tag, ident)] for s in srcs))
        for a in sorted(akeys):
            vals = {s: maps[s][(tag, ident)].get(a, ABSENT) for s in srcs}
            if _differ(vals):
                suffix = "(text)" if a == "#text" else f"`{a}`"
                rows.append((f"{base} · {suffix}", vals))
    return rows


def diff_group(recipe: dict, tag: str, ident: str, nodes: dict, ignore: set[str]) -> NodeDiff:
    """N-way diff of a group of nodes (one per source) sharing the same identity."""
    srcs = list(nodes)
    nd = NodeDiff(tag=tag, ident=ident, sources=srcs)

    # own attributes / text
    own = {}
    for s in srcs:
        el = nodes[s]
        own[s] = {k: v for k, v in el.attrib.items() if k not in (ignore | key_attrs(recipe, tag))}
        if len(list(el)) == 0:
            text = (el.text or "").strip()
            if text:
                own[s]["#text"] = text
    nd.rows = _attr_rows(own, srcs)

    # leaf / inline children → rows
    nd.rows += _leaf_rows({s: _leaf_children(recipe, nodes[s], ignore) for s in srcs}, srcs)

    # container children → recurse
    groups: dict = {}
    for s in srcs:
        for c in nodes[s]:
            if not is_container(recipe, c):
                continue
            k = (c.tag, identity(recipe, c.tag, c))
            groups.setdefault(k, {})[s] = c
    for ctag, cid in sorted(groups):
        occ = groups[(ctag, cid)]
        if len(occ) < len(srcs):
            nd.presence_children.append((ctag, cid, {s: (s in occ) for s in srcs}))
            continue
        child = diff_group(recipe, ctag, cid, occ, ignore)
        if child.changed():
            nd.child_diffs.append(child)
        else:
            nd.identical += 1
    return nd


# ---------------------------------------------------------------------------
# N-way orchestration
# ---------------------------------------------------------------------------
def diff_sources(recipe: dict, sources: list) -> list:
    """Diff N sources.

    ``sources`` is a list of ``(env, label, root_element)``. Returns one result
    per unit that has differences across two or more sources.
    """
    ignore = set(recipe["defaults"]["ignore_attrs"])
    unit_tag = recipe["defaults"].get("unit")
    applied = recipe.get("applied_env")

    index: dict = {}
    for env, label, root in sources:
        units = root.iter(unit_tag) if unit_tag else list(root)
        for el in units:
            if unit_tag and el.tag != unit_tag:
                continue
            key = (el.tag, identity(recipe, el.tag, el))
            index.setdefault(key, {})[label] = (env, el)

    results = []
    for (tag, ident), occ in sorted(index.items()):
        if len(occ) < 2:
            continue
        labels = sorted(occ, key=lambda lbl: (occ[lbl][0] == applied, occ[lbl][0], lbl))
        nodes = {lbl: occ[lbl][1] for lbl in labels}
        nd = diff_group(recipe, tag, ident, nodes, ignore)
        if not nd.changed():
            continue
        if applied is None:
            cls, conflict = "DIFF", True
        else:
            nonapplied = [lbl for lbl in labels if occ[lbl][0] != applied]
            conflict = len(nonapplied) >= 2
            cls = "CONFLICT" if conflict else "INFO"
        results.append({"node": nd, "cls": cls, "conflict": conflict})
    return results


# ---------------------------------------------------------------------------
# recipe validation (dependency-free; mirrors recipes/recipe.schema.json)
# ---------------------------------------------------------------------------
_DEFAULT_KEYS = {"unit", "unordered", "ignore_attrs"}


def _valid_key_token(tok: object) -> bool:
    if not isinstance(tok, str) or not tok:
        return False
    if tok in ("#text", "*tag", "*kinds"):
        return True
    if tok.startswith("@") and len(tok) > 1:
        return True
    if tok.startswith("child:"):
        rest = tok[6:]
        return ("@" in rest and not rest.endswith("@")) or rest.endswith("#text")
    return False


def validate_recipe(data: dict) -> list[str]:
    """Validate a parsed recipe dict; return a list of problems (empty = valid)."""
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["recipe must be a TOML table"]

    for k in data:
        if k not in ("name", "applied_env", "defaults", "elements"):
            problems.append(f"unknown top-level key: {k!r}")
    if "name" in data and not isinstance(data["name"], str):
        problems.append("`name` must be a string")
    if "applied_env" in data and not isinstance(data["applied_env"], str):
        problems.append("`applied_env` must be a string")

    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        problems.append("`defaults` must be a table")
    else:
        for k in defaults:
            if k not in _DEFAULT_KEYS:
                problems.append(f"unknown key in [defaults]: {k!r}")
        if "unit" in defaults and not isinstance(defaults["unit"], str):
            problems.append("`defaults.unit` must be a string")
        if "unordered" in defaults and not isinstance(defaults["unordered"], bool):
            problems.append("`defaults.unordered` must be a boolean")
        ia = defaults.get("ignore_attrs")
        if ia is not None and not (
            isinstance(ia, list) and all(isinstance(x, str) for x in ia)
        ):
            problems.append("`defaults.ignore_attrs` must be a list of strings")

    elements = data.get("elements", {})
    if not isinstance(elements, dict):
        problems.append("`elements` must be a table")
    else:
        for tag, cfg in elements.items():
            if not isinstance(cfg, dict):
                problems.append(f"[elements.{tag}] must be a table")
                continue
            for k in cfg:
                if k not in ("key", "inline"):
                    problems.append(f"unknown key in [elements.{tag}]: {k!r}")
            key = cfg.get("key")
            if key is not None:
                if not isinstance(key, list) or not key:
                    problems.append(f"[elements.{tag}] `key` must be a non-empty list")
                else:
                    bad = [t for t in key if not _valid_key_token(t)]
                    if bad:
                        problems.append(f"[elements.{tag}] invalid key token(s): {bad}")
            if "inline" in cfg and not isinstance(cfg["inline"], bool):
                problems.append(f"[elements.{tag}] `inline` must be a boolean")

    return problems
