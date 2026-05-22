"""
ID: f13
Strate: complex
Complexité cyclomatique attendue: 8
Notes: algorithmique, détection de cycle (DFS), récursion.
"""


def topological_sort(graph: dict) -> list:
    """
    Effectue un tri topologique d'un graphe orienté.

    Le graphe est représenté en liste d'adjacence :
    {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}

    - Retourne une liste de nœuds dans un ordre topologique valide
    - Lève ValueError si le graphe contient un cycle
    - Lève TypeError si l'entrée n'est pas un dict
    - Un dict vide retourne une liste vide
    """
    if not isinstance(graph, dict):
        raise TypeError("Le graphe doit être un dict")

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    result = []

    def dfs(node):
        if node not in color:
            color[node] = WHITE
        if color[node] == GRAY:
            raise ValueError("Cycle détecté dans le graphe")
        if color[node] == BLACK:
            return
        color[node] = GRAY
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        color[node] = BLACK
        result.append(node)

    for node in list(graph.keys()):
        if color[node] == WHITE:
            dfs(node)

    return result[::-1]
