from arches.app.models.models import EditLog, LatestResourceEdit, ResourceInstance
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Commands for managing datatypes
    """
    def handle(self, *args, **options):
        edits = EditLog.objects.order_by('resourceinstanceid', '-timestamp').distinct('resourceinstanceid')
        
        for edit in edits:
            if ResourceInstance.objects.filter(resourceinstanceid=edit.resourceinstanceid).exists():
                if LatestResourceEdit.objects.filter(resourceinstanceid=edit.resourceinstanceid, edittype = 'create').exists():
                    if LatestResourceEdit.objects.filter(resourceinstanceid=edit.resourceinstanceid).exclude(edittype = 'create'):
                        LatestResourceEdit.objects.filter(resourceinstanceid = edit.resourceinstanceid).delete()
                    latest_edit = LatestResourceEdit()
                    latest_edit.resourceinstanceid = edit.resourceinstanceid
                    latest_edit.timestamp = edit.timestamp
                    latest_edit.edittype = edit.edittype
                    latest_edit.save()
                else:
                    latest_edit = LatestResourceEdit()
                    latest_edit.resourceinstanceid = edit.resourceinstanceid
                    latest_edit.timestamp = edit.timestamp
                    latest_edit.edittype = edit.edittype
                    latest_edit.save()
                    
        print(f'{len(edits)} edits saved')
