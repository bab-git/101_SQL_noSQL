# SQL_py_noSQL

A classification task based on noSQL databases (mongoDB) writting in python.


## mongo_to_google_data_extract.py
The pipeline to extract data from mongoDB and to save to google spread sheet for annotation.


## add_device_google_sheet.py
The pipeline add new devices to the already extracted mongoDB data in the google spread sheet
for annotation.

## H_annot_google_sheet.py
The pipeline filters the already extracted mongoDB data of the google spread sheet based on the hand-coded annotation list (H-annot).

## forward_annot_google_sheet.py
The pipeline brings not annotated cases or missed cases forward (higher rows) 
int the google sheet to be annotated earlier.


## traj_extract.py
The pipeline extract sequene data for cases we need the trajectory of the fails to performs a temporal analysis on the data.

## classifier_design.py
Analyzing of the annotated data of mongoDB (stored in google sheets) which contain failed-checks to train or hand-design check classifiers


## mongo_classifier.py
The module contains the hand-coded labeling rules and the designed classifiers for check categorization.

## Classifier_eval.py
Evaluating the designed classifier using mongoDB data