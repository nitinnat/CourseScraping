# -*- coding: utf-8 -*-
"""
Created on Mon Jan  1 22:26:03 2018

@author: Nitin

This piece of code grabs professor rating information from the Rate My Professors website and 
stores them in a pickle file.
"""
import requests
import json
import time
import pickle

"""
counter = 0
professorlist = []
for i in range(1,210):
    query = "http://www.ratemyprofessors.com/filter/professor/?department=&institution=University+at+Buffalo&page="+str(i)+"&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=960"
    try:
        print("Trying " + str(i) )
        page = requests.get(query)
        jsonpage = json.loads(page.content)
        professorlist.append(jsonpage['professors'])
        
    except:
        pass
    time.sleep(1)
    
plist = [p for p in professorlist if p != []]
pickle.dump(plist, open("profRatings.pkl",'wb'),protocol=2)
"""
plist = pickle.load(open("./profRatings.pkl",'rb'))
comp_list = []
for item in plist:
    for sub_item in item:
        if 'computer' in sub_item["tDept"].lower():
            comp_list.append(sub_item)
            print("Found...")