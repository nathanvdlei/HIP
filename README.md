# HIP
### Background:
This project presents the Highway Inspection Planning (HIP) prototype. The main idea here is to be able to use the publically available accidents dataset called BRON to assess the likelihood a specific accident caused damage to the Dutch highway system. This information can then be used to optimize inspection plannings for maintenance contractors.

This repository was developed for the Knowledge Engineering course (2020-2021) at the Vrije Universitieit (VU) in Amsterdam. The CommonKADS model was applied to achieve the structure demonstrated in this prototype.


### How to use:
Step 1: To use the application download the one of the accident dataset yourself from the BRON database:
    https://data.overheid.nl/dataset/9841-verkeersongevallen---bestand-geregistreerde-ongevallen-nederland. We have tested compatebility with the 2010-2019 version.

Step 2: Download the HIP project to your local machine

Step 3: Open the DEMO Jupyter Notebook to interact with the data

Step 4: Change the file location of the dataset to your local copy of the database from step 1. Change the file location of the field name descriptions file to the location on your machine.

Step 5: You can interact with the knowledge based HIP system using the DEMO notebook

### Documentation:

The HIP.py file contains some general input functions. The data itself, i.e. accidents, road segments and parties, are imported from the downloaded csv files and are stored in Pandas dataframes.  The BRON database is structured in such a way that reference files are used to explain specific variable IDs. The reference files are all downloaded and stored in a dictionary ref_files. 

The HIP.py file also contains two classes: Accident and Roadsegment. These classes are the object-oriented approach to the assesment and planning tasks. The expected damage assesment is performed in HIP.Accident.assesment_task_assess_damage_level(). The planning task is not yet implemented, but it is possible to print the accidents with abstracted features that happend on a specific road segment using HIP.Roadsegment.print_accidents_on_roadsegment_details()
