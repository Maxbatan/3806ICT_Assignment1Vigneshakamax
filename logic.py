from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Iterable, Set

@dataclass(frozen=True, order=True)
class Term:
    name: str
    is_var: bool = False

    def __str__(self) -> str:
        return self.name

@dataclass(frozen=True, order=True)
class Formula:
    pass

@dataclass(frozen=True, order=True)
class Top(Formula):
    def __str__(self) -> str:
        return "Top"

@dataclass(frozen=True, order=True)
class Bot(Formula):
    def __str__(self) -> str:
        return "Bot"

@dataclass(frozen=True, order=True)
class Pred(Formula):
    name: str
    args: Tuple[Term, ...] = ()

    def __str__(self) -> str:
        if not self.args:
            return self.name
        return f"{self.name}(" + ",".join(str(a) for a in self.args) + ")"

@dataclass(frozen=True, order=True)
class Not(Formula):
    f: Formula
    def __str__(self) -> str:
        return f"~{paren(self.f)}"

@dataclass(frozen=True, order=True)
class And(Formula):
    left: Formula
    right: Formula
    def __str__(self) -> str:
        return f"({self.left} & {self.right})"

@dataclass(frozen=True, order=True)
class Or(Formula):
    left: Formula
    right: Formula
    def __str__(self) -> str:
        return f"({self.left} | {self.right})"

@dataclass(frozen=True, order=True)
class Imp(Formula):
    left: Formula
    right: Formula
    def __str__(self) -> str:
        return f"({self.left} -> {self.right})"

@dataclass(frozen=True, order=True)
class Forall(Formula):
    var: str
    body: Formula
    def __str__(self) -> str:
        return f"forall {self.var}. {self.body}"

@dataclass(frozen=True, order=True)
class Exists(Formula):
    var: str
    body: Formula
    def __str__(self) -> str:
        return f"exists {self.var}. {self.body}"

@dataclass(frozen=True)
class Sequent:
    left: frozenset[Formula]
    right: frozenset[Formula]

    def key(self) -> tuple:
        return (tuple(sorted(map(str, self.left))), tuple(sorted(map(str, self.right))))

    def __str__(self) -> str:
        l = ", ".join(sorted(map(str, self.left))) or " "
        r = ", ".join(sorted(map(str, self.right))) or " "
        return f"{l} |- {r}"

def paren(f: Formula) -> str:
    if isinstance(f, (Pred, Top, Bot)):
        return str(f)
    return f"({f})"

def substitute(formula: Formula, var: str, term: Term) -> Formula:
    if isinstance(formula, (Top, Bot)):
        return formula
    if isinstance(formula, Pred):
        new_args = tuple(term if (a.is_var and a.name == var) else a for a in formula.args)
        return Pred(formula.name, new_args)
    if isinstance(formula, Not):
        return Not(substitute(formula.f, var, term))
    if isinstance(formula, And):
        return And(substitute(formula.left, var, term), substitute(formula.right, var, term))
    if isinstance(formula, Or):
        return Or(substitute(formula.left, var, term), substitute(formula.right, var, term))
    if isinstance(formula, Imp):
        return Imp(substitute(formula.left, var, term), substitute(formula.right, var, term))
    if isinstance(formula, Forall):
        if formula.var == var:
            return formula
        return Forall(formula.var, substitute(formula.body, var, term))
    if isinstance(formula, Exists):
        if formula.var == var:
            return formula
        return Exists(formula.var, substitute(formula.body, var, term))
    raise TypeError(formula)

def collect_terms_formula(formula: Formula) -> Set[Term]:
    if isinstance(formula, Pred):
        return {a for a in formula.args if not a.is_var}
    if isinstance(formula, (Top, Bot)):
        return set()
    if isinstance(formula, Not):
        return collect_terms_formula(formula.f)
    if isinstance(formula, (And, Or, Imp)):
        return collect_terms_formula(formula.left) | collect_terms_formula(formula.right)
    if isinstance(formula, (Forall, Exists)):
        return collect_terms_formula(formula.body)
    return set()

def collect_terms_sequent(seq: Sequent) -> Set[Term]:
    out: Set[Term] = set()
    for f in seq.left | seq.right:
        out |= collect_terms_formula(f)
    return out

def formula_size(f: Formula) -> int:
    if isinstance(f, (Pred, Top, Bot)):
        return 1
    if isinstance(f, Not):
        return 1 + formula_size(f.f)
    if isinstance(f, (And, Or, Imp)):
        return 1 + formula_size(f.left) + formula_size(f.right)
    if isinstance(f, (Forall, Exists)):
        return 1 + formula_size(f.body)
    return 1
