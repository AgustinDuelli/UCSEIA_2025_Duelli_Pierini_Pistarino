from simpleai.search import CspProblem, backtrack
from itertools import combinations

# restricciones

# verificar que exista por lo menos una posición adjacente al Jedi que no sea una pared
def no_walls_adjacent_to_jedi(vars_acc, vars_val):
    jedi, walls = vars_val[0], vars_val[1:]
    
    jedi_x, jedi_y = jedi
    adjacents = [(jedi_x+1, jedi_y), (jedi_x-1,jedi_y), (jedi_x,jedi_y-1),(jedi_x,jedi_y+1)]

    adjacencies = 0

    for adjacent in adjacents:
        if adjacent in walls:
            adjacencies += 1

    return adjacencies <= 3

# verificar que las variables ocupen diferentes posiciones en el mapa
def different_position(vars_acc: list[str], vars_val: list[str]):
    first, second = vars_val

    return first != second

# verificar que existan, entre dos posiciones de droides, como máximo 6 droides
def at_most_six_adjacents(vars_acc, vars_val):
    droid1, droid2 = vars_val

    x, y = droid1
    first_adjacents = [(x+1, y), (x-1, y), (x, y-1), (x, y+1)]

    if droid2 not in first_adjacents:
        return True
    
    var_droid1, var_droid2 = vars_acc[0], vars_acc[1]
    first_idx, second_idx = int(var_droid1.split("_")[1]), int(var_droid2.split("_")[1])

    return droid_amounts[first_idx] + droid_amounts[second_idx] <= 6


droid_amounts = []
map_x = 0
map_y = 0


# agregar todas las restricciones para las variables
def add_restrictions(jedi, walls, droids):
    restrictions= []

    # jedi with walls adjacency
    restrictions.append((([jedi] + walls), no_walls_adjacent_to_jedi))

    # different positions for all walls and droids between them, with droids
    for first, second in combinations(walls + droids,2):
        restrictions.append(((first, second),different_position))

    # different positions for all walls with jedi
    for wall in walls:
        restrictions.append(((wall, jedi),different_position))

    # check adjacent droids
    for first, second in combinations(droids, 2):
        restrictions.append(((first, second), at_most_six_adjacents))

    return restrictions

 
def build_map(map_size: tuple[int, int], walls: int, droids: tuple[int, ...]):

    # usar globales para permitir usarlas al generar las restricciones
    global droid_amounts
    global map_x, map_y
    
    # 1 Jedi
    JEDI = "jedi"
    # Restricciones:
    # 1. No puede ocupar casilleros de PAREDES
    # 2. No puede estar rodeado de paredes en todos sus lados adyacentes
    # 3. No debe estar al borde del mapa


    # Variable cantidad de paredes
    PAREDES = [
        f"wall_{i}" for i in range(walls)
    ]
    # Restricciones:
    # 1. No pueden ubicarse donde estén DROIDES o el JEDI
    # 2. No pueden haber múltiples PAREDES en el mismo casillero


    # DROIDES se inicializa también con la cantidad necesaria
    DROIDES = [
        f"droid_{i}" for i in range(len(droids))
    ]
    # Restricciones:
    # 1. No pueden ocuparse en casilleros de PAREDES
    # 2. No pueden haber múltiples DROIDES en el mismo casillero
    # 3. Los DROIDES adyacentes no pueden sumar más de 6 droides entre sí

    # mantiene la cantidad de droides por casillero
    droid_amounts = droids

    VARIABLES = [JEDI] + PAREDES + DROIDES
    DOMAINS = {}

    map_x, map_y = map_size
    total_domain = [
        (row, col)
        for row in range(map_x)
        for col in range(map_y)
    ]

    no_borders_domain = [
        (row, col)
        for row in range(1, map_x -1)
        for col in range(1, map_y -1)
    ]

    for variable in VARIABLES:
        DOMAINS[variable] = total_domain

    DOMAINS[JEDI] = no_borders_domain


    restrictions = add_restrictions(JEDI, PAREDES, DROIDES)


    problem = CspProblem(VARIABLES, DOMAINS, restrictions)

    #solution = backtrack(problem, variable_heuristic=MOST_CONSTRAINED_VARIABLE)
    solution = backtrack(problem, inference=False)

    steps = []

    for step in solution:
        x, y = solution[step]
        if step == JEDI:
            steps.append((JEDI, x, y))
        if step in PAREDES:
            steps.append(("wall", x, y))
        if step in DROIDES:
            idx = int(step.split("_")[1])
            droid_amount = droid_amounts[idx]
            steps.append((droid_amount, x, y))

    return steps
