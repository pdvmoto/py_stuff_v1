# py_net:  find which net-comms are taking place, port, program

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
# - list in order of bytes recv/send, highest at bottom?
# - show parent-pid or hierarchy (for easy kill)
# - add arg1: interval, arg2: nr of times (0 or empty = endless)
#
# loop: while true ; do python3 py_net.py ; sleep 3 ; done  

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

# constants, like data-directory, masks.

# take the filename, to use as prefix for print- and trace-stmnts
pyfile = os.path.basename(__file__)

# functions:
# f_prfx : from other file
# f_inspect_obj( s_objname, o_obj ): what is in an object


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
# ps_cpu_tim = psutil.cpu_times() 
# print ( f_prfx(), "CPU times: ", ps_cpu_tim )


ps_cpu_phys = psutil.cpu_count(logical=False)
ps_cpu_log  = psutil.cpu_count(logical=True)
print ( f_prfx(), "CPU count, logical and phys", ps_cpu_log, ps_cpu_phys )

hit_enter = input ( f_prfx() + "cpu data...., hit enter.." )

print ( f_prfx(), "cpu freq   : " , psutil.cpu_freq(percpu=True) )

print ( f_prfx(), "virtual mem: ", psutil.virtual_memory() )

print ( f_prfx(), "battery    : ", psutil.sensors_battery() )

# print ( f_prfx(), "temperature: ", psutil.sensors_temperatures() )
# print ( f_prfx(), "fans       : ", psutil.sensors_fans() )
print ( f_prfx(), "net_io pernic: ", psutil.net_io_counters(pernic=False, nowrap=True)  )

hit_enter = input ( f_prfx() + "various data..., hit enter.." )


net_conn = psutil.net_connections(kind='all') 
print ( f_prfx(), "connections (need root!) : ", net_conn ) 

hit_enter = input ( f_prfx() + "connections,..., hit enter.." )


# -- old code below -- 

# hit_enter = input ( f_prfx() + "now measring cpu 3sec " + "...., hit enter.." )

for proc in psutil.process_iter( ['pid', 'name', 'username', 'cpu_percent', 'ppid', 'num_threads' ] ):
  # print( f_prfx(), " proc info: ", proc.info)
  # f_inspect_obj( 'proc_info', proc.info )
  proc_cpu_perc = proc.info.get('cpu_percent') 
  proc_pid      = proc.info.get('pid') 
  proc_ppid     = proc.info.get('ppid') 
  proc_name     = proc.info.get('name') 
  # print ( f_prfx(), " pid + cpu percent: ", proc_pid, proc_cpu_perc, proc_name )
  
# initialized counters and properties ..

tim.sleep ( 3) 

# initiate
perc_total = 0.0
pslist=[] 

# 2nd call.. to have meaningful values
for proc in psutil.process_iter( ['pid', 'name', 'username', 'cpu_percent', 'ppid', 'num_threads' ] ):
  # print( f_prfx(), " proc info: ", proc.info)
  # f_inspect_obj( 'proc_info', proc.info )
  proc_cpu_perc = proc.info.get('cpu_percent') 
  proc_pid      = proc.info.get('pid') 
  proc_ppid     = proc.info.get('ppid') 
  proc_name     = proc.info.get('name') 
  proc_nthreads = proc.info.get('num_threads') 

  if not isinstance(proc_cpu_perc, float):
    f_perc = 0.0
  else:
    f_perc = float ( proc_cpu_perc ) 
    perc_total = perc_total + f_perc
  
  if f_perc > 0.2 :
    # print ( f_prfx(), " pid + cpu percent: ", repr(proc_ppid).rjust(5), repr(proc_pid).rjust(7), '{:7.1f}'.format ( f_perc ), " " + proc_name )
    pslist.append ( proc.info ) 
  
# end 2nd loop, printed values above threshold

# try sorting the collected list, highest cpu-perc at bottom of list
pslist.sort( key=lambda x: (x['cpu_percent'], x['ppid'], x['pid']) ) 

# print ( pslist )
# f_inspect_obj( 'pslist after sorting: ', pslist )

for  psinfo in pslist :
  proc_cpu_perc = psinfo.get('cpu_percent') 
  proc_pid      = psinfo.get('pid') 
  proc_ppid     = psinfo.get('ppid') 
  proc_name     = psinfo.get('name') 
  proc_nthreads = psinfo.get('num_threads')
  f_perc = float ( proc_cpu_perc ) 
  print ( f_prfx(), " pid + cpu percent: ", repr(proc_ppid).rjust(5), repr(proc_pid).rjust(7), '{:7.1f}'.format ( f_perc ), " ", proc_name , "(", proc_nthreads, ")" )

# end for, printed ps-data in order of sort

# print ( f_prfx(), " -------- End of Loop -------- " )
# print ( f_prfx() )

# show the last one, inspect
# f_inspect_obj( 'proc_info', proc.info )

print ( f_prfx() )
print ( f_prfx(), "                        Total cpu-perc", round ( perc_total, 2) )
print ( f_prfx() )
print ( f_prfx(), " -------- End of program -------- " )



