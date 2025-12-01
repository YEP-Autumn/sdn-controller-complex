from renix_py_api.renix import *
import time


class RenixBackend:


    def __init__(self):
        self.sys_entry = get_sys_entry()
        initialize(log_level=logging.INFO)

<<<<<<< Updated upstream
    def  port_bring_online(assign_port):
        BringPortsOnlineCommand(PortList=[assign_port.handle]).execute()

    def port_bring_offline(self, assign_port):
        BringPortsOfflineCommand(PortList=assign_port.handle).execute()
=======
    def port_bring_online(self, assign_port):
        BringPortsOnlineCommand(PortList=[assign_port.handle]).execute()

    def port_bring_offline(self, assign_port):
        BringPortsOfflineCommand(PortList=[assign_port.handle]).execute()

    def start_stream(self, assign_port, file_path, cnt):
        assert assign_port.handle
>>>>>>> Stashed changes

    def start_stream(self, assign_port, file_path, cnt):
        create_stream_from_pcap_cmd = CreateStreamFromPcapCommand(
            PortList=[assign_port.handle], FilePath=file_path
        )
        create_stream_from_pcap_cmd.execute()

        stream_port_config = assign_port.get_children(StreamPortConfig.cls_name())[0]
        assert stream_port_config
        assert stream_port_config.handle

        # 配置step模式
        stream_port_config.edit(TransmitMode=EnumTransmitMode.STEP)
        step_trans_config = stream_port_config.get_children(
            StepTransmitConfig.cls_name()
        )[0]
        step_trans_config.edit(Frames=cnt)

        stream = assign_port.get_children(StreamTemplate.cls_name())[0]
<<<<<<< Updated upstream
=======
        StartStreamCommand(StreamList=[stream.handle]).execute()

    def start_udf_stream(self, assign_port, file_path, cnt):
        pass
        # update_header_cmd = UpdateHeaderCommand(
        #     Stream=stream.handle,
        #     Parameter="ethernetII_1.sourceMacAdd=00:01:01:a0:00:01 "
        #     "ipv4_1.destination=10.10.0.1 "
        #     "ipv4_1.checksum=auto "
        #     "ipv4_1.source.XetModifier:a.StreamType=InterModifier "
        #     "ipv4_1.source.XetModifier:a.Type=Increment "
        #     "ipv4_1.source.XetModifier:a.Start=10.10.1.1 "
        #     "ipv4_1.source.XetModifier:a.Step=1 "
        #     "ipv4_1.source.XetModifier:a.Count=50",
        # )
        # update_header_cmd.execute()
>>>>>>> Stashed changes

    def start_burst_stream(self, assign_port, file_path, cnt):
        pass
        # 配置burst模式
        # stream_port_config.edit(TransmitMode=EnumTransmitMode.BURST)
        # stream_port_burst_cfgs = stream_port_config.get_children(BurstTransmitConfig.cls_name())
        # stream_port_burst_cfg = stream_port_burst_cfgs[0]
        # stream_port_burst_cfg.edit(FramePerBurst=100, BurstCount=1)

<<<<<<< Updated upstream
    def start_udf_stream(self, assign_port, file_path, cnt):
        pass
        # update_header_cmd = UpdateHeaderCommand(
        #     Stream=stream.handle,
        #     Parameter="ethernetII_1.sourceMacAdd=00:01:01:a0:00:01 "
        #     "ipv4_1.destination=10.10.0.1 "
        #     "ipv4_1.checksum=auto "
        #     "ipv4_1.source.XetModifier:a.StreamType=InterModifier "
        #     "ipv4_1.source.XetModifier:a.Type=Increment "
        #     "ipv4_1.source.XetModifier:a.Start=10.10.1.1 "
        #     "ipv4_1.source.XetModifier:a.Step=1 "
        #     "ipv4_1.source.XetModifier:a.Count=50",
        # )
        # update_header_cmd.execute()

    def start_burst_stream(self, assign_port, file_path, cnt):
        pass
        # 配置burst模式
        # stream_port_config.edit(TransmitMode=EnumTransmitMode.BURST)
        # stream_port_burst_cfgs = stream_port_config.get_children(BurstTransmitConfig.cls_name())
        # stream_port_burst_cfg = stream_port_burst_cfgs[0]
        # stream_port_burst_cfg.edit(FramePerBurst=100, BurstCount=1)

    def stop_stream(self, assign_port):
        pass

    def start_capture(self, assign_port, file_name, file_path):
        bring_port_online_cmd = BringPortsOnlineCommand(PortList=[port.handle])
        bring_port_online_cmd.execute()

        start_cap_cmd = StartCaptureCommand(CaptureConfigs=cap_conf.handle)
        start_cap_cmd.execute()

    def stop_capture(self, assign_port):
        cap_conf = assign_port.get_children(CaptureConfig.cls_name())[0]
=======
    def stop_stream(self, assign_port):
        stream = assign_port.get_children(StreamTemplate.cls_name())[0]
        StopStreamCommand(StreamList=[stream.handle]).execute()

    def start_capture(self, assign_port):
        BringPortsOnlineCommand(PortList=[assign_port.handle]).execute()

        StartCaptureCommand(CaptureConfigs=cap_conf.handle).execute()

    def stop_capture(self, assign_port):
        cap_conf = assign_port.get_children(CaptureConfig.cls_name())[0]

        StopCaptureCommand(CaptureConfigs=cap_conf.handle).execute()
>>>>>>> Stashed changes

    def get_capture(self, assign_port, file_path, file_name):
        cap_conf = assign_port.get_children(CaptureConfig.cls_name())[0]

    def get_capture(self, assign_port):
        cap_conf = assign_port.get_children(CaptureConfig.cls_name())[0]

        download_cap_data_cmd = DownloadCaptureDataCommand(
            CaptureConfigs=cap_conf.handle,
            FileDir=file_path,
            FileName=file_name,
            MaxDownloadDataCount=50,
        )

        download_cap_data_cmd.execute()


if __name__ == '__main__':
    backend = RenixBackend()

<<<<<<< Updated upstream
    port = Port(upper=backend.sys_entry, Location='//192.168.2.11/5/13')

    path = os.path.dirname(os.path.realpath(__file__)) + "/../../resource/test.pcap"

    backend.port_bring_online(port)
    backend.send_stream(port, path, 100)
    backend.port_bring_offline(port)
=======
    resource_path = os.path.dirname(os.path.realpath(__file__)) + "/../../resource/"
    send_pkt_path = resource_path + "test.pcap"
    save_pkt_path = resource_path + "capture.pcap"

    send_port = Port(upper=backend.sys_entry, Location='//192.168.2.11/5/13')
    # capture_port = Port(upper=backend.sys_entry, Location='//192.168.2.11/5/14')

    backend.port_bring_online(send_port)

    # backend.start_capture()
    backend.start_stream(send_port, send_pkt_path, 100)

    time.sleep(2)
    backend.port_bring_offline(send_port)
>>>>>>> Stashed changes
