from datetime import datetime
from poe import get_queue_info, print_queue_info
from db import SQLiteDB

DEBUG = False #True
current_date = datetime.now()


def find_next_change_time(q):
    for time_ in q:
        if time_ > current_date:
            break
        prev_time = time_
    return time_, prev_time

db = SQLiteDB()
db.create_tables()
db.set_global_info(new_value='Updated', name='is_updated')
queues = db.get_queues()
queues_info, is_updated = get_queue_info()
if is_updated:
    db.set_global_info(new_value='Updated', name='is_updated')
else:
    db.set_global_info(new_value='Not updated', name='is_updated')
for q in queues:
    q_num = str(q[1])
    queue_info = queues_info[q_num]
    next_time_, curent_time_= find_next_change_time(queue_info)
    if DEBUG:
        print(20*"=", q_num + 20*"=")
        print_queue_info(queues_info, q_num)
    state = queue_info[next_time_]
    state_now = queue_info[curent_time_]
    db.update_queue(next_time_ , state['value'], curent_time_, state_now['value'], q_num)

db.close_connection()