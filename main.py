from bs4 import BeautifulSoup
import requests

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
for i in range(8,len(tr_text)-3):
    temp = tr_text[i].strip().split('\n')
    temp = [st.strip() for st in temp]
    temp = [st for st in temp if not st =='']
    #If length of list is 11, drop the "Room" attribute
    if len(temp) == len(headers) + 1:
        temp.pop(7)
    assert len(temp) == len(headers)
    #Remove intermediate header rows as on webpage
    if not temp[0] == 'Class':
        course_details.append(temp)
    #Format the time column, column 6
    temp[6] = '-'.join([t.strip() for t in temp[6].split('-')])
        
    
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
             Instructor text, Status text)''')
#Insert rows
for i,row in enumerate(course_details):
    value_str = '(' + ','.join(["'" + t + "'" for t in row]) + ')'
    c.execute("INSERT INTO UBcourses VALUES " + value_str)

# Save (commit) the changes
conn.commit()


##----------View contents of database---------------###


for row in c.execute('SELECT * FROM UBcourses'):
    print(row)
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
