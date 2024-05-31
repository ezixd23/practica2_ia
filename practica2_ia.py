import json
from itertools import permutations
from geopy.distance import geodesic

with open('/restaurants.json', 'r') as file:
    restaurants = json.load(file)

with open('/orders.json', 'r') as file:
    orders = json.load(file)

with open('/specialities.json', 'r') as file:
    specialities = json.load(file)



# Crear un diccionari per accedir ràpidament a les dades de les especialitats
specialities_dict = {s['especialitat']: s for s in specialities}

# Afegir les dades de compromís i pes a les comandes
for order in orders:
    especialitat = order['especialitat']
    order['compromis'] = specialities_dict[especialitat]['compromis']
    order['pes'] = specialities_dict[especialitat]['pes']

# Funció per calcular la distància entre dos punts
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

# Coordenades de la seu
hub_coordinates = (41.528154350078815, 2.4346229558256196)

for restaurant in restaurants:
    restaurant['coordenades'] = tuple(map(float, restaurant['coordenades'].split(", ")))

# Calcular totes les distàncies entre la seu i els restaurants, i entre restaurants
def calculate_all_distances(hub, locations):
    distances = {}
    for loc1 in locations:
        coord1 = loc1["coordenades"]
        distances[(hub, loc1["id"])] = calculate_distance(hub, coord1)
        for loc2 in locations:
            if loc1 != loc2:
                coord2 = loc2["coordenades"]
                distances[(loc1["id"], loc2["id"])] = calculate_distance(coord1, coord2)
    return distances

restaurant_distances = calculate_all_distances(hub_coordinates, restaurants)

# Algoritme TSP per determinar l'ordre de visita dels restaurants
def tsp(locations, start):
    n = len(locations)
    all_points = list(range(n))
    memo = {}

    def visit(visited, last):
        if visited == (1 << n) - 1:
            return restaurant_distances[(locations[last]["id"], start)]

        if (visited, last) in memo:
            return memo[(visited, last)]

        min_dist = float('inf')
        for point in all_points:
            if visited & (1 << point) == 0:
                dist = restaurant_distances[(locations[last]["id"], locations[point]["id"])] + visit(visited | (1 << point), point)
                min_dist = min(min_dist, dist)

        memo[(visited, last)] = min_dist
        return min_dist

    return visit(1, 0)

# Determinar l'ordre de visita dels restaurants
restaurant_order = tsp(restaurants, hub_coordinates)

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

# Seleccionar les comandes per cada restaurant
orders_by_restaurant = {}
for order in orders:
    for restaurant in restaurants:
        if order['especialitat'] == restaurant['especialitat']:
            if restaurant['id'] not in orders_by_restaurant:
                orders_by_restaurant[restaurant['id']] = []
            orders_by_restaurant[restaurant['id']].append(order)
            break

selected_orders_by_restaurant = {}
for restaurant_id, orders in orders_by_restaurant.items():
    selected_orders_by_restaurant[restaurant_id] = knapsack(orders, max_capacity)
