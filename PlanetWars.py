#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout


class Fleet:
  def __init__(self, owner, num_ships, source_planet, destination_planet, \
   total_trip_length, turns_remaining):
    self.owner = owner
    self.num_ships = num_ships
    self.source = source_planet
    self.destination = destination_planet
    self.trip_len = total_trip_length
    self.turns_left = turns_remaining


class Planet:
  def __init__(self, planet_id, owner, num_ships, growth_rate, x, y):
    self.id = planet_id
    self.owner = owner
    self.num_ships = num_ships
    self.growth_rate = growth_rate
    self.x = x
    self.y = y

  def __str__(self):
    return "Planet %d"%self.id

  def __repr__(self):
    return str(self)

class PlanetWars:
  def __init__(self, gameState):
    self.planets = []
    self.fleets = []
    self.parse_game_state(gameState)

  @property
  def my_planets(self):
    return set([p for p in self.planets if p.owner==1])

  @property
  def neutral_planets(self):
    return set([p for p in self.planets if p.owner==0])

  @property
  def enemy_planets(self):
    return set([p for p in self.planets if p.owner>1])

  @property
  def my_production(self):
    return sum(p.growth_rate for p in self.my_planets)

  @property
  def enemy_production(self):
    return sum(p.growth_rate for p in self.enemy_planets)

  @property
  def my_fleets(self):
    return set([f for f in self.fleets if f.owner==1])

  @property
  def enemy_fleets(self):
    return set([f for f in self.fleets if f.owner>1])


  def distance(self, source, destination):
    #log('distance between %s %s'%(source,destination))
    if not isinstance(source, Planet):
      source = self.planets[source]
    if not isinstance(destination, Planet):
      destination = self.planets[destination]
    dx = source.x - destination.x
    dy = source.y - destination.y
    distance= int(ceil(sqrt(dx * dx + dy * dy)))
    #log(distance)
    return distance

  def order(self, source_planet, destination_planet, num_ships):
    stdout.write("%d %d %d\n" % \
     (source_planet, destination_planet, num_ships))
    stdout.flush()

  def is_alive(self, player_id):
    if any(p.owner==player_id for p in self.planets):
      return True
    if any(f.owner==player_id for f in self.fleets):
      return True
    return False

  def parse_game_state(self, s):
    self.planets = []
    self.fleets = []
    lines = s.split("\n")
    planet_id = 0

    for line in lines:
      line = line.split("#")[0] # remove comments
      tokens = line.split(" ")
      if len(tokens) == 1:
        continue
      if tokens[0] == "P":
        if len(tokens) != 6:
          return 0
        p = Planet(planet_id, # The ID of this planet
                   int(tokens[3]), # Owner
                   int(tokens[4]), # Num ships
                   int(tokens[5]), # Growth rate
                   float(tokens[1]), # X
                   float(tokens[2])) # Y
        planet_id += 1
        self.planets.append(p)
      elif tokens[0] == "F":
        if len(tokens) != 7:
          return 0
        f = Fleet(int(tokens[1]), # Owner
                  int(tokens[2]), # Num ships
                  int(tokens[3]), # Source
                  int(tokens[4]), # Destination
                  int(tokens[5]), # Total trip length
                  int(tokens[6])) # Turns remaining
        self.fleets.append(f)
      else:
        return 0
    return 1

  def finish(self):
    stdout.write("go\n")
    stdout.flush()

  def __str__(self):
    s = ''
    for p in self.planets:
      s += "P %f %f %d %d %d\n" % \
       (p.x, p.y, p.owner, p.num_ships, p.growth_rate)
    for f in self._fleets:
      s += "F %d %d %d %d %d %d\n" % \
       (f.owner, f.num_ships, f.source, f.destination, \
        f.trip_len, f.turns_left)
    return s
