import pandas as pd 

def overarchingType(typeList):

	if "H" in typeList:
		return "Homicide"
	else:
		return "Non-Fatal Shooting"

def countHomicideVictims(typeList):

	count = 0

	for event in typeList:
		if event == "H":
			count = count + 1

	return count 

def countNonFatalVictims(typeList):

	count = 0

	for event in typeList:
		if event == "B":
			count = count + 1

	return count

def overarchingTitle(EventList, Referred):

	for event in EventList:
		for ref in Referred:

			if event == "Homicide" and ref == "Yes":
				return 'Homicide - Referred'

			if event == 'Homicide' and ref == "No":
				return 'Homicide - Not Referred'

			if event == 'Non-Fatal Shooting' and ref == "Yes":
				return 'Non-Fatal - Referred'

			if event == 'Non-Fatal Shooting' and ref == 'No':
				return 'Non-Fata - Not Referred'

shootingDataPath = "ShootingData\\2021 Shooting Data.xlsx"


shootingData = pd.read_excel(shootingDataPath)
shootingData = shootingData[~shootingData['IncidentAddress'].str.contains('Unknown, Kansas City, MO')]
shootingData = shootingData[shootingData['JaCo']=='Yes']
shootingData['DateTime'] = shootingData.DateTime.astype(str)
underReview = shootingData[['geometry', 'Ref']]

crns = shootingData[['CRN', 'geometry']]
byCrn = shootingData.groupby('geometry')['CRN'].apply(set).apply(str).to_frame().reset_index()
byAddress = shootingData.groupby('geometry')['IncidentAddress'].apply(set).to_frame().reset_index()
byDate = shootingData.groupby('geometry')['DateTime'].apply(set).to_frame().reset_index()

byPoint = shootingData.groupby('geometry')['Type'].apply(list).to_frame().reset_index()
byPoint = byPoint.merge(underReview, on = 'geometry', how = 'left')
byPoint = byPoint.merge(byCrn, on = 'geometry', how = 'left')
byPoint = byPoint.merge(byAddress, on = 'geometry', how = 'left')
byPoint = byPoint.merge(byDate, on = 'geometry', how = 'left')
byPoint['Number of Casualties'] = byPoint.Type.apply(lambda x: len(x))

# new data frame with split value columns
byPoint["geometry"] = byPoint["geometry"].str.replace("(", "")
byPoint["geometry"] = byPoint["geometry"].str.replace(")", "")
coordinates = byPoint["geometry"].str.split(" ", n = 2, expand = True)

byPoint['Longitude'] = coordinates[1]
byPoint['Latitude'] = coordinates[2]
#print(byPoint.head())

byPoint['Event'] = byPoint.Type.apply(lambda x: overarchingType(x))
byPoint['Homicide Casualties'] = byPoint.Type.apply(lambda x: countHomicideVictims(x))
byPoint['Non-Fatal Casualties'] = byPoint.Type.apply(lambda x: countNonFatalVictims(x))

byPoint['Ref'] = byPoint['Ref'].str.replace("Yes", " - Referred")
byPoint['Ref'] = byPoint['Ref'].str.replace("No", " - Not Referred")
byPoint['Label'] = byPoint['Event'] + byPoint['Ref']


byPoint['Total Casualties'] = byPoint['Homicide Casualties'] + byPoint['Non-Fatal Casualties']

byPoint = byPoint.drop_duplicates(subset = 'CRN')

byPoint = byPoint.astype(str)

#byPoint['DateTime'] = byPoint['DateTime'].str.replace('{', "")

print(byPoint.DateTime.head())

byPoint.to_csv("MapData.csv", index = False)