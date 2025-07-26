import csv

# Delhi approximate bounding box
min_lat, max_lat = 28.40, 28.90
min_lng, max_lng = 76.85, 77.40

# Granularity: every 0.01 degrees ≈ ~1.1km
lat_steps = 51  # ~50 points
lng_steps = 56

lat_points = [min_lat + i * (max_lat - min_lat) / (lat_steps - 1) for i in range(lat_steps)]
lng_points = [min_lng + i * (max_lng - min_lng) / (lng_steps - 1) for i in range(lng_steps)]

locations = [(lat, lng) for lat in lat_points for lng in lng_points]

# Write to CSV for further use
with open('delhi_grid.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['lat', 'lng'])
    writer.writerows(locations)

print(f"Generated {len(locations)} Delhi locations")
