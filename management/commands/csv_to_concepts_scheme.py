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
from django.core.management.base import BaseCommand, CommandError
from arches.app.models.concept import Concept, ConceptValue

class Command(BaseCommand):
    """
    Description:
    This command takes a .csv file containing a list of countries to create Concept Schemes based on them
    The csv can only be one column with a header
    Example:
    
    header,
    data1,
    data2,
    data3,
    
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
        data_tuple = get_data_and_header(csv_path) #splits the csv into title and a list of countries
        header = data_tuple[0]
        data = data_tuple[1]
        
        #Create the parent concept
        main_concept  = create_concept("ConceptScheme", header) # creates a the main concepts
        main_concept.save()
        
        #create a concept for each item in the data
        concepts = []
        for d in data:
            concepts.append(create_concept("Concept", d, main_concept))

        #append all created concepts to parent concept
        main_concept.subconcepts = concepts # concepts = list of all subconcepts
        
        #Save parent concept to db
        main_concept.save()
        
        #Create a collection from parent concept
        main_concept.make_collection()
        


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
    c.id = str(uuid.uuid1())
    c.nodetype = concept_type
    c.conceptid = str(uuid.uuid1())
    c.nodetype_id = concept_type
    c.legacyoid = data
    c.save()
    
    #If function has parent concept create a child
    if parent_concept:
        #Get above basic concept from db
        stub_parent_concept = Concept().get(
                        id=parent_concept.id,
                        include_subconcepts=False,
                        include_parentconcepts=False,
                        include_relatedconcepts=False,
                        depth_limit=None,
                        up_depth_limit=None,
                    )
        stub_parent_concept.relationshiptype = 'hasTopConcept'
        c.parentconcepts.append(stub_parent_concept)
        c.relationshiptype = 'hasTopConcept'
    #Else create parent
    else:
        c.relationshiptype = ''
        c.hassubconcepts = True
        
    #Create a value for the concept
    val = ConceptValue()
    val.conceptid = c.id
    val.type = 'prefLabel'
    val.category = "label"
    val.value = data
    val.language = 'en'
    val.save()
    
    #Add the create value to concept
    c.values.append(val)
    
    #Return just concept
    return c
    
def get_data_and_header(csv_path):
    '''
    Description:
    Function to take a one column list stored as a CSV and return a tuple with
    a header and dataunder the header as list
    
    Parameters:
    :csv_path: Filepath to the csv file
    
    Returns:
    :tuple: containing Header of the CSV file 
    '''
    
    header = ""
    data = []
    
    first = True
    #Open target file as a dictionary
    with open (csv_path, newline="") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        #Loop over all lines in csv reader
        for row in csv_reader:
            #If it is the first time going around the loop set header
            if first:
                header = list(row.keys())[0]
                first = False
            #append the data under the header key to a new list
            data.append(row[list(row.keys())[0]]) #list(row.keys())[0] = Header
    return (header, data)
    
