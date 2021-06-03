# py_pslist: find out which processes are using the system , notably top-users

############
#
# comments, design, struture, layout here...
# 1. use some debug-stuff from other py sources..
# 2. user psutil library
# 2a. verify the data .. e.g. processes + their data, verify with ps-ef
# 3. examine and list the contents in loop
# 4. store in DB or file (need datmodel.. based on timestamp + pid...?
#
# todo:
# - list in order of cpu, highest at bottom?
# - show parent-pid or hierarchy (for easy kill)
# - add arg1: interval, arg2: nr of times (0 or empty = endless)
#
# loop: while true ; do python3 py_pslist.py ; sleep 3 ; done  

############

# import some...

import os
import sys
import glob
import math
import psutil
import time as tim
from datetime import datetime, date, time, timezone
import cx_Oracle

# import the prefix function, did not work becasue __file__ is needed
# from py_prfx import *
# from py_inspectobj import *

# constants, like data-directory, masks.

# take the filename, to use as prefix for print- and trace-stmnts
pyfile = os.path.basename(__file__)

# the file to read, for the moment..
# s_json_fname = str ( "testloc.json" )
s_json_fname = str ( "locations.json" )


# functions:
# f_prfx : from other file
# f_ins_trip, create trip-record and return trip_id
# f_ins_gps_file_rec, create file_record and return file_id
# f_runk_do_gpx,  process gpx-file, return nr-points added


# ------------------------------------------------
def f_prfx():
  # set a prefix for debug-output, sourcefile + timestamp
  s_timessff = str ( datetime.now() )[11:23]
  s_prefix = pyfile + ' ' + s_timessff + ': '
  # print ( prfx, ' in function f_prfx: ' , s_prefix )
  return str ( s_prefix )
# end of f_prfx, set sourcefile and timestamp


# inspect a python object:
# show type, dir, length, rep, and more..
# ------------------------------------------------
def f_inspect_obj( s_objname, o_obj ):

  print ( f_prfx(), "-------- Object :", s_objname, "--------" )

  print ( f_prfx(), "o_obj -[", o_obj, "]-" )
  print ( f_prfx(), "o_obj type  : ",  type (o_obj ) )
  print ( f_prfx(), "o_obj length: ",  len (o_obj ) )
  print ( f_prfx(), "o_obj dir   : ",  dir (o_obj ) )
  print ( " " )
  hit_enter = input ( f_prfx() + "meta data from " + s_objname + "...., hit enter.." )

  print ( "--- repr --->" )
  print ( f_prfx(), "o_obj repr  : ",  repr ( o_obj ) )
  print ( "<--- repr ---  " )

  print ( f_prfx(), " ------ inspected o_obj ", s_objname, " ---------- " )
  hit_enter = input ( f_prfx() + "about to go back...., hit enter.." )

# end of f_inspect_obj, show properties of an object


print ( f_prfx() ) 
print ( f_prfx(), " -------- Starting Main -------- " )
print ( f_prfx() ) 

# print ( f_prfx(), " ------ start opening and reding psutil ------ " )


# ps_temps = psutil.sensors_temperatures()
ps_cpu_tim = psutil.cpu_times() 
# print ( f_prfx(), "CPU times: ", ps_cpu_tim )


ps_cpu_phys = psutil.cpu_count(logical=False)
ps_cpu_log  = psutil.cpu_count(logical=True)
# print ( f_prfx(), "CPU count, logical and phys", ps_cpu_log, ps_cpu_phys )

# print ( f_prfx(), "cpu freq " , psutil.cpu_freq(percpu=True) )

# print ( f_prfx(), "virtual mem ", psutil.virtual_memory() )

# print ( f_prfx(), "temp: ", psutil.sensors_battery() )


# hit_enter = input ( f_prfx() + "now measring cpu 3sec " + "...., hit enter.." )

for proc in psutil.process_iter( ['pid', 'name', 'username', 'cpu_percent'] ):
  # print( f_prfx(), " proc info: ", proc.info)
  # f_inspect_obj( 'proc_info', proc.info )
  proc_cpu_perc = proc.info.get('cpu_percent') 
  proc_pid      = proc.info.get('pid') 
  proc_name      = proc.info.get('name') 
  # print ( f_prfx(), " pid + cpu percent: ", proc_pid, proc_cpu_perc, proc_name )
  
# initialized counters and properties ..

tim.sleep ( 5) 

perc_total = 0.0

# 2nd call.. to have meaningful values
for proc in psutil.process_iter( ['pid', 'name', 'username', 'cpu_percent'] ):
  # print( f_prfx(), " proc info: ", proc.info)
  # f_inspect_obj( 'proc_info', proc.info )
  proc_cpu_perc = proc.info.get('cpu_percent') 
  proc_pid      = proc.info.get('pid') 
  proc_name      = proc.info.get('name') 

  if not isinstance(proc_cpu_perc, float):
    f_perc = 0.0
  else:
    f_perc = float ( proc_cpu_perc ) 
    perc_total = perc_total + f_perc
  
  if f_perc > 1.0 :
    print ( f_prfx(), " pid + cpu percent: ", proc_pid, f_perc, proc_name )
  
# 2nd loop, printed values above threshold

print ( f_prfx() )
print ( f_prfx(), " Total cpu-perc", perc_total )
print ( f_prfx() )
print ( f_prfx(), " -------- End -------- " )



