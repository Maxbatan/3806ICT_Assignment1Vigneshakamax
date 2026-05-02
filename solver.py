from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, Optional, List
from logic import *

@dataclass
class ProofResult:
    proved: bool
    steps: int
    max_depth_seen: int
    reason: str

@dataclass
class SolverConfig:
    max_depth: int = 70
    max_steps: int = 5000
    max_fresh_terms: int = 4
    improved: bool = False

UsedMap = Dict[Tuple[str, str, str], frozenset[str]]

@dataclass
class Solver:
    config: SolverConfig
    steps: int = 0
    max_depth_seen: int = 0
    fresh_count: int = 0
    visited: Set[tuple] = field(default_factory=set)

    def prove(self, formula: Formula) -> ProofResult:
        self.steps = 0
        self.max_depth_seen = 0
        self.fresh_count = 0
        self.visited.clear()
        seq = Sequent(frozenset(), frozenset({formula}))
        ok = self._prove(seq, 0, {})
        reason = "closed" if ok else "open branch or resource limit"
        return ProofResult(ok, self.steps, self.max_depth_seen, reason)

    def _prove(self, seq: Sequent, depth: int, used: UsedMap) -> bool:
        self.steps += 1
        self.max_depth_seen = max(self.max_depth_seen, depth)
        if self.steps > self.config.max_steps or depth > self.config.max_depth:
            return False

        seq = self._normalise(seq)
        if self._closed(seq):
            return True

        if self.config.improved:
            inst_key = tuple(sorted((a, b, c, tuple(sorted(v))) for (a, b, c), v in used.items()))
            key = (seq.key(), inst_key)
            if key in self.visited:
                return False
            self.visited.add(key)

        next_seq = self._non_branching(seq)
        if next_seq is not None:
            return self._prove(next_seq, depth + 1, used)

        branches = self._branching(seq)
        if branches is not None:
            return all(self._prove(b, depth + 1, dict(used)) for b in branches)

        quant = self._quantifier_copy(seq, used)
        if quant is not None:
            next_seq, next_used = quant
            return self._prove(next_seq, depth + 1, next_used)

        return False

    def _normalise(self, seq: Sequent) -> Sequent:
        return Sequent(frozenset(seq.left), frozenset(seq.right))

    def _closed(self, seq: Sequent) -> bool:
        return bool(seq.left & seq.right) or any(isinstance(f, Bot) for f in seq.left) or any(isinstance(f, Top) for f in seq.right)

    def _fresh(self, prefix: str = "c") -> Optional[Term]:
        if self.fresh_count >= self.config.max_fresh_terms:
            return None
        t = Term(f"{prefix}{self.fresh_count}", False)
        self.fresh_count += 1
        return t

    def _terms(self, seq: Sequent) -> List[Term]:
        terms = sorted(collect_terms_sequent(seq), key=lambda t: t.name)
        return terms if terms else [Term("a", False)]

    def _ordered(self, items):
        # The improved solver uses a deterministic small-first order for decomposable formulae.
        if not self.config.improved:
            return list(items)
        return sorted(items, key=lambda f: (formula_size(f), str(f)))

    def _non_branching(self, seq: Sequent) -> Optional[Sequent]:
        for f in self._ordered(seq.left):
            rest = set(seq.left); rest.remove(f)
            if isinstance(f, And):
                return Sequent(frozenset(rest | {f.left, f.right}), seq.right)
            if isinstance(f, Not):
                return Sequent(frozenset(rest), frozenset(set(seq.right) | {f.f}))
            if isinstance(f, Exists):
                t = self._fresh("e")
                if t is None:
                    return None
                return Sequent(frozenset(rest | {substitute(f.body, f.var, t)}), seq.right)
        for f in self._ordered(seq.right):
            rest = set(seq.right); rest.remove(f)
            if isinstance(f, Or):
                return Sequent(seq.left, frozenset(rest | {f.left, f.right}))
            if isinstance(f, Imp):
                return Sequent(frozenset(set(seq.left) | {f.left}), frozenset(rest | {f.right}))
            if isinstance(f, Not):
                return Sequent(frozenset(set(seq.left) | {f.f}), frozenset(rest))
            if isinstance(f, Forall):
                t = self._fresh("u")
                if t is None:
                    return None
                return Sequent(seq.left, frozenset(rest | {substitute(f.body, f.var, t)}))
        return None

    def _branching(self, seq: Sequent) -> Optional[List[Sequent]]:
        for f in self._ordered(seq.right):
            rest = set(seq.right); rest.remove(f)
            if isinstance(f, And):
                return [Sequent(seq.left, frozenset(rest | {f.left})),
                        Sequent(seq.left, frozenset(rest | {f.right}))]
        for f in self._ordered(seq.left):
            rest = set(seq.left); rest.remove(f)
            if isinstance(f, Or):
                return [Sequent(frozenset(rest | {f.left}), seq.right),
                        Sequent(frozenset(rest | {f.right}), seq.right)]
            if isinstance(f, Imp):
                return [Sequent(frozenset(rest), frozenset(set(seq.right) | {f.left})),
                        Sequent(frozenset(rest | {f.right}), seq.right)]
        return None

    def _quantifier_copy(self, seq: Sequent, used: UsedMap) -> Optional[Tuple[Sequent, UsedMap]]:
        candidates = []
        for f in self._ordered(seq.left):
            if isinstance(f, Forall):
                candidates.append(("forall_left", f))
        for f in self._ordered(seq.right):
            if isinstance(f, Exists):
                candidates.append(("exists_right", f))

        for side, f in candidates:
            terms = self._terms(seq)
            if self.config.improved:
                terms = self._coordinated_terms(f, seq, terms)
            key = (side, str(f), f.var)
            already = set(used.get(key, frozenset()))
            for t in terms:
                if t.name in already:
                    continue
                instance = substitute(f.body, f.var, t)
                if side == "forall_left" and instance in seq.left:
                    continue
                if side == "exists_right" and instance in seq.right:
                    continue
                new_used = dict(used)
                new_used[key] = frozenset(already | {t.name})
                if side == "forall_left":
                    return Sequent(frozenset(set(seq.left) | {instance}), seq.right), new_used
                return Sequent(seq.left, frozenset(set(seq.right) | {instance})), new_used

            fresh = self._fresh("q")
            if fresh is not None:
                instance = substitute(f.body, f.var, fresh)
                new_used = dict(used)
                new_used[key] = frozenset(already | {fresh.name})
                if side == "forall_left":
                    return Sequent(frozenset(set(seq.left) | {instance}), seq.right), new_used
                return Sequent(seq.left, frozenset(set(seq.right) | {instance})), new_used
        return None

    def _coordinated_terms(self, quant: Formula, seq: Sequent, terms: List[Term]) -> List[Term]:
        wanted = []
        pool = seq.right if isinstance(quant, Forall) else seq.left
        for f in pool:
            if isinstance(f, Pred):
                wanted.extend([a for a in f.args if not a.is_var])
        seen = set()
        ordered = []
        for t in wanted + terms:
            if t.name not in seen:
                seen.add(t.name)
                ordered.append(t)
        return ordered

def prove_baseline(formula: Formula, max_depth: int = 70) -> ProofResult:
    return Solver(SolverConfig(max_depth=max_depth, improved=False)).prove(formula)

def prove_improved(formula: Formula, max_depth: int = 70) -> ProofResult:
    return Solver(SolverConfig(max_depth=max_depth, improved=True)).prove(formula)
