from datetime import datetime
from importlib import resources
from platform import node
from site import execsitecustomize
from urllib import request
import uuid
from venv import create
from arches.app.models.models import Concept as modelConcept
from arches.app.models.concept import Concept
from arches.app.models.tile import Tile
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
import json
from arches.app.models.models import EditLog, LatestResourceEdit
from arches.app.models.resource import Resource
from dev.models.models import ResourceInstance


details = {
    "name": "Record editing dates",
    "type": "node",
    "description": "",
    "defaultconfig": {"triggering_nodegroups": []},
    "classname": "RecordEditingDates",
    "component": "views/components/functions/record_editing_dates",
}

#TODO: Update UUID's to match the live server

def getCreationData(edits):
    '''
    Description:
    Get info on when and who by the resource was created 
    
    Parameters:
    :edits: Queryset containing all 'create' type events for current resource
    
    Return:
    :tuple: Contaning a username and timestamp
    '''
    creation_event = edits.get(edittype = 'create')
    return (creation_event.username, creation_event.timestamp)

def checkRecordEditExists(resourceId, req):
    '''
    Description:
    Check whether current tile already has a RecordEdit node exists
    and if so update it current information
    
    Returns:
    :Bool: True if tile has been found and update/ False if tile has not been found and update 
    '''
    #Nodes
    record_edit_date = '66d789d0-90b1-11ec-8148-00155d9326d1'
    latest_edit = '01afed44-90b2-11ec-8e68-00155d9326d1'
    edited_by = '1d748602-90b2-11ec-8e68-00155d9326d1'
    
    #Get current resource 
    res = Resource.objects.get(resourceinstanceid = resourceId)
    res.load_tiles()
    
    #For each tile in resource find record edit date tile
    for tile in res.tiles:
        if str(tile.nodegroup_id) == record_edit_date:  #If record edit tile exits
            tile.data[latest_edit] = datetime.today().strftime('%Y-%m-%d')
            tile.data[edited_by] = req.user.username
            tile.save() #Update edit date/edited by and save tile
            
            return True

    return False

def createRecordEditTile(tile, req):
    '''
    Description:
    Creates a Record Edit tile
    
    Parameters:
    :tile: Triggering tile
    :req: Request object
    
    Returns:
    :new_tile: Returns a new tile with all required data
    '''
    #Nodes
    record_edit_date = '66d789d0-90b1-11ec-8148-00155d9326d1'
    creation_date = '6f5ad594-90b1-11ec-8e68-00155d9326d1'
    created_by = 'f8e5177a-90b1-11ec-8e68-00155d9326d1'
    latest_edit = '01afed44-90b2-11ec-8e68-00155d9326d1'
    edited_by = '1d748602-90b2-11ec-8e68-00155d9326d1'
    
    #Request new blank tile of resource instance from current resource 
    new_tile = Tile().get_blank_tile_from_nodegroup_id(record_edit_date, tile.resourceinstance_id)
    
    #Queryset containing all creation events for current resource instance
    edits = LatestResourceEdit.objects.order_by('resourceinstanceid', '-timestamp').filter(resourceinstanceid=tile.resourceinstance_id, edittype = 'create')
    
    #Define creation data
    creation_data = "None"
    
    #Check whether edits returned any creation event
    if edits.exists():
        #Set new tile date for creation 
        creation_data = getCreationData(edits)
        new_tile.data[creation_date] = creation_data[1].strftime("%Y-%m-%d")
        new_tile.data[created_by] = creation_data[0]
    
    #Update set most recent edit
    new_tile.data[latest_edit] = datetime.today().strftime('%Y-%m-%d')
    new_tile.data[edited_by] = req.user.username

    return new_tile

class RecordEditingDates(BaseFunction):

    def save(self, tile, request):  
        if checkRecordEditExists(tile.resourceinstance_id, request):
            print("successs")
        else:
            new_tile = createRecordEditTile(tile, request)
            new_tile.save()
        
        return     