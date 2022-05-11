import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyproj import CRS, Proj, transform

def loadShootingData():
	folder = 'ShootingData\\'
	masterShootingDataFrame = pd.DataFrame()


	frames = []
	for item in os.listdir(folder):
		tempYearDataFrame = pd.read_excel(folder+item)
		frames.append(tempYearDataFrame)

	masterShootingDataFrame = pd.concat(frames)
	return masterShootingDataFrame

def cleanData(dataFrame):
	dataFrame = dataFrame.reset_index()
	agencyDataFrame = pd.read_csv("PD Agency.csv",)
	dataFrame = dataFrame.merge(agencyDataFrame, on = "Agency", how = 'left')

	dataFrame = dataFrame[['PD NAME', 'Type','DateTime', 'Vsex', 'Vrace', 'Ref', 'Filed', 'Disposed', 'Declined', 'ILat', 'ILng']]
	
	dataFrame['DateTime'] = pd.to_datetime(dataFrame['DateTime'])
	dataFrame['Year'] = dataFrame['DateTime'].dt.year
	dataFrame['Type'] = dataFrame['Type'].replace('H', 'Homicide')
	dataFrame['Type'] = dataFrame['Type'].replace('B', 'Non-Fatal')
	dataFrame['Type'] = dataFrame['Type'].replace('S', 'Self-Inflicted')

	dataFrame = dataFrame[dataFrame['Ref'] != "NoJuris"]
	dataFrame = dataFrame[dataFrame['Type'] != "Self-Inflicted"]
	dataFrame.to_csv("ShootingMapV2.csv", encoding = 'utf-8', index = False)

def runMapMaker():
	shootingDataFrame = loadShootingData()
	cleanData(shootingDataFrame)