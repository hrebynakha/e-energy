from energy import get_queue_info
from db import SQLiteDB

db = SQLiteDB()
queues = db.get_queues()

for q in queues:
    q_num, queue_info = get_queue_info(q[1])
    print("Processing q,", q, queue_info)
    db.update_queue(queue_info["date"], queue_info["state_now"], q_num)


db.close_connection()