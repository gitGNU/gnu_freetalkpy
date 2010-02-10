#                                                                                                             
#   Copyright (c) 2010 Harshavardhana                                                                         
#   This file is part of freetalkpy.                                                                          
#                                                                                                             
#   FreetalkPy is free software; you can redistribute it and/or                                                
#   modify it under the terms of the GNU General Public License as                                             
#   published by the Free Software Foundation; either version 3 of                                             
#   the License, or (at your option) any later version.                                                         

#   FreetalkPy is distributed in the hope that it will be useful, but                                          
#   WITHOUT ANY WARRANTY; without even the implied warranty of                                                 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU                                          
#   General Public License for more details.                                                                    

#   You should have received a copy of the GNU General Public License                                          
#   along with this program.  If not, see                                                                      
#   <http://www.gnu.org/licenses/>.  

import telepathy
from telepathy.interfaces import CONN_MGR_INTERFACE
import dbus

def parse_account(s):
    lines = s.splitlines()
    pairs = []
    manager = None
    protocol = None

    for line in lines:
        if not line.strip():
            continue

        k, v = line.split(':', 1)
        k = k.strip()
        v = v.strip()

        if k == 'manager':
            manager = v
        elif k == 'protocol':
            protocol = v
        else:
            if k not in ("account", "password"):
                if v.lower() == "false":
                    v = False
                elif v.lower() == "true":
                    v = True
                else:
                    try:
                        v = dbus.UInt32(int(v))
                    except:
                        pass
            pairs.append((k, v))

    assert manager
    assert protocol
    return manager, protocol, dict(pairs)

def read_account(path):
    return parse_account(file(path).read())

def connect(manager, protocol, account, ready_handler=None):
    reg = telepathy.client.ManagerRegistry()
    reg.LoadManagers()

    mgr = reg.GetManager(manager)
    conn_bus_name, conn_object_path = \
        mgr[CONN_MGR_INTERFACE].RequestConnection(protocol, account)
    return telepathy.client.Connection(conn_bus_name, conn_object_path,
        ready_handler=ready_handler)

def connection_from_file(path, ready_handler=None):
    manager, protocol, account = read_account(path)
    return connect(manager, protocol, account, ready_handler=ready_handler)

