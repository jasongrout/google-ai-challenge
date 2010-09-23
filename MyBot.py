#!/usr/bin/env python

from __future__ import division

from sys import stdin

"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own. Check out the tutorials and articles on the contest website at
// http://www.ai-contest.com/resources.
"""

from PlanetWars import PlanetWars

def do_turn(pw):
  if pw.my_production >= pw.enemy_production:
    num_fleets=1
  else:
    num_fleets=3

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
    log('d %s %s'%(s,p))
    d=pw.distance(s, p)
    log('d %s'%d)
    log(p.growth_rate)
    log(p.num_ships)
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


def log(s):
  return False
#  with open('test','a') as f:
#    f.write(str(s)+'\n')


def main():
  map_data = ''
  log('finished')
  i=0
  while True:
    current_line = stdin.readline()
    if len(current_line) >= 2 and current_line.startswith("go"):
      i+=1
      log(i)
      pw = PlanetWars(map_data)
      log(i)
      do_turn(pw)
      log(i)
      pw.finish()
      log(i)
      map_data = ''
    else:
      map_data += current_line
  log('finished')
  log(map_data)

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
