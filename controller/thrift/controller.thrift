namespace cl stream
namespace cpp stream
namespace d stream
namespace dart stream
namespace java stream
namespace php stream
namespace perl stream
namespace haxe stream
namespace netstd stream

enum Operation {
    ADD,
    DEL,
    UPDATE
}

struct Port {
    1: i32 if_index,
    2: string name
}

struct PortUpdate {
    1: i32 if_index,
    2: string name,
    3: i32 state,
    4: Operation op
}

struct InterconnectionLink {
    1: i32 local_if_index,
    2: string local_if_name,
    3: string peer_device_name,
    4: optional i32 peer_if_index,
    5: optional string peer_if_name
}

struct InterconnectionLinkUpdate {
    1: i32 local_if_index,
    2: string local_if_name,
    3: string peer_device_name,
    4: optional i32 peer_if_index,
    5: optional string peer_if_name
}

struct Device
{
    1: string name,
    2: list<Port> port_list,
    3: list<InterconnectionLink> link_list
}

struct DeviceUpdate {
    1: string name,
    2: list<PortUpdate> port_update_list,
    3: list<InterconnectionLinkUpdate> link_update_list
}

enum ForwardEntryType {
    ENCAP,
    DECAP,
    FORWARD,
    LOCAL
}

struct ForwardEntry {
    1: i32 vlan_id,
    2: i32 in_if_index,
    3: i32 out_if_index,
    4: ForwardEntryType type
}

struct Stream {
    1: i32 stream_id,
    2: ForwardEntry entry
}

struct ConfigUpdate {
    1: list<Stream> streams_add_list,
    2: list<Stream> streams_del_list,
    3: list<Stream> streams_update_list
}

struct Config {
    1: list<Stream> streams_list
}

service ControllerService {
    ConfigUpdate keep_alive(1: DeviceUpdate device_update),
    Config link_full_request(1: Device device)
}
