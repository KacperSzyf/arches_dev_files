from datetime import date
from importlib import resources
from platform import node
from site import execsitecustomize
import uuid
from venv import create
from arches.app.models.models import Concept as modelConcept
from arches.app.models.concept import Concept
from arches.app.models.tile import Tile
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
import json

details = {
    "name": "Generate KMSQ",
    "type": "node",
    "description": "Just a sample demonstrating node group selection",
    "defaultconfig": {"triggering_nodegroups": []},
    "classname": "GenerateKMSQ",
    "component": "views/components/functions/generate_KMSQ",
}

#Methods
def createNewTile(tile):
    location_qualifiers =  "ffbcc420-8ff9-11ec-9340-00155d9326d1"
    location = 'ffbcc420-8ff9-11ec-9340-00155d9326d1'
    mapsheet = "19bcfcb4-8ffa-11ec-9340-00155d9326d1"
    kmsq = "12becea6-8ffa-11ec-9340-00155d9326d1"
    loaction_accuracy = "81194e3e-7dcc-11ec-871b-00155db3508e"
    map_reference = "f58199ea-8ff9-11ec-9340-00155d9326d1"
    
    new_tile = Tile().get_blank_tile_from_nodegroup_id(location_qualifiers, tile.resourceinstance_id)
    
    new_tile.data[kmsq] = NRGtoKMSQ(tile.data[map_reference])
    new_tile.data[mapsheet] = NRGtoMapsheet(tile.data[map_reference])
    return new_tile

def NRGtoKMSQ(ngr):   
    return ngr[:2] + ngr[2:4] + ngr[7:9]

def NRGtoMapsheet(nrg):
    first_letter = ""
    second_letter= ""
    first_number = int(nrg[3])
    second_number = int(nrg[8])
    
    if first_number >= 0 and first_number <= 4:
        first_letter += "W"
        
    if first_number >= 5 and first_number <= 9:
        first_letter += "E"
        
        
    if second_number >= 0 and second_number <= 4:
        second_letter += "S"
        
        
    if second_number >= 5 and second_number <=9:
        second_letter += "N"
        
    
    return nrg[:2] + nrg[2:3] + nrg[7:8] + second_letter + first_letter

class GenerateKMSQ(BaseFunction):

    def save(self, tile, request):
        new_tile = createNewTile(tile)
        new_tile.save()
        return     