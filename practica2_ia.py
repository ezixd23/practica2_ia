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

# Funció per calcular la distància entre dos punts
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

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


# Definir la capacitat màxima de la motxilla
max_capacity = 10  # Exemple, pots ajustar-ho segons la capacitat real

# Funció per seleccionar les comandes segons el problema de la motxilla
def knapsack(orders, max_capacity):
    # Ordenar les comandes per temps de compromís (més curts primer)
    orders = sorted(orders, key=lambda x: x['compromis'])
    
    selected_orders = []
    total_weight = 0
    
    for order in orders:
        if total_weight + order['pes'] <= max_capacity:
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

if __name__ == "__main__":
    # Determinar l'ordre de visita dels restaurants
    restaurant_distances = calculate_all_distances(restaurants[0], restaurants)
    restaurant_order = tsp(restaurants, restaurant_distances)

    orders_by_restaurant = select_orders_by_restaurant(restaurants, orders)

    selected_orders_by_restaurant = {}
    for restaurant_id, orders in orders_by_restaurant.items():
        selected_orders_by_restaurant[restaurant_id] = knapsack(orders, max_capacity)

    print(selected_orders_by_restaurant)