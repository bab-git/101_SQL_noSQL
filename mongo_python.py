# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:55:19 2019

@author: Babak Hosseini
"""

#import pymongo
from pymongo import Connection
from pymongo import MongoClient
client = MongoClient('mongodb://192.168.2.208:27018')

db = client.sms

collection = db.clients
#connection = Connection()
#connection = Connection()