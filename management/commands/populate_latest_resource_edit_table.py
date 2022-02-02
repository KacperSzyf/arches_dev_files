from arches.app.models.models import EditLog, LatestResourceEdit, ResourceInstance
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Commands for managing datatypes
    """
    def handle(self, *args, **options):
        #Pull all edit logs and order time decending by time
        edits = EditLog.objects.order_by('resourceinstanceid', '-timestamp').distinct('resourceinstanceid')
        
        for edit in edits:
            #Check if edit still exists within the resource
            if ResourceInstance.objects.filter(resourceinstanceid=edit.resourceinstanceid).exists():
                #Ensure each resource has a creation event
                if LatestResourceEdit.objects.filter(resourceinstanceid=edit.resourceinstanceid, edittype = 'create').exists():
                    #Check if a resource has an even other than creation
                    if LatestResourceEdit.objects.filter(resourceinstanceid=edit.resourceinstanceid).exclude(edittype = 'create'):
                        #If so remove the existing even
                        LatestResourceEdit.objects.filter(resourceinstanceid = edit.resourceinstanceid).delete()
                    #And replace it with the most recent edit even
                    latest_edit = LatestResourceEdit()
                    latest_edit.resourceinstanceid = edit.resourceinstanceid
                    latest_edit.timestamp = edit.timestamp
                    latest_edit.edittype = edit.edittype
                    latest_edit.save()
                #If a resource only has a creation event, save it as a new edit type creation
                else:
                    latest_edit = LatestResourceEdit()
                    latest_edit.resourceinstanceid = edit.resourceinstanceid
                    latest_edit.timestamp = edit.timestamp
                    latest_edit.edittype = edit.edittype
                    latest_edit.save()
                    
        print(f'{len(edits)} edits saved')
