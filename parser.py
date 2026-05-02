from __future__ import annotations
import re
from typing import List, Set
from logic import Term, Formula, Top, Bot, Pred, Not, And, Or, Imp, Forall, Exists

TOKEN_RE = re.compile(r"\s*(->|[()&|~.,]|forall\b|exists\b|Top\b|Bot\b|[A-Za-z_][A-Za-z0-9_]*)")

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, text: str):
        self.tokens = TOKEN_RE.findall(text)
        joined = "".join(self.tokens)
        compact = re.sub(r"\s+", "", text)
        if joined.replace(" ", "") != compact:
            raise ParseError(f"Cannot tokenise input near: {text}")
        self.i = 0
        self.bound: Set[str] = set()

    def peek(self) -> str | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def pop(self, expected: str | None = None) -> str:
        if self.i >= len(self.tokens):
            raise ParseError("Unexpected end of input")
        tok = self.tokens[self.i]
        if expected is not None and tok != expected:
            raise ParseError(f"Expected {expected}, got {tok}")
        self.i += 1
        return tok

    def parse(self) -> Formula:
        f = self.parse_imp()
        if self.peek() is not None:
            raise ParseError(f"Unexpected token: {self.peek()}")
        return f

    def parse_imp(self) -> Formula:
        left = self.parse_or()
        if self.peek() == "->":
            self.pop("->")
            right = self.parse_imp()
            return Imp(left, right)
        return left

    def parse_or(self) -> Formula:
        f = self.parse_and()
        while self.peek() == "|":
            self.pop("|")
            f = Or(f, self.parse_and())
        return f

    def parse_and(self) -> Formula:
        f = self.parse_unary()
        while self.peek() == "&":
            self.pop("&")
            f = And(f, self.parse_unary())
        return f

    def parse_unary(self) -> Formula:
        tok = self.peek()
        if tok == "~":
            self.pop("~")
            return Not(self.parse_unary())
        if tok in ("forall", "exists"):
            quant = self.pop()
            var = self.pop()
            self.pop(".")
            old = set(self.bound)
            self.bound.add(var)
            body = self.parse_imp()
            self.bound = old
            return Forall(var, body) if quant == "forall" else Exists(var, body)
        if tok == "(":
            self.pop("(")
            f = self.parse_imp()
            self.pop(")")
            return f
        return self.parse_atom()

    def parse_atom(self) -> Formula:
        name = self.pop()
        if name == "Top":
            return Top()
        if name == "Bot":
            return Bot()
        args = []
        if self.peek() == "(":
            self.pop("(")
            if self.peek() != ")":
                while True:
                    tname = self.pop()
                    args.append(Term(tname, is_var=(tname in self.bound)))
                    if self.peek() == ",":
                        self.pop(",")
                        continue
                    break
            self.pop(")")
        return Pred(name, tuple(args))

def parse_formula(text: str) -> Formula:
    line = text.strip()
    if not line or line.startswith("#"):
        raise ParseError("Empty/comment line")
    return Parser(line).parse()

def parse_file(path: str) -> List[Formula]:
    formulas = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            try:
                formulas.append(parse_formula(text))
            except ParseError as e:
                raise ParseError(f"{path}:{line_no}: {e}") from e
    return formulas
