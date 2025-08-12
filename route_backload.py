from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import matplotlib.pyplot as plt

print("Running route optimization with backload logic...")

# Sample data: distance matrix and demands for 13 locations (including depot at 0)
distance_matrix = [
    [0, 7, 9, 13, 15, 6, 7, 8, 12, 14, 18, 20, 25],
    [7, 0, 10, 14, 18, 5, 8, 9, 11, 15, 19, 21, 22],
    [9, 10, 0, 8, 13, 6, 9, 10, 7, 11, 15, 18, 20],
    [13, 14, 8, 0, 6, 9, 13, 14, 10, 7, 12, 16, 18],
    [15, 18, 13, 6, 0, 11, 15, 17, 14, 9, 8, 10, 12],
    [6, 5, 6, 9, 11, 0, 4, 5, 7, 10, 13, 15, 18],
    [7, 8, 9, 13, 15, 4, 0, 3, 6, 8, 12, 14, 16],
    [8, 9, 10, 14, 17, 5, 3, 0, 5, 7, 10, 12, 15],
    [12, 11, 7, 10, 14, 7, 6, 5, 0, 5, 8, 11, 14],
    [14, 15, 11, 7, 9, 10, 8, 7, 5, 0, 5, 8, 12],
    [18, 19, 15, 12, 8, 13, 12, 10, 8, 5, 0, 5, 9],
    [20, 21, 18, 16, 10, 15, 14, 12, 11, 8, 5, 0, 6],
    [25, 22, 20, 18, 12, 18, 16, 15, 14, 12, 9, 6, 0],
]

demands = [0, 5, 10, 12, 8, 4, 7, 6, 9, 5, 7, 4, 3]

vehicle_capacities = [30, 30, 30]
num_vehicles = len(vehicle_capacities)
depot = 0

# Coordinates for visualization (x, y) for each node
locations = {
    0: (0, 0),
    1: (2, 3),
    2: (5, 2),
    3: (6, 6),
    4: (8, 3),
    5: (1, 7),
    6: (3, 8),
    7: (7, 1),
    8: (9, 6),
    9: (4, 5),
    10: (8, 8),
    11: (6, 1),
    12: (7, 7),
}

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance_matrix
    data['demands'] = demands
    data['vehicle_capacities'] = vehicle_capacities
    data['num_vehicles'] = num_vehicles
    data['depot'] = depot
    return data

def plot_routes(routes):
    colors = ['r', 'g', 'b', 'c', 'm', 'y']
    plt.figure(figsize=(10, 8))
    
    for i, route in enumerate(routes):
        x = [locations[node][0] for node in route]
        y = [locations[node][1] for node in route]
        plt.plot(x, y, marker='o', color=colors[i % len(colors)], label=f'Vehicle {i+1} Route')
        for j, node in enumerate(route):
            plt.text(locations[node][0], locations[node][1], str(node), fontsize=12, fontweight='bold')

    plt.scatter(locations[0][0], locations[0][1], c='k', marker='s', s=100, label='Depot')
    plt.title("Optimized Routes Visualization")
    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    data = create_data_model()

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback (distance callback)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity'
    )

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = 10

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print("Solved!")
        routes = []
        total_distance = 0
        total_load = 0
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route_distance = 0
            route_load = 0
            route = [data['depot']]
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data['demands'][node_index]
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                if not routing.IsEnd(index):
                    route.append(manager.IndexToNode(index))
            route.append(data['depot'])

            print(f"Route for vehicle {vehicle_id + 1}:")
            print(" -> ".join(str(n) for n in route), f"(Load: {route_load} tons)")
            print(f"Distance of the route: {route_distance} units")
            print(f"Load of the route: {route_load} tons\n")
            total_distance += route_distance
            total_load += route_load
            routes.append(route)
        
        print(f"Total distance of all routes: {total_distance} units")
        print(f"Total load delivered across all routes: {total_load} tons")

        # Plot routes visually
        plot_routes(routes)
    else:
        print("No solution found!")

if __name__ == '__main__':
    main()
