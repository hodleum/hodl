from net2.protocol import server
from net2.models import drop_db, create_db
import sys

drop_db()
create_db()

server.run(int(sys.argv[1]))
