"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A bi-level symbol table for Jack compilation.

    Public API (matches the book):
        * start_subroutine()               – reset sub-routine scope
        * define(name, type_, kind)        – define a new identifier
        * var_count(kind) -> int           – count of identifiers of kind
        * kind_of(name)  -> str | None     – STATIC | FIELD | ARG | VAR | None
        * type_of(name)  -> str | None     – declared type (class or primitive)
        * index_of(name) -> int | None     – running index within its kind
    """

    _VALID_KINDS = {"STATIC", "FIELD", "ARG", "VAR"}

    def __init__(self) -> None:
        self._class_scope: dict[str, dict[str, object]] = {}  # Class-level: STATIC/FIELD
        self._sub_scope: dict[str, dict[str, object]] = {}    # Subroutine: ARG/VAR
        self._counts: dict[str, int] = {k: 0 for k in self._VALID_KINDS}  # Running indexes

    def start_subroutine(self) -> None:
        """Reset ARG and VAR tables at start of each subroutine. Class scope stays."""
        self._sub_scope.clear()
        self._counts["ARG"] = 0
        self._counts["VAR"] = 0

    def define(self, name: str, type_: str, kind: str) -> None:
        """Define new identifier and assign it the next index of kind."""
        kind = kind.upper()
        if kind not in self._VALID_KINDS:
            raise ValueError(f"Invalid kind: {kind}")

        index: int = self._counts[kind]
        entry = {"type": type_, "kind": kind, "index": index}

        if kind in ("STATIC", "FIELD"):
            self._class_scope[name] = entry
        else:  # ARG or VAR
            self._sub_scope[name] = entry

        self._counts[kind] += 1

    def var_count(self, kind: str) -> int:
        """Return number of variables of this kind already defined."""
        kind = kind.upper()
        if kind not in self._VALID_KINDS:
            raise ValueError(f"Invalid kind: {kind}")
        return self._counts[kind]

    def _lookup(self, name: str) -> dict[str, object] | None:
        """Return entry for name, searching subroutine scope first, then class."""
        return self._sub_scope.get(name) or self._class_scope.get(name)

    def kind_of(self, name: str):
        """Return kind of name or None if not found."""
        entry = self._lookup(name)
        return entry["kind"] if entry else None

    def type_of(self, name: str):
        """Return type of name or None if not found."""
        entry = self._lookup(name)
        return entry["type"] if entry else None

    def index_of(self, name: str):
        """Return index of name or None if not found."""
        entry = self._lookup(name)
        return entry["index"] if entry else None
