# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 17:22:35 2019

@author: Babak Hosseini
"""
#import rhinoscriptsyntax as rs
import json
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#from PIL import Image
import io, bson, multiprocessing
#import bson
filename_meta = "C:\Databases\sms_exported_mongodb_collections\client.metadata.json"
filename = "C:\Databases\sms_exported_mongodb_collections\client.bson"

data = bson.decode_file_iter(open(filename, 'rb'))

product_to_category=dict()

f=open(filename_meta, 'rb')
data_meta = json.load(f)

df = pd.DataFrame(bson.decode_all(f.read()))

for c,d in enumerate(data):
    product_id = d['_id']
    category_id = d['category_id']
    product_to_category[product_id] = category_id