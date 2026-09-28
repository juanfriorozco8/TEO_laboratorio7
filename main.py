from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from grammar import (
    EPSILON,
    Grammar,
    GrammarSyntaxError,
    eliminate_epsilon_productions,
    find_nullable_symbols,
    format_grammar,
    format_removed_positions,
    load_grammar,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Elimina producciones épsilon de gramáticas libres de contexto."
    )
    parser.add_argument(
        "files",
        metavar="ARCHIVO",
        nargs="+",
        type=Path,
        help="archivo de texto con una gramática",
    )
    return parser


def show_process(path: Path, grammar: Grammar) -> None:
    print(f"\n{'=' * 72}")
    print(f"Gramática: {path}")
    print("Validación: todas las producciones son válidas.")
    print("\nGramática original:")
    print(format_grammar(grammar))

    nullable, nullable_steps = find_nullable_symbols(grammar)
    print("\n1. Búsqueda de símbolos anulables:")
    if nullable_steps:
        for number, step in enumerate(nullable_steps, start=1):
            print(f"   {number}. {step.symbol} es anulable porque {step.reason}.")
    else:
        print("   No se encontraron símbolos anulables.")
    rendered_nullable = ", ".join(sorted(nullable)) if nullable else "∅"
    print(f"   Conjunto final: {{{rendered_nullable}}}")

    result, combinations = eliminate_epsilon_productions(grammar, nullable)
    print("\n2. Generación de nuevas producciones:")
    for step in combinations:
        removed = format_removed_positions(step.original_body, step.removed_positions)
        action = "se agrega" if step.included else "se descarta para eliminar ε"
        print(
            f"   {step.head} -> {step.original_body}: caso "
            f"{step.case_number}/{step.total_cases}, se quita {removed} "
            f"=> {step.generated_body} ({action})."
        )

    print(f"\n3. Gramática final sin producciones-{EPSILON}:")
    print(format_grammar(result))


def main(arguments: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)

    # Primero se validan todos los archivos para no ejecutar el algoritmo parcialmente.
    try:
        loaded = [(path, load_grammar(path)) for path in args.files]
    except GrammarSyntaxError as error:
        print(f"ERROR: {error}")
        return 1

    for path, grammar in loaded:
        show_process(path, grammar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
