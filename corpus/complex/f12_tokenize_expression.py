"""
ID: f12
Strate: complex
Complexité cyclomatique attendue: 9
Notes: parseur custom, machine à états implicite, beaucoup d'edge cases.
"""


def tokenize_arithmetic_expression(expr: str) -> list:
    """
    Tokenize une expression arithmétique simple.

    Tokens reconnus :
    - nombres entiers et décimaux : ("NUM", valeur_float)
    - opérateurs : ("OP", "+"), ("OP", "-"), ("OP", "*"), ("OP", "/")
    - parenthèses : ("LPAREN", "("), ("RPAREN", ")")

    Les espaces sont ignorés. Lève ValueError sur caractère inconnu
    ou nombre malformé (ex. "1.2.3"). Lève TypeError si l'entrée n'est
    pas une chaîne.
    """
    if not isinstance(expr, str):
        raise TypeError("L'entrée doit être une chaîne")

    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in "+-*/":
            tokens.append(("OP", c))
            i += 1
        elif c == "(":
            tokens.append(("LPAREN", "("))
            i += 1
        elif c == ")":
            tokens.append(("RPAREN", ")"))
            i += 1
        elif c.isdigit() or c == ".":
            start = i
            dot_count = 0
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    dot_count += 1
                i += 1
            if dot_count > 1:
                raise ValueError(f"Nombre malformé: {expr[start:i]}")
            tokens.append(("NUM", float(expr[start:i])))
        else:
            raise ValueError(f"Caractère inconnu: {c}")
    return tokens
