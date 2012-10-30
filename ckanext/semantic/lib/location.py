import math


earth_radius = 6378.0


def distance(latitude1, longitude1, latitude2, longitude2):
    latitude_haversine = haversine(latitude1 - latitude2)
    longitude_haversine = haversine(longitude1 - longitude2)
    
    s = latitude_haversine + math.cos(latitude1) * math.cos(latitude2) * longitude_haversine
    distance = 2 * earth_radius * math.asin(min(1.0, math.sqrt(s)))

    return distance


def haversine(x):
    return (1 - math.cos(x)) / 2

