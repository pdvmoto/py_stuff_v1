import time
import cx_Oracle
import os

print('hello world, testing conn')

# define merge-stmnts here, use triple-quotes for multi-lines

merge_st1="""
merge into bt_mon_stats u
  using ( select
  o.statistic#
, o.new_val     new_old_val
, s.value       new_val
-- , ( s.value - o.old_val )  diff -- unreliable
from bt_mon_stats o
   , v$sysstat s
where o.statistic# = s.statistic#
        ) n
  on ( u.statistic# = n.statistic# )
when matched then
  update set u.old_val = n.new_old_val
           , u.new_val = n.new_val
           --, u.diff = n.diff        -- better (new_val - new_old_val)
           , u.diff    = (n.new_val - n.new_old_val)
           , u.per_sec = (n.new_val - n.new_old_val)
                          / ( (sysdate - u.dt_recorded) * 24 * 3600)
           , u.dt_recorded = sysdate
"""

# define select stmnts , formatted, here
select_st_title=""" 
select 'Inst: ' || i.instance_name || ' @ ' 
                || i.host_name                        
                || ' nr-Sess: ' || count (*) 
                || ' time: ' || to_char ( sysdate, 'YYYY-MON-DD HH24:MI:SS' )
from gv$instance i
   , gv$session s
where i.inst_id = s.inst_id
group by i.instance_name, i.host_name, i.startup_time, i.status
""" 

# need cursor for time-stats.

# need cursor for stats other than time.
select_st_other=""" 
select 
    rpad ( name, 20 )                   || ' ' 
||  to_char (    diff, '999,999,999.9') || ' ' 
||  to_char ( per_sec,     '999,999.999') as name
from bt_mon_stats
where name not like '%tim%'
order by name 
""" 


#  con = cx_Oracle.connect('pdevisser/change_on_install@127.0.0.1:9000/pcs')
con = cx_Oracle.connect('scott/tiger@127.0.0.1:1521/orclpdb1')
print (con.version)

# print ('cur.connection is:')
# print ( select_st_other )

print ( '0....,....1....,....2....,....3....,....4')
print ( ' - - - - - - - - - -   - - - - ' )
print ( 'StatName             -        diff    - per_sec' )

# need a cursor
cur = con.cursor()

#create the new data
cur.execute( merge_st1) 

#fetch in loop(s)
cur.execute(select_st_other)
for result in cur:
  # print (cur.rowcount)
  print ( result[0] )
cur.close()

# issue commit to prevent locking (risk = multiple-runs)
con.commit()

# main loop: every X seconds: merge + query new stats.
while True:
  print ('doing while loop')
  time.sleep (2)
  print ('been sleeping 2')

  cur = con.cursor() # need a cursor, again?

  #create the new data
  cur.execute( merge_st1) 

  # optionally: clear screen
  os.system('clear')

  # fetch the heading: instance, time, + nr conns
  print ( '.' ) 
  print ( '0....,....1....,....2....,....3....,....4....,....5')
  cur.execute(select_st_title)
  for result in cur:
    # print (cur.rowcount)
    print ( result[0] )

  # fetch the time-data, in loop

  # fetch other data, in loop
  print ( '.' ) 
  print ( '0....,....1....,....2....,....3....,....4....,....5')
  print ( 'StatName              -        diff    - per_sec' )

  cur.execute(select_st_other)
  for result in cur:
    # print (cur.rowcount)
    print ( result[0] )
  cur.close()

  con.commit() # prevent locking, but beware of multiple-runs

  time.sleep(5) # wait for next.. make it variable

  # end mail loop

# end
con.close()

