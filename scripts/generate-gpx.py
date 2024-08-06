import math
import requests
import random
import sys
import argparse
import os

def bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing between two points.
    """
    lat1, lat2 = map(math.radians, [lat1, lat2])
    diff_long = math.radians(lon2 - lon1)

    x = math.sin(diff_long) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diff_long))

    initial_bearing = math.atan2(x, y)
    
    # Normalize bearing to 0-360 degrees
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing

def offset_point_normal_to_path(lat, lon, bearing, distance):
    """
    Offset a geographic coordinate by a certain distance perpendicular to the path.
    
    Args:
    lat (float): Latitude of the point.
    lon (float): Longitude of the point.
    bearing (float): Bearing of the path.
    distance (float): Distance to offset in meters.
    
    Returns:
    tuple: New latitude and longitude.
    """
    # Earth's radius in meters
    R = 6371000

    # Convert bearing to radians and add 90 degrees to get normal direction
    theta = math.radians(bearing + 90)
    
    # Convert distance to radians
    d = distance / R

    # Calculate offset in radians
    d_lat = d * math.cos(theta)
    d_lon = d * math.sin(theta) / math.cos(math.radians(lat))

    # Calculate new coordinates
    new_lat = lat + math.degrees(d_lat)
    new_lon = lon + math.degrees(d_lon)
    
    return new_lat, new_lon

def route_exec(points, elevations, num_points, mean=0, stddev=10):
    """
    Generate a second set of points with random offsets, mimicking detours.

    Args:
    points (list): List of tuples (lat, lon) for original points.
    elevations (list): List of elevations corresponding to original points.
    num_points (int): Number of points.
    mean (float): Mean of the offset distance in meters.
    stddev (float): Standard deviation of the offset distance in meters.

    Returns:
    list: A new set of points with random offsets.
    list: New elevations for the offset points.
    """
    new_points = []
    
    # First point remains the same
    new_points.append(points[0])
    
    for i in range(1, num_points - 1):
        lat1, lon1 = points[i-1]
        lat2, lon2 = points[i]
        lat3, lon3 = points[i+1] if i + 1 < num_points else points[i]
        
        # Calculate the bearing from the previous point to the next point
        bear = bearing(lat1, lon1, lat3, lon3)
        
        # Generate a random offset distance
        offset_distance = random.gauss(mean, stddev)
        
        # Offset the current point normally to the path
        new_lat, new_lon = offset_point_normal_to_path(lat2, lon2, bear, offset_distance)
        new_points.append((new_lat, new_lon))
    
    # Last point remains the same
    new_points.append(points[-1])
    
    # Fetch new elevations for the new set of points
    new_elevations = []
    for i in range(0, len(new_points), 100):
        batch = new_points[i:i+100]
        lats = ",".join([f"{lat:.2f}" for lat, _ in batch])
        lons = ",".join([f"{lon:.2f}" for _, lon in batch])
        new_elevations.extend(get_elevations(lats, lons))
    
    return new_points, new_elevations

def get_elevations(latitudes: str, longitudes: str) -> list:
    """
    Get elevations for given pairs of latitude and longitude.

    Args:
    latitudes (str): Comma delimited string of latitudes, rounded to two decimal places.
    longitudes (str): Comma delimited string of longitudes, rounded to two decimal places.

    Returns:
    list: A list of elevations corresponding to the given latitude and longitude pairs.

    Example:
    latitudes = "52.52,48.85"
    longitudes = "13.41,2.35"
    elevations = get_elevations(latitudes, longitudes)
    print(elevations)  # Example output: [38.0, 46.0]
    """
    # Construct the URL for the API request
    url = f"https://api.open-meteo.com/v1/elevation?latitude={latitudes}&longitude={longitudes}"
    
    # Make the request to the API
    response = requests.get(url)
    
    # Raise an exception if the request was not successful
    response.raise_for_status()
    
    # Parse the JSON response
    data = response.json()
    
    # Extract the elevations from the response
    elevations = data.get('elevation', [])
    
    return elevations

def intermediate_point(lat1, lon1, lat2, lon2, f):
    """
    Calculate an intermediate point on a great circle path between two points on the Earth's surface.

    Args:
    lat1 (float): Latitude of the starting point in decimal degrees
    lon1 (float): Longitude of the starting point in decimal degrees
    lat2 (float): Latitude of the ending point in decimal degrees
    lon2 (float): Longitude of the ending point in decimal degrees
    f (float): A fraction between 0 and 1. 0 is close to the start, 1 is close to the end.

    Returns:
    tuple: A pair of floats (latitude, longitude) representing the intermediate point

    This function uses spherical trigonometry to compute a point on the great circle
    path between two points. The parameter 'f' determines how far along the path the
    intermediate point is located. For f=0, the result will be close to (lat1, lon1),
    and for f=1, it will be close to (lat2, lon2).

    The calculation assumes a spherical Earth model. The result is returned in degrees.
    """        
    phi1 = math.radians(lat1)
    lambda1 = math.radians(lon1)
    phi2 = math.radians(lat2)
    lambda2 = math.radians(lon2)
    
    # Compute spherical distance between the two points
    delta_phi = phi2 - phi1
    delta_lambda = lambda2 - lambda1
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    delta_sigma = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Compute the intermediate point
    A = math.sin((1 - f) * delta_sigma) / math.sin(delta_sigma)
    B = math.sin(f * delta_sigma) / math.sin(delta_sigma)
    
    x = A * math.cos(phi1) * math.cos(lambda1) + B * math.cos(phi2) * math.cos(lambda2)
    y = A * math.cos(phi1) * math.sin(lambda1) + B * math.cos(phi2) * math.sin(lambda2)
    z = A * math.sin(phi1) + B * math.sin(phi2)
    
    phi = math.atan2(z, math.sqrt(x**2 + y**2))
    lambda_val = math.atan2(y, x)
    
    return math.degrees(phi), math.degrees(lambda_val)

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)

    Args:
    lat1 (float): Latitude of the first point in decimal degrees
    lon1 (float): Longitude of the first point in decimal degrees
    lat2 (float): Latitude of the second point in decimal degrees
    lon2 (float): Longitude of the second point in decimal degrees

    Returns:
    float: Distance between the two points in meters

    This function uses the haversine formula to calculate the great-circle distance 
    between two points on a sphere given their longitudes and latitudes. It assumes 
    a spherical Earth with radius 6,371,000 meters.

    The variable 'c' in the return statement represents the central angle between 
    the two points in radians. When multiplied by the Earth's radius, it gives 
    the distance along the surface of the sphere.
    """       
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generate_gpx_data(start_coords, end_coords, interval=100):
    total_distance = haversine(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
    num_points = int(total_distance / interval) + 1

    # Generate all points
    points = [intermediate_point(start_coords[0], start_coords[1], end_coords[0], end_coords[1], i / (num_points - 1))
              for i in range(num_points)]

    # Fetch elevations in batches of 100
    elevations = []
    for i in range(0, len(points), 100):
        batch = points[i:i+100]
        lats = ",".join([f"{lat:.2f}" for lat, _ in batch])
        lons = ",".join([f"{lon:.2f}" for _, lon in batch])
        elevations.extend(get_elevations(lats, lons))

    return points, elevations, num_points

def write_gpx_file(points, elevations, num_points, filename='trail.gpx', creator="GeoWiz", name="GeoWiz-Synthetic", author_link="https://www.geowiz.com", author_text="GeoWiz", author_type="text/html"):
    
    # Create the 'output' directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the full file path
    file_path = os.path.join(output_dir, filename)

    with open(file_path, 'w') as file:
        file.write('<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n')
        file.write(f'<gpx version="1.1" creator="{creator}" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">\n')
        file.write('  <metadata>\n')
        file.write(f'    <name>{name}</name>\n')
        file.write('    <author>\n')
        file.write(f'      <link href="{author_link}">\n')
        file.write(f'        <text>{author_text}</text>\n')
        file.write(f'        <type>{author_type}</type>\n')
        file.write('      </link>\n')
        file.write('    </author>\n')
        file.write('  </metadata>\n')
        file.write('  <trk>\n')
        file.write(f'    <name>{name}</name>\n')
        file.write('    <trkseg>\n')

        for (lat, lon), ele in zip(points, elevations):
            file.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}">\n')
            file.write(f'        <ele>{ele:.1f}</ele>\n')
            file.write(f'        <time>2024-07-20T13:56:45.232Z</time>\n')
            file.write('      </trkpt>\n')

        file.write('    </trkseg>\n')
        file.write('  </trk>\n')
        file.write('</gpx>')

    print(f"GPX file '{filename}' has been generated with {num_points} points.")

def generate_gpx(start_coords, end_coords, interval=100, filename='trail.gpx'):
    points, elevations, num_points = generate_gpx_data(start_coords, end_coords, interval)
    write_gpx_file(points, elevations, num_points, filename)

# Example usage
# Start - Bamburgh Beach
# start = (55.6112176200343, -1.702550745082108)
# # End - Gretna
# end = (54.97818870154609, -3.001548002556341)
# # generate planned walk
# points, elevations, num_points = generate_gpx_data(start, end, interval=100)
# write_gpx_file(points, elevations, num_points, filename='planned_trail.gpx')
# # generate simulated walk
# new_points, new_elevations = route_exec(points, elevations, num_points, mean=0, stddev=100)
# write_gpx_file(new_points, new_elevations, num_points, filename='executed_trail.gpx')



def main():
    parser = argparse.ArgumentParser(description='Generate planned and executed GPX trails.')
    parser.add_argument('--start_lat', type=float, required=True, help='Starting latitude')
    parser.add_argument('--start_lon', type=float, required=True, help='Starting longitude')
    parser.add_argument('--end_lat', type=float, required=True, help='Ending latitude')
    parser.add_argument('--end_lon', type=float, required=True, help='Ending longitude')
    parser.add_argument('--interval', type=int, default=100, help='Interval between points in meters (default: 100)')
    parser.add_argument('--mean', type=float, default=0, help='Mean deviation for simulated walk (default: 0)')
    parser.add_argument('--stddev', type=float, default=100, help='Standard deviation for simulated walk (default: 100)')
    parser.add_argument('--planned_filename', type=str, default='planned_trail.gpx', help='Filename for planned trail (default: planned_trail.gpx)')
    parser.add_argument('--executed_filename', type=str, default='executed_trail.gpx', help='Filename for executed trail (default: executed_trail.gpx)')
    parser.add_argument('--creator', type=str, default='GeoWiz', help='Creator of the GPX file (default: GeoWiz)')
    parser.add_argument('--name', type=str, default='GeoWiz-Synthetic', help='Name of the route (default: GeoWiz-Synthetic)')
    parser.add_argument('--author_link', type=str, default='https://github.com/dsikar', help='Link for the author (default: https://www.geowiz.com)')
    parser.add_argument('--author_text', type=str, default='DanielSikar', help='Text for the author (default: GeoWiz)')
    parser.add_argument('--author_type', type=str, default='text/html', help='Type of the author link (default: text/html)')

    args = parser.parse_args()

    start = (args.start_lat, args.start_lon)
    end = (args.end_lat, args.end_lon)

    try:
        # Generate planned walk
        points, elevations, num_points = generate_gpx_data(start, end, interval=args.interval)
        write_gpx_file(points, elevations, num_points, 
                       filename=args.planned_filename,
                       creator=args.creator,
                       name=f"{args.name} - Planned",
                       author_link=args.author_link,
                       author_text=args.author_text,
                       author_type=args.author_type)

        # Generate simulated walk
        new_points, new_elevations = route_exec(points, elevations, num_points, mean=args.mean, stddev=args.stddev)
        write_gpx_file(new_points, new_elevations, num_points, 
                       filename=args.executed_filename,
                       creator=args.creator,
                       name=f"{args.name} - Executed",
                       author_link=args.author_link,
                       author_text=args.author_text,
                       author_type=args.author_type)

        print("GPX files generated successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Example call
    
# python generate-gpx.py \
# --start_lat 55.6112176200343 \
# --start_lon -1.702550745082108 \
# --end_lat 54.97818870154609 \
# --end_lon -3.001548002556341 \
# --interval 100 \
# --mean 0 \
# --stddev 25 \
# --planned_filename planned_trail.gpx \
# --executed_filename executed_trail_0_mean_25_stdev.gpx \
# --creator DanielSikar \
# --name "GeoWizzardSynthetic_0_mean_50_stdev" \
# --author_link https://www.github.com/dsikar \
# --author_text MyApp \
# --author_type text/html    