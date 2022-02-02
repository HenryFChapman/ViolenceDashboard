import os
import pandas as pd
import numpy as np
from geopy import distance
import math
import geopandas as gpd
from pyproj import CRS, Proj, transform
from shapely.geometry import Point
from pandas.api.types import CategoricalDtype 
import datetime as dt
from datetime import datetime
from DataPreparer import loadKarpelCases, getNewestFile
from HelperMethods import getYearList, getCaseLabel, getCaseTypes, filterDataFrameByCaseType


def getVictimGender(shootingDataFrame, agencyLabel):
	gender = pd.DataFrame()
	caseTypes = getCaseTypes()
	
	#For Each Year of Shooting Data
	for tempYear in getYearList():
		genderList = list(set(shootingDataFrame['Vsex'].tolist()))
		cleanedList = [x for x in genderList if x != '']

		tempVictimGenderDF = pd.DataFrame(index=cleanedList)
		tempVictimGenderDF.reset_index()
		tempVictimGenderDF = tempVictimGenderDF.reset_index().dropna().set_index('index')

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseSpecificDataFrame = caseSpecificDataFrame.dropna(subset = ['Vsex'])

			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]

			caseLabel = getCaseLabel(caseType)

			tempVictimGenderDF[caseLabel] = tempShootingDF.groupby(['Vsex']).size()
			tempVictimGenderDF[caseLabel] = tempVictimGenderDF[caseLabel].fillna(0).astype(int)
			tempVictimGenderDF['Category'] = tempVictimGenderDF.index
			tempVictimGenderDF['Year'] = tempYear
		gender = gender.append(tempVictimGenderDF)

	gender['dataType'] = "GenderDemographics"
	gender['Agency'] = agencyLabel
	gender = gender[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	gender.reset_index(inplace=False)
	gender.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - GenderDemographics.csv", encoding='utf-8', index=False)

def getVictimAge(shootingDataFrame, agencyLabel):
	age = pd.DataFrame()
	caseTypes = getCaseTypes()

	#For Each Year of Shooting Data
	for tempYear in getYearList():
		tempVictimAgeDF = pd.DataFrame()

		tempVictimAgeDF.reset_index()
		tempVictimAgeDF = tempVictimAgeDF.reset_index().dropna().set_index('index')

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseSpecificDataFrame = caseSpecificDataFrame.dropna(subset = ['VDOB'])

			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			caseLabel = getCaseLabel(caseType)

			#Drop Nulls and Unknowns
			tempShootingDF = tempShootingDF.dropna(subset = ['VDOB'])
			tempShootingDF = tempShootingDF.reset_index()

			#Calculate Ages of Victims
			tempShootingDF['DateTime'] = pd.to_datetime(tempShootingDF['DateTime'])
			tempShootingDF['VDOB'] = pd.to_datetime(tempShootingDF['VDOB'])
			tempShootingDF['Age'] = tempShootingDF['DateTime'] - tempShootingDF['VDOB']
			tempShootingDF['Age'] = tempShootingDF['Age']/np.timedelta64(1, "Y")

			#Sort Ages into Bins
			tempShootingDF = tempShootingDF.sort_values('Age')
			bins = np.arange(0, 110, 10)
			ind = np.digitize(tempShootingDF['Age'], bins)

			tempVictimAgeDF[caseLabel] = tempShootingDF['Age'].value_counts(bins=bins, sort=False)

			tempVictimAgeDF[caseLabel] = tempVictimAgeDF[caseLabel].fillna(0).astype(int)
			tempVictimAgeDF['Category'] = tempVictimAgeDF.index
			tempVictimAgeDF['Year'] = tempYear
		age = age.append(tempVictimAgeDF)

	age['dataType'] = "AgeDemographics"
	age['Agency'] = agencyLabel
	age = age[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	age.reset_index(inplace=False)
	age.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - AgeDemographics.csv", encoding='utf-8', index=False)

def getVictimRace(shootingDataFrame, agencyLabel):
	race = pd.DataFrame()
	shootingDataFrame = shootingDataFrame.dropna(subset = ['Vrace'])
	caseTypes = getCaseTypes()

	#For Each Year of Shooting Data
	for tempYear in getYearList():

		raceList = list(set(shootingDataFrame['Vrace'].tolist()))
		cleanedList = [x for x in raceList if x != '']

		tempVictimRaceDF = pd.DataFrame(index=cleanedList)
		tempVictimRaceDF.reset_index()
		tempVictimRaceDF = tempVictimRaceDF.reset_index().dropna().set_index('index')

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			caseLabel = getCaseLabel(caseType)

			tempVictimRaceDF[caseLabel] = tempShootingDF.groupby(['Vrace']).size()
			tempVictimRaceDF = tempVictimRaceDF.fillna(0)
			tempVictimRaceDF[caseLabel] = tempVictimRaceDF[caseLabel].fillna(0).astype(int)
			tempVictimRaceDF['Category'] = tempVictimRaceDF.index
			tempVictimRaceDF['Year'] = tempYear
		race = race.append(tempVictimRaceDF)

	race['dataType'] = "RaceDemographics"
	race['Agency'] = agencyLabel
	race = race[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	race.reset_index(inplace=False)
	race.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - RaceDemographics.csv", encoding='utf-8', index=False)

def getVictimFelon(shootingDataFrame, agencyLabel):
	victimFelon = pd.DataFrame()
	caseTypes = getCaseTypes()
	shootingDataFrame = shootingDataFrame.dropna(subset = ['vFelon'])

	#For Each Year of Shooting Data
	for tempYear in getYearList():

		#Initialize DataFrame
		tempVictimFelon = pd.DataFrame(index=set(shootingDataFrame['vFelon'].tolist()))
		tempVictimFelon.reset_index()
		tempVictimFelon = tempVictimFelon.reset_index().dropna().set_index('index')

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseLabel = getCaseLabel(caseType)

			#Load That Year's DataFrame
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]

			tempVictimFelon[caseLabel] = tempShootingDF.groupby(['vFelon']).size()
			tempVictimFelon = tempVictimFelon.fillna(0)
			tempVictimFelon[caseLabel] = tempVictimFelon[caseLabel].fillna(0).astype(int)
			tempVictimFelon['Category'] = tempVictimFelon.index
			tempVictimFelon['Year'] = tempYear

		victimFelon = victimFelon.append(tempVictimFelon)

	victimFelon['dataType'] = "Felons"
	victimFelon['Agency'] = agencyLabel
	victimFelon = victimFelon[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	victimFelon.reset_index(inplace=False)
	victimFelon.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - Felon.csv", encoding='utf-8', index=False)

def getHospital(shootingDataFrame, agencyLabel):
	hospital = pd.DataFrame()
	caseTypes = getCaseTypes()
	shootingDataFrame = shootingDataFrame.dropna(subset = ['Hospital'])

	#For Each Year of Shooting Data
	for tempYear in getYearList():
		tempHospitalDF = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()

			#Drop Nulls and Unknowns
			tempShootingDF = tempShootingDF.dropna(subset = ['Hospital'])
			tempShootingDF = tempShootingDF[tempShootingDF['Hospital'] != "Unknown"]
			tempShootingDF = tempShootingDF[tempShootingDF['Hospital'] != "None"]

			tempHospitalDF[caseLabel] = tempShootingDF.groupby(['Hospital']).size()
			tempHospitalDF['Category'] = tempHospitalDF.index
			tempHospitalDF['Year'] = tempYear
		hospital = hospital.append(tempHospitalDF)

	hospital['dataType'] = "Hospital"
	hospital['Agency'] = agencyLabel
	hospital = hospital[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	hospital.reset_index(inplace=False)
	hospital.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - Hospital.csv", encoding='utf-8', index=False)

def getShellCasings(shootingDataFrame, agencyLabel):
	shellCasings = pd.DataFrame()
	caseTypes = getCaseTypes()

	#Remove Duplicates of File Numbers
	shootingDataFrame = shootingDataFrame.drop_duplicates(subset='CRN', keep="first")

	#For Each Year of Shooting Data
	for tempYear in getYearList():
		tempShellCasingsDF = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()

			tempShootingDF = tempShootingDF.dropna(subset = ['GunsUsed'])
			tempShootingDF['GunsUsed'] = tempShootingDF['GunsUsed'].str.split(",")
			tempShootingDF = tempShootingDF.explode('GunsUsed').reset_index(drop=True)
			tempShootingDF["GunsUsed"] = tempShootingDF["GunsUsed"].map(str.strip)
			tempShootingDF = tempShootingDF[tempShootingDF['GunsUsed'] != "None Recovered"]
			tempShootingDF = tempShootingDF[tempShootingDF['GunsUsed'] != "Stabbing"]
			tempShootingDF = tempShootingDF[tempShootingDF['GunsUsed'] != "Unknown"]
			tempShootingDF = tempShootingDF[tempShootingDF['GunsUsed'] != "Blunt Force Trauma"]
			tempShootingDF = tempShootingDF[tempShootingDF['GunsUsed'] != "Shovel and Car"]
			tempShootingDF = tempShootingDF[tempShootingDF['GunsUsed'] != ""]
			tempShootingDF = tempShootingDF.dropna(subset = ['GunsUsed'])

			tempShellCasingsDF[caseLabel] = tempShootingDF.groupby(['GunsUsed']).size()
			tempShellCasingsDF['Category'] = tempShellCasingsDF.index

			tempShellCasingsDF['Year'] = tempYear

			tempShellCasingsDF = tempShellCasingsDF.sort_values(caseLabel,ascending=False)
			tempShellCasingsDF = tempShellCasingsDF.dropna(subset = ['Category'])

		shellCasings = shellCasings.append(tempShellCasingsDF)

	shellCasings['dataType'] = "GunsUsed"
	shellCasings['Agency'] = agencyLabel
	shellCasings = shellCasings[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	shellCasings.reset_index(inplace=False)
	shellCasings.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - GunsUsed.csv", index = False)

def getWoundTypes(shootingDataFrame, agencyLabel):
	woundLocations = pd.DataFrame()
	caseTypes = getCaseTypes()

	#For Each Year of Shooting Data
	for tempYear in getYearList():

		tempWoundDF = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()

			tempShootingDF['GSW'] = tempShootingDF['GSW'].str.split(",")
			tempShootingDF = tempShootingDF.explode('GSW').reset_index(drop=True)
			tempShootingDF["GSW"] = tempShootingDF["GSW"].map(str.strip)

			tempShootingDF = tempShootingDF.dropna(subset = ['GSW'])
			tempShootingDF = tempShootingDF[tempShootingDF['GSW'] != "Unknown"]
			tempShootingDF = tempShootingDF[tempShootingDF['GSW'] != "None"]
			tempShootingDF = tempShootingDF[tempShootingDF['GSW'] != ""]

			tempWoundDF[caseLabel] = tempShootingDF.groupby(['GSW']).size()
			tempWoundDF['Category'] = tempWoundDF.index

			tempWoundDF['Year'] = tempYear

			tempWoundDF = tempWoundDF.sort_values(caseLabel,ascending=False)
			tempWoundDF = tempWoundDF.dropna(subset = ['Category'])

		woundLocations = woundLocations.append(tempWoundDF)

	woundLocations['dataType'] = "WoundLocations"
	woundLocations['Agency'] = agencyLabel
	woundLocations = woundLocations[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	woundLocations.reset_index(inplace=False)
	woundLocations.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - WoundLocations.csv", index = False)

def getDVAffiliated(shootingDataFrame, agencyLabel):
	victimDV = pd.DataFrame()
	caseTypes = getCaseTypes()
	shootingDataFrame = shootingDataFrame.dropna(subset = ['DV'])

	#For Each Year of Shooting Data
	for tempYear in getYearList():
		#tempShootingDF = shootingDataFrame[shootingDataFrame['DateTime'].dt.year == tempYear]
		tempVictimDVDF = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()

			tempVictimDVDF[caseLabel] = tempShootingDF.groupby(['DV']).size()
			tempVictimDVDF['Category'] = tempVictimDVDF.index
			tempVictimDVDF['Year'] = tempYear

		victimDV = victimDV.append(tempVictimDVDF)

	victimDV['dataType'] = "DV"
	victimDV['Agency'] = agencyLabel
	victimDV = victimDV[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	victimDV.reset_index(inplace=False)
	victimDV.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - DV.csv", encoding='utf-8', index=False)

def getDaysOfTheWeek(shootingDataFrame, agencyLabel):
	weekDay = pd.DataFrame()
	caseTypes = getCaseTypes()

	#For Each Year of Shooting Data
	for tempYear in getYearList():
		tempWeekday = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()

			tempShootingDF = tempShootingDF.dropna(subset = ['DateTime'])
			tempShootingDF = tempShootingDF.reset_index()

			tempShootingDF['DateTime'] = pd.to_datetime(tempShootingDF['DateTime'])
			tempShootingDF['DayOfWeek'] = tempShootingDF['DateTime'].dt.day_name()

			tempWeekday[caseLabel] = tempShootingDF.groupby(['DayOfWeek']).size()
			tempWeekday['Category'] = tempWeekday.index
			tempWeekday['Year'] = tempYear

			cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

			tempWeekday['Category'] = pd.Categorical(tempWeekday['Category'], categories=cats, ordered=True)
			tempWeekday = tempWeekday.sort_values('Category')

		weekDay = weekDay.append(tempWeekday)

	weekDay['dataType'] = "Weekday"
	weekDay['Agency'] = agencyLabel
	weekDay = weekDay[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	weekDay.reset_index(inplace=False)
	weekDay.to_csv("DataForDashboard\\"+agencyLabel+" - Victim - Weekday.csv", encoding='utf-8', index=False)

def getTimeOfDay(shootingDataFrame, agencyLabel):
	hourOfDay = pd.DataFrame()
	caseTypes = getCaseTypes()
	shootingDataFrame = shootingDataFrame.reset_index(drop = True)
	shootingDataFrame['DateTime'] = pd.to_datetime(shootingDataFrame['DateTime'])
	shootingDataFrame['HourOfDay'] = shootingDataFrame['DateTime'].dt.hour

	#For Each Year of Shooting Data
	for tempYear in getYearList():
		tempHour = pd.DataFrame(index = set(shootingDataFrame['HourOfDay'].tolist()))

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)
			#Drop Nulls and Unknowns
			tempShootingDF = tempShootingDF.drop_duplicates(subset = ['CRN'])
			tempShootingDF = tempShootingDF.dropna(subset = ['DateTime'])
			tempShootingDF = tempShootingDF.reset_index()

			tempHour[caseLabel] = tempShootingDF.groupby(['HourOfDay']).size()
			tempHour['Category'] = tempHour.index
			tempHour['Year'] = tempYear
			tempHour = tempHour.sort_values('Category', ascending = True)

		hourOfDay = hourOfDay.append(tempHour)

	hourOfDay['dataType'] = "HourOfDay"
	hourOfDay['Category'] = hourOfDay['Category'].astype(str)
	hourOfDay['Category'] = hourOfDay['Category'].str.zfill(2)
	hourOfDay['Category'] = hourOfDay['Category'] + ":00"
	hourOfDay['Agency'] = agencyLabel
	hourOfDay = hourOfDay[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	hourOfDay.reset_index(inplace=False)
	hourOfDay.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - HourOfDay.csv", encoding='utf-8', index=False)

def getPatrolDivision(shootingDataFrame, agencyLabel):
	patrolDivision = pd.DataFrame()
	caseTypes = getCaseTypes()
	patrolList = set(shootingDataFrame['Patrol'].tolist())
	cleanedList = [x for x in patrolList if x != '']
	cleanedList = [x for x in cleanedList if x != 'UNKNOWN']

	#For Each Year of Shooting Data
	for tempYear in getYearList():

		tempPatrolDivision = pd.DataFrame(index=cleanedList)

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			#tempShootingDF = tempShootingDF[tempShootingDF['Patrol'] != "UNK"]
			tempPatrolDivision[caseLabel] = tempShootingDF.groupby(['Patrol']).size()

			tempPatrolDivision['Category'] = tempPatrolDivision.index
			tempPatrolDivision['Year'] = tempYear
		patrolDivision = patrolDivision.append(tempPatrolDivision)

	patrolDivision['dataType'] = "PatrolDivision"
	patrolDivision['caseLabel'] = caseLabel
	patrolDivision = patrolDivision[patrolDivision['Category']!= "UNK"]

	patrolDivision['Agency'] = agencyLabel
	patrolDivision = patrolDivision[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	patrolDivision.reset_index(inplace=False)

	patrolDivision.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - PatrolDivision.csv", encoding='utf-8', index=False)

def getRefferalStats(shootingDataFrame, agencyLabel):
	caseReferrals = pd.DataFrame()
	caseTypes = getCaseTypes()

	shootingDataFrame = shootingDataFrame[shootingDataFrame['Ref'] != "NoJuris"]

	for tempYear in getYearList():
		tempReferralStats = pd.DataFrame(index= ["Yes", "No"])

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]

			#tempShootingDF = tempShootingDF.drop_duplicates(subset = ['CRN'])
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			tempReferralStats[caseLabel] = tempShootingDF.groupby(['Ref']).size()
			
			tempReferralStats['Category'] = tempReferralStats.index
			tempReferralStats['Year'] = tempYear

		caseReferrals = caseReferrals.append(tempReferralStats)


	caseReferrals['dataType'] = "ReferralRate"
	caseReferrals['Agency'] = agencyLabel
	caseReferrals = caseReferrals[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	caseReferrals.reset_index(inplace=False)
	caseReferrals.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - ReferralRate.csv", encoding='utf-8', index=False)

def getFilingStats(shootingDataFrame, agencyLabel):
	caseFilings = pd.DataFrame()
	caseTypes = getCaseTypes()

	shootingDataFrame = shootingDataFrame[shootingDataFrame['Filed'] != "NoJuris"]

	for tempYear in getYearList():
		tempFilingStats = pd.DataFrame(index= ["Yes", "No"])

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			#tempShootingDF = tempShootingDF.drop_duplicates(subset = ['CRN'])

			tempShootingDF = tempShootingDF.reset_index()

			tempFilingStats[caseLabel] = tempShootingDF.groupby(['Filed']).size()
			tempFilingStats['Category'] = tempFilingStats.index
			tempFilingStats['Year'] = tempYear
		caseFilings = caseFilings.append(tempFilingStats)

	caseFilings['dataType'] = "FiledRate"
	caseFilings['Agency'] = agencyLabel
	caseFilings = caseFilings[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	caseFilings.reset_index(inplace=False)
	caseFilings.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - FilingRate.csv", encoding='utf-8', index=False)

def disposalStats(shootingDataFrame, agencyLabel):
	caseDisposal = pd.DataFrame()
	caseTypes = getCaseTypes()

	shootingDataFrame = shootingDataFrame[shootingDataFrame['Filed'] != "NoJuris"]

	for tempYear in getYearList():
		tempDisposalStats = pd.DataFrame(index= ["Yes", "No"])

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)
			
			#tempShootingDF = tempShootingDF.drop_duplicates(subset = ['CRN'])

			tempShootingDF = tempShootingDF.reset_index()

			tempDisposalStats[caseLabel] = tempShootingDF.groupby(['Disposed']).size()
			tempDisposalStats['Category'] = tempDisposalStats.index
			tempDisposalStats['Year'] = tempYear

		caseDisposal = caseDisposal.append(tempDisposalStats)

	caseDisposal['dataType'] = "DisposedRate"
	caseDisposal['Agency'] = agencyLabel
	caseDisposal = caseDisposal[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	caseDisposal.reset_index(inplace=False)
	caseDisposal.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - DisposalRate.csv", encoding='utf-8', index=False)

def getReviewRate(shootingDataFrame, agencyLabel):
	caseReview = pd.DataFrame()
	caseTypes = getCaseTypes()

	shootingDataFrame = shootingDataFrame[shootingDataFrame['Review'] != "NoJuris"]

	for tempYear in getYearList():
		tempReviewStats = pd.DataFrame(index= ["Yes", "No"])

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()

			
			tempShootingDF = tempShootingDF[tempShootingDF['Filed']=='No']
			tempShootingDF = tempShootingDF[tempShootingDF['Disposed']=='No']
			caseLabel = getCaseLabel(caseType)
			
			#tempShootingDF = tempShootingDF.drop_duplicates(subset = ['CRN'])

			tempShootingDF = tempShootingDF.reset_index()

			tempReviewStats[caseLabel] = tempShootingDF.groupby(['Review']).size()
			tempReviewStats['Category'] = tempReviewStats.index
			tempReviewStats['Year'] = tempYear

		caseReview = caseReview.append(tempReviewStats)

	caseReview['dataType'] = "ReviewRate"
	caseReview['Agency'] = agencyLabel
	caseReview = caseReview[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	caseReview.reset_index(inplace=False)
	caseReview.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - ReviewRate.csv", encoding='utf-8', index=False)

def getDeclineRate(shootingDataFrame, agencyLabel):
	caseDisposal = pd.DataFrame()
	caseTypes = getCaseTypes()

	shootingDataFrame = shootingDataFrame[shootingDataFrame['Declined'] != "NoJuris"]

	for tempYear in getYearList():
		tempDisposalStats = pd.DataFrame(index= ["Yes", "No"])

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()

			tempShootingDF = tempShootingDF[tempShootingDF['Filed']=='No']

			caseLabel = getCaseLabel(caseType)

			#tempShootingDF = tempShootingDF.drop_duplicates(subset = ['CRN'])

			tempShootingDF = tempShootingDF.reset_index()

			tempDisposalStats[caseLabel] = tempShootingDF.groupby(['Declined']).size()
			tempDisposalStats['Category'] = tempDisposalStats.index
			tempDisposalStats['Year'] = tempYear

		caseDisposal = caseDisposal.append(tempDisposalStats)

	caseDisposal['dataType'] = "DeclinedRate"
	caseDisposal['Agency'] = agencyLabel
	caseDisposal = caseDisposal[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	caseDisposal.reset_index(inplace=False)
	caseDisposal.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - DeclineRate.csv", encoding='utf-8', index=False)

def getKCJacksonCountyIncidents(shootingDataFrame, agencyLabel):
	JaCoIncidents = pd.DataFrame()
	caseTypes = getCaseTypes()

	for tempYear in getYearList():
		tempJackStats = pd.DataFrame(index = caseTypes)

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			#tempShootingDF = tempShootingDF.drop_duplicates(subset = ['CRN'])
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = tempShootingDF[tempShootingDF['JaCo'] == "Yes"]
			tempShootingDF = tempShootingDF[tempShootingDF['Ref'] != "Nojuris"]

			tempShootingDF = tempShootingDF.reset_index()

			tempJackStats[caseLabel] = tempShootingDF.groupby(['Type']).size()

			tempJackStats['Category'] = tempJackStats.index
			tempJackStats['Year'] = tempYear

		JaCoIncidents = JaCoIncidents.append(tempJackStats)

	JaCoIncidents['dataType'] = "JaCoIncidents"
	JaCoIncidents['Agency'] = agencyLabel
	JaCoIncidents = JaCoIncidents[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]

	JaCoIncidents.reset_index(inplace=False)
	JaCoIncidents.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - JaCoIncidents.csv", encoding='utf-8', index=False)

def getJailStats(shootingDataFrame, filedCases, disposedCases, agencyLabel):
	inmateLibraryDataFrame = pd.read_csv(r'C:\Users\hchapman\OneDrive - Jackson County Missouri\Documents\Dashboards\Jail Dashboard\JailInmateLibrary.csv', encoding = 'utf-8')

	jailInmates = pd.DataFrame()
	caseTypes = getCaseTypes()

	for tempYear in getYearList():
		tempJailStats = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = tempShootingDF[tempShootingDF['Filed'] == "Yes"]
			tempShootingDF = tempShootingDF.merge(filedCases, on='CRN', how='left')
			tempShootingDF = tempShootingDF.merge(inmateLibraryDataFrame, on = 'File #', how='left')
			tempShootingDF = tempShootingDF.drop_duplicates(subset='File #', keep="first")
			disposedCases = disposedCases.drop_duplicates(subset='File #', keep="first")
			tempShootingDF = tempShootingDF[~tempShootingDF['File #'].isin(disposedCases['File #'])]

			tempShootingDF['inJail'] = ["Yes" if x > 1 else "No" for x in tempShootingDF['InmateNum']]

			tempShootingDF = tempShootingDF.reset_index()

			#tempShootingDFOutput = tempShootingDF.merge()
			#tempShootingDF.to_csv(caseLabel + str(tempYear) + ".csv", index = False)

			tempJailStats[caseLabel] = tempShootingDF.groupby(['inJail']).size()

			tempJailStats['Category'] = tempJailStats.index
			tempJailStats['Year'] = tempYear

		jailInmates = jailInmates.append(tempJailStats)

	jailInmates['dataType'] = "JailInmates"

	jailInmates['Agency'] = agencyLabel
	jailInmates = jailInmates[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	jailInmates.reset_index(inplace=False)
	jailInmates.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - JailInmates.csv", encoding='utf-8', index=False)

#Time Between Incident and Case Entry
def getReferralTimeline(shootingDataFrame, referredCases, agencyLabel):
	referralTimeline = pd.DataFrame()
	caseTypes = getCaseTypes()
	shootingDataFrame = shootingDataFrame.drop_duplicates(subset='CRN', keep="first")

	for tempYear in getYearList():
		tempReferralTimeline = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF[tempShootingDF['Ref'] == 'Yes']
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = tempShootingDF.merge(referredCases, on='CRN', how='left')
			tempShootingDF = tempShootingDF.drop_duplicates(subset='File #', keep="first")

			#Drop Nulls and Unknowns
			tempShootingDF = tempShootingDF.reset_index()

			#Calculate Ages of Referred Cases
			tempShootingDF['DateTime'] = pd.to_datetime(tempShootingDF['DateTime'])
			tempShootingDF['Enter Dt.'] = pd.to_datetime(tempShootingDF['Enter Dt.'])
			tempShootingDF['Age'] = tempShootingDF['Enter Dt.'] - tempShootingDF['DateTime']
			tempShootingDF['Age'] = tempShootingDF['Age']/np.timedelta64(1, "M")

			#Sort Ages into Bins
			tempShootingDF = tempShootingDF.sort_values('Age')
			bins = np.arange(0, 10, 1)
			ind = np.digitize(tempShootingDF['Age'], bins)

			tempReferralTimeline[caseLabel] = tempShootingDF['Age'].value_counts(bins=bins, sort=False)

			tempReferralTimeline['Category'] = tempReferralTimeline.index
			tempReferralTimeline['Year'] = tempYear
		referralTimeline = referralTimeline.append(tempReferralTimeline)

	referralTimeline['dataType'] = "CaseReferralAge"
	referralTimeline['Agency'] = agencyLabel
	referralTimeline = referralTimeline[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]

	referralTimeline.reset_index(inplace=False)
	referralTimeline.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - CaseReferralAge.csv", encoding='utf-8', index=False)

#Time Between Case Entry and Case Filing
def getFilingTimeLine(shootingDataFrame, filedCases, agencyLabel):
	filingTimeline = pd.DataFrame()
	caseTypes = getCaseTypes()
	shootingDataFrame = shootingDataFrame.drop_duplicates(subset='CRN', keep="first")

	for tempYear in getYearList():
		tempFilingTimeline = pd.DataFrame()

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = tempShootingDF.merge(filedCases, on='CRN', how='left')
			tempShootingDF = tempShootingDF.drop_duplicates(subset='File #', keep="first")

			#Drop Nulls and Unknowns
			tempShootingDF = tempShootingDF.reset_index()

			#Calculate Ages of Filed Cases
			tempShootingDF['DateTime'] = pd.to_datetime(tempShootingDF['DateTime'])
			tempShootingDF['Enter Dt.'] = pd.to_datetime(tempShootingDF['Enter Dt.'])
			tempShootingDF['Filing Dt.'] = pd.to_datetime(tempShootingDF['Filing Dt.'])
			tempShootingDF['Age'] = tempShootingDF['Filing Dt.'] - tempShootingDF['Enter Dt.']
			tempShootingDF['Age'] = tempShootingDF['Age']/np.timedelta64(1, "M")

			#Sort Ages into Bins
			tempShootingDF = tempShootingDF.sort_values('Age')
			bins = np.arange(0, 10, 1)
			ind = np.digitize(tempShootingDF['Age'], bins)

			tempFilingTimeline[caseLabel] = tempShootingDF['Age'].value_counts(bins=bins, sort=False)

			tempFilingTimeline['Category'] = tempFilingTimeline.index
			tempFilingTimeline['Year'] = tempYear
		filingTimeline = filingTimeline.append(tempFilingTimeline)

	filingTimeline['dataType'] = "CaseFilingAge"
	filingTimeline['Agency'] = agencyLabel
	filingTimeline = filingTimeline[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	filingTimeline.reset_index(inplace=False)
	filingTimeline.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - CaseFilingAge.csv", encoding='utf-8', index=False)

def getDeclineReasons(shootingDataFrame, declinedCases, agencyLabel):
	declineReasons = pd.DataFrame()
	caseTypes = getCaseTypes()

	shootingDataFrame = shootingDataFrame.drop_duplicates(subset = 'CRN', keep = 'first')
	shootingDataFrame = shootingDataFrame[shootingDataFrame['Filed']=='No']
	shootingDataFrame = shootingDataFrame.merge(declinedCases, on = 'CRN', how = 'left')

	for tempYear in getYearList():

		dispList = list(set(shootingDataFrame['Disp. Code'].tolist()))
		cleanedList = [x for x in dispList if x != '']

		tempDeclineReasons = pd.DataFrame(index = cleanedList)

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			tempShootingDF = tempShootingDF.reset_index()
			caseLabel = getCaseLabel(caseType)

			tempShootingDF = tempShootingDF.drop_duplicates(subset = 'File #')
			tempShootingDF = tempShootingDF.dropna(subset=['Disp. Code'])
			tempShootingDF = tempShootingDF.reset_index()

			tempDeclineReasons[caseLabel] = tempShootingDF.groupby(['Disp. Code']).size()
			tempDeclineReasons = tempDeclineReasons.fillna(0)
			tempDeclineReasons[caseLabel] = tempDeclineReasons[caseLabel].fillna(0).astype(int)

			tempDeclineReasons['Category'] = tempDeclineReasons.index
			tempDeclineReasons['Year'] = tempYear

		declineReasons = declineReasons.append(tempDeclineReasons)
	
	declineReasons['Sum'] = declineReasons['Homicide'] + declineReasons['Non-Fatal'] + declineReasons['Self-Inflicted']
	declineReasons = declineReasons[declineReasons['Sum']!=0] 
	declineReasons = declineReasons.dropna(subset=['Category'])
	declineReasons['dataType'] = 'CaseDeclineReasons'
	declineReasons['Agency'] = agencyLabel
	declineReasons = declineReasons[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	declineReasons.reset_index(inplace = False)
	declineReasons.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - CaseDeclineReasons.csv", encoding = 'utf-8', index = False)

	return 0

def getCurrentPercentageThroughYear(shootingDataFrame):

	shootingDataFrame = shootingDataFrame.sort_values(by = ['DateTime'], ascending = False)

	lastDate = shootingDataFrame['DateTime'].tolist()[0]
	lastYear= datetime.date(lastDate).year
	lastDateDate = lastDate.date()
	januaryFirst = datetime.now().date().replace(year =lastYear, month=1, day=1)    
	days_in_the_year = (lastDateDate - januaryFirst).days + 1

	yearPercent = days_in_the_year/365

	return yearPercent

def getYearByYearChange(shootingDataFrame, agencyLabel):
	yearByYearChange = pd.DataFrame()

	#Get Current Percentage Through Year
	yearPercent = getCurrentPercentageThroughYear(shootingDataFrame)

	#Sum Past Years' Homicides and Non-Fatal Shootings
	#Create New Column For Years
	shootingDataFrame = shootingDataFrame.reset_index(drop = True)
	shootingDataFrame['Year'] = shootingDataFrame['DateTime'].dt.year

	#Cut Out 2021 Homicides
	oldShootings = shootingDataFrame[(shootingDataFrame['Year']!=2022) & (shootingDataFrame['JaCo']=="Yes")]

	#Sum Homicides
	sumHomicides = len(oldShootings[oldShootings['Type']=="H"].index)
	
	#Divide By Number Of Years to Get Average Per Year
	averageHomicides = sumHomicides/(len(getYearList())-1)
	averageHomicidesToThisPoint = averageHomicides*yearPercent

	#Sum Non-Fatals
	sumNonFatals = len(oldShootings[oldShootings['Type']=="B"].index)

	#Divide By Number Of Years to Get Average Per Year
	averageNonFatals = sumNonFatals/(len(getYearList())-1)
	averageNonFatalsToThisPoint = averageNonFatals*yearPercent

	#Get Number of 2020 Homicides and Non-Fatal Shootings
	newShootings = shootingDataFrame[(shootingDataFrame['Year']==2022) & (shootingDataFrame['JaCo']=="Yes")]
	sumCurrentHomicides = len(newShootings[newShootings['Type']=="H"].index)
	sumCurrentNonFatals = len(newShootings[newShootings['Type']=="B"].index)

	currentHomicidesNonFatals = []
	currentHomicidesNonFatals.append(sumCurrentHomicides)
	currentHomicidesNonFatals.append(sumCurrentNonFatals)

	if averageHomicidesToThisPoint != 0:
		yearToDateHomicideChange = sumCurrentHomicides/averageHomicidesToThisPoint
	else:
		yearToDateHomicideChange = 0
	if averageNonFatalsToThisPoint != 0:
		yearToDateNonFatalChange = sumCurrentNonFatals/averageNonFatalsToThisPoint
	else: 
		yearToDateNonFatalChange = 0
	yearByYearChange = pd.DataFrame()
	yearByYearChange['Homicide'] = [int(yearToDateHomicideChange*100)]
	yearByYearChange['Non-Fatal'] = [int(yearToDateNonFatalChange*100)]
	yearByYearChange['Year'] = [2022]
	yearByYearChange['Self-Inflicted'] = [0]
	yearByYearChange['Category'] = ["Average Change"]
	yearByYearChange['dataType'] = ["YearToDate"]

	yearByYearChange['Agency'] = agencyLabel
	yearByYearChange = yearByYearChange[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	yearByYearChange.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - YearByYear.csv", encoding='utf-8', index=False)

	return currentHomicidesNonFatals

def getHistoricalGraph(currentHomicidesNonFatals, shootingDataFrame, agencyLabel):
	yearPercent = getCurrentPercentageThroughYear(shootingDataFrame)
	historicalData = pd.read_csv("HistoricalHomicideRate.csv", encoding = 'utf-8')

	#Add Projected 2021 Value
	#Homicides
	currentHomicides = currentHomicidesNonFatals[0]
	projectedFinalHomicide = currentHomicides/yearPercent

	#NonFatals
	currentNonFatals = currentHomicidesNonFatals[1]
	projectedFinalNonFatal= currentNonFatals/yearPercent

	tempDataFrame = pd.DataFrame()
	tempDataFrame['Category'] = [datetime.now().year]
	tempDataFrame['Year'] = 2022
	tempDataFrame['Homicide'] = [projectedFinalHomicide]
	tempDataFrame['Non-Fatal'] = [projectedFinalNonFatal]

	historicalData = historicalData.append(tempDataFrame)
	historicalData['Self-Inflicted'] = historicalData.iloc[:,2].rolling(window=3).mean()

	historicalData['dataType'] = 'HistoricalHomicides'

	historicalData['Agency'] = agencyLabel
	historicalData.to_csv("DataForDashboard\\"+agencyLabel+" - Crime - HistoricalProjection.csv", encoding = 'utf-8', index=False)

def runAnalysis(shootingDataFrame, karpelCases, agencyLabel):
	getVictimGender(shootingDataFrame, agencyLabel)
	getVictimAge(shootingDataFrame, agencyLabel)
	getVictimRace(shootingDataFrame, agencyLabel)
	getVictimFelon(shootingDataFrame, agencyLabel)
	getHospital(shootingDataFrame, agencyLabel)
	getShellCasings(shootingDataFrame, agencyLabel)
	getWoundTypes(shootingDataFrame, agencyLabel)
	getDVAffiliated(shootingDataFrame, agencyLabel)
	getDaysOfTheWeek(shootingDataFrame, agencyLabel)
	getTimeOfDay(shootingDataFrame, agencyLabel)
	getPatrolDivision(shootingDataFrame, agencyLabel)
	getKCJacksonCountyIncidents(shootingDataFrame, agencyLabel)


	referredCases = karpelCases[0]
	referredCases = referredCases.dropna(subset=['CRN'])
	filedCases = karpelCases[1]
	filedCases = filedCases.dropna(subset=['CRN'])
	disposedCases = karpelCases[2]
	disposedCases = disposedCases.dropna(subset=['CRN'])
	declinedCases = karpelCases[3]
	declinedCases = declinedCases.dropna(subset=['CRN'])

	getJailStats(shootingDataFrame, filedCases, disposedCases, agencyLabel)
	getReferralTimeline(shootingDataFrame,referredCases, agencyLabel)
	getFilingTimeLine(shootingDataFrame, filedCases, agencyLabel)
	getRefferalStats(shootingDataFrame, agencyLabel)
	getFilingStats(shootingDataFrame, agencyLabel)
	disposalStats(shootingDataFrame, agencyLabel)
	getDeclineRate(shootingDataFrame, agencyLabel)
	getDeclineReasons(shootingDataFrame, declinedCases, agencyLabel)
	getReviewRate(shootingDataFrame, agencyLabel)

	currentHomicidesNonFatals = getYearByYearChange(shootingDataFrame, agencyLabel)
	getHistoricalGraph(currentHomicidesNonFatals, shootingDataFrame, agencyLabel)

def getVictimDemographics(shootingDataFrame, karpelCases, agencyLabel):
	runAnalysis(shootingDataFrame, karpelCases, agencyLabel)