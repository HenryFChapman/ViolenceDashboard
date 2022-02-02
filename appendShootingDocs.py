import pandas as pd 
import os 


bigDataFrame = pd.DataFrame()
listOfDataFrames = []


for year in os.listdir("ShootingData"):

	tempYear = pd.read_excel("ShootingData\\"+year)
	listOfDataFrames.append(tempYear)


bigDataFrame = pd.concat(listOfDataFrames)
bigDataFrame.to_csv("BigDataFrame.csv")