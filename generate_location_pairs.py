locations_by_zone = {
    "NORTH": ["Rohini", "Azadpur", "Model Town", "Kashmiri Gate", "Majnu ka Tila"],
    "SOUTH": ["Saket", "Hauz Khas", "Vasant Kunj", "Malviya Nagar", "Mehrauli"],
    "EAST": ["Laxmi Nagar", "Mayur Vihar", "Preet Vihar", "Patparganj", "New Ashok Nagar"],
    "WEST": ["Punjabi Bagh", "Janakpuri", "Rajouri Garden", "Tilak Nagar", "Paschim Vihar"],
    "CENTRAL": ["Connaught Place", "Karol Bagh", "Jor Bagh", "Khan Market", "Lajpat Nagar"],
    "NCR": ["Noida Sector 18", "Cyber Hub", "IGI Airport", "Ghaziabad", "Faridabad", "Gurgaon"]
}

# Flatten all locations into a single list
all_locations = [loc for zone in locations_by_zone.values() for loc in zone]

# Generate all ordered (pickup, drop) pairs excluding same-location pairs
LOCATION_PAIRS = [(pickup, drop) for pickup in all_locations for drop in all_locations if pickup != drop]

# Example: print first 10 pairs
for pair in LOCATION_PAIRS[:10]:
    print(pair)

# Total number of pairs
print(f"\nTotal pickup-drop pairs: {len(LOCATION_PAIRS)}")