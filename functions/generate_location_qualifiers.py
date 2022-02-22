from datetime import datetime
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
from arches.app.models.resource import Resource
import json


#TODO: Update UUID's to match live server 
details = {
    "name": "Generate Location Qualifiers",
    "type": "node",
    "description": "Just a sample demonstrating node group selection",
    "defaultconfig": {"triggering_nodegroups": []},
    "classname": "GenerateLocationQualifiers",
    "component": "views/components/functions/generate_location_qualifiers",
}


#TODO: figure out why renaming broke everything
#Methods
def createNewTile(tile):
    '''
    Description:
    Creates a new Location Qualifer tile 
    
    Parameters:
    :tile: Triggering tile
    
    Returns:
    :new_tile: Returns a new tile with all required data
    '''
    
    #Nodes
    location_qualifiers =  "ffbcc420-8ff9-11ec-9340-00155d9326d1"
    mapsheet = "19bcfcb4-8ffa-11ec-9340-00155d9326d1"
    kmsq = "12becea6-8ffa-11ec-9340-00155d9326d1"
    map_reference = "f58199ea-8ff9-11ec-9340-00155d9326d1"
    
    #Request new blank tile of resource instance from current resource 
    new_tile = Tile().get_blank_tile_from_nodegroup_id(location_qualifiers, tile.resourceinstance_id)
    
    #Populate new tile with generated data
    new_tile.data[kmsq] = NRGtoKMSQ(tile.data[map_reference])
    new_tile.data[mapsheet] = NRGtoMapsheet(tile.data[map_reference])
    return new_tile

def checkIfRefValuesExist(mainTile):

    '''
    Description:
    Check whether current tile already has a RecordEdit node exists
    and if so update it current information
    
    Returns:
    :Bool: True if tile has been found and update/ False if tile has not been found and update 
    '''
    #Nodes
    location_qualifiers =  "ffbcc420-8ff9-11ec-9340-00155d9326d1"
    mapsheet = "19bcfcb4-8ffa-11ec-9340-00155d9326d1"
    kmsq = "12becea6-8ffa-11ec-9340-00155d9326d1"
    map_reference = "f58199ea-8ff9-11ec-9340-00155d9326d1"
    
    #Get current resource 
    res = Resource.objects.get(resourceinstanceid = mainTile.resourceinstance_id)
    res.load_tiles()
    print(mainTile.data[map_reference])
    
    #For each tile in resource find record edit date tile
    for tile in res.tiles:
        print(str(tile.nodegroup_id) == location_qualifiers)
        print(vars(tile))
        if str(tile.nodegroup_id) == location_qualifiers:  #If record edit tile exits
            tile.data[mapsheet] = NRGtoMapsheet(mainTile.data[map_reference])
            tile.data[kmsq] = NRGtoKMSQ(mainTile.data[map_reference])
            tile.save() #Update edit date/edited by and save tile
            
            return True

    return False

def NRGtoKMSQ(ngr): 
    '''
    Description:
    Returns first two values of eastings and northings
    
    Params:
    :nrg: String passed from tile
    '''  
    return ngr[:2] + ngr[2:4] + ngr[7:9]


def NRGtoMapsheet(nrg):
    '''
    Descriptions:
    Calculates the Mapsheet value
    
    Params:
    :nrg: String passed in from tile
    
    Returns:
    :string: Formatted mapsheet string
    '''
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

class GenerateLocationQualifiers(BaseFunction):

    def save(self, tile, request):
        print("printing saved")
        if checkIfRefValuesExist(tile):
            print("success")
        else:
            new_tile = createNewTile(tile)
            new_tile.save()
        return     