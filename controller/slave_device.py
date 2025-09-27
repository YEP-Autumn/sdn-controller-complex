
class SlaveDevice:

    __port_list = []  # List of Port instances

    __interconnection_links = []

    __streams = []

    __message_queue = []  # Cache for messages


    def __init__(self, device_id):
        self.device_id = device_id


