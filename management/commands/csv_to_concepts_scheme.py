#imports
from fileinput import close
from json.tool import main
from platform import node
from re import sub
from termios import ICRNL
from types import new_class
from uuid import uuid1, uuid4
import uuid
import csv
import sys
from django.core.management.base import BaseCommand, CommandError
from arches.app.models.concept import Concept, ConceptValue

sys.setrecursionlimit(14196) # TODO: This needs sorting, its dodgy 

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

        #Get data to process
        #data_tuple[0] = header, data_tuple[1] = countries 
        data_tuple = get_countries_and_header(csv_path) #splits the csv into title and a list of countries
        
        #Create the parent concept
        main_concept  = create_concept("ConceptScheme", data_tuple[0]) # creates a the main concepts
        main_concept.save()
        
        #create a concept for each item in the datat_uple
        concepts = []
        for country in data_tuple[1]:
            concepts.append(create_concept("Concept", country, main_concept))

        #add all the subconcepts to parent concepts 
        main_concept.subconcepts = concepts # concepts = list of all subconcepts 
        main_concept.save()


def create_concept(concept_type, data, parent_concept = None):
    '''
    Descriptions:
    Function to create a concept and its value (if needed)
     
    Parameters:
    :concept_type: string deciding what type of concept is to be made
    :data: string containing the data to be stored in concept.data
    :parent_concept: a Concept object to be referenced as a parent for the new Concept being created
    
    Returns:
    :c: the concept object being created
    '''
    
    #Create the base concept
    c = Concept()
    c.id = uuid.uuid1()
    c.nodetype = concept_type
    c.conceptid = uuid.uuid1()
    c.nodetype_id = concept_type
    
    #Decide if concept is a parent or a child 
    if parent_concept:
        c.parentconcepts.append(parent_concept)
        c.relationshiptype = 'narrower'
    else:
        c.relationshiptype = 'hasTopConcept'
        c.hassubconcepts = True
        c.values = []
    c.legacyoid = data
    c.save()
    
    #Create a value for the concept
    val = ConceptValue()
    val.conceptid = c.id
    val.type = 'prefLabel'
    val.category = "label"
    val.value = data
    val.language = 'en'
    val.save()
    
    #If the concept is a child add the value created to itself
    if parent_concept:
        c.values = []
    else:
        c.values.append(val)
    
    return c
    
def get_countries_and_header(csv_path):
    '''
    Description:
    Function to take a one column list stored as a CSV and return a tuple with
    a header and datalist
    
    Parameters:
    :csv_path: Filepath to the csv file
    
    Returns:
    :tuple: containing Header of the CSV file 
    '''
    
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
    return (header, countries)
    
