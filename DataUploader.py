import os
import json
import arcgis
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from arcgis.features import FeatureLayerCollection

def main():
	print("Starting upload")
	gis = GIS("home")

	print("Violence Dashboard")
	feature_layer_item = gis.content.search("025115e9685b4cc6ae886d72864dc001")[0]
	print(feature_layer_item)
	flayers = feature_layer_item.tables
	flayer = flayers[0]
	flayer.manager.truncate()
	data_file_location = r'C:\Users\hchapman\OneDrive - Jackson County Missouri\Documents\Dashboards\Violence Dashboard - v2.0\CombinedShootingDataV2.csv'
	flayerNew = FeatureLayerCollection.fromitem(feature_layer_item)
	flayerNew.manager.overwrite(data_file_location)

	print("Violence Dashboard - Map")
	feature_layer_item = gis.content.search("786f36a3059d4129b7778d6646966905")[0]
	print(feature_layer_item)
	flayers = feature_layer_item.layers
	flayer = flayers[0]
	flayer.manager.truncate()
	data_file_location = r'C:\Users\hchapman\OneDrive - Jackson County Missouri\Documents\Dashboards\Violence Dashboard - v2.0\ShootingMapV2.csv'
	flayerNew = FeatureLayerCollection.fromitem(feature_layer_item)
	flayerNew.manager.overwrite(data_file_location)

if __name__ == "__main__":
	main()