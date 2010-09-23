#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout

from sys import stderr

def log_file(s):
  s=str(s)+'\n'
  f=open('test','a')
  f.write(s)
  f.close()
  stderr.write(s)

def log_dummy(s):
  pass

def log_stderr(s):
  print >> stderr, s

log=log_file
log=log_dummy
log=log_stderr


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

from copy import deepcopy
from collections import defaultdict

def split(lst, key):
  ret=defaultdict(list)
  for i in lst:
    ret[key(i)].append(i)
  return ret

def predict_state(pw, turns):
  """
  This function returns a list of ``turns`` PlanetWars objects that predict the state for ``turns`` turns in the future, based on current planet growth rates and fleets. The first element (turn 0) is the passed in PlanetWars object.
  """
  state=[pw]
  
  # calculate next state
  for turn in range(1,turns):
    #log('predicting turn %d'%turn)
    state.append(deepcopy(state[-1]))
    pw=state[-1]
    #log('  new state created')
    # make fleets depart -- nothing to do
    # advance fleets
    #log('  advancing %s fleets'%len(pw.fleets))
    for f in pw.fleets:
      f.turns_left-=1

    # grow planet populations
    #log('  growing %s planets'%len(pw.planets))
    for p in pw.planets:
      if p.owner>0:
        p.num_ships+=p.growth_rate

    # update planets according to arriving fleets
    fleets_arriving = split([f for f in pw.fleets if f.turns_left==0], 
                            key=lambda f: f.destination)
    for p_id,fleets in fleets_arriving.items():
      p=pw.planets[p_id]
      # combine fleets with the same owner into a single force
      # forces key=player id, value=number of ships
      forces=defaultdict(int)
      forces[p.owner]+=p.num_ships
      for f in fleets:
        forces[f.owner]+=f.num_ships
      force_list=sorted(forces.items(), key=lambda x: x[1])
      max_force_player, max_force_ships=force_list[-1]
      if len(force_list)>1:
        max_force_ships-=force_list[-2][1]
      if max_force_ships==0:
        p.num_ships=0
        # owner does not change
      else:
        p.owner=max_force_player
        p.num_ships=max_force_ships
    # delete old fleets
    pw.fleets=[f for f in pw.fleets if f.turns_left>1]
  return  state

class PlanetWars:
  """
  Represents the game state.
  """

  def __init__(self):
    self.planets = []
    self.fleets = []
    self._distance_cache=dict()

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
    if not isinstance(source, Planet):
      source = self.planets[source]
    if not isinstance(destination, Planet):
      destination = self.planets[destination]
    if (source.id, destination.id) in self._distance_cache:
      return self._distance_cache[(source.id, destination.id)]

    dx = source.x - destination.x
    dy = source.y - destination.y
    distance= int(ceil(sqrt(dx * dx + dy * dy)))

    self._distance_cache[(source.id, destination.id)]=distance
    self._distance_cache[(destination.id, source.id)]=distance
    #log('distance between %s %s: %s'%(source,destination, distance))
    return distance

  def order(self, source_planet, destination_planet, num_ships):
    log("New fleet: %s %s, ships=%s"%(source_planet, destination_planet, num_ships))
    s="%d %d %d\n" % \
     (source_planet, destination_planet, num_ships)
    stdout.write(s)
    log(s)
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
    log('finished turn')

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
