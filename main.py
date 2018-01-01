from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

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
        and (not temp[2] in ['Supervised Research', 'Thesis Guidance','Independent Study'])):
        
        ##Get information about the course by scraping its site
        courseInfoURL = "https://catalog.buffalo.edu/courses/index.php?abbr=CSE&num=" + str(temp[1].split()[1][0:3])
        temppage = requests.get(courseInfoURL)
        tempsoup = BeautifulSoup(temppage.content, 'html.parser')
        p =  tempsoup.find_all('p',{ "class" : "course-description" })
        for wrapper in p:
            course_desc = wrapper.get_text()
        temp.append(course_desc)
        
        #Format the time column, column 6
        if temp[6] != 'TBA':
            temp[6] = '-'.join([t.strip() for t in temp[6].split('-')])
        course_details.append(temp)
headers.append('Course Information')

       
    
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
             Instructor text, Status text, CourseInfo text)''')



"""
#Insert rows
for i,row in enumerate(course_details):
    #value_str = '(' + ','.join(["'" + t + "'" for t in row]) + ')'
    temp_store = []
    for item in row:
"""        
c.executemany("""INSERT INTO UBcourses (Class, Course, Title, Section, 
                Type, Days, Time, Location, Instructor, Status, CourseInfo) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""", course_details)

# Save (commit) the changes
conn.commit()

##----------View contents of database---------------###
for row in c.execute('SELECT * FROM UBcourses'):
    print(row)
conn.close()
