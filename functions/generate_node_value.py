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
    "name": "Generate Node Value",
    "type": "node",
    "description": "Just a sample demonstrating node group selection",
    "defaultconfig": {"triggering_nodegroups": [],
                      "keys": { 
                        #Key_Value : Mapping
                        }
                      },
    "classname": "UnitaryFunction",
    "component": "views/components/functions/generate_node_value",
}

#Methods
def createNewTile(keys, source_tile):
    target_tile = Tile()
    target_tile.nodegroup_id = 'ad18a6a2-79d9-11ec-8fb5-00155db3508e' #Unitary_Authority
    target_tile.resourceinstance_id = source_tile.resourceinstance_id
    target_tile.parenttile_id = source_tile.parenttile_id
    #                       'Unitary_value'                 'value from key dictionary based on the value of source tile data'
    target_tile.data = {'ad18a6a2-79d9-11ec-8fb5-00155db3508e' : keys[source_tile.data[list(source_tile.data.keys())[0]]]} #
    target_tile.sortorder = 0
    target_tile.provisionaledits = None
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
    
    source_thesauri_id = "117cddf0-8403-4e16-b325-43327efc9e1f" # to be changed 
    target_thesauri_id = "06cf74db-f2b8-46a9-8c2f-565bedaa6424" # to be changed
    
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

class UnitaryFunction(BaseFunction):

    def save(self, tile, request):
        #Get concept UUIDs from word values
        self.config['keys'] = getConcepts(self) #
        
        #Variables
        source_tile = tile
        exists = False

        #Create target tile 
        target_tile = createNewTile(self.config['keys'], source_tile)
        
        
        #Check if source_tile has once or more target tiles 
        if Tile.objects.filter(resourceinstance_id = source_tile.resourceinstance_id, nodegroup_id = target_tile.nodegroup_id).exists():
            #if true called all instances of target tile 
            target_tiles = Tile.objects.filter(resourceinstance_id = source_tile.resourceinstance_id, nodegroup_id = target_tile.nodegroup)
            
            #check if incoming data matches any data already present
            for tile in target_tiles:
                if tile.data['ad18a6a2-79d9-11ec-8fb5-00155db3508e'] == self.config['keys'][source_tile.data['a8533c04-79d9-11ec-8fb5-00155db3508e']]:
                    exists = True    
                    
        
        if not exists:
            target_tile.save()
                
