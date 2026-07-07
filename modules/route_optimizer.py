import networkx as nx
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def optimize_routes(bins_data, start_loc=(6.9150, 79.8620)):
    """
    Finds an optimized route for collecting full bins.
    Uses NetworkX TSP approximation.
    """
    # Filter bins that need collection (e.g. >= 80%)
    full_bins = [b for b in bins_data if b.get('fill_level', 0) >= 80]
    
    if not full_bins:
        return ["No full bins to collect"], [], None
        
    G = nx.Graph()
    
    # Add depot
    G.add_node('Depot', pos=start_loc)
    
    # Add full bins as nodes
    for b in full_bins:
        G.add_node(b['location_name'], pos=(b['latitude'], b['longitude']))
        
    # Build complete graph with distances as weights
    nodes = list(G.nodes(data=True))
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            n1, d1 = nodes[i]
            n2, d2 = nodes[j]
            dist = calculate_distance(d1['pos'][0], d1['pos'][1], d2['pos'][0], d2['pos'][1])
            G.add_edge(n1, n2, weight=dist)
            
    # TSP optimization using Simulated Annealing for potentially better results
    tsp_path = nx.approximation.simulated_annealing_tsp(G, "greedy", max_iterations=5000)
    
    # Extract coordinates for mapping
    coords = [G.nodes[node]['pos'] for node in tsp_path]
    
    # Calculate total distance
    total_dist_degrees = 0
    for i in range(len(tsp_path) - 1):
        n1 = tsp_path[i]
        n2 = tsp_path[i+1]
        total_dist_degrees += G[n1][n2]['weight']
        
    total_dist_km = total_dist_degrees * 111.0 # rough conversion to km
    
    # Traffic & Vehicle Type Logic for Colombo
    has_narrow_roads = any(node == 'Pettah Market' for node in tsp_path)
    vehicle_type = "Small Compactor" if has_narrow_roads else "Large Truck"
    
    # Apply traffic multiplier and vehicle specific parameters
    # Colombo traffic is heavy, so we adjust speed and mileage
    if has_narrow_roads:
        traffic_multiplier = 1.5 # Pettah has heavy traffic
        avg_speed = 15.0 # km/h in congestion
        mileage = 8.0 # Small compactor mileage
    else:
        traffic_multiplier = 1.2 # Regular Colombo traffic
        avg_speed = 25.0
        mileage = 6.0 # Large truck mileage
        
    total_dist_km = total_dist_km * traffic_multiplier
    
    # Import budget calculator
    from modules.budget_calculator import calculate_route_cost
    
    # Assuming config is not passed, we use the defaults in calculate_route_cost but override speed/mileage
    cost_metrics = calculate_route_cost(total_dist_km, avg_speed=avg_speed, mileage=mileage)
    cost_metrics['distance_km'] = round(total_dist_km, 2)
    cost_metrics['vehicle_type'] = vehicle_type
    
    return tsp_path, coords, cost_metrics
