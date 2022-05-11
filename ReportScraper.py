from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import os
import pandas as pd
import re

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def convertPDFs(OriginDirectory, DestionationDirectory):

	rawDataExport = pd.DataFrame()

	incidentTypeList = ['HOMICIDE', 'NFS/CASUALTY', 'NFS']
	patrolsList = ['EPD/', 'SPD/', 'SCPD/', 'NPD/', 'CPD/', 'MPD/']
	CRNList = ['LOW PERSON', "MEDIUM PERSON", "HIGH PERSON"]

	DescriptorsToRemoveLevels = ['LOW', 'MEDIUM', 'HIGH']
	DescriptorsToRemoveType = ['PERSON', 'PLACE']

	count = 0
	#Per Document
	for item in os.listdir(OriginDirectory):
		outputString = ""

		#Per Page
		for page_layout in extract_pages(OriginDirectory+item):
			tempIncidentType = ""
			tempCRN = ""
			tempDate = ""
			tempAddress = ""
			tempPatrol = ""
			tempSector = ""

			#Per Element in Page
			for index, element in enumerate(page_layout):
				if isinstance(element, LTTextContainer):
					tempTextSegment = element.get_text()
					tempOutputString = re.sub(r'(?:(?<=\/) | (?=\/))','',tempTextSegment)
					tempOutputString = re.sub(r"\s\s+", " ", tempOutputString)

					for incidentType in incidentTypeList:
						if incidentType in tempOutputString and "IMPACT SCORE:" in tempOutputString:
							tempDate = re.findall(r"[\d]{1,2}[-/][\d]{1,2}[-/][\d]{4}\s\d{2}\d{2}|$", tempOutputString)[0]
							tempIncidentType = incidentType
							break

					for CRN in CRNList:
						if CRN in tempOutputString:
							justCRNSIncidents = re.sub("LOW PERSON/", "", tempOutputString)
							justCRNSIncidents = re.sub("LOW PLACE", "", justCRNSIncidents)
							justCRNSIncidents = re.sub("MEDIUM PERSON/", "", justCRNSIncidents)
							justCRNSIncidents = re.sub("MEDIUM PLACE", "", justCRNSIncidents)
							justCRNSIncidents = re.sub("HIGH PERSON/", "", justCRNSIncidents)
							justCRNSIncidents = re.sub("HIGH PLACE", "", justCRNSIncidents)

							if "CRN" in justCRNSIncidents:
								tempCRN = justCRNSIncidents.split("CRN")[1]
								tempAddress = justCRNSIncidents.split("CRN")[0]
							elif "#" in justCRNSIncidents:
								tempCRN = justCRNSIncidents.split("#")[1]
								tempAddress = justCRNSIncidents.split("#")[0]

					for patrol in patrolsList:
						if patrol in tempOutputString:
							tempOutputString = tempOutputString.upper().lstrip()
							justPatrols = re.sub("RTM AREA: NO ", "", tempOutputString)
							justPatrols = re.sub("RTM AREA: YES ", "", justPatrols)
							justPatrols = re.sub("PVO SUBJECT: NO ", "", justPatrols)
							justPatrols = re.sub("PVO SUBJECT: YES ", "", justPatrols)
							if "/" in justPatrols:
								tempPatrol = justPatrols.split("/")[0]
								tempSector = justPatrols.split("/")[1]

					if "VICTIM" in tempOutputString:
						tempOutputString = tempOutputString.split("SUSPECT")[0]


			incidentOutput = tempIncidentType + "," + tempCRN + "," + tempDate + "," + tempAddress + "," + tempPatrol + "," + tempSector + "\n"

			if ",,,,," in incidentOutput:
				continue
			else:
				outputString = outputString + incidentOutput

		textfile = open(DestionationDirectory + item.split(".")[0]+'.txt', 'w', encoding='utf-8')
		textfile.write(outputString)
		textfile.close()

def main():
	OriginDirectory = "ShootReviewReports\\"
	DestionationDirectory = "ShootReviewReports - Text\\"
	convertPDFs(OriginDirectory, DestionationDirectory)

main()