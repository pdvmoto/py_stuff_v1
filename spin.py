import sys
import datetime
import time
import cx_Oracle
import os
import random


# todo
# - put SID in variable, to avoid calling function in rows
# - benchmark overhead of execute from python. how many user-calls?
# - does python hide not-found-errors ? other ORA-errors ? 


print('hello world, testing conn')

# set arg0 , ready to use in print
arg0 = sys.argv[0] + ": " 

# initialize oracle conn
conn = cx_Oracle.connect('scott/tiger@127.0.0.1/orclpdb1')

# -------- need some sql-stmnts: del / upd / ins ------ 

n_records = 4000 # hardcoded for the moment, equal to pl/sql PoC

ins_my_sid_set = """
  insert into tst_lfs ( id, par_id, payload )
  select rownum,  USERENV('SID'),
            'r:' || to_char ( rownum ) || 'par_id: '
            || to_char ( USERENV('SID') ) 
            || ' sysdate: ' || to_char ( sysdate, 'YYYY-MON-DD HH24:MI:SS' )
  from dual
  where USERENV('SID') not in ( select par_id from tst_lfs )
  connect by level <= :n_records
"""

del_one_rec = """
    delete from tst_lfs where id = :n_recid and par_id = userenv ( 'SID') 
"""

upd_one_rec = """
    update tst_lfs
      set payload  = payload || 'upd at cntr: ' || to_char ( :n_counter )
      where id     = mod ( :n_recid + :n_counter , 1000 ) + 1
      and par_id = userenv ( 'SID') 
"""

ins_one_rec = """
    insert into tst_lfs
      values ( :n_recid, userenv ( 'SID' ) 
      , 'Fresh Insert @ cntr: ' || to_char ( :n_counter )
      || ' at tmstmp: ' || to_char ( sysdate, 'YYYY-MON-DD HH24:MI:SS' ) ) 
"""
# --------- start pogram here -------------------------

# verify conn is working
print ( arg0 + "is using oracle version: " + conn.version )

# if you need a cursor:
# cur = conn.cursor ()

# try define a function
def hello_w():
  print ( arg0 + "Hi world")
  return

# call the functin
# print ("spin: Call the function...")
# hello_w ()

# try define a function to Qry..
def get_param ( p_param ):
  #print ( " function got parameter " )
  #print ( p_param )
  cur = conn.cursor ()
  sql_to_get_param="select value from v$parameter where name like :1 "
  cur.execute ( sql_to_get_param, (p_param,) ) 
  res = cur.fetchall()
  cur.close()
  return res[0][0]   # <--- funny way to get element 0/0

# get teh param
print ( arg0 + ": value of comm-wait would be [" + get_param ( "commit_wait") + ']' )

# print ( arg0 + "value local_listener would be " )
# print ( arg0 + get_param ( "local_listener") )

print ( arg0 + " ------[ now test time ] ---------- " )
n_counter = 0
n_secs    = 0

print ( arg0 + "time.time() : " )
print ( arg0 + "time.time() is: " +  str ( time.time() ) )

print ( arg0 + "sleeping 1sec " ) 
start = time.time()
time.sleep(1)
end   = time.time()

difftime = end - start
print ( arg0 + "difftime over 1 sec time.sleep(1) is:" + str( difftime )  )

# insert the testset
cur = conn.cursor ()

cur.execute ( ins_my_sid_set, n_records=n_records ) 
conn.commit() 

# convert first arg into number
max_sec = float ( sys.argv[1] )
print ( arg0 + "loop will run for " + str ( max_sec ) + " seconds" ) 

start = time.time()
while  time.time() - start <  max_sec : # ---- start while -----
  n_counter = n_counter+1
  n_random_id = int (random.uniform ( 1, 1000 ) )
  # print ( arg0 + "random nr is " + str ( n_random_id )) 

  # use this cursor for del/upd/ins.
  cur = conn.cursor ()

  # delete and commit
  cur.execute ( del_one_rec, n_recid=n_random_id ) 
  conn.commit ()

  # updates a record nearby and commit
  cur.execute ( upd_one_rec, n_counter=n_counter, n_recid=n_random_id ) 
  conn.commit

  # re-insert the records, and commit
  cur.execute ( ins_one_rec, n_recid=n_random_id, n_counter=n_counter ) 
  conn.commit ()

  # cleanup
  cur.close()  

  # ------------------------------------ end while -------
  

print (" n_counter was : " + str ( n_counter ) )
print ( n_counter ) 

end   = time.time()
difftime = end - start
print ( "while-difftime is " )
print ( difftime ) 

print ( " ------------ [ now test args ] -----------" )

print ( sys.argv[0] + ": " + "This is the name of the script: ", sys.argv[0] )
print ( sys.argv[0] + ": " + "Number of arguments: ", len(sys.argv) )
print ( sys.argv[0] + ": " + "The arguments are: " , str(sys.argv) )

print ( sys.argv[0] + ": " + "nr of secnds would be: " , str(sys.argv[1]) )

# close if needed (this will remove SID..)
conn.close()
