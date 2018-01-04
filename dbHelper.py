# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 23:56:32 2018

@author: Nitin
"""
import sqlite3


def createTable(dbname, tablename,colnames,coltypes, colvalues, override=True):

    assert len(colnames) == len(coltypes), "The number of column headers and their types should have the same size"
    ##----------Enter into database---------------###
        
    
    print("Connecting to database...")
    conn = sqlite3.connect(dbname + '.db')
    c = conn.cursor()
    
    #Drop existing table if override is True
    if override:
        print("Dropping existing table...")
        c.execute("DROP TABLE IF EXISTS " + tablename)
        
    else:
        print("Writing to existing table...")
    #Create table based on colnames and colvalues parameters
    #colnames and coltypes are lists specifying the column name and type
    column_query_part = ','.join([colnames[i] + ' ' + coltypes[i] for i in range(len(colnames))])
    table_creation_query = "CREATE TABLE IF NOT EXISTS " + tablename +\
                           " (" + column_query_part + ")"                        
    print(table_creation_query)
    try:
        print("Creating table...")                
        c.execute(table_creation_query)
    except:
        print("Unable to create table.")
    

    print("Inserting values into the table...")
    column_value_part = "INSERT INTO " + tablename +\
                        " (" + ','.join(colnames) + ") " +\
                        "VALUES (" + ",".join(['?']*len(colnames)) +")"
    c.executemany(column_value_part, colvalues)

    # Save (commit) the changes
    conn.commit()
    print("Changes committed.")
    ##----------View contents of database---------------###
    count = 0
    print("Printing top 5 rows of the table.")
    for row in c.execute('SELECT * FROM ' + tablename):
        if count == 4:
            break
        print(row)
        count += 1
    conn.close()
    
