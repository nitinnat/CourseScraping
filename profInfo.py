from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import os
import pickle
import json
import time

def grabProfRatings(override = False):
    if not os.path.exists("./profRatings.pkl"):
        print("Loading professor information for the first time. This may take a while.")
        professorlist = []
        #210 is an arbitrary large number to make sure we have got all the profs' information
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
        print("Professor ratings stored in profRatings.pkl in the current directory.")
    else:
        plist = pickle.load(open("./profRatings.pkl",'rb'))
    
    #Only need to return the computer science prof information
    if not os.path.exists("./CSProfList.pkl"):
        cs_profs_list = []
        for item in plist:
            for sub_item in item:
                if 'computer' in sub_item["tDept"].lower():
                    cs_profs_list.append(sub_item)
                    print("Found...")
        
        #For each professor, grab all their comments, etc from their individual 
        #sites using tid attribute
        
        for i,item in tqdm(enumerate(cs_profs_list)):
            tid = item["tid"]
            profURL =  "http://www.ratemyprofessors.com/ShowRatings.jsp?tid=" + str(tid)
            response = requests.get(profURL)
            soup = BeautifulSoup(response.content, 'html.parser')
            td_class = soup.find_all('td','class')
            td_comments = soup.find_all('td','comments')
            
            """
            #List of lists containing information for each class taken and 
            #comments given
            For example:
            ['CSE586', 'For Credit:', 'Yes', 'Attendance:', 'Not Mandatory', 
            'Textbook Used:', 'No', 'Would Take Again:', 'Yes', 'Grade Received:', 'N/A']
            
            AND
            
            ['TOUGH GRADER', "SKIP CLASS? YOU WON'T PASS.", "Good professor, 
            but the course was very theoretical. At the end of the course, you'll 
            know some distributed algorithms, but wouldn't have made any real-word 
            applications. Quite disorganized and no proper material to study from. 
            Exams are tough.", '0', 'people', 'found this useful', '0', 'people', 
            'did not find this useful', 'report this rating']
            """
            class_info = [list(item.stripped_strings) for item in td_class]
            comment_info = [list(item.stripped_strings) for item in td_comments]
            
            #Add these to the dictionary containing this prof's information
            cs_profs_list[i]["class_info"] = class_info
            cs_profs_list[i]["comment_info"] = comment_info
            pickle.dump(cs_profs_list, open("CSProfList.pkl",'wb'),protocol=2)
    else:
        cs_profs_list = pickle.load(open("./CSProfList.pkl",'rb'))
    return cs_profs_list

