import pandas as pd
import itertools
from caseHistoryGenerator import generateAllCaseHistory
import re


def sankeyGenerator(shootingDataFrame, karpelCases):

	#shootingDataFrame['CRN'] = shootingDataFrame['CRN'].astype(str).str.replace(r'\D+', '').str[:2] + "-" + shootingDataFrame['CRN'].astype(str).str.replace(r'\D+', '').str[2:].astype('int64').astype(str)
	#karpelCases[0]['CRN'] = karpelCases[0]['CRN'].astype(str).str.replace(r'\D+', '').str[:2] + "-" + karpelCases[0]['CRN'].astype(str).str.replace(r'\D+', '').str[2:].astype(float).astype('int64').astype(str)

	shootingDataFrame['Type'] = shootingDataFrame['Type'].str.replace("B", 'Non-Fatal')
	shootingDataFrame['Type'] = shootingDataFrame['Type'].str.replace("H", 'Homicide')

	incidents = shootingDataFrame.groupby('CRN')['Type'].apply(set).to_frame().reset_index()

	karpelCases[0]["File #"] = karpelCases[0]['File #'].astype(int)

	referredFileNumbers = karpelCases[0].groupby('CRN')['File #'].apply(set).to_frame().reset_index()

	years = shootingDataFrame.groupby("CRN")['Year'].apply(set).to_frame().reset_index()

	incidents = incidents.merge(referredFileNumbers, on = 'CRN', how = 'left')
	incidents = incidents.merge(years, on = 'CRN', how = 'left')


	#Get Category List
	categoryList = list(set(shootingDataFrame['Type'].tolist()))
	yearList = list(set(shootingDataFrame['Year'].tolist()))


	for category in categoryList:

		if category == "S":
			continue

		for year in yearList:

			tempDF = incidents[incidents['Type'].astype(str).str.contains(category)==True]
			tempDF = tempDF[tempDF['Year'].astype(str).str.contains(year)==True]


			numberOfIncidents = len(tempDF.index)

			tempDF = tempDF.dropna(subset = ['File #'])

			#Count Number of Non-Nulls (Number of Cases with at Least 1 Received Defendant)
			atLeast1ReferredCase = len(tempDF.index)
			
			listOfFNs = list(set(itertools.chain.from_iterable(tempDF['File #'].apply(list).tolist())))

			if listOfFNs == 0 or len(tempDF.index) == 0:
				continue

			fileName = str(year) + " - " + category

			generateAllCaseHistory(fileName, numberOfIncidents, atLeast1ReferredCase, listOfFNs, karpelCases)

		tempDF = incidents[incidents['Type'].astype(str).str.contains(category)==True]
		numberOfIncidents = len(tempDF.index)
		tempDF = tempDF.dropna(subset = ['File #'])

		#Count Number of Non-Nulls (Number of Cases with at Least 1 Received Defendant)
		atLeast1ReferredCase = len(tempDF.index)

		listOfFNs = list(set(itertools.chain.from_iterable(tempDF['File #'].apply(list).tolist())))

		if listOfFNs == 0 or len(tempDF.index) == 0:
			continue

		fileName = "All" + " - " + category
		generateAllCaseHistory(fileName, numberOfIncidents, atLeast1ReferredCase, listOfFNs, karpelCases)

	return None 
