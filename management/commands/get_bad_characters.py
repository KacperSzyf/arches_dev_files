
#Core arches imports
from arches.app.models.system_settings import settings
from arches.app.models.resource import Resource
#Django imports
from django.core.management.base import BaseCommand, CommandError


from arches.app.models.models import ResourceInstance


class Command(BaseCommand):
    """
    Commands to find resources containing encoded chracters 
    """
    
    #TODO: Think about how to speed this up 
    # if we know what nodes to look it that would avoid one for loop 
    # if its not all resources we could shrink the queryest 
    def handle(self, *args, **options):
        #Pull all edit logs and order time decending by time and exclude system setting changes
        file = open("dodgy_resources.csv", "a")
        resources = Resource.objects.all()
        for res in resources:
            res.load_tiles()
            dodgy = False
            for tile in res.tiles:
                # if "?" in tile.data['name uuid'] or "?" in tile.data['desc uuid']:
                #     dodgy = True
                for key in list(tile.data.keys()):
                    if isinstance(tile.data[key], str) and "?" in tile.data[key]:
                        print(f'{key} : {tile.data[key]}')
                        dodgy = True
            if dodgy:
                file.write(f'{res.resourceinstanceid},')
        file.close()
                        
       