#Imports
import uuid

#Django imports
from django.contrib.gis.db import models

class LatestResourceEdit(models.Model):
    editlogid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    username = models.TextField(blank=True, null=True)
    resourcedisplayname = models.TextField(blank=True, null=True)
    resourceinstanceid = models.TextField(blank=True, null=True)
    edittype = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "latest_resource_edit"