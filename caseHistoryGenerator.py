import pandas as pd 
import plotly.graph_objects as go
import numpy as np
from DispositionCounter import disposedCaseCounter, declinedCaseCounter
import re

def factorize(s):
    a = pd.factorize(s, sort=True)[0]
    return (a + 0.01) / (max(a) + 0.1)


def reasonsToNodes(reasonDF, links):

	reasonDictionaries = reasonDF.to_dict(orient = 'records')

	links.extend(reasonDictionaries)

	return links

def generateAllCaseHistory(crimeCategory, numberOfIncidents, atLeast1ReferredCase, receivedFileNumbers, listOfKarpelCases):

	remainingMultiDefendants = len(receivedFileNumbers) - atLeast1ReferredCase

	numberNotReferred = numberOfIncidents-atLeast1ReferredCase

	#Filed - Count How Many of Those File Numbers Appear in Filed
	filedSet = set(listOfKarpelCases[1]['File #'].tolist())
	filedFileNumbers = filedSet.intersection(receivedFileNumbers)

	#Not Filed - Count How Many of Those File Numbers Appear in Not-Filed
	declinedSet = set(listOfKarpelCases[3]['File #'].tolist())
	declinedFileNumbers = declinedSet.intersection(receivedFileNumbers)
	declinedFileNumbers = declinedFileNumbers.difference(filedSet)
	declineReasons = declinedCaseCounter(declinedFileNumbers, listOfKarpelCases[3])

	#Under Review = Received - Filed - Not Filed
	reviewSet = set(receivedFileNumbers).difference(filedSet).difference(declinedFileNumbers)

	#Disposed Cases
	disposedSet = set(listOfKarpelCases[2]['File #'].tolist())
	disposedFileNumbers = disposedSet.intersection(receivedFileNumbers)
	disposedFileNumbers = list(disposedSet.intersection(filedFileNumbers))
	disposalReasons = disposedCaseCounter(disposedFileNumbers, listOfKarpelCases[2])

	#Currently Pending/Under Warrant Status
	#Currently Pending = Filed - Disposed
	activeSet = set(filedFileNumbers).difference(disposedFileNumbers)

	links = [
		{'source': 'A - Incidents Occured', 'target':'B - Received by Office', 'value': atLeast1ReferredCase},
		{'source': 'A - Additional Defendants', 'target':'B - Received by Office', 'value':remainingMultiDefendants},
		{'source': 'A - Incidents Occured', 'target':'B - Not Received By Office', 'value':numberNotReferred},
		{'source': 'B - Received by Office', 'target':'C - Declined', 'value':len(declinedFileNumbers)},
		{'source': 'B - Received by Office', 'target':'C - Under Review', 'value':len(reviewSet)},
		{'source': 'B - Received by Office', 'target':'C - Cases Filed', 'value':len(filedFileNumbers)},
		{'source': 'C - Cases Filed', 'target':'D - Case Active', 'value':len(activeSet)},
		{'source': 'C - Cases Filed', 'target':'D - Cases Disposed', 'value':len(disposedFileNumbers)},
	]

	reasonsToNodes(disposalReasons, links)
	reasonsToNodes(declineReasons, links)

	df = pd.DataFrame(links)

	nodes = np.unique(df[["source","target"]], axis=None)
	nodes = pd.Series(index=nodes, data=range(len(nodes)))

	#work out node position
	nodes = (
		nodes.to_frame("id").assign(
			x = lambda d: factorize(d.index.str[0]),
			y = lambda d: factorize(d.index.str[0])/2,
		)
	)

	fig = go.Figure(
    	go.Sankey(
    		arrangement = "snap",
    	    node={"label": nodes.index.str[3:], "x": nodes["x"], "y": nodes["y"]},
    	    link={
    	        "source": nodes.loc[df["source"], "id"],
    	        "target": nodes.loc[df["target"], "id"],
     	       	"value": df["value"],
     	       	"color": 'grey'
     	   },
    	)
	)

	updatedTitle = crimeCategory

	if "All" in crimeCategory:
		updatedTitle = re.sub("All", "2017 through Present", crimeCategory)

	fig.update_layout(title =  dict(text ="KCPD Case Referrals of " + updatedTitle + " Cases",
                               font =dict(size=30,
                               color = 'Black')), font_size=10, title_x=0.5)	

	#fig.update_layout(title =  dict(text ="KCPD Case Referrals of " + updatedTitle + " Cases",
    #                           font =dict(size=30,
    #                           color = 'White')), font_size=15, title_x=0.5, plot_bgcolor='rgba(34,34,34,255)', paper_bgcolor='rgba(34,34,34,255)',)

	path = "C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\KCPD Clearance Dashboard\\Sankeys\\ViolenceDashboard\\"
	fig.write_html(path + crimeCategory + ".html")
