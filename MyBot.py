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
  log('planets: %s'%[p.num_ships for p in pw.my_planets])
  log('in air: %s'%sum(f.num_ships for f in pw.my_fleets))

  pw.new_fleets=set()
  pw_future=predict_state(pw,MAX_TURNS)
  enemy_fleets=sorted(pw.enemy_fleets,key=lambda x: x.num_ships)
  if len(enemy_fleets)>0:
    mode_enemy_fleet=enemy_fleets[len(enemy_fleets)//2].num_ships
  else:
    mode_enemy_fleet=1

  # Give the planets some metadata
  for p in pw.planets:
    p.future=[i.planets[p.id].num_ships if i.planets[p.id].owner==1 \
                else -i.planets[p.id].num_ships for i in pw_future]
    p.close=planet_distance_list(pw, p.id)
    p.my_close=[i for i in p.close if i in pw.my_planet_ids]
    p.not_my_close=[i for i in p.close if i not in pw.my_planet_ids]

  if pw.my_production >= 3*pw.enemy_production:
    num_fleets=5
  else:
    num_fleets=30

  if len(pw.my_fleets) >= num_fleets:
    return
  if len(pw.my_planets)==0 or len(pw.not_my_planets)==0:
    return

  for p in pw.my_planets:
    #what is closest non-conquered planet?
    if len(pw.my_fleets)>=num_fleets:
      return
    if p.num_ships>0:
      if mode_enemy_fleet<20:
        ships=int(p.num_ships-mode_enemy_fleet*4)
      else:
        ships=int(p.num_ships//2)
      if ships<1:
        continue
      def dest_score(t):
        d=pw.distance(t,p)
        fut=min(d,MAX_TURNS-1)
        t_ships=-t.future[fut]+3
        if t_ships==0:
          t_ships=1
        return float(t.growth_rate**2+t.owner)/(t_ships)/(1+d**2)
      #dest_score=lambda x: float(x.growth_rate**2)/(1+x.num_ships)/(1+pw.distance(x,p)**4)
      target=sorted(pw.planets, key=dest_score,reverse=True)
      #log([(i, pw.distance(i,p), dest_score(i)) for i in target])
      for t in target:
        if ships==0:
          break
        if t.id==p.id:
          break
        d=pw.distance(t,p)
        fut=min(d,MAX_TURNS-1)
        t_ships=-t.future[fut]+3
        if ships<t_ships*0.05:
          continue
        else:
          t_ships=min(ships,t_ships)
        if t_ships>0:
          pw.order(p,t, t_ships)
          num_fleets-=1
          for i in range(d,MAX_TURNS):
            t.future[i]-=t_ships
          for i in range(1,MAX_TURNS):
            p.future[i]-=t_ships
          ships-=t_ships
          p.num_ships-=t_ships

  my_planets=copy(pw.my_planets)
  evacuate=set()
  # if any of my planets is dying on the next turn, evacuate
  for p in my_planets:
    if p.future[1]<0:
      evacuate.add(p)
  my_planets-=evacuate
  if len(my_planets)==0:
    my_planets=set([pw.planets[0]])
  for p in evacuate:
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
      #if MAX_TURNS>10:
      #  MAX_TURNS=10
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
