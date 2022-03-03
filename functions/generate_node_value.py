from datetime import date
from importlib import resources
from platform import node
from site import execsitecustomize
import uuid
from venv import create

from numpy import var
from arches.app.models.models import Concept as modelConcept
from arches.app.models.concept import Concept
from arches.app.models.tile import Tile
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
import json

details = {
    "name": "Generate Node Value",
    "type": "node",
    "description": "Just a sample demonstrating node group selection",
    "defaultconfig": {"triggering_nodegroups": [],
                      "keys": { 
                        "Cefn Cribwr":"Bridgend",
                        "Pencoed":"Bridgend",
                        "Coychurch Lower":"Powys",
                        "Bettws (Newport)":"Powys",
                        "Bettws (Powys)" : "Bridgend"
                        }
                      },
    "classname": "UnitaryFunction",
    "component": "views/components/functions/generate_node_value",
}

#Methods
def createNewTile(keys, source_tile):
    '''
    Description:
    Creates a new Unitary Authority tile 
    
    Parameters:
    :source_tile: Triggering tile
    
    Returns:
    :target_tile: Returns a new tile with all required data
    '''
    
    #Nodes
    unitary_authority = '01340830-94c9-11ec-b43d-00155db05fb1' #Unitary Authority nodegroup uuid
    ua_value = "01340830-94c9-11ec-b43d-00155db05fb1" #Unitary Authority's node uuid
    
    #UUID's for the right side of the default.config.keys dictionary 
    rhs_key = source_tile.data[list(source_tile.data.keys())[0]] #Always fetch the first element as only one value can be selected
    
    #Request new blank tile of resource instance from unitary authority
    #Location UUID = bb04598c-94c8-11ec-9a3e-00155db05fb1
    
    target_tile = Tile().get_blank_tile_from_nodegroup_id(unitary_authority, source_tile.resourceinstance_id)
    target_tile.parenttile_id = source_tile.parenttile_id

    #Add UA data to new tile
    target_tile.data[ua_value] = keys[rhs_key]

    return target_tile

def getConcepts(self):
    '''
    Description:
    This functions takes a word dictionary and convert it to UUID dictionary
    
    Parameters:
    'source_thesauri_id': Left hand thesauri  of the default config keys
    'target_thesauri_id': Right hand thesauri of th default config keys
    
    Returns:
    'new_keys': Returns the original dictionary with words converted to UUID's
    '''
    #source_thesauri_id
    source_thesauri_id = "6718532c-1bf4-41e0-9243-ff605a6bf168" # to be changed  community value thesauri uuid
    target_thesauri_id = "691be2ee-a3fc-4b38-be2d-7752e5f4d927" # to be changed unitary authority thesauri uuid
    
    new_keys = {}

    #Left hand side of default config keys
    source_thesauri = Concept().get(
        id=source_thesauri_id,
        include_subconcepts=True,
        include_parentconcepts=False,
        include_relatedconcepts=True,
        depth_limit=None,
        up_depth_limit=None,
    )

    #Right hand side of default config keys
    target_thesauri = Concept().get(
        id=target_thesauri_id,
        include_subconcepts=True,
        include_parentconcepts=False,
        include_relatedconcepts=True,
        depth_limit=None,
        up_depth_limit=None,
    )
    

    for source_subc in source_thesauri.subconcepts: # for each concept in left hand thesauri
        for target_subc in target_thesauri.subconcepts:# for each concept in right hand thesauri 
            if target_subc.values[0].value == self.config['keys'][source_subc.values[0].value]: # check whether left hand concept(text) matches default config keys
                new_keys[source_subc.values[0].id] = target_subc.values[0].id # If match create a new key with lef hand concept UUID and right hand concept UUID
                
    return new_keys

#TODO: Stop it form triggering twice 

class UnitaryFunction(BaseFunction):

    def save(self, tile, request):
        print("FIRED!!!!!!!!!!!!!!!!")
        #Get concept UUIDs from word values
        self.config['keys'] = getConcepts(self)
        #get tile.parent.tile id 
        
        #Variables
        source_tile = tile
        print(f'srouce tile: {vars(source_tile)}')
        exists = False

        #Create target tile 
        target_tile = createNewTile(self.config['keys'], source_tile)
        
        #Check if source_tile has one or more target tiles 
        if Tile.objects.filter(resourceinstance_id = source_tile.resourceinstance_id, nodegroup_id = target_tile.nodegroup_id).exists():
            #if true called all instances of target tile 
            target_tiles = Tile.objects.filter(resourceinstance_id = source_tile.resourceinstance_id, nodegroup_id = target_tile.nodegroup)
            
            #For each tile check if Unitary Authority tile already exists
            for tile in target_tiles:
                if str(tile.nodegroup_id) == '01340830-94c9-11ec-b43d-00155db05fb1': #Unitary Authority 
                    #If so remove it and add the new one, since there can only be one
                    tile.delete()
                    target_tile.save()
                    return

        #If no target tiles exist just save a new tile   
        if not exists:
            target_tile.save()
            
        return
                
