import pandas as pd 
from locationiq.geocoder import LocationIQ
import os, shutil
import time
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyproj import Proj, transform
from datetime import datetime
from HelperMethods import getYearList, getAgencyDictionary

def geocodeCases(tempShootingYear):

	text_file = open("key.txt", "r")
	key = text_file.read()
	geocoder = LocationIQ(key)

	#Initialize DataFrames
	tempIncidentAddressDF = pd.DataFrame()
	tempVictimAddressDF = pd.DataFrame()

	#Filters Shooting Dataframe by Null Latitude and Longitude Values
	noLatLong = tempShootingYear[~tempShootingYear['VLat'].notnull() | ~tempShootingYear['ILat'].notnull()]

	#Initializes Lists
	allIAddresses = []
	allILatitudes = []
	allILongitudes = []

	allVAddresses = []
	allVLatitudes = []
	allVLongitudes = []

	for i, row in noLatLong.iterrows():

		tempIncidentAddress = row['IncidentAddress']
		try:
			tempIncidentCoordinates = geocoder.geocode(tempIncidentAddress)
			tempILat = [float(tempIncidentCoordinates[0]['lat'])]
			tempILng = [float(tempIncidentCoordinates[0]['lon'])]

		except:
			tempILat = [0]
			tempILng = [0]

		tempVictimAddress = row['Vaddress']

		try:
			tempIncidentCoordinates = geocoder.geocode(tempVictimAddress)
			tempVLat = [float(tempIncidentCoordinates[0]['lat'])]
			tempVLng = [float(tempIncidentCoordinates[0]['lon'])]
		except:
			tempVLat = [0]
			tempVLng = [0]

		allIAddresses.append(tempIncidentAddress)
		allILatitudes.extend(tempILat)
		allILongitudes.extend(tempILng)

		allVAddresses.append(tempVictimAddress)
		allVLatitudes.extend(tempVLat)
		allVLongitudes.extend(tempVLng)

		print(tempIncidentAddress)

	tempIncidentAddressDF['IncidentAddress'] = allIAddresses
	tempIncidentAddressDF['IncidentLatitude'] = allILatitudes
	tempIncidentAddressDF['IncidentLongitude'] = allILongitudes

	iLatDict = dict(zip(tempIncidentAddressDF.IncidentAddress, tempIncidentAddressDF.IncidentLatitude))
	iLonDict = dict(zip(tempIncidentAddressDF.IncidentAddress, tempIncidentAddressDF.IncidentLongitude))

	tempShootingYear.ILat = tempShootingYear.ILat.fillna(tempShootingYear.IncidentAddress.map(iLatDict))
	tempShootingYear.ILng = tempShootingYear.ILng.fillna(tempShootingYear.IncidentAddress.map(iLonDict))

	tempVictimAddressDF['VictimAddress'] = allVAddresses
	tempVictimAddressDF['VictimLatitude'] = allVLatitudes
	tempVictimAddressDF['VictimLongitude'] = allVLongitudes

	VLatDict = dict(zip(tempVictimAddressDF.VictimAddress, tempVictimAddressDF.VictimLatitude))
	VLonDict = dict(zip(tempVictimAddressDF.VictimAddress, tempVictimAddressDF.VictimLongitude))

	tempShootingYear.VLat = tempShootingYear.VLat.fillna(tempShootingYear.Vaddress.map(VLatDict))
	tempShootingYear.VLng = tempShootingYear.VLng.fillna(tempShootingYear.Vaddress.map(VLonDict))

	return tempShootingYear

def withinFunction(dataframe):
	CRN = []
	KansasCity = []
	JacksonCounty = []
	tempWithinDataFrame = pd.DataFrame()

	tempDataFrame = dataframe
	#tempDataFrame = dataframe[~dataframe['JaCo'].notnull()]
	
	geometry = [Point(xy) for xy in zip(tempDataFrame['ILng'], tempDataFrame['ILat'])]
	crs = 'EPSG:4326'
	points = gpd.GeoDataFrame(tempDataFrame, crs=crs, geometry=geometry)

	JacksonCountyBorder = gpd.GeoDataFrame.from_file("Maps\\JacksonCountyCorrectCRS.shp").loc[0]
	KansasCityBorder = gpd.GeoDataFrame.from_file("Maps\\KansasCityCorrectCRS.shp").loc[0]

	for i, pt in tempDataFrame.iterrows():
		CRN.append(pt['CRN'])
		if JacksonCountyBorder.geometry.contains(pt.geometry) or pt['Patrol'] == 'EPD' or pt['Patrol'] == 'SPD' or pt['Patrol'] == 'EPD' or pt['Patrol'] == 'MPD' or pt['Patrol'] == 'CPD' or pt['Agency']!=2:
			JacksonCounty.append("Yes")
		else:
			JacksonCounty.append("No")

		if KansasCityBorder.geometry.contains(pt.geometry):
			KansasCity.append("Yes")
		else:
			KansasCity.append("No")

	tempWithinDataFrame['CRN'] = CRN
	tempWithinDataFrame['KansasCity'] = KansasCity
	tempWithinDataFrame['JacksonCounty'] = JacksonCounty

	jcDict = dict(zip(tempWithinDataFrame.CRN, tempWithinDataFrame.JacksonCounty))
	kcDict = dict(zip(tempWithinDataFrame.CRN, tempWithinDataFrame.KansasCity))

	dataframe.JaCo = dataframe.JaCo.fillna(dataframe.CRN.map(jcDict))
	dataframe.KansasCity = dataframe.KansasCity.fillna(dataframe.CRN.map(kcDict))

	return dataframe

def getNewestFile(weeklyUpload):

	#Initializes Blank List 
	allDates = []

	#Loops through the Weekly Data Drop Folder
	for item in os.listdir(weeklyUpload):

		#Pulls the Date from Each File in the Folder
		date = int(item.split("_")[1])

		#Appends it to a list
		allDates.append(date)

	#Removes all the duplicates
	allDates = list(set(allDates))

	#Sorts the List without Duplicates
	allDates.sort()

	#Grabs the most recent file
	mostRecent = str(allDates[-1])

	#Returns that most recent file. 
	return mostRecent

def loadKarpelCases(directory, mostRecent):
	karpelDataFrames = []

	#Old Received Cases
	oldReceivedCases = pd.read_csv("OldHistoricalKarpelData\\1 - Received.csv")
	oldReceivedCases = oldReceivedCases[['File #', "CRN", "Enter Dt.", "Def. Name", "Def. Sex", "Def. Race", "Def. DOB", "Agency"]]
	oldReceivedCases = oldReceivedCases[oldReceivedCases['Agency'] == 2]

	#New Received Cases
	receivedCases = pd.read_csv(directory + "Rcvd_"+mostRecent+"_1800.CSV", encoding='utf-8')

	receivedCases = receivedCases.rename({'Def  Name': 'Def. Name', 'Enter Dt ': 'Enter Dt.', 'Def  DOB': "Def. DOB", "Def  Race":"Def. Race", "Def Sex":"Def. Sex"}, axis=1) 
	receivedCases = receivedCases[['File #', "CRN", "Enter Dt.","Def. Name", "Def. Race", "Def. Sex", "Def. DOB",  "Agency"]]
	receivedCases = receivedCases[receivedCases['Agency'] == 2]

	oldReceivedCases = pd.concat([oldReceivedCases, receivedCases])
	
	oldReceivedCases = oldReceivedCases.dropna(subset = ['CRN'])
	oldReceivedCases = oldReceivedCases[oldReceivedCases['CRN'].str.contains(r'\d')]
	#oldReceivedCases['CRN'] = oldReceivedCases['CRN'].astype(str).str.replace(r'\D+', '').str[:2] + "-" + oldReceivedCases['CRN'].astype(str).str.replace(r'\D+', '').str[2:].astype('int64').astype(str)
	karpelDataFrames.append(oldReceivedCases)

	#Old Filed Cases
	oldFiledCases = pd.read_csv("OldHistoricalKarpelData\\2 - Filed.csv")
	oldFiledCases = oldFiledCases[['File #', 'Def. Name', "CRN", "Filing Dt.", "Enter Dt.", "Agency"]]
	oldFiledCases = oldFiledCases[oldFiledCases['Agency'] == 2]

	#New Filed Cases
	filedCases = pd.read_csv(directory + "Fld_"+mostRecent+"_1800.CSV", encoding='utf-8')
	filedCases = filedCases[['File #', 'Def. Name', "CRN", "Enter Dt.", "Filing Date.", "Agency"]]
	filedCases = filedCases[filedCases['Agency'] == 2]
	filedCases = filedCases.rename(columns={'Filing Date.': 'Filing Dt.'})
	oldFiledCases = pd.concat([oldFiledCases, filedCases])
	karpelDataFrames.append(oldFiledCases)

	#Old Disposed Cases
	oldDisposedCases = pd.read_csv("OldHistoricalKarpelData\\3 - Disposed.csv")
	oldDisposedCases = oldDisposedCases[["File #", "CRN", "Disp. Code", "Disp. Dt.", "Agency", "Enter Dt."]]
	oldDisposedCases = oldDisposedCases[oldDisposedCases['Agency'] == 2]

	#New Disposed Cases
	disposedCases = pd.read_csv(directory + "Disp_"+mostRecent+"_1800.CSV", encoding='utf-8')
	disposedCases = disposedCases[["File #", "CRN", "Disp. Code", "Disp. Dt.", "Agency", "Enter Dt."]]
	disposedCases = disposedCases[disposedCases['Agency'] == 2]
	oldDisposedCases = pd.concat([oldDisposedCases, disposedCases])

	#oldDisposedCases = oldDisposedCases.append(disposedCases)

	disposalReasons = pd.read_csv("Disposition Codes.csv", encoding = 'utf-8')
	oldDisposedCases = oldDisposedCases.merge(disposalReasons, on = 'Disp. Code', how = 'left')
	karpelDataFrames.append(oldDisposedCases)

	#Old Refused Cases
	oldDeclinedCases = pd.read_csv("OldHistoricalKarpelData\\4 - Refused.csv")
	oldDeclinedCases = oldDeclinedCases[["File #", "CRN", "Disp. Code", "Disp. Dt.", "Agency", "Enter Dt."]]
	oldDeclinedCases = oldDeclinedCases[oldDeclinedCases['Agency'] == 2]

	declinedCases = pd.read_csv(directory + "Ntfld_"+mostRecent+"_1800.csv")
	declinedCases = declinedCases[["File #", "CRN", "Disp. Code", "Disp. Dt.", "Agency", "Enter Dt."]]
	oldDeclinedCases = pd.concat([oldDeclinedCases, declinedCases])

	declineReasons = pd.read_csv("RefusalReasons.csv", encoding = 'utf-8')
	oldDeclinedCases = oldDeclinedCases.merge(declineReasons, on = 'Disp. Code', how = 'left')
	oldDeclinedCases = oldDeclinedCases[["File #", "CRN", "Reason", "Disp. Dt.", "Agency", "Enter Dt.", "Activity"]]
	oldDeclinedCases = oldDeclinedCases.rename(columns = {'Reason':'Disp. Code'})

	karpelDataFrames.append(oldDeclinedCases)

	return karpelDataFrames

def fixCRNS(shootingDataFrame):

	shootingDataFrame['CRN'] = shootingDataFrame['CRN'].astype(str)

	fixedCRNS = []
	for i, row in shootingDataFrame.iterrows():
		
		if "KC" not in row['CRN'] and "-" not in row['CRN'] and row['Agency'] == 2:
			fixedCRN = row['CRN'][0:2] + "-" + row['CRN'][2:]
		else:
			fixedCRN = row['CRN']
		fixedCRNS.append(fixedCRN)

	shootingDataFrame['CRN'] = fixedCRNS

	return shootingDataFrame

def checkReferrals(shootingDataFrame, OldHistoricalKarpelData, agencyList):
	CRN = []
	Referred = []
	Filed = []
	Disposed = []
	Declined = []
	Review = []

	agencyDictionary = getAgencyDictionary(OldHistoricalKarpelData, agencyList)

	for i, row in shootingDataFrame.iterrows():
		tempAgency = row['Agency']
		agencySpecificList= agencyDictionary.get(tempAgency)

		#Check Received Cases
		if row['CRN'] in agencySpecificList[0]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Referred.append("Yes")
		elif row['CRN'] not in agencySpecificList[0]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Referred.append("No")
		else:
			Referred.append("NoJuris")

		#Check Filed Cases
		if row['CRN'] in agencySpecificList[1]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Filed.append("Yes")
		elif row['CRN'] not in agencySpecificList[1]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Filed.append("No")
		else:
			Filed.append("NoJuris")

		#Check Disposed Cases
		if row['CRN'] in agencySpecificList[2]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Disposed.append("Yes")
		elif row['CRN'] not in agencySpecificList[2]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Disposed.append("No")
		else:
			Disposed.append("NoJuris")

		#Check Declined Cases
		if row['CRN'] in agencySpecificList[3]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Declined.append("Yes")
		elif row['CRN'] not in agencySpecificList[3]['CRN'].tolist() and row['JaCo'] == 'Yes':
			Declined.append("No")
		else:
			Declined.append("NoJuris")

		if Declined[i]=='No' and Filed[i]=='No' and Referred[i] == 'Yes':
			Review.append("Yes")
		elif Declined[i]=='NoJuris' or Filed[i]=='NoJuris' or Referred[i] == 'NoJuris':
			Review.append("NoJuris")
		else:
			Review.append("No")

	shootingDataFrame = shootingDataFrame.reset_index(drop=True)

	shootingDataFrame['Ref'] = Referred
	shootingDataFrame['Filed'] = Filed
	shootingDataFrame['Disposed'] = Disposed
	shootingDataFrame['Declined'] = Declined
	shootingDataFrame['Review'] = Review

	return shootingDataFrame

def prepareData(shootingDataFrame, agencyList):

	#Location to Shooting Data
	shootingFolderLocation = "ShootingData\\"

	#Remove Old Analysis from DataForDashboard
	#Deletes and Remakes Data For Dashboard Folder
	if os.path.exists("DataForDashboard"):
		shutil.rmtree("DataForDashboard")
	os.makedirs("DataForDashboard")

	#Location to Daily Karpel Data Update
	weeklyUpload = "H:\\Units Attorneys and Staff\\01 - Units\\DT Crime Strategies Unit\\Weekly Update\\"
	
	#Calling loadKarpelCases using the newest potential data
	karpelCases = loadKarpelCases(weeklyUpload, getNewestFile(weeklyUpload))

	#For Each Year in Shooting Data Location (2017 through the present)
	for year in getYearList():
		tempShootingDF = shootingDataFrame[shootingDataFrame['DateTime'].dt.year == year]
		tempShootingDF = tempShootingDF.reset_index(drop=True)

		#Geocode Cases
		tempShootingDF = geocodeCases(tempShootingDF)

		#Within
		tempShootingDF = withinFunction(tempShootingDF)

		#Check Referrals, Filings, Declines, and Disposals
		tempShootingDF['CRN']

		tempShootingDF = checkReferrals(tempShootingDF, karpelCases, agencyList)

		#Export Each Updated Dataframe to Excel
		tempShootingDF.to_excel(shootingFolderLocation+str(year) + " Shooting Data.xlsx", index= False)

	return karpelCases
