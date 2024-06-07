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
    especialitat = restaurant['especialitat']
    restaurant['coordenades'] = tuple(map(float, restaurant['coordenades'].split(", ")))
    if especialitat == '-':
        restaurant['compromis'] = 0
    else:
        restaurant['compromis'] = specialities_dict[especialitat]['compromis']
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

def tsp2(locations: list, restaurant_distances: dict):
    start = locations[0]
    current = start
    visited = [start]
    unvisited = locations[1:]

    visited_orders = []

    total_distance = 0

    while unvisited:
        min_dist = float('inf')
        min_loc = None

        for loc in unvisited:
            if loc['especialitat'] in visited_orders:
                unvisited.remove(loc)
                continue

            dist = get_distance(restaurant_distances, current, loc)
            compromis = loc['compromis'] / 60
            print(dist)
            print(compromis)
            print("---")
            dist += compromis
            if dist < min_dist:
                min_dist = dist
                min_loc = loc


        if min_loc is None:
            continue        

        total_distance += min_dist

        visited_orders.append(min_loc['especialitat'])

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

def plot_tsp_route(route):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    x_coords = [restaurant['coordenades'][0] for restaurant in route]
    y_coords = [restaurant['coordenades'][1] for restaurant in route]
    plt.scatter(x_coords, y_coords, color='blue')


    for i, restaurant in enumerate(route):
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

    restaurant_order = tsp2(restaurants, restaurant_distances)
    orders_by_restaurant = select_orders_by_restaurant(restaurant_order, knapsack(orders))

    selected_restaurants = []
    new_order = []
    for restaurant_id in orders_by_restaurant.keys():
        selected_restaurants.append(restaurants[restaurant_id])
        new_order.append(restaurants[restaurant_id])

    for restaurant in selected_restaurants:
        print(restaurant['nom'])
        for order in orders_by_restaurant[restaurant['id']]:
            print(f"    Comanda: {order['especialitat']}")

    plot_tsp_route(restaurant_order)


    
