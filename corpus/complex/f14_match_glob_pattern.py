"""
ID: f14
Strate: complex
Complexité cyclomatique attendue: 8
Notes: programmation dynamique implicite, beaucoup de branches.
"""


def match_glob_pattern(pattern: str, string: str) -> bool:
    """
    Vérifie si `string` correspond au pattern glob `pattern`.

    Wildcards supportés :
    - `*` : correspond à zéro ou plusieurs caractères (n'importe lesquels)
    - `?` : correspond à exactement un caractère
    - autres : correspondance littérale (sensible à la casse)

    Lève TypeError si l'un des arguments n'est pas une chaîne.
    """
    if not isinstance(pattern, str) or not isinstance(string, str):
        raise TypeError("pattern et string doivent être des chaînes")

    m, n = len(pattern), len(string)
    # dp[i][j] = True si pattern[:i] match string[:j]
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True

    # un pattern qui commence par des '*' peut matcher la chaîne vide
    for i in range(1, m + 1):
        if pattern[i - 1] == "*":
            dp[i][0] = dp[i - 1][0]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if pattern[i - 1] == "*":
                dp[i][j] = dp[i - 1][j] or dp[i][j - 1]
            elif pattern[i - 1] == "?" or pattern[i - 1] == string[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = False

    return dp[m][n]
