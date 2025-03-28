# hafler_lab_website
Readme
Tabs
Data Processing Side Tab
This is the part of the website that handles file I/O (in/out). Uploaded files must be CSVs (by changing file in Excel via “Save as”, then click down to comma separated values (.csv). The exact upload button will depend on whether you are uploading from a Dana Farber manifest, a UCSF manifest, a Freezerworks Export.

Once a CSV is uploaded, then two more buttons appear on the this tab:
The Freezerworks Import button contains the necessary CSV to upload for the samples to be imported into Freezerworks (via the “Modify And Add Aliquots From The Website CSVs (WITH HEADERS)”.
The “Patient Report” button generates a patient report with the following columns:
This is just an example, these exact values may or may not exist.

(Neuro) Patient ID
(HaflerLab) Substudy Visit
[one column per aliquot type to measure count. Example: PBMC Aliquot #]
P01
PRE14
1
YU03
V33
4
DF12
V17
2


Search & View
This tab allows for the viewing of information about a particular patient. If no patient is selected, the Freezerworks import dataframe* and the patient report dataframe are shown. If a patient is selected, it will list the number of aliquot types (graph one) and total amount for the aliquots (graph two) according the (HaflerLab) Substudy Visit.
It is also possible to download each from a button seen by hovering over the top right of the interactive dataframe. *If you do this, then be sure to delete the leftmost column from the freezerworks import CSV (the one filled with zeros) to prevent an import error.
Although the main function of this tab is to search up a patient, querying by other values is also allowed (and may be useful if you want a dataframe of only a particular aliquot type or (HaflerLab) Substudy Visit

Add/Edit Sample
Currently, this tab has the fewest (complete) features. Importantly, though, it can generate the (Hafler Lab) Sample IDs. To do this
Other functionality might be implemented

Summary Statistics
This tab allows you to see statistics about multiple patients at once. It allows you to see the aliquot* counts (colored by patient), aliquot *counts (colored by sample type), and aliquot counts (colored by aliquot type) per (HaflerLab) Substudy Visit. It also allows you to see the patient retention** over the (HaflerLab) Substudy Visits. Lastly, there is a graph which shows the aliquot current amount per substudy visit, colored by patient. The user must select an aliquot type (appropriate ones listed) to query.
The (HaflerLab) Substudy Visits should be in nearly ideal order. If an edge case (new visit that doesn’t follow any previous sorting rules) occurs, the red boxes can be dragged and dropped to manually change the order of the (HaflerLab) Substudy Visits to any order desired.
*Some of the graphs still say “Sample” even though they actually mean aliquot.
**computed as a fraction of the number of (Neuro) patient IDs in the leftmost (first) (HaflerLab) Substudy Visit.
Tips & Tricks
Website
Unfortunately, tumor samples & aliquots must be entered manually (they cannot be read in from a manifest).
The link to the github is: https://github.com/jwalewski/hafler_lab_website 
Freezerworks
To look at only available aliquots, select “aliquot status” “is equal to” “available” in Freezerworks
Non available aliquots should be marked as “Depleted”, except for OCT which are marked as “Temporary Storage” as they physically move to different storage when sliced and can be re-used
If Freezerworks complains about the name of “(HaflerLab) Sample ID” it’s because the column name in Freezerworks has TWO spaces instead of one. Mention that I tried to fix this, but no one responded in time. They should be able to, though.
Be careful about the EXACT number of aliquots from every site, especially when importing into freezerworks and logging sample positions… or else subsequent imports will be offset by the number of erroneous aliquots
