from DataPreparer import prepareData
from VictimDemographics import getVictimDemographics
from DefendantDemographics import getDefendantDemographics
from MapMaker import runMapMaker
from DataUploaderRunner import DataUploaderRunner
from HelperMethods import concatenateCases, loadDataFrame, getListOfAgencies, filterDataFrameByAgency, getAgencyLabel, getAgencyDictionary
from sankeyGenerator import sankeyGenerator

# Script: ViolenceDashboardRunner.py
# Purpose:  This is the main runner of the ViolenceDashboardRunner. It collects cases from the shared H-Drive, analyzes them, 
#           then uploads them to the Violence Dashboard. It utilizes Violence Data collected from the weekly Shoot Review process.
# Author:   Henry Chapman, hchapman@jacksongov.org
# Dependencies:
#	 External: Pandas, os, shutil
#	 Functions: DataPreparer, DefendantDemographics, Case VictimDemographics, HelperMethods, MapMaker, DataUploaderRunner

def main():

	#Step 1: Load shooting dataframe and get a list of police agencies.
	shootingDataFrame = loadDataFrame()
	agencyList = getListOfAgencies(shootingDataFrame)

	#Step 2: Prepare Data: Looks if we've recieved, filed, and disposed cases.
	print("Preparing Data")
	karpelCases = prepareData(shootingDataFrame, agencyList)

	#Step 3: Loops through each police agency. Conducts analytical process for each agency.
	for agency in agencyList:

		#Filter dataframe by just that agency
		agencySpecificShootings = filterDataFrameByAgency(shootingDataFrame, agency)
		agencyDictionary = getAgencyDictionary(karpelCases, agencyList)
		agencySpecificCases = agencyDictionary.get(agency)
		
		agencyLabel = getAgencyLabel(agency)
		print(agencyLabel)
		
		#Conducts victim and defendant based analysis on just that agency's cases
		getVictimDemographics(agencySpecificShootings, agencySpecificCases, agencyLabel)
		getDefendantDemographics(agencySpecificShootings, agencySpecificCases, agencyLabel)

	#Conducts analysis for entire shooting population (All Cases)
	print("Running Victim Demographics")
	getVictimDemographics(shootingDataFrame, karpelCases, "All")

	print("Running Defendant Demographics")
	getDefendantDemographics(shootingDataFrame, karpelCases, "All")

	#Generate Case Sankeys
	sankeyGenerator(shootingDataFrame, karpelCases)

	#Concatenates All Data Together to one CSV for upload
	print("Concatenating Cases")
	concatenateCases()

	#Makes a map using the geocoded points
	print("Making Map")
	runMapMaker()

	#Update Data to ESRI Dashboard.
	print("Uploading Data")
	DataUploaderRunner()

main()