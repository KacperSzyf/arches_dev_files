import uuid
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.resource import Resource
from django.contrib.auth.models import User, Group, Permission
from arches.app.models.tile import Tile
import json
import logging

from arches.app.utils.permission_backend import (
    get_restricted_users,
    get_groups_for_object)

from guardian.shortcuts import (
    assign_perm,
    get_perms,
    remove_perm,
    get_group_perms,
    get_user_perms,
    get_groups_with_perms,
    get_users_with_perms,
    get_perms_for_model,
)

logger = logging.getLogger(__name__)

""" 
A function designed to apply resource instance permissions en masse, based upon that resource containing
a specified concept(s). 

Data required from front-end component:
1. Nodegroup id                                selected_nodegroup
2. Node id                                     target_node
3. Concept id(s)                               select_val
4. Group + boolean access pairs                user_groups
"""

details = {
    "name": "EamenaPermissions",
    "type": "node",
    "description": "Just a sample demonstrating node group selection",
    "defaultconfig": {"triggering_nodegroups":[], "selected_nodegroup": "", "selected_node":"","selected_val": [], "user_groups": []},
    "classname": "EamenaPermissions",
    "component": "views/components/functions/eamena-permissions",
    "functionid": "be239b0a-145d-4e27-bb71-beaa855dcc11"
}


class EamenaPermissions(BaseFunction):

    def get(self):
        raise NotImplementedError

    def save(self, tile, request):
        print("!!! Calling EamenaPermissions function save...")

        data = tile.data
        node = self.config['selected_node']
        value = self.config['selected_val']
        identities = self.config['user_groups']
        print(identities)

        print(tile._getFunctionClassInstances())

        # if tile.data has the config selected node and selected value 
        if data[node] and data[node] in value:

            # grab resource object and see current permissions
            resource_instance = models.ResourceInstance.objects.get(pk=tile.resourceinstance_id)
            resource = Resource.objects.get(pk=tile.resourceinstance_id)

            current_perms = get_restricted_users(resource)
            current_restricted_users = {User.objects.get(pk=userid) for userid in current_perms['no_access']}

            # Find a way to get current restricted groups
            #current_restricted_groups = get_groups_for_object('no_access_to_resourceinstance', resource_instance)
            #print(set(current_restricted_groups))

            # look in config user groups and list who has access = false
            new_restricted_users = {User.objects.get(pk=_user['identityId']) for _user in identities if _user['identityType'] == 'user' and not _user['identityVal']}
            #new_restricted_groups = {Group.objects.get(pk=_group['identityId']) for _group in identities if _group['identityType'] == 'group' and not _group['identityVal']}

            users_to_allow = list(current_restricted_users - new_restricted_users)
            users_to_restrict = list(new_restricted_users - current_restricted_users)
            #groups_to_allow = list(set(current_restricted_groups) - new_restricted_groups)
            #groups_to_restrict = list(new_restricted_groups - set(current_restricted_groups))

            #print({'to allow': users_to_allow + groups_to_allow, 'to restrict': users_to_restrict + groups_to_restrict})
      
            for identityModel in (users_to_restrict):# + groups_to_restrict):
                print(identityModel)
                # first remove all the current permissions
                for perm in get_perms(identityModel, resource_instance):
                    remove_perm(perm, identityModel, resource_instance)

                assign_perm("no_access_to_resourceinstance", identityModel, resource_instance)

            for identityModel in (users_to_allow + groups_to_allow):
                print(identityModel)
                # first remove all the current permissions
                for perm in get_perms(identityModel, resource_instance):
                    remove_perm(perm, identityModel, resource_instance)

            resource = Resource(str(resource_instance.resourceinstanceid))
            # resource.graph_id = resource_instance.graph_id
            resource.index()


# write test, verify that the resource instance permissions are as expected. 
# call ES, get instance and check it is indexed as expected 
# call django gaurdian get_group_perms + get_user_perms,


    # def delete(self, tile, request):
    #     raise NotImplementedError

    # def on_import(self, tile):
    #     raise NotImplementedError

    # def after_function_save(self, functionxgraph, request):
    #     raise NotImplementedError
