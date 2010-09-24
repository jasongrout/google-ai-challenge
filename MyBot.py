#!/usr/bin/env python

from __future__ import division

from sys import stdin
from copy import copy
from math import ceil
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
from PlanetWars import PlanetWars, log, predict_state, Planet, Fleet, planet_distance_list

def do_turn(pw):
  log('planets: %s'%[(p.id, p.num_ships) for p in pw.my_planets])
  
  pw.new_fleets=set()
  pw_future=predict_state(pw,MAX_TURNS)

  # Give the planets some metadata
  for p in pw.planets:
    p.future=[i.planets[p.id].num_ships if i.planets[p.id].owner==1 \
                else -i.planets[p.id].num_ships for i in pw_future]
    p.close=planet_distance_list(pw, p.id)
    p.my_close=[i for i in p.close if i in pw.my_planet_ids]

  if pw.my_production >= 1.5*pw.enemy_production:
    num_fleets=2
  else:
    num_fleets=5

  if len(pw.my_fleets) >= num_fleets:
    return
  if len(pw.my_planets)==0:
    return

  target_planets=set(pw.planets)-pw.my_planets
  #target_planets-=set(pw.planets[f.destination] for f in pw.my_fleets)

  # get the top targets
  dest_score=lambda p: float(p.growth_rate)/(1+p.num_ships)/(1+min([pw.distance(i,p) for i in pw.my_planets]))
  target=sorted(target_planets, key=dest_score)[-2:]

  # Now how can I conquer these planets?
  for p in reversed(target):
    # select 5 closest planets - what can they give up?
    donors=[pw.planets[i] for i in p.my_close[:2]]
    attack_fleets=[]
    for q in donors:
      if q.future[5]>q.num_ships:
        # if we're growing on this planet, donate something
        ships=int(q.future[0]*0.5)
        if ships==0:
          continue
        attack_fleets.append((q,ships))
    if sum(i[1] for i in attack_fleets)>1.2*p.future[5]:
      for q, ships in attack_fleets:
        pw.order(q,p, ships)
        pw.new_fleets.add(Fleet(1, ships, q.id, p.id, 
                                pw.distance(p,q), pw.distance(p,q)))
        for i in range(len(q.future)):
          q.future[i]-=ships
        #q.num_ships-=ships

#   # identify my planets will have a surplus after 5 turns
#   surplus=set([pw.planets[p] for p in pw.my_planet_ids & pw_future[5].my_planet_ids])

#   if len(surplus)>0:
#     surpluskey=lambda p: float(p.num_ships)/( (p.future[5]-p.num_ships) if p.future[5]!=p.num_ships else 0.1)
#     surplus=sorted(surplus, key=surpluskey)
#     # (3) Find the weakest enemy or neutral planet, as long as I'm not
#     # already sending a fleet there.
#     if len(dest)>0:
#       #log('sending')
#       # (4) Send half the ships from my strongest planet to the weakest
#       # planet that I do not own.
#       for s in surplus[-2:]:
# #        ships_to_spare=ceil(min(0.9*s.num_ships,
# #                           (pw_future[5].planets[s.id].num_ships-s.num_ships)*3))
#         ships_to_spare=0.5*s.num_ships
#         if ships_to_spare>5:
#           d=min(dest, key=lambda p: pw.distance(p,s))
#           pw.order(s.id, d.id, ships_to_spare)
#           log('new fleet: %d %d: %d'%(s.id, d.id, ships_to_spare))
#           pw.new_fleets.add(Fleet(1, ships_to_spare, s.id, d.id, 
#                                   pw.distance(d,s), pw.distance(d,s)))

  my_planets=copy(pw.my_planets)
  evacuate=set()
  # if any of my planets is dying on the next turn, evacuate
  for p in my_planets:
    new_owner=pw_future[1].planets[p.id].owner
    if new_owner!=1:
      evacuate.add(p)
  my_planets-=evacuate
  if len(my_planets)==0:
    my_planets=set([pw.planets[0]])
  for p in evacuate:
    p.num_ships -= sum(f.num_ships for f in pw.new_fleets if f.source==p.id)
    if p.num_ships>0:
      dest=min(my_planets, key=lambda x: pw.distance(p,x))
      log('evacuating %d to %d'%(p.id,dest.id))
      pw.order(p.id, dest.id, p.num_ships)
      
MAX_TURNS=None
#from itertools import product
# needed because they only support python 2.5!
def product(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)

def main():
  global MAX_TURNS
  map_data = ''
  log('*'*30)
  turn=0
  while True:
    current_line = stdin.readline()
    if len(current_line) >= 2 and current_line.startswith("go"):
      log('Turn %d '%turn+'='*30+'Turn %d'%turn)
      pw = PlanetWars()
      pw.parse_game_state(map_data)
      if MAX_TURNS is None:
        for p,q in product(pw.planets,repeat=2):
          d=pw.distance(p,q)
          if d>MAX_TURNS:
            MAX_TURNS=d
      if MAX_TURNS>10:
        MAX_TURNS=10
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
