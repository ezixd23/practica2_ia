import json
from itertools import permutations
from geopy.distance import geodesic

def load_json_array(filename):
    with open(str(filename) + '.json', 'r') as file:
        return json.load(file)[filename]

restaurants = load_json_array('restaurants')
orders = load_json_array('orders')
specialities = load_json_array('specialities')

specialities_dict = {s['especialitat']: s for s in specialities}

# Afegir les dades de compromís i pes a les comandes
for order in orders:
    especialitat = order['especialitat']
    order['compromis'] = specialities_dict[especialitat]['compromis']
    order['pes'] = specialities_dict[especialitat]['pes']


for index, restaurant in enumerate(restaurants):
    restaurant['coordenades'] = tuple(map(float, restaurant['coordenades'].split(", ")))
    restaurant['id'] = index

# Calcular totes les distàncies entre la seu i els restaurants, i entre restaurants
def calculate_all_distances(hub, locations):
    distances = {}
    for loc1 in locations:
        store_distance(distances, hub, loc1)
        for loc2 in locations:
            if loc1 != loc2:
                store_distance(distances, loc1, loc2)
    return distances

# Algoritme TSP per determinar l'ordre de visita dels restaurants
def tsp(locations: list, restaurant_distances: dict):
    start = locations[0] # Seu
    locations.pop(0) # Eliminar la seu de la llista de restaurants
    n = len(locations)
    all_points = list(range(n))
    memo = {}

    def visit(visited, last):
        if visited == (1 << n) - 1:
            return get_distance(restaurant_distances, locations[last], start)

        if (visited, last) in memo:
            return memo[(visited, last)]

        min_dist = float('inf')
        for point in all_points:
            if visited & (1 << point) == 0:
                dist = get_distance(restaurant_distances, locations[last], locations[point])
                min_dist = min(min_dist, dist)

        memo[(visited, last)] = min_dist
        return min_dist

    return visit(1, 0)


def tsp2(locations: list, restaurant_distances: dict):
    start = locations[0]
    current = start
    visited = [start]
    unvisited = locations[1:]

    total_distance = 0

    while unvisited:
        min_dist = float('inf')
        min_loc = None

        for loc in unvisited:
            dist = get_distance(restaurant_distances, current, loc)
            if dist < min_dist:
                min_dist = dist
                min_loc = loc

        total_distance += min_dist

        visited.append(min_loc)
        unvisited.remove(min_loc)
        current = min_loc

    print("Distance: " + str(total_distance))
    return visited


# Funció per seleccionar les comandes segons el problema de la motxilla
def knapsack(orders):
    # Ordenar les comandes per temps de compromís (més curts primer)
    orders = sorted(orders, key=lambda x: x['compromis'])
    
    selected_orders = []
    total_weight = 0
    
    for order in orders:
        if total_weight + order['pes'] <= 12000:
            selected_orders.append(order)
            total_weight += order['pes']
    
    return selected_orders

def select_orders_by_restaurant(restaurants, orders):
    # Seleccionar les comandes per cada restaurant
    orders_by_restaurant = {}
    for order in orders:
        for restaurant in restaurants:
            if order['especialitat'] == restaurant['especialitat']:
                if restaurant['id'] not in orders_by_restaurant:
                    orders_by_restaurant[restaurant['id']] = []
                orders_by_restaurant[restaurant['id']].append(order)
                break
    return orders_by_restaurant

# Funció per calcular la distància entre dos punts
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

def store_distance(distances: dict, loc1, loc2):
    coord1 = loc1["coordenades"]
    coord2 = loc2["coordenades"]
    distances[(coord1, coord2)] = calculate_distance(coord1, coord2)
    distances[(coord2, coord1)] = distances[(coord1, coord2)]
    return distances

def get_distance(distances: dict, loc1, loc2):
    coord1 = loc1["coordenades"]
    coord2 = loc2["coordenades"]
    return distances[(coord1, coord2)]

def plot_tsp_route(restaurants, route):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    x_coords = [restaurant['coordenades'][0] for restaurant in restaurants]
    y_coords = [restaurant['coordenades'][1] for restaurant in restaurants]
    plt.scatter(x_coords, y_coords, color='blue')


    for i, restaurant in enumerate(restaurants):
        plt.text(restaurant['coordenades'][0], restaurant['coordenades'][1], f"{i}: {restaurant['nom']}")

    route_coords = [restaurant['coordenades'] for restaurant in route]
    route_x = [coord[0] for coord in route_coords]
    route_y = [coord[1] for coord in route_coords]

    plt.plot(route_x, route_y, color='red', linestyle='-', marker='o')
    plt.title("TSP Route")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Determinar l'ordre de visita dels restaurants
    restaurant_distances = calculate_all_distances(restaurants[0], restaurants)
    orders_by_restaurant = select_orders_by_restaurant(restaurants, knapsack(orders))

    selected_restaurants = []
    for restaurant_id in orders_by_restaurant.keys():
        selected_restaurants.append(restaurants[restaurant_id])

    restaurant_order = tsp2(selected_restaurants, restaurant_distances)

    print()
    print()
    print("Comandes seleccionades:")
    for restaurant_id, orders in orders_by_restaurant.items():
        restaurant_name = restaurants[restaurant_id]['nom']
        print(f"Restaurante: {restaurant_name}")
        for order in orders:
            print(f"    Comanda: {order['especialitat']}")

    for restaurant in restaurant_order:
        print(restaurant['nom'])

    plot_tsp_route(selected_restaurants, restaurant_order)


    
