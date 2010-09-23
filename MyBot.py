#!/usr/bin/env python

from __future__ import division

from sys import stdin

"""
Strategies to implement:

* Using the knowledge about fleets, predict the game state in the future
* Create a list of high priority planets for me and for the enemy
* expansion phase when the enemy does not have that many planets (i.e., at beginning) or when the enemy does not have much strength
* evacuate planet if it is doomed
* Calculate the growth rate for me for every planet (i.e., how many ships it is producing for me).  Enemy planets count as negative growth rate.  Neutral planets count as 0 growth rate.
* Calculate the potential growth rate and cost of taking over any planet
* Calculate the risk of any of my planets, based on the fleets coming in.  Determine if I should "save" the planet or evacuate the planet.
* Move headquarters if needed (maybe at every stage, any planet with more than X ships could move 3/4 of them to another planet to try to take over it?)


Philosophies:

* Getting a planet to produce is more important than battling enemy ships.
* Prevent the enemy from becoming too strong

"""


from PlanetWars import PlanetWars, log, predict_state

def do_turn(pw):
  pw_future=predict_state(pw,MAX_TURNS)
  if pw.my_production >= 1.5*pw.enemy_production:
    num_fleets=1
  else:
    num_fleets=5

  if len(pw.my_fleets) >= num_fleets:
    return
  log('finding source')
  # (2) Find my strongest planet.
  source = -1
  source_score = -999999.0
  source_num_ships = 0
  for p in pw.my_planets:
    score = p.num_ships/(1+p.growth_rate)
    if score > source_score:
      source_score = score
      source = p.id
      s=p
      source_num_ships = p.num_ships

  log('finding dest')
  # (3) Find the weakest enemy or neutral planet.
  dest = -1
  dest_score = -999999.0
  not_my_planets=set(pw.planets)-pw.my_planets
  for p in not_my_planets:
    score = (1+p.growth_rate) / (1+p.num_ships)/(1+pw.distance(s,p))
    if score > dest_score:
      dest_score = score
      dest = p.id
  
  log('sending')
  # (4) Send half the ships from my strongest planet to the weakest
  # planet that I do not own.
  if source >= 0 and dest >= 0:
    num_ships = source_num_ships / 2
    pw.order(source, dest, num_ships)


MAX_TURNS=None
from itertools import product
def main():
  global MAX_TURNS
  map_data = ''
  log('*'*30)
  turn=0
  while True:
    current_line = stdin.readline()
    if len(current_line) >= 2 and current_line.startswith("go"):
      log('Turn %d '%turn+'='*30)
      pw = PlanetWars()
      pw.parse_game_state(map_data)
      if MAX_TURNS is None:
        for p,q in product(pw.planets[:3],repeat=2):
          d=pw.distance(p,q)
          if d>MAX_TURNS:
            MAX_TURNS=d
        log("predicting %s turns in the future"%MAX_TURNS)
      do_turn(pw)
      pw.finish()
      map_data = ''
      turn+=1
    else:
      map_data += current_line

if __name__ == '__main__':
  try:
    import psyco
    psyco.full()
  except ImportError:
    pass
  try:
    main()
  except KeyboardInterrupt:
    print 'ctrl-c, leaving ...'
