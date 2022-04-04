import os 
import pandas as pd
from datetime import datetime


def loadDataFrame():
	shootingFolderLocation = "ShootingData\\"

	shootingDataFrame = pd.DataFrame()

	frames = []

	#For Each Year of Shooting Data
	for item in os.listdir(shootingFolderLocation):
		tempShootingDF = pd.read_excel(shootingFolderLocation+item)
		tempShootingDF['DateTime'] = pd.to_datetime(tempShootingDF['DateTime'])
		tempShootingDF['Gang'] = tempShootingDF['Gang'].fillna("").str.title()
		tempShootingDF['DV'] = tempShootingDF['DV'].fillna("").str.title()
		tempShootingDF['GSW'] = tempShootingDF['GSW'].fillna("").str.title()
		tempShootingDF['vFelon'] = tempShootingDF['vFelon'].fillna("").str.title()
		tempShootingDF['VictimMO'] = tempShootingDF['VictimMO'].fillna("").str.title()
		tempShootingDF['Vrace'] = tempShootingDF['Vrace'].fillna("").str.title()
		tempShootingDF['Vsex'] = tempShootingDF['Vsex'].fillna("").str.title()
		tempShootingDF['Ref'] = tempShootingDF['Ref'].fillna("").str.title()
		tempShootingDF['Filed'] = tempShootingDF['Filed'].fillna("").str.title()
		tempShootingDF['Filed'] = tempShootingDF['Filed'].fillna("").str.title()
		tempShootingDF['Patrol'] = tempShootingDF['Patrol'].fillna("").str.upper()
		tempShootingDF['Year'] = item.split(" ")[0]
		frames.append(tempShootingDF)

	shootingDataFrame = pd.concat(frames)

	return shootingDataFrame

def generateSankeyLinks(largeDataFrame):

	path = "C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\KCPD Clearance Dashboard\\Sankeys\\ViolenceDashboard\\"
	sankeys = os.listdir(path)
	dataType = []
	Agency = []
	Category = []
	years = []
	links = []

	for item in sankeys:
		dataType.append("LinksToSankeys")
		justName = item.split(".")[0]
		Agency.append(justName.split(" - ")[1])
		years.append(justName.split(" - ")[0])
		justName = item.replace(" ", "%20")

		link = "https://kcpdclearance.firebaseapp.com/ViolenceDashboard/"+justName
		links.append(link)

	dataFrame = pd.DataFrame()
	dataFrame['dataType'] = dataType
	dataFrame['Agency'] = Agency
	dataFrame['Category'] = links
	dataFrame['Year'] = years
	dataFrame['Homicide'] = 0
	dataFrame['Non-Fatal'] = 0
	dataFrame['Self-Inflicted'] = 0
	dataFrame['Sum'] = 0

	largeDataFrame = pd.concat([largeDataFrame,dataFrame])

	return largeDataFrame


def concatenateCases():
	dataDirectoryLabel = "DataForDashboard\\"
	dataFolder = os.listdir("DataForDashboard")

	largeDataFrame = pd.DataFrame()

	frames = []

	for data in dataFolder:
		tempDataFrame = pd.read_csv(dataDirectoryLabel+data)
		column_list = list(tempDataFrame)
		column_list.remove("dataType")
		column_list.remove("Category")
		column_list.remove("Year")
		tempDataFrame["Sum"] = tempDataFrame[column_list].sum(axis=1, numeric_only=True)

		frames.append(tempDataFrame)
	largeDataFrame = pd.concat(frames)

	largeDataFrame['Year'] = largeDataFrame['Year'].astype(int).astype(str)
	largeDataFrame['Category'] = largeDataFrame['Category'].astype(str)
	largeDataFrame['Category'] = largeDataFrame['Category'].str.replace(', ', " - ")

	largeDataFrame['Agency'] = largeDataFrame['Agency'].str.replace('All', '*All')

	largeDataFrame = generateSankeyLinks(largeDataFrame)

	largeDataFrame.to_csv("CombinedShootingDataV2.csv", encoding = 'utf-8', index = False)

def getYearList():
	currentYear = datetime.now().year
	currentYearList = []

	for year in range(currentYear, 2016, -1):
		currentYearList.append(year)
		currentYearList.sort()
		
	return currentYearList

def getCaseTypes():
	caseTypes = ["B", "H", "S"]

	return caseTypes 

def getCaseLabel(shortCaseType):
	if shortCaseType == "B":
		return "Non-Fatal"

	if shortCaseType == "H":
		return "Homicide"

	if shortCaseType == "S":
		return "Self-Inflicted"

	if shortCaseType == "All":
		return "All"

def getAgencyLabel(agency):
	agencyDataFrame = pd.read_csv("PD Agency.csv",)
	agencyDataFrame = agencyDataFrame[agencyDataFrame['Agency'] == agency]

	agencyLabel = agencyDataFrame['PD NAME'].tolist()[0]
	return agencyLabel

def filterDataFrameByCaseType(dataFrame, shortCaseType):
	caseSpecificDataFrame = dataFrame[dataFrame['Type']==shortCaseType]
	return caseSpecificDataFrame

def filterDataFrameByAgency(dataFrame, agency):
	agencySpecificDataFrame = dataFrame[dataFrame['Agency']==agency]
	return agencySpecificDataFrame

def getListOfAgencies(shootingDataFrame):
	agenciesList = list(set(shootingDataFrame['Agency'].tolist()))

	return agenciesList

def getAgencyDictionary(OldHistoricalKarpelData, agencyList):
	historicalReceived = OldHistoricalKarpelData[0]
	historicalFiled = OldHistoricalKarpelData[1]
	historicalDisposed = OldHistoricalKarpelData[2]
	historicalDeclined = OldHistoricalKarpelData[3]

	agencyCases = []
	#Construct Dictionary of Agency-Specific Cases
	for agency in agencyList:
		tempAgencyCase = []
		agencySpecificReceived = historicalReceived[historicalReceived['Agency']==agency]
		agencySpecificReceived = agencySpecificReceived.reset_index(drop = True)
		tempAgencyCase.append(agencySpecificReceived)
		agencySpecificFiled = historicalFiled[historicalFiled['Agency']==agency]
		agencySpecificFiled = agencySpecificFiled.reset_index(drop = True)
		tempAgencyCase.append(agencySpecificFiled)
		agencySpecificDisposed = historicalDisposed[historicalDisposed['Agency']==agency]
		agencySpecificDisposed = agencySpecificDisposed.reset_index(drop = True)
		tempAgencyCase.append(agencySpecificDisposed)
		agencySpecificDeclined= historicalDeclined[historicalDeclined['Agency']==agency]
		agencySpecificDeclined = agencySpecificDeclined.reset_index(drop = True)
		tempAgencyCase.append(agencySpecificDeclined)
		agencyCases.append(tempAgencyCase)		
	agencyDictionary = dict(zip(agencyList, agencyCases))

	return agencyDictionary