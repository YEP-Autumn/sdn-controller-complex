from django.db import models

# Create your models here.

class TopologyLink(models.Model):
    src_device = models.CharField(max_length=20)
    src_device_port = models.IntegerField()
    dst_device = models.CharField(max_length=20)
    dst_device_port = models.IntegerField()

    def __str__(self):
        return "TopologyLink(src_device={}, src_device_port={}, dst_device={}, dst_device_port={})".format(self.src_device, self.src_device_port, self.dst_device, self.dst_device_port)