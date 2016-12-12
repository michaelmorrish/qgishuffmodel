##Consumer_Layer_with_Distance_Matrix=vector
##Consumer_Layer_ID_Field=field Consumer_Layer_with_Distance_Matrix
##Centre_Layer=vector
##Centre_Layer_ID_Field=field Centre_Layer
##Centre_Layer_Size_Field=field Centre_Layer
##Output_Layer=output file

# Script: RyersonGEo - Huff Model
# Author: Michael Morrish
# Date: December 9, 2016
#
# This script takes in two input shapefiles and three field specifications and
# produces Huff model probabilities.


# Imports.
from qgis.core import *
from PyQt4.QtCore import *

# Get the layers.
lyrConsumer = processing.getObject(Consumer_Layer_with_Distance_Matrix)
lyrCentre = processing.getObject(Centre_Layer)

# Get the fields.
fldConsumerID_index = lyrConsumer.fieldNameIndex(Consumer_Layer_ID_Field)
fldCentreID_index = lyrCentre.fieldNameIndex(Centre_Layer_ID_Field)
fldCentreSize_index = lyrCentre.fieldNameIndex(Centre_Layer_Size_Field)

# Need to prepare output layer and add new field.
# New field is "Hi" plus the ID of the Centre.
# Loop through each Centre to construct new field names.
lyrOutput = processing.getObject(Output_Layer)
provider = lyrOutput.dataProvider() 

for centreFeature in lyrCentre.getFeatures():
    
    # Capture value of fldCentreID_index (current ID).
    currentCentreID = centreFeature[fldCentreID_index]

    # Add and name the field.   
    new_field_name = 'Hi' + currentCentreID    
    provider.addAttributes([QgsField(new_field_name, QVariant.Double)])
    lyrOutput.updateFields()

# Loop through each Consumer feature.
for consumerFeature in lyrConsumer.getFeatures():
    
    # Capture value of fldConsumerID_index (current ID).
    currentConsumerID = consumerFeature[fldConsumerID_index]
    
    # Create a total field for the sumJ of Sj/dij values for use in the nested loop.
    sumJ_sjdivdij = 0.0
    
    # Huff Formula: [(sj/dij)/(SUMj(sj/dij))] for a given consumer i and centre j.
    # sumJ_sjdivdij is the denominator of this formula and is first loop below.
    # Second loop below calculates numerator and completes Huff calc for a given ij.
    
    # Loop through each Centre feature to calculate a consumer's sumJ_sjdivdij.
    # This is the Huff formula denominator.
    for centreFeature in lyrCentre.getFeatures():
        
        # Capture value of fldCentreID_index (current ID).
        currentCentreID = centreFeature[fldCentreID_index]
        
        # Capture value of fldCentreSize_index (current Centre Size).
        currentCentreSize = centreFeature[fldCentreSize_index]
        
        # Capture distance value for this Centre and this Consumer.
        # currentCentreID should match to field name in attrib table.
        currentDistance = consumerFeature[currentCentreID]
        
        # Calculate Centre Size / Distance (Sj/dij)
        sjdivdij = currentCentreSize / currentDistance
        
        # Add new Sj/dij to sumJ_sjdivdij.
        sumJ_sjdivdij = sumJ_sjdivdij + sjdivdij
        
    # Loop through each Centre a second time to calculate Huff proportion.
    for centreFeature in lyrCentre.getFeatures():
        
        # Capture value of fldCentreID_index (current ID).
        currentCentreID = centreFeature[fldCentreID_index]
        
        # Capture value of fldCentreSize_index (current Centre Size).
        currentCentreSize = centreFeature[fldCentreSize_index]
        
        # Capture distance value for this Centre and this Consumer.
        # currentCentreID should match to field name in attrib table.
        currentDistance = consumerFeature[currentCentreID]
        
        # Calculate Centre Size / Distance (Sj/dij)
        sjdivdij = currentCentreSize / currentDistance
        
        # Complete the Huff formula calculation.
        calcHuffI = sjdivdij / sumJ_sjdivdij

        # Set the value of the new Hi field for the current Consumer and Centre.
        lyrOutput.startEditing()
        current_Huff_field = 'Hi' + currentCentreID
        Huff_field_index = lyrOutput.fieldNameIndex(current_Huff_field)
        lyrOutput.changeAttributeValue(consumerFeature.id(), Huff_field_index,calcHuffI)
        lyrOutput.commitChanges()