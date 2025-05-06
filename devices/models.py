from django.db import models
from companies.models import Company

# Create your models here.
class Device(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    aibox_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    desc= models.TextField(blank=True)

    def __str__(self):
        return self.name
    

# Create your models here.
class Source(models.Model):
    source_id = models.CharField(max_length=100)
    ipv4 = models.GenericIPAddressField(protocol='IPv4')
    desc = models.TextField(blank=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    def __str__(self):
        return self.source_id