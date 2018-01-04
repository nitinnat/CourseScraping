from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import os
import pickle
import json
import time
from profInfo import grabProfRatings  #Function to get info from Rate My Professors




##----------Load course information---------------###
if not os.path.exists("./courseDict.pkl"):
    #Run pdfextract.py file
    print("Extracting course area information from the pdf...")
    exec(open('pdfextract.py').read())
else:
    print("Loading course area information from pickle file...")
    courseDict = pickle.load(open("courseDict.pkl",'rb'))

##----------Retrieve page content---------------###
courseScheduleURL = "http://www.buffalo.edu/class-schedule?switch=showcourses&semester=spring&division=GRAD&dept=CSE"
page = requests.get(courseScheduleURL)
soup = BeautifulSoup(page.content, 'html.parser')

##----------Retrieve headers---------------###

tr = soup.find_all('tr')
tr_text = [tr[i].get_text().replace(u'\xa0', u' ') for i in range(len(tr))
            if not tr[i].get_text() == '\n\n']
headers = tr_text[7].strip().split('\n')
headers = [header.strip() for header in headers]
headers.remove('Room') #Not required for any analysis. Most of them have ARR


##----------Retrieve content in each row---------------###
course_details = []
for i in tqdm(range(8,len(tr_text)-3)):
    temp = tr_text[i].strip().split('\n')
    temp = [st.strip() for st in temp]
    temp = [st for st in temp if not st =='']
    #If length of list is 11, drop the "Room" attribute
    if len(temp) == len(headers) + 1:
        temp.pop(7)
    
    #Remove intermediate header rows as on webpage
    #Remove Thesis Guidance, Independent Study and Supervised Research
    if (not temp[0] == 'Class'
        and (not temp[2] in ['Supervised Research', 'Thesis Guidance',
             'Independent Study', 'Computr Sci For Nonmajr 1',
             'Computr Sci For Nonmajr 2'])
        ):

        ##Get information about the course by scraping its site
        courseCatalogURL = "https://catalog.buffalo.edu/courses/index.php?abbr=CSE&num=" + str(temp[1].split()[1][0:3])
        temppage = requests.get(courseCatalogURL)
        tempsoup = BeautifulSoup(temppage.content, 'html.parser')
        p =  tempsoup.find_all('p',{ "class" : "course-description" })
        for wrapper in p:
            course_desc = wrapper.get_text()
        temp.append(course_desc)
        
        ##Add the course focus area and type information
        try:
            temp.append(courseDict['CSE' + temp[1].split()[-1][0:3]]['area'])
        except KeyError:
            temp.append('N/A')
        
        try:
            temp.append(courseDict['CSE' + temp[1].split()[-1][0:3]]['type'])
        except KeyError:
            temp.append('N/A') 
        try:
            temp.append(str(courseDict['CSE' + temp[1].split()[-1][0:3]]['prerequisites']))
        except KeyError:
            temp.append('N/A')
        
        ##Now to scrape the professor and course rating info!
        ##Part 1 - Scrape prof's full name from UB Course directory
        courseInfoURL = '''http://www.buffalo.edu/class-schedule?switch=showclass&semester=
                            spring&division=GRAD&dept=CSE&regnum=''' + str(temp[0])
        temppage2 = requests.get(courseInfoURL)
        tempsoup2 = BeautifulSoup(temppage2.content, 'html.parser')
        profLookupLink =  [link['href'] for link in tempsoup2.find_all('a', href=True, text='look up')]
        print(profLookupLink)
        try:
            profLookupLink = profLookupLink[0]
            #Part 2 - Scrape the prof's full name from the directory
            
            temppage3 = requests.get(profLookupLink)
            tempsoup3 = BeautifulSoup(temppage3.content, 'html.parser')
            profFullName = [b_tag.get_text() for b_tag in tempsoup3.find_all('b') 
                            if temp[8].split(',')[0].lower() in b_tag.get_text().lower()][0]
            temp.append(profFullName)
            
            #Part 3 - Scrape the prof's ratings from Rate My Professors
        except IndexError:
            profLookupLink = 'N/A'
            temp.append('N/A')
        
        
        
    
        #Format the time column, column 6
        if temp[6] != 'TBA':
            temp[6] = '-'.join([t.strip() for t in temp[6].split('-')])
        course_details.append(temp)
headers.append('Course Information')
headers.append('Focus Area')
headers.append('Core/Elective')
headers.append('Prerequisites')
headers.append('Prof Full Name')


       

##----------Enter into database---------------###
    
import sqlite3
conn = sqlite3.connect('CourseSchedule.db')
c = conn.cursor()

#Drop existing table
c.execute('''DROP TABLE IF EXISTS UBcourses''')

#Create table
c.execute('''CREATE TABLE IF NOT EXISTS UBcourses
             (Class text, Course text, 
             Title text, Section text, 
             Type text, Days text,
             Time text, Location text,
             Instructor text, Status text, 
             CourseInfo text, FocusArea text,
             CoreElective text, Prerequisites text,
             ProfFullName text)''')



     
c.executemany('''INSERT INTO UBcourses (Class, Course, Title, Section, 
                Type, Days, Time, Location, Instructor, Status, CourseInfo,
                FocusArea, CoreElective, Prerequisites,ProfFullName) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', course_details)

# Save (commit) the changes
conn.commit()

##----------View contents of database---------------###
for row in c.execute('SELECT * FROM UBcourses'):
    print(row)
conn.close()
