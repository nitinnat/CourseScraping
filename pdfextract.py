# -*- coding: utf-8 -*-
"""
Created on Mon Jan  1 14:56:38 2018

@author: Nitin Nataraj


"""

import PyPDF2
import re
import pickle
import os

"""
#Extracts Course Area information from the graduate handbook pdf
and creates a nested dictionary to hold the information

"""
def extractFromPDF(override = False):
    if (not os.path.exists('./courseDict.pkl')) or (override is True):
        pdfFileObj = open('grad-handbook-2016.pdf', 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        
        #Extract pages 12-14
        pagesNeeded = '\n'.join([pdfReader.getPage(i).extractText() for i in range(11,14)])
        
        #Check page 12 for Focus Areas and Core Courses
        
        ##Find the starting and ending indices to look for, for focus area courses
        pg = pagesNeeded.split('\n')
        count = 0
        while True:
            if 'FocusAreasandCoreCourses' in pg[count]:
                startInd = count
                break
            count += 1
            
        count = 0
        while True:
            if 'Focusareacourses' in pg[count]:
                endInd = count
                break
            count += 1
        
        inds = []
        for i in range(startInd,endInd+1):
            if 'Theory/AlgorithmsArea(T/A)' in pg[i]:
                inds.append(i)
            if 'ArIntelligenceArea(AI)' in pg[i]:
                inds.append(i)
            if 'SoftwareandInformationSystemsArea(SW)' in pg[i]:
                inds.append(i)
            if 'HardwareandNetworkedSystemsArea(HW)' in pg[i]:
                inds.append(i)
        
        courseDict = {}
        #Look for all the courses in this text and add it to the dictionary
        for i,ind in enumerate(inds):
            firstInd = ind
            if i == 3: lastInd = endInd
            else: lastInd = inds[i+1]+1
            courses = re.findall('CSE\d\d\d', '\n'.join(pg[firstInd:lastInd]))
            for j,course in enumerate(courses):
                courseDict[course] = {}
                courseDict[course]['area'] = pg[ind].split('(')[-1].split(')')[0]
                courseDict[course]['prerequisites'] = []
                courseDict[course]['type'] = 'core'
            
        ##Now do the same for the other courses
        startInd = endInd
        endInd = len(pg)-1
        
        otherInds = []
        for i in range(startInd,endInd+1):
            if 'Theory/AlgorithmsArea(T/A)' in pg[i]:
                otherInds.append(i)
            if 'ArIntelligenceArea(AI)' in pg[i]:
                otherInds.append(i)
            if 'SoftwareandInformationSystemsArea(SW)' in pg[i]:
                otherInds.append(i)
            if 'HardwareandNetworkedSystemsArea(HW)' in pg[i]:
                otherInds.append(i)
        
        for i,ind in enumerate(otherInds):
            firstInd = ind
            if i == 2: lastInd = endInd
            else: lastInd = otherInds[i+1]+1
            
            lines = pg[firstInd:lastInd]
            for line in lines:
                courses = re.findall('CSE\d\d\d', line)
                if courses:
                    if not courses[0] in courseDict.keys():
                        
                        courseDict[courses[0]] = {}
                        courseDict[courses[0]]['area'] = pg[ind].split('(')[-1].split(')')[0]
                        courseDict[courses[0]]['type'] = 'elective'
                        if len(courses) > 0:
                            courseDict[courses[0]]['prerequisites'] = courses[1:]
                        else: 
                            courseDict[courses[0]]['prerequisites'] = None
        
        ##-----Enter information into a pickle file-------#
        
        pickle.dump(courseDict,open('courseDict.pkl','wb'),protocol=2)
    else:
        courseDict = pickle.load(open('courseDict.pkl','rb'))
    
    return courseDict
                

                
    
    
