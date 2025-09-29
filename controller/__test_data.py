class TestData:

    device_1 = {
        'hostname': 'device_1',
        'interconnection_links': [
            {'src': {'id': 'device_2', 'port': 21}, 'dst': {'id': 'device_1', 'port': 12}},
            {'src': {'id': 'device_3', 'port': 31}, 'dst': {'id': 'device_1', 'port': 13}},
            {'src': {'id': 'device_4', 'port': 41}, 'dst': {'id': 'device_1', 'port': 14}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }

    device_2 = {
        'hostname': 'device_2',
        'interconnection_links': [
            {'src': {'id': 'device_1', 'port': 12}, 'dst': {'id': 'device_2', 'port': 21}},
            {'src': {'id': 'device_3', 'port': 32}, 'dst': {'id': 'device_2', 'port': 23}},
            {'src': {'id': 'device_4', 'port': 42}, 'dst': {'id': 'device_2', 'port': 24}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }

    device_3 = {
        'hostname': 'device_3',
        'interconnection_links': [
            {'src': {'id': 'device_1', 'port': 13}, 'dst': {'id': 'device_3', 'port': 31}},
            {'src': {'id': 'device_2', 'port': 23}, 'dst': {'id': 'device_3', 'port': 32}},
            {'src': {'id': 'device_4', 'port': 43}, 'dst': {'id': 'device_3', 'port': 34}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }

    device_4 = {
        'hostname': 'device_4',
        'interconnection_links': [
            {'src': {'id': 'device_1', 'port': 14}, 'dst': {'id': 'device_4', 'port': 41}},
            {'src': {'id': 'device_2', 'port': 24}, 'dst': {'id': 'device_4', 'port': 42}},
            {'src': {'id': 'device_3', 'port': 34}, 'dst': {'id': 'device_4', 'port': 43}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }
