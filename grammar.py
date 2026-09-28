from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence


EPSILON = "ε"
PRODUCTION_PATTERN = re.compile(
    r"^\s*([A-Z])\s*(?:->|→)\s*"
    r"((?:[A-Za-z0-9]+|ε)(?:\s*\|\s*(?:[A-Za-z0-9]+|ε))*)\s*$"
)


class GrammarSyntaxError(ValueError):
    """Indica que una producción no cumple con el formato solicitado."""


@dataclass(frozen=True, slots=True)
class Grammar:
    start_symbol: str
    productions: Mapping[str, frozenset[str]]

    def __post_init__(self) -> None:
        immutable = {
            head: frozenset(bodies) for head, bodies in self.productions.items()
        }
        object.__setattr__(self, "productions", MappingProxyType(immutable))


@dataclass(frozen=True, slots=True)
class NullableStep:
    symbol: str
    reason: str


@dataclass(frozen=True, slots=True)
class CombinationStep:
    head: str
    original_body: str
    case_number: int
    total_cases: int
    removed_positions: tuple[int, ...]
    generated_body: str
    included: bool


def load_grammar(path: Path) -> Grammar:
    """Carga un archivo completo y detiene el proceso en la primera línea inválida."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise GrammarSyntaxError(f"No se pudo leer '{path}': {error}") from error

    if not lines:
        raise GrammarSyntaxError(f"El archivo '{path}' está vacío.")

    start_symbol: str | None = None
    productions: dict[str, set[str]] = {}

    for line_number, line in enumerate(lines, start=1):
        match = PRODUCTION_PATTERN.fullmatch(line)
        if match is None:
            raise GrammarSyntaxError(
                f"{path}:{line_number}: producción inválida: {line!r}. "
                "Use el formato A -> cuerpo1 | cuerpo2."
            )

        head, alternatives_text = match.groups()
        alternatives = {alternative.strip() for alternative in alternatives_text.split("|")}
        if start_symbol is None:
            start_symbol = head
        productions.setdefault(head, set()).update(alternatives)

    if start_symbol is None:  # Protección adicional para mantener el tipo no opcional.
        raise GrammarSyntaxError(f"El archivo '{path}' no contiene producciones.")

    return Grammar(
        start_symbol=start_symbol,
        productions={head: frozenset(bodies) for head, bodies in productions.items()},
    )


def find_nullable_symbols(grammar: Grammar) -> tuple[frozenset[str], tuple[NullableStep, ...]]:
    """Encuentra anulables por punto fijo hasta que ya no aparezcan símbolos nuevos."""
    nullable: set[str] = set()
    steps: list[NullableStep] = []

    for head in grammar.productions:
        if EPSILON in grammar.productions[head]:
            nullable.add(head)
            steps.append(NullableStep(head, f"{head} -> {EPSILON}"))

    changed = True
    while changed:
        changed = False
        for head, bodies in grammar.productions.items():
            if head in nullable:
                continue
            for body in sorted(bodies):
                # Un cuerpo es anulable solamente si todos sus símbolos ya lo son.
                if body != EPSILON and all(symbol in nullable for symbol in body):
                    nullable.add(head)
                    steps.append(
                        NullableStep(
                            head,
                            f"{head} -> {body}; todos los símbolos de {body} son anulables",
                        )
                    )
                    changed = True
                    break

    return frozenset(nullable), tuple(steps)


def eliminate_epsilon_productions(
    grammar: Grammar, nullable: frozenset[str]
) -> tuple[Grammar, tuple[CombinationStep, ...]]:
    """Genera las 2^m combinaciones al conservar o quitar ocurrencias anulables."""
    new_productions: dict[str, set[str]] = {
        head: set() for head in grammar.productions
    }
    steps: list[CombinationStep] = []

    for head, bodies in grammar.productions.items():
        for body in sorted(bodies):
            if body == EPSILON:
                continue

            nullable_positions = tuple(
                index for index, symbol in enumerate(body) if symbol in nullable
            )
            total_cases = 1 << len(nullable_positions)

            # Cada bit de la máscara decide si se elimina una ocurrencia anulable.
            for mask in range(total_cases):
                removed = tuple(
                    position
                    for bit, position in enumerate(nullable_positions)
                    if mask & (1 << bit)
                )
                removed_set = set(removed)
                generated = "".join(
                    symbol
                    for index, symbol in enumerate(body)
                    if index not in removed_set
                )
                included = bool(generated)
                if included:
                    new_productions[head].add(generated)

                steps.append(
                    CombinationStep(
                        head=head,
                        original_body=body,
                        case_number=mask + 1,
                        total_cases=total_cases,
                        removed_positions=removed,
                        generated_body=generated or EPSILON,
                        included=included,
                    )
                )

    result = Grammar(
        start_symbol=grammar.start_symbol,
        productions={
            head: frozenset(bodies) for head, bodies in new_productions.items()
        },
    )
    return result, tuple(steps)


def format_grammar(grammar: Grammar) -> str:
    lines: list[str] = []
    for head, bodies in grammar.productions.items():
        rendered_bodies = " | ".join(sorted(bodies)) if bodies else "∅"
        lines.append(f"{head} -> {rendered_bodies}")
    return "\n".join(lines)


def format_removed_positions(body: str, positions: Sequence[int]) -> str:
    if not positions:
        return "ninguna"
    return ", ".join(f"{body[position]}[{position + 1}]" for position in positions)
