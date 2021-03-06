
#Core arches imports
from arches.app.models.system_settings import settings
from arches.app.models.models import FunctionXGraph
from arches.app.models.tile import Tile
#Django imports
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Commands to load and resave all resources
    """
    def handle(self, *args, **options):
        #Get Ringfencing function
        ringfencing_func_id = 'be239b0a-145d-4e27-bb71-beaa855dcc11' #Replace with local uuid
        ringfencing = FunctionXGraph.objects.get(function_id = ringfencing_func_id)
        
        #Get all triggering nodegroups from the ringfencing function
        triggeringNodeGroups = ringfencing.config['triggering_nodegroups']
        
        #For each triggering node group
        for nodeGroup in triggeringNodeGroups:
            #Get all tiles with the nodegroup id of triggering nodegroup
            tiles = Tile.objects.filter(nodegroup_id = nodeGroup)
            #Save each tile in the nodegroup
            for tile in tiles:
                tile.save()
            