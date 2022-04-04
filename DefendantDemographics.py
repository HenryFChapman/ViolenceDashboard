from geopy import distance
import math
import geopandas as gpd
from pyproj import CRS, Proj, transform
from shapely.geometry import Point
from pandas.api.types import CategoricalDtype 
import datetime as dt
from datetime import datetime
from DataPreparer import loadKarpelCases, getNewestFile
import pandas as pd
import os
import numpy as np
from HelperMethods import getYearList, getCaseLabel, getCaseTypes, filterDataFrameByCaseType


# Script: DefendantDemographics.py
# Purpose:  This program handles the demographic analysis associated with our gun violence defendants. 
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, geopy, math, geopandas, pyproj, shapely, datetime, os, numpy
#	 Functions: getYearList, getCaseLabel, getCaseTypes, filterDataFrameByCaseType



# Function:  getDefendantGender
# Purpose:   This method returns the counts of each defendant's gender for each reporting police agency
# Arguments: shootingDataFrame (list where each element is a filter dataframe of shooting victims), agencyLabel (string of the police agency name)
# Return:    No return values, but saves a CSV for each police agency's defendant's gender.
def getDefendantGender(shootingDataFrame, agencyLabel):
	
	#Initializes DataFrame
	gender = pd.DataFrame()

	#Grabs Case Types
	caseTypes = getCaseTypes()


	frames = []
	#For Each Year of Shooting Data
	for tempYear in getYearList():
		
		#Gets a unique list of genders
		genderList = list(set(shootingDataFrame['Def. Sex'].tolist()))
		
		#Removes null values from gender list
		cleanedList = [x for x in genderList if x != '']

		#Initalizes Gender Dataframes using the identified index
		tempDefendantGenderDF = pd.DataFrame(index=cleanedList)
		tempDefendantGenderDF.reset_index()
		tempDefendantGenderDF = tempDefendantGenderDF.reset_index().dropna().set_index('index')

		#Loops through each case type (Homicide, Non-Fatal, and Self-Inflicted)
		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseSpecificDataFrame = caseSpecificDataFrame.dropna(subset = ['Def. Sex'])

			#Filters just the year we want
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]

			caseLabel = getCaseLabel(caseType)

			#Counts the Number of Each Sex
			tempDefendantGenderDF[caseLabel] = tempShootingDF.groupby(['Def. Sex']).size()
			tempDefendantGenderDF[caseLabel] = tempDefendantGenderDF[caseLabel].fillna(0).astype(int)
			tempDefendantGenderDF['Category'] = tempDefendantGenderDF.index
			tempDefendantGenderDF['Year'] = tempYear
		
		#Appends that data to the entire gender dataframe
		frames.append(tempDefendantGenderDF)

	#Cleans entire gender dataframe and exports it as a CSV file.

	gender = pd.concat(frames)
	gender['dataType'] = "defendantGenderDemographics"
	gender['Agency'] = agencyLabel
	gender = gender[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	gender.reset_index(inplace=False)
	gender.to_csv("DataForDashboard\\"+agencyLabel+" - Defendant- GenderDemographics.csv", encoding='utf-8', index=False)


# Function:  getDefendantRace
# Purpose:   This method returns the counts of each defendant's race for each reporting police agency
# Arguments: shootingDataFrame (list where each element is a filter dataframe of shooting victims), agencyLabel (string of the police agency name)
# Return:    No return values, but saves a CSV for each police agency's defendant's race.

def getDefendantRace(shootingDataFrame, agencyLabel):

	#Initializes DataFrame
	race = pd.DataFrame()

	#Grabs Case Types
	caseTypes = getCaseTypes()

	frames = []

	#For Each Year of Shooting Data
	for tempYear in getYearList():

		#Gets a unique list of races
		genderList = list(set(shootingDataFrame['Def. Race'].tolist()))

		#Removes null values
		cleanedList = [x for x in genderList if x != '']


		#Initalizes Race Dataframes using the identified index
		tempDefendantRaceDF = pd.DataFrame(index=cleanedList)
		tempDefendantRaceDF.reset_index()
		tempDefendantRaceDF = tempDefendantRaceDF.reset_index().dropna().set_index('index')


		#Loops through each case type (Homicide, Non-Fatal, and Self-Inflicted)
		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseSpecificDataFrame = caseSpecificDataFrame.dropna(subset = ['Def. Race'])

			#Filters just the year we want
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]

			caseLabel = getCaseLabel(caseType)

			#Counts the Number of Each Race
			tempDefendantRaceDF[caseLabel] = tempShootingDF.groupby(['Def. Race']).size()
			tempDefendantRaceDF[caseLabel] = tempDefendantRaceDF[caseLabel].fillna(0).astype(int)
			tempDefendantRaceDF['Category'] = tempDefendantRaceDF.index
			tempDefendantRaceDF['Year'] = tempYear

		#Appends that data to the entire race dataframe
		frames.append(tempDefendantRaceDF)

	race = pd.concat(frames)
	#Cleans entire race dataframe and exports it as a CSV file.
	race['dataType'] = "defendantRaceDemographics"
	race['Agency'] = agencyLabel
	race = race[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]
	race.reset_index(inplace=False)
	race.to_csv("DataForDashboard\\"+agencyLabel+" - Defendant- RaceDemographics.csv", encoding='utf-8', index=False)

# Function:  getDefendantAge
# Purpose:   This method returns the counts of each defendant's age for each reporting police agency
# Arguments: shootingDataFrame (list where each element is a filter dataframe of shooting victims), agencyLabel (string of the police agency name)
# Return:    No return values, but saves a CSV for each police agency's defendant's age.

def getDefendantAge(shootingDataFrame, agencyLabel):
	age = pd.DataFrame()
	caseTypes = getCaseTypes()

	frames = []

	#For Each Year of Shooting Data
	for tempYear in getYearList():

		#Initializes DataFrame
		tempDefendantAgeDF = pd.DataFrame()

		tempDefendantAgeDF.reset_index()
		tempDefendantAgeDF = tempDefendantAgeDF.reset_index().dropna().set_index('index')

		for caseType in caseTypes:
			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseSpecificDataFrame = caseSpecificDataFrame.dropna(subset = ['Def. DOB'])

			#Filters just the year we want
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			caseLabel = getCaseLabel(caseType)

			#Drop Nulls and Unknowns
			tempShootingDF = tempShootingDF.dropna(subset = ['Def. DOB'])
			tempShootingDF = tempShootingDF.reset_index()

			#Calculate Ages of Victims
			tempShootingDF['DateTime'] = pd.to_datetime(tempShootingDF['DateTime'])

			tempShootingDF['Def. DOB'] = pd.to_datetime(tempShootingDF['Def. DOB'], errors = 'coerce', infer_datetime_format=True)
			tempShootingDF['Age'] = tempShootingDF['DateTime'] - tempShootingDF['Def. DOB']
			tempShootingDF['Age'] = tempShootingDF['Age']/np.timedelta64(1, "Y")

			#Sort Ages into Bins
			tempShootingDF = tempShootingDF.sort_values('Age')
			bins = np.arange(0, 110, 10)
			ind = np.digitize(tempShootingDF['Age'], bins)

			tempDefendantAgeDF[caseLabel] = tempShootingDF['Age'].value_counts(bins=bins, sort=False)

			tempDefendantAgeDF[caseLabel] = tempDefendantAgeDF[caseLabel].fillna(0).astype(int)
			tempDefendantAgeDF['Category'] = tempDefendantAgeDF.index
			tempDefendantAgeDF['Year'] = tempYear
		
		#Appends that data to the entire race dataframe
		frames.append(tempDefendantAgeDF)

	age = pd.concat(frames)
	#Cleans entire age dataframe and exports it as a CSV file.
	age['dataType'] = "defendantAgeDemographics"
	age['Agency'] = agencyLabel
	age = age[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]

	age.reset_index(inplace=False)
	age.to_csv("DataForDashboard\\"+agencyLabel+" - Defendant - AgeDemographics.csv", encoding='utf-8', index=False)


def getDefendantBond(shootingDataFrame, agencyLabel):
	bonds = pd.DataFrame()
	caseTypes = getCaseTypes()


	frames = []
	#For each year of shooting data:
	for tempYear in getYearList():

		#Initializes DataFrame
		tempDefendantBondDF = pd.DataFrame()

		tempDefendantBondDF.reset_index()
		tempDefendantBondDF = tempDefendantBondDF.reset_index().dropna().set_index('index')

		for caseType in caseTypes:

			caseSpecificDataFrame = filterDataFrameByCaseType(shootingDataFrame, caseType)
			caseSpecificDataFrame = caseSpecificDataFrame.dropna(subset = ['Initial Bond'])

			#Filters just the year we want
			tempShootingDF = caseSpecificDataFrame[caseSpecificDataFrame['DateTime'].dt.year == tempYear]
			caseLabel = getCaseLabel(caseType)

			#Drop Nulls and Unknowns
			tempShootingDF = tempShootingDF.dropna(subset = ['Initial Bond'])
			tempShootingDF = tempShootingDF.reset_index()

			tempShootingDF['Initial Bond'] = tempShootingDF['Initial Bond']/1000

			#Sort Ages into Bins
			tempShootingDF = tempShootingDF.sort_values('Initial Bond')
			bins = np.arange(0, 250, 25)
			ind = np.digitize(tempShootingDF['Initial Bond'], bins)

			tempDefendantBondDF[caseLabel] = tempShootingDF['Initial Bond'].value_counts(bins=bins, sort=False)
			tempDefendantBondDF[caseLabel] = tempDefendantBondDF[caseLabel].fillna(0).astype(int)
			tempDefendantBondDF['Category'] = tempDefendantBondDF.index
			tempDefendantBondDF['Year'] = tempYear
		
		#Appends that data to the entire race dataframe
		frames.append(tempDefendantBondDF)

	bonds = pd.concat(frames)
	#Cleans entire Bonds dataframe and exports it as a CSV file.
	bonds['dataType'] = "defendantInitialBond"
	bonds['Agency'] = agencyLabel
	bonds = bonds[['dataType', 'Agency', 'Category', 'Year', "Homicide", "Non-Fatal", "Self-Inflicted"]]

	bonds.reset_index(inplace=False)
	bonds.to_csv("DataForDashboard\\"+agencyLabel+" - Defendant - Bonds.csv", encoding='utf-8', index=False)

# Function:  runAnalysis
# Purpose:   This function calls the gender, race, and age functions.
# Arguments: shootingDataFrame, karpelCases, agencyLabel
# Return:    0

def runAnalysis(shootingDataFrame, karpelCases, agencyLabel):
	
	#Removes self-inflicted shootings and non-Jackson county shootings.
	#Looks at cases that have only been referred. 
	shootingDataFrame = shootingDataFrame[shootingDataFrame['Type']!="S"]
	shootingDataFrame = shootingDataFrame[shootingDataFrame['JaCo']=="Yes"]
	receivedCases = karpelCases[0]
	shootingDataFrame = shootingDataFrame.merge(receivedCases, on='CRN', how = 'left')
	shootingDataFrame = shootingDataFrame[shootingDataFrame['Ref']=="Yes"]

	#load bonds
	bonds = "C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\BondGatherer\\AllBonds.csv"
	bondsDataFrame = pd.read_csv(bonds)
	shootingDataFrame = shootingDataFrame.merge(bondsDataFrame, on ='File #', how = 'left')

	shootingDataFrame = shootingDataFrame.drop_duplicates()

	getDefendantGender(shootingDataFrame, agencyLabel)

	getDefendantRace(shootingDataFrame, agencyLabel)

	getDefendantAge(shootingDataFrame, agencyLabel)

	getDefendantBond(shootingDataFrame, agencyLabel)

	return 0

#Main Function that calls runAnalysis.
def getDefendantDemographics(shootingDataFrame, karpelCases, agencyLabel):
	runAnalysis(shootingDataFrame, karpelCases, agencyLabel)