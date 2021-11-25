import pandas as pd
filePath = input("Enter csv file name [full path]: ")
while ".csv" not in filePath:
    print(filePath + " is not a csv file.")
    filePath = input("Enter csv file name [full path]: ")
fileName = ""

def extractFileName(path):
    y = path.find(".")
    x = 0
    for i in range(y,0,-1):
        if path[i] == "/":
            x = i+1
            break
    return path[x:y]

fileName = extractFileName(filePath)

fileDict = {}
dummy = ""
csvFile = open(filePath, "r")
i = 0
while 1:
    dummy = csvFile.readline()
    if dummy == "":
        break
    fileDict[i] = dummy.split(",")
    i+=1
csvFile.close()

typeDict = {}
response = input("Would you like to auto-detect and assign data types to table columns?(y/n): ")
response = response.lower()
while response != "y" and response != "n":
    print("Invalid input")
    response = input("Enter y/n: ")

pos = 0
row = 1
if response == "y": #auto assign data type
    print("In order to detect the suitable data type, you need to enter the row number of the first row that has complete values in all its columns")
    row = input("Enter row number here: ")
    while row.isnumeric() == False:
        print("Invalid input. Input must be a number")
        row = input("Enter row number here: ")

    for i in fileDict[int(row)-1]:  
        if i == "" or i == "\n":
            typeDict.update({fileDict[0][pos]:"VARCHAR(255)"}) #Null cells is assigned varchar by default
        elif i.isnumeric():
            typeDict.update({fileDict[0][pos]:"INT"})    #Assign float value to numbers
        elif "." in i:
            try:
                test = float(i)
                typeDict.update({fileDict[0][pos]:"FLOAT(24)"})
            except ValueError:
                typeDict.update({fileDict[0][pos]:"VARCHAR(255)"})
        elif i[0].isnumeric() and len(i) == 10 and "-" in i:
            typeDict.update({fileDict[0][pos]:"DATE"})
        else:
            typeDict.update({fileDict[0][pos]:"VARCHAR(255)"}) #Any other type is varchar by default
        pos+=1
else:
    for i in fileDict[row]:
        typeDict.update({fileDict[0][pos]:"VARCHAR(255)"}) #assign varchar as default data type
        pos+=1


# print("Detected data types: ")
# print(typeDict)

# print(fileDict)
sqlFileName = filePath[:-4] + "_copy.sql"
try:
    print("New filename is: " + sqlFileName)
    sqlFile = open(sqlFileName, "x")
except FileExistsError:
    print("File '" + sqlFileName +"' already exists. It will be overwritten.")
sqlFile = open(sqlFileName, "w")

#create database
sqlFile.write("/* DROP DATABASE IF EXISTS " + fileName + "_db;\nCREATE DATABASE IF NOT EXISTS " + fileName + "_db;\nUSE " + fileName + "_db; */\n\n")
#create table
sqlFile.write("DROP TABLE IF EXISTS " + fileName + ";\n")
sqlFile.write ("CREATE TABLE " + fileName +" (\n")
for i in fileDict[0]:
    if "\n" in i: 
       
        sqlFile.write("   " + i[0:i.find("\n")] + " " + typeDict[i] + " \n);\n\n")
    else:
        sqlFile.write("   " + i + " " + typeDict[i] + ",\n")
#insert values into table
sqlFile.write("INSERT INTO '" +  fileName + "' VALUES ")
for i in range(1,len(fileDict)):
    sqlFile.write("  (")
    count = 0
    for j in fileDict[i]:
        if typeDict[fileDict[0][count]] == "FLOAT(24)" or typeDict[fileDict[0][count]] == "INT": #don't add quotes to numeric values
            if "\n" in j:
                sqlFile.write(j[0:j.find("\n")]) #remove newline character, don't add comma
            else:    
                sqlFile.write(j + ",") #add comma
        else:   #add quote to other values
            if "\n" in j:
                 sqlFile.write("'" + j[0:j.find("\n")] + "'") #remove newline character, don't add comma
            else:
                sqlFile.write("'"+ j +"',")    #add comma
        count+=1
    if i == len(fileDict)-1: sqlFile.write(");\n\n")
    else: sqlFile.write("),\n")
sqlFile.close()
print(str(len(fileDict)) + " values inserted into query: " + sqlFileName)

