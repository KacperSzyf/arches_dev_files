#imports
from fileinput import close
import json
from json.tool import main
from platform import node
from re import sub
from termios import ICRNL
from types import new_class
from uuid import uuid1, uuid4
from django.core.management.base import BaseCommand, CommandError

from arches.app.models.models import Concept as modelConcept
from arches.app.models.concept import Concept
class Command(BaseCommand):
    
    def handle(self, *args, **options):
        conceptSchemeUUID = get_all_concept_schemes()
        lookup_dict = get_concept_uuid_dict("Old_County", conceptSchemeUUID)

        json.dump( lookup_dict, open( "v3topconcept_lookup.json", 'w' ) )
        

def get_all_concept_schemes():
    concepts = modelConcept.objects.all()
    conceptSchemeUUID = []
    for concept in concepts:
        if concept.nodetype_id == "ConceptScheme":
            conceptSchemeUUID.append(str(concept.conceptid))
    return conceptSchemeUUID

def get_concept_uuid_dict(perfLabel, conceptSchemeUUID):
    lookup_dict = {}
    for conceptId in conceptSchemeUUID:
        concept = Concept().get(id = conceptId, include_subconcepts=True)
        if perfLabel == concept.get_preflabel().value:
            for subConcept in concept.subconcepts:
                lookup_dict[subConcept.get_preflabel().value] = subConcept.id
    return lookup_dict