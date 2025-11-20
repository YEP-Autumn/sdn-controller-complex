from django.db import models

# Create your models here.


class Topology(models.Model):
    name = models.CharField(max_length=100)
    links = models.ManyToManyField("TopologyLink", blank=True, related_name="topologies")

    def __str__(self):
        return "Topology(name={})".format(self.name)


class TopologyLink(models.Model):
    src_port_index = models.IntegerField()
    src_device = models.IntegerField()
    dst_port_index = models.IntegerField()
    dst_device = models.IntegerField()
    is_two_way = models.BooleanField(default=False)

    def __str__(self):
        return "TopologyLink(src_device={}, src_port_index={}, dst_device={}, dst_port_index={}, is_two_way={})".format(
            self.src_device,
            self.src_port_index,
            self.dst_device,
            self.dst_port_index,
            self.is_two_way,
        )
