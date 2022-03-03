
from fileinput import close
from json.tool import main
from platform import node
from re import sub
from termios import ICRNL
from types import new_class
from uuid import uuid1, uuid4
import uuid
from django.core.management.base import BaseCommand, CommandError

#imports
import csv
from arches.app.models import concept
import sys
sys.setrecursionlimit(14196)

# from arches.app.models.concept import Concept
# from arches.app.models.models import Concept, DRelationType 
from arches.app.models.concept import Concept, ConceptValue
from arches.app.models.models import DNodeType, Value
from arches.app.models.models import Relation


# from arches.app.models.concept import Concept

#Core Arches
# from arches.app.models.concept import Concept

class Command(BaseCommand):
    """
    Description:
    This command takes a .csv file containing a list of countries to create Concept Schemes based on them 
    Parameters:
    '-s': path to .csv
    Returns:
    Saves concept schemes to database 
    """
    def add_arguments(self, parser):

        parser.add_argument("-s", "--source", action="store", dest="file_path", default="", help="File path to csv containing ResourceID's")

        

    def handle(self, *args, **options):
    
        #Load CSV
        csv_path = options['file_path']
        create_concept_scheme() # does nothing other than printing some stuff 

        data_tuple = get_countries_and_header(csv_path) #splits the csv into title and a list of countries
        print(data_tuple[1])
        main_concept  = create_concept("ConceptScheme", data_tuple[0]) # creates a the main concepts
        print(vars(main_concept))
        breakpoint()
        main_concept.save()
        # print(vars(main_concept[0]))
        # print(vars(main_concept[1]))
        
        # print("val", main_concept[0].values)
        concepts = []
        for country in data_tuple[1]:
            # main_concept.subconcepts.append(create_concept("Concept", country, main_concept ))
            concepts.append(create_concept("Concept", country, main_concept))
        # main_concept.save()
        breakpoint
        main_concept.subconcepts = concepts # concepts = list of all subconcepts 
        main_concept.save()
        print(vars(main_concept))
        print(data_tuple[0], data_tuple[1][1]) #43


def create_concept(concept_type, data, subconcept = None):
    c = Concept()
    c.id = uuid.uuid1()
    c.nodetype = concept_type
    c.conceptid = uuid.uuid1()
    c.nodetype_id = concept_type
    if subconcept:
        c.parentconcepts.append(subconcept)
        c.relationshiptype = 'narrower'
    else:
        c.relationshiptype = 'hasTopConcept'
        c.hassubconcepts = True
        c.values = []
    c.legacyoid = data
    c.save()
    
    val = ConceptValue()
    val.conceptid = c.id
    val.type = 'prefLabel'
    val.category = "label"
    val.value = data
    val.language = 'en'
    
    val.save()
    if subconcept:
        c.values = []
    else:
        c.values.append(val)
    
    
    
    return c
    
    
def create_concept_scheme():
    concept = Concept().get(
                id='117cddf0-8403-4e16-b325-43327efc9e1f',
                include_subconcepts=True,
                include_parentconcepts=True,
                include_relatedconcepts=True,
                depth_limit=None,
                up_depth_limit=None,
            )
    print(vars(concept))
    print(vars(concept.subconcepts[0]))
    
def get_countries_and_header(csv_path):
    header = ""
    countries = []
    
    first = True
    #Open target file as a dictionary
    with open (csv_path, newline="") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        #Copy all ResourceID's to new array
        for row in csv_reader:
            if first:
                header = list(row.keys())[0]
                first = False
            countries.append(row["Country"])
    print("countriers", len(countries))
    return (header, countries)
    
