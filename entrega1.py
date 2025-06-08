from simpleai.search import SearchProblem, astar
from itertools import permutations


# Un Jedi debe derrotar a todos los droides en el menor tiempo posible

# Droides por casilla: variable.
# Concentración: utilizado para acciones.
# Paredes: casillas que no se ocupan por Jedi o droides.

""" Acciones:
1. Moverse
    El Jedi se mueve en casillas adjacentes. No puede atravesar paredes.
    Tiempo: 1s
    Concentración comsumida: 0
2. Saltar con la fuerza
    El Jedi se mueve diagonalmente. No pude atravesar paredes ni pararse sobre una casilla que sea pared.
    Tiempo: 1s
    Concentración consumida: 1
3. Atacar
    El Jedi ataca a un droide en su casilla. SOLO DESTRUYE 1 DROIDE. No importan cuantos droides existan en la casilla.
    Tiempo: 1s
    Concentración comsumida: 1
4. Atacar con la fuerza
    El Jedi ataca a todos los droides de la casilla con un solo ataque.
    Tiempo: 2s
    Concentración consumida: 5
5. Descansar (para recuperar concentración)
    El Jedi toma un descanso lejos de los droides para recuperarse. No pueden haber droides en su casilla ni en las adyacentes.
    Tiempo: 3s
    Concentración consumida: -10
"""

MOVE = "move"
JUMP = "jump"
SLASH = "slash"
FORCE = "force"
REST = "rest"

ACTION_RELATION = {
    # NOMBRE: (TIEMPO, CONCENTRACIÓN_CONSUMIDA)
    MOVE: (1, 0),
    JUMP: (1, 1),
    SLASH: (1, 1),
    FORCE: (2, 5),
    REST: (3, -10),
}

WALLS = []


def find_droids_for_position(position, droids):
    # obtener datos de posición a averiguar
    x, y = position

    for droid in droids:
        x_position, y_position, amount = droid

        if x == x_position and y == y_position:
            return True
    return False


def diminish_droids_in_position(position, droids):
    # obtener datos de posición
    x, y = position

    for i, droid in enumerate(droids):
        x_position, y_position, amount = droid

        if x == x_position and y == y_position:
            amount -= 1
            droids[i] = (x_position, y_position, amount)
            return droids, amount
    return droids, -1


def remove_droid_position(position, droids):
    # obtener datos de posición a averiguar
    x, y = position

    for droid in droids:
        x_position, y_position, amount = droid

        if x == x_position and y == y_position:
            droids.remove(droid)
    return droids


# funciones para calcular heurística
# calculate_attack_amount
# quadrants_distance(incluye: brute_force_travel_distance, chebyshev_distance)


def calculate_attack_amount(
    droids: tuple[tuple[int, int, int]], jedi_concentration: int
):
    """
    Calcula cantidad de ataques mínimos necesarios para ganar. Por cada casilla con drones, mínimo se necesita un ataque. \n
    Si se tienen múltiples drones, se agrega otro valor (ataque de fuerza de costo 2). \n
    Si se tienen más de 5 drones pero no concentración, se agrega el costo de descansar (3s) más 2s en el primer caso de ataque con fuerza. \n
    """

    total = 0

    concentration_left = jedi_concentration

    for droid in droids:
        # si existe la posición hay un dron
        # como mínimo se necesita atacar (costo: 1s)
        total += 1

        _, _, amount = droid

        # si hay más de un dron, como mínimo se necesitan dos segundos
        if amount > 1:
            # si tiene suficiente concentración para un ataque en área con fuerza, la consume y realiza el ataque
            if concentration_left >= 5:
                total += 2
                concentration_left -= 5
            # sino, como mínimo, necesita realizar 2 ataques, requiriendo 2s
            else:
                total += 1

    return total


def quadrants_distance(droids: tuple[tuple[int, int, int]], jedi: tuple[int, int]):
    """
    Calcula distancias máximas de cada cuadrante del mapa
    Permite omitir celdas que se encuentra una detrás de otra
    Busca el camino más corto para llegar a cada punto uno detrás de otros.

    \n
    Ejemplo:
    #   [ D  P  _  _  P  D]
    #   [ _  P  _  _  P  _]
    #   [ _  _  J  _  _  _]
    #   [ _  D  _  D  D  D]
    #   [ _  _  _  _  _  _]
    P = pared J = jedi D = droides
    \n
    Para el cuadrante izquierdo superior (0), la distancia mayor es la esquina. \n
    Para el cuadrante derecho inferior (2), la distancia mayor es el que está más cercano a la pared, aproximado por distancia de chevyshev.\n
    Luego de tener la distancia máxima de cada cuadrante, se busca el camino más corto para recorrer todos los puntos.
    """

    # obtiene posiciones de droide y jedi descompuestas en eje vertical y horizontal
    x_jedi, y_jedi = jedi

    quadrant_0 = 0
    quadrant_0_position = None
    quadrant_1 = 0
    quadrant_1_position = None
    quadrant_2 = 0
    quadrant_2_position = None
    quadrant_3 = 0
    quadrant_3_position = None

    for droid in droids:
        x_droid, y_droid, _ = droid

        # verificar que no sea la misma casilla que el Jedi
        if x_droid == x_jedi and y_droid == y_jedi:
            continue

        # calculo de distancia de droide a jedi
        # sirve para saber si son los droides más alejados en ese cuadrante en el que se encuentran
        temp_dist = chebyshev_distance((x_droid, y_droid), jedi)

        # cuadrante 0
        if x_droid <= x_jedi and y_droid < y_jedi and temp_dist >= quadrant_0:
            quadrant_0 = temp_dist
            quadrant_0_position = (x_droid, y_droid)
        # cuadrante 1
        elif x_droid < x_jedi and y_droid >= y_jedi and temp_dist >= quadrant_1:
            quadrant_1 = temp_dist
            quadrant_1_position = (x_droid, y_droid)
        # cuadrante 2
        elif x_droid >= x_jedi and y_droid > y_jedi and temp_dist >= quadrant_2:
            quadrant_2 = temp_dist
            quadrant_2_position = (x_droid, y_droid)
        # cuadrante 3
        elif x_droid > x_jedi and y_droid <= y_jedi and temp_dist >= quadrant_3:
            quadrant_3 = temp_dist
            quadrant_3_position = (x_droid, y_droid)

    # se genera una lista con los valores máximos de posición por distancia al Jedi de cada cuadrante
    quadrants_max_value = [
        quadrant_0_position,
        quadrant_1_position,
        quadrant_2_position,
        quadrant_3_position,
    ]

    # se eliminan aquellos cuadrantes sin droides alejados de la posición del Jedi
    quadrants_max_position = list(
        quadrant for quadrant in quadrants_max_value if quadrant is not None
    )

    # se busca la distancia de viaje mínima para recorrer todos los puntos
    total_travel_distance = brute_force_travel_distance(jedi, quadrants_max_position)

    return total_travel_distance


def brute_force_travel_distance(
    start: tuple[int, int], points: list[tuple[int, int]]
) -> float:
    """
    Busca de las permutaciones de todos los puntos, el camino más corto desde el punto de inicio para alcanzar todos los puntos

    points: puntos que deben recorrerse
    start: punto de inicio

    Los puntos son la posición en dos ejes con valores discretos.
    """

    min_cost = float("inf")

    for permutation in permutations(points):
        cost = 0
        current = start
        for point in permutation:
            cost += chebyshev_distance(current, point)
            current = point
        if cost < min_cost:
            min_cost = cost

    return min_cost


def chebyshev_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class JediProblem(SearchProblem):

    def is_goal(self, state):
        jedi, droids = state

        # si no existen droides en el estado, se llegó a la meta
        return len(droids) == 0

    def cost(self, state, action, action2):
        # toma los datos de la acción realizada
        action_type, _ = action

        # calculo de costo por segundos de tiempo tomados para realizar la acción
        time, _ = ACTION_RELATION[action_type]

        return time

    def actions(self, state):
        jedi, droids = state
        global WALLS

        jedi_x, jedi_y, jedi_concentration = jedi

        available_actions = []

        # acciones que no necesitan concentración

        # movimientos adjacentes
        adjacent_movements = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        # variable para verificar droides adjacentes
        no_adjacency = True

        if find_droids_for_position((jedi_x, jedi_y), droids):
            no_adjacency = False

        for move in adjacent_movements:
            x_movement, y_movement = move
            jedi_new_position = jedi_x + x_movement, jedi_y + y_movement

            # si la posición nueva es una pared, no se puede hacer la acción
            if jedi_new_position in WALLS:
                continue
            # si hay droides en la posición nueva, entonces hay droides adjacentes a la posición actual
            if find_droids_for_position(jedi_new_position, droids):
                no_adjacency = False

            available_actions.append((MOVE, jedi_new_position))

        # si no hay droides adjacentes a posiciones actual, se puede descansar
        if no_adjacency:
            available_actions.append((REST, None))

        # verificar concentración antes de avanzar
        if jedi_concentration < 1:
            return available_actions

        # acciones que necesitan concentración
        # movimientos diagonales
        diagonal_movements = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for move in diagonal_movements:
            x_movement, y_movement = move
            jedi_new_position = jedi_x + x_movement, jedi_y + y_movement

            # si la posición nueva es una pared, no se puede hacer la acción
            if jedi_new_position in WALLS:
                continue

            available_actions.append((JUMP, jedi_new_position))

        # verificar si hay droides en la posición actual del Jedi
        jedi_position = jedi_x, jedi_y
        if find_droids_for_position(jedi_position, droids):
            # puede atacar debido a que tiene concentración
            available_actions.append((SLASH, None))

            # si tiene suficiente concentración, puede hacer un ataque con la fuerza
            if jedi_concentration >= 5:
                available_actions.append((FORCE, None))

        return available_actions

    def result(self, state, action):
        # cambiar de tuplas a listas el estado
        state_list = list(list(state_item) for state_item in state)
        jedi, droids = state_list

        # obtener datos de Jedi
        jedi_x, jedi_y, jedi_concentration = jedi

        # obtener datos de tipo de acción y el movimiento (si hubo)
        type_action, movement = action

        # obtener el dato de tiempo y concentración relacionado a la acción
        time, concentration_used = ACTION_RELATION[type_action]

        # consumir o aumentar la concentración según sea necesario
        jedi_concentration -= concentration_used

        # si no es nulo, hay movimiento
        if movement is not None:
            x_movement, y_movement = movement
            jedi_x = x_movement
            jedi_y = y_movement

        # se genera el ataque a droide
        jedi_position = (jedi_x, jedi_y)
        if type_action == SLASH:
            droids, droids_left_position = diminish_droids_in_position(
                jedi_position, droids
            )

            # si se eliminó el último droid, eliminar droides de lista
            if droids_left_position == 0:
                droids = remove_droid_position(jedi_position, droids)

        # se atacan a todos los droides de la casilla actual
        if type_action == FORCE:
            droids = remove_droid_position(jedi_position, droids)

        # rearmar el estado como tuplas
        jedi_state = (jedi_x, jedi_y, jedi_concentration)
        droids_state = tuple(droids)

        return (jedi_state, droids_state)

    def heuristic(self, state):
        jedi, droids = state

        jedi_x, jedi_y, jedi_concentration = jedi

        # inicializar la heurística
        heuristic = 0

        # calcular cantidad de ataques mínimos necesarios por droides
        heuristic += calculate_attack_amount(droids, jedi_concentration)

        # suma la distancia necearia para visitar los droides más lejanos de cada cuadrante
        # visita los droides en orden para mejor aproximación
        # cuadrantes:
        #   [ 0   1  1 ]
        #     0   j  2
        #   [ 3   3  2 ]
        # j = jedi
        #
        heuristic += quadrants_distance(droids, (jedi_x, jedi_y))
        return heuristic


def play_game(jedi_at, jedi_concentration, walls, droids):
    # generar tuplas del estado
    jedi_x_pos, jedi_y_pos = jedi_at
    global WALLS
    WALLS = walls
    state_droids = tuple(droid for droid in droids)

    # estado inicial del problema
    state = ((jedi_x_pos, jedi_y_pos, jedi_concentration), state_droids)

    # llamar al problema de búsqueda
    problem = JediProblem(state)

    # seleccionar el método de búsqueda
    solution = astar(problem, graph_search=True)

    # tomar acciones de la solución
    jedi_actions = []

    if solution is not None:
        for action, _ in solution.path():
            if action is None:
                continue
            jedi_actions.append(action)
    else:
        print("what the potato?")
    return jedi_actions


# mejoras posibles de heurística:
# 1. ver si hay paredes en el medio
