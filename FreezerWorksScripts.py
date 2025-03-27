#Part zero: import packages
import numpy
import pandas
import re
import math #was requested to use math to floor aliquot numbers
from typing import Union
from datetime import datetime
import logging
import sys
import io
import plotly.express as px
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)  # Clear existing handlers

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)

#################### I/O FUNCTIONS ###############

def read_file(input_data_filename:str, import_style:str, row_offset:Union[int, None]=None) -> pandas.DataFrame: #alternate datatypes could be pandas dataframes, both for the lists and each element
    """Reads in a csv file from varying sources (dependent on "style") and returns a pandas dataframe in a freezerworks-like format, minus the headers"""
    #We start each instance by reading in a file
    output_columns = [
        "(Neuro) Patient ID", "(HaflerLab) Substudy Visit", "(HaflerLab) Aliquot ID", 
        "(HaflerLab) Sample ID", "YCCI_Sample Type", "Sample Additive", 
        "Aliquot Type", "Sample Collection Date", "Aliquot Additive", 
        "Current Amount", "Aliquot UOM", "Sample Volume", "Sample UOM", "Notes"
    ]
    ONE_MILLION=1000000 #One million
    output_dataframe = pandas.DataFrame(columns=output_columns)
    if row_offset:
        current_dataframe = pandas.read_csv(input_data_filename, header=row_offset) #could hypothetically be moved inside the parameters for each site
    else:
        current_dataframe = pandas.read_csv(input_data_filename)
    if import_style=="DF":
        #make sure there are no completely empty rows
        #Now, parse information for the new Freezerworks style dataframe
        for idx, row in current_dataframe.iterrows(): 
            #Could one day even add an if statement up here for tumor samples if I deem it necessary
            if row.isnull().all() :
                continue #skip this row
            logging.debug(f"this loop runs, and we are on row \n {row} and index {idx}\n")
            output_row = pandas.Series()  # Temporary dictionary to store the transformed row
            # Populate each field according to the transformation logic

            # (Neuro) Patient ID
            if not pandas.isna(row["Patient ID (SitePatient Number_B_Timepoint)"]):
                neuro_patient_id = row["Patient ID (SitePatient Number_B_Timepoint)"][:2] + row["Patient ID (SitePatient Number_B_Timepoint)"][4:6] #extracts DF and ##, and then adds them
                output_row["(Neuro) Patient ID"] = neuro_patient_id
            else:
                logging.warning(f"Warning: value {row['Patient ID (SitePatient Number_B_Timepoint)']} detected in row {row}\n")
            
            # (HaflerLab) Substudy Visit
            row_value = row["Patient ID (SitePatient Number_B_Timepoint)"]
            if type(row_value) == str:
                visit_day=row_value[9:]
                if "EOT" in visit_day: #Highest priority
                    visit_day = "EOT"
                elif "SURG" in visit_day: #replace with OR
                    visit_day = "OR"
                elif visit_day[0]=="C": #replace with V... and remove D# part
                    visit_day = visit_day[:-2] #take everything but last two chars (which are always D1)
                    if len(visit_day)==2:
                        visit_day = "V0"+visit_day[1:]
                    else:
                        visit_day = "V"+visit_day[1:]
                elif visit_day == "PRE7":
                    visit_day = "PRE07"
            output_row["(HaflerLab) Substudy Visit"] = visit_day
                
            #Also, there is no condition for PRE patients, because the syntax they already use is what we use
            #print(visit_day)
            #get everything after the second underscore
    
        
            # (HaflerLab) Aliquot ID (placeholder)
            output_row["(HaflerLab) Aliquot ID"] = None  # Modify with actual logic as needed
            
            # (HaflerLab) Sample ID (placeholder)
            output_row["(HaflerLab) Sample ID"] = None  # Modify with actual logic as needed
            #line from script iteration
            #haflerlab_sample_id= ''.join(str(num) for num in [ord(char) for char in (neuro_patient_id+haflerlab_substudy_visit+ycci_sample_type+sample_volume)])+"," #creates a unique sample ID based on the concatenation of patient ID, substudy visit, sample type, and sample volume
    
            # YCCI_Sample Type
            output_row["YCCI_Sample Type"] = "Blood"
            
            # Sample Collection Date
            output_row["Sample Collection Date"] = row["Date"]
            
            # Sample UOM
            output_row["Sample UOM"] = "mL"
            
            # Notes
            output_row["Notes"] = "Computer Generated Entry"
        
            #Update Sample ID based off ASCII information 
            #output_row["(HaflerLab) Sample ID"]=''.join(str(num) for num in [ord(char) for char in (output_row["(Neuro) Patient ID"]+output_row["(HaflerLab) Substudy Visit"]+output_row["YCCI_Sample Type"]+str(output_row["Sample Volume"]))]) #suffixes a number after the sample ID for the aliqout ID
    
            #For Serum Aliquots
            #temporarily assign sample volume to 6 and aliwuot type to Serum for Serum, then 25 and PBMC for PBMC after serum for loop is done
            output_row["Sample Volume"] = 6 #Sample UOM can be filled out earlier as it is mL in both cases
            output_row["Sample Additive"] = "No Additive"
            sample_id_string = (str(output_row["(Neuro) Patient ID"])+str(output_row["(HaflerLab) Substudy Visit"])+str(output_row["YCCI_Sample Type"])+str(output_row["Sample Volume"]))
            output_row["(HaflerLab) Sample ID"] = ''.join(str(num) for num in [ord(char) for char in sample_id_string])
            #print(f"Here is sample_id_string for Serum: {sample_id_string}")
            output_row["Aliquot Type"] = "Serum"   
            output_row["Aliquot Additive"] = "No Additive"
            output_row["Aliquot UOM"] = "mL"
            #output_row["(HaflerLab) Sample ID"]=''.join(str(num) for num in [ord(char) for char in (output_row["(Neuro) Patient ID"]+output_row["(HaflerLab) Substudy Visit"]+output_row["YCCI_Sample Type"]+str(output_row["Sample Volume"]))]) #suffixes a number after the sample ID for the aliqout ID
            number_of_serum_aliquots=row["Number of Serum Vials"]
            output_row = pandas.DataFrame(output_row) #These might work up here, otherwise they will have to move into the loops
            output_row=output_row.transpose()
            if not pandas.isna(number_of_serum_aliquots):
                output_row["Current Amount"] = .5
                for i in range(int(number_of_serum_aliquots)): 
                    logging.debug(f' Sample_id_string is: {sample_id_string} and its type is: {type(sample_id_string)}\nMeanwhile, output_row["(Neuro) Patient ID"]) is: {output_row["(Neuro) Patient ID"]}\noutput_row["(HaflerLab) Substudy Visit"] is: {output_row["(HaflerLab) Substudy Visit"]}\noutput_row["YCCI_Sample Type"] is: {output_row["YCCI_Sample Type"]}\noutput_row["Sample Volume"] is {output_row["Sample Volume"]}')
                    output_row["(HaflerLab) Aliquot ID"] = ''.join(str(num) for num in [ord(char) for char in sample_id_string])+"."+str(i)#suffixes a number after the sample ID for the aliqout ID
                    logging.debug(f'We are outputting aliquot number {i} with sample ID {output_row["(HaflerLab) Sample ID"]} and aliquot id {output_row["(HaflerLab) Aliquot ID"]}')
                    output_dataframe = pandas.concat([output_dataframe, output_row])
            
            #For PBMC Aliquots
            output_row["Sample Volume"] = 25  #Sample UOM can be filled out earlier as it is mL in both cases
            output_row["Sample Additive"] = "Lithium Heparin"
            output_row["Aliquot Type"] = "PBMC"
            output_row["Aliquot Additive"] = "DMSO"
            output_row["Aliquot UOM"] = "million"
            #output_row["(HaflerLab) Sample ID"]=''.join(str(num) for num in [ord(char) for char in (output_row["(Neuro) Patient ID"]+output_row["(HaflerLab) Substudy Visit"]+output_row["YCCI_Sample Type"]+str(output_row["Sample Volume"]))]) #suffixes a number after the sample ID for the aliqout ID
            sample_id_string = (str(output_row["(Neuro) Patient ID"].values[0])+str(output_row["(HaflerLab) Substudy Visit"].values[0])+str(output_row["YCCI_Sample Type"].values[0])+str(output_row["Sample Volume"].values[0]))
            logging.debug(f"Here is sample_id_string for PBMCs: {sample_id_string}")
            output_row["(HaflerLab) Sample ID"] = ''.join(str(num) for num in [ord(char) for char in sample_id_string])
            number_of_pbmc_aliquots=row["Number of PBMCs Vials"]
            # Current Amount
            logging.debug(f'This is {row["PBMC count (total cells/sample)"]} and this is wether it is pandas.isna(): {pandas.isna(row["PBMC count (total cells/sample)"])} and whether it is numpy.isnan(): {numpy.isnan(row["PBMC count (total cells/sample)"])}')
            if (not pandas.isna(number_of_pbmc_aliquots)) and (not pandas.isna(row["PBMC count (total cells/sample)"])):
                output_row["Current Amount"] = math.floor(int(row["PBMC count (total cells/sample)"]) / int(number_of_pbmc_aliquots)/ONE_MILLION) #if not pandas.isna(row["PBMC count (total cells/sample)"]) else print(f"Warning: NA value {row["PBMC count (total cells/sample)"]} in row {row}")
                for i in range(int(number_of_pbmc_aliquots)):
                    id_string = (str(output_row["(Neuro) Patient ID"].values[0])+str(output_row["(HaflerLab) Substudy Visit"].values[0])+str(output_row["YCCI_Sample Type"].values[0])+str(output_row["Sample Volume"].values[0]))
                    #output_row["(HaflerLab) Aliquot ID"] = ''.join(str(num) for num in [ord(char) for char in id_string])+"."+str(i)#suffixes a number after the sample ID for the aliqout ID
                    logging.debug(f'id_string is: {id_string} and its type is: {type(id_string)}\nMeanwhile, output_row["(Neuro) Patient ID"]) is: {output_row["(Neuro) Patient ID"]}\noutput_row["(HaflerLab) Substudy Visit"] is: {output_row["(HaflerLab) Substudy Visit"]}\noutput_row["YCCI_Sample Type"] is: {output_row["YCCI_Sample Type"]}\noutput_row["Sample Volume"] is {output_row["Sample Volume"]}')
                    output_row["(HaflerLab) Aliquot ID"] = ''.join(str(num) for num in [ord(char) for char in sample_id_string])+"."+str(i)#suffixes a number after the sample ID for the aliqout ID
                    logging.debug(f'We are outputting aliquot number {i} with sample ID {output_row["(HaflerLab) Sample ID"]} and aliquot id {output_row["(HaflerLab) Aliquot ID"]}')
                    output_dataframe = pandas.concat([output_dataframe, output_row])
        return output_dataframe 
    
    if import_style == "SF":
        #Remove rows with NA PBMC counts that represent the other PBMC samples via bitwise logic
        current_dataframe = current_dataframe.loc[~((current_dataframe["Cell Count"].isna()) & (current_dataframe["Sample Type"] == "PBMC"))]
        #do regex to convert scientific notation to python friendly version
        #in theory, this could be done inside the loop for efficiency, but that will come later
        current_dataframe["Cell Count"] = current_dataframe["Cell Count"].apply(lambda x: float(re.sub(r'.10\^', 'e', str(x))) if (isinstance(x, str) and ('X10^' or 'x10' in x)) else x)
        #Now, parse information for the new Freezerworks style dataframe
        for idx, row in current_dataframe.iterrows():
            #print(f"this loop runs, and we are on row \n {row} and index {idx}\n")
            output_row = pandas.Series()  # Temporary dictionary to store the transformed row
            # Populate each field according to the transformation logic
            
            # (Neuro) Patient ID
            neuro_patient_id = "SF" + row["Sample ID"][-2:] if isinstance(row["Sample ID"], str) else None
            output_row["(Neuro) Patient ID"] = neuro_patient_id
            
            # (HaflerLab) Substudy Visit
            visit_day = row.get("Visit Day", "")
            if "C" in visit_day:
                number=re.search("[0-9]+", visit_day)
                number=str(number.group()) #extracts the actual # from number and converts it to a str
                if len(number) ==1:
                    output_row["(HaflerLab) Substudy Visit"] = "V0" + visit_day[1]
                else:
                    output_row["(HaflerLab) Substudy Visit"] = "V" + visit_day[1]
                
            elif "PRE" in visit_day: #will have to handle later; current manifest does not have this so I don't know that their syntax is
                output_row["(HaflerLab) Substudy Visit"] = visit_day
            elif any(term in visit_day for term in ["OR", "SURG"]): #will have to handle later; current manifest does not have this so I don't know that their syntax is
                output_row["(HaflerLab) Substudy Visit"] = visit_day
            elif "Safety Follow Up" in visit_day:
                output_row["(HaflerLab) Substudy Visit"] = "FU01" #stands for follow up. For now, we only have 01.
            else:
                raise Exception(f"Invalid timepoint {visit_day} in Visit Day. Check CSV.")
        
            # (HaflerLab) Aliquot ID (placeholder)
            output_row["(HaflerLab) Aliquot ID"] = None  # Modify with actual logic as needed
            
            # (HaflerLab) Sample ID (placeholder)
            output_row["(HaflerLab) Sample ID"] = None  # Modify with actual logic as needed
            #line from script iteration
            #haflerlab_sample_id= ''.join(str(num) for num in [ord(char) for char in (neuro_patient_id+haflerlab_substudy_visit+ycci_sample_type+sample_volume)])+"," #creates a unique sample ID based on the concatenation of patient ID, substudy visit, sample type, and sample volume

            # YCCI_Sample Type
            output_row["YCCI_Sample Type"] = "Blood"
        
            # Sample Additive
            output_row["Sample Additive"] = "Lithium Heparin" if row["Sample Type"] == "PBMC" else "No Additive"
        
            # Aliquot Type
            output_row["Aliquot Type"] = row["Sample Type"]
        
            # Sample Collection Date
            output_row["Sample Collection Date"] = row["Sample Date"]
        
            # Aliquot Additive
            output_row["Aliquot Additive"] = "DMSO" if row["Sample Type"] == "PBMC" else "No Additive"
        
            # Current Amount
            output_row["Current Amount"] = math.floor(int(row["Cell Count"]) / int(row["Number of Aliquots Total"])/ONE_MILLION) if row["Sample Type"] == "PBMC" else 0.5
        
            # Aliquot UOM
            output_row["Aliquot UOM"] = "million" if row["Sample Type"] == "PBMC" else "mL"
        
            # Sample Volume
            output_row["Sample Volume"] = 25 if row["Sample Type"] == "PBMC" else 6
        
            # Sample UOM
            output_row["Sample UOM"] = "mL"
            
            # Notes
            output_row["Notes"] = "Computer Generated Entry"
        
            #Update Sample ID based off ASCII information 
            output_row["(HaflerLab) Sample ID"]=''.join(str(num) for num in [ord(char) for char in (output_row["(Neuro) Patient ID"]+output_row["(HaflerLab) Substudy Visit"]+output_row["YCCI_Sample Type"]+str(output_row["Sample Volume"]))]) #suffixes a number after the sample ID for the aliqout ID

            #convert series to DataFrame
            output_row=pandas.DataFrame(output_row)
            output_row=output_row.transpose()
        
            logging.debug(f"output row is: \n{output_row}\n")
            
            # Append the transformed row to Freezerworks_CSVsframe depending on the number of aliqouts with this information
            number_of_aliquots=row["Number of Aliquots Total"]
            for i in range(int(number_of_aliquots)):
                id_string = (str(output_row["(Neuro) Patient ID"].values[0])+str(output_row["(HaflerLab) Substudy Visit"].values[0])+str(output_row["YCCI_Sample Type"].values[0])+str(output_row["Sample Volume"].values[0]))
                logging.debug(f'id_string is: {id_string} and its type is: {type(id_string)}\nMeanwhile, output_row["(Neuro) Patient ID"]) is: {output_row["(Neuro) Patient ID"]}\noutput_row["(HaflerLab) Substudy Visit"] is: {output_row["(HaflerLab) Substudy Visit"]}\noutput_row["YCCI_Sample Type"] is: {output_row["YCCI_Sample Type"]}\noutput_row["Sample Volume"] is {output_row["Sample Volume"]}')
                output_row["(HaflerLab) Aliquot ID"] = ''.join(str(num) for num in [ord(char) for char in id_string])+"."+str(i)#suffixes a number after the sample ID for the aliqout ID
                output_dataframe = pandas.concat([output_dataframe, output_row])
        return output_dataframe



    if import_style=="Freezer_Works_Import": #there is no YU style because we don't have a manifest for ourselves. Instead it's just the freezerworks exports, which could come from any site
        #this one should be fairly easy because we're just re-importing the CSV
        output_columns= [
            "(Neuro) Patient ID", "(HaflerLab) Substudy Visit", "(HaflerLab) Aliquot ID", 
            "(HaflerLab) Sample ID", "YCCI_Sample Type", "Sample Additive", 
            "Aliquot Type", "Sample Collection Date", "Aliquot Additive", 
            "Current Amount", "Aliquot UOM", "Sample Volume", "Sample UOM", "Notes"
        ] #required to assign unique column names to sort 
        #Note, technically ones exported straight from FW will have the headers still in and an empty row in the indexes, so they should have headers and indices of 0      
        if(len(current_dataframe.columns) == len(output_columns)):
            current_dataframe.columns = output_columns
            current_dataframe = current_dataframe.set_index("(Neuro) Patient ID")
            return current_dataframe
        else:
            if len(current_dataframe.columns ==30):#30 is the # of columns that FW exports
                raise Exception(f"The number of columns in the old dataframe ({len(current_dataframe.columns)}) does not match the number of columns that is expected of this style ({len(output_columns)}). Did you mean style=Freezer_Works_Export ?")
            else:
                raise Exception(f"The number of columns in the old dataframe ({len(current_dataframe.columns)}) does not match the number of columns that is expected of this style ({len(output_columns)}).")

    if import_style=="Freezer_Works_Export":
        output_columns= [
            "(Neuro) Patient ID", "(HaflerLab) Substudy Visit", "(HaflerLab) Aliquot ID", 
            "(HaflerLab) Sample ID", "YCCI_Sample Type", "Sample Additive", 
            "Aliquot Type", "Sample Collection Date", "Aliquot Additive", 
            "Current Amount", "Aliquot UOM", "Sample Volume", "Sample UOM", #Notes is not in the "Hafler Lab" Export, but I could make a new export style on FW with it if needed
        ] #required to assign unique column names to sort 
        #Note, technically ones exported straight from FW will have the headers still in and an empty row in the indexes, so they should have headers and indices of 0      
        try:
            #Before assinging the dataframe, we have to be sure that the column is renamed in case it has the double space for sample ID
            current_dataframe.columns = current_dataframe.columns.str.replace(r'\s+', ' ', regex=True)
            current_dataframe =current_dataframe[output_columns]
            current_dataframe["(HaflerLab) Substudy Visit"] = current_dataframe["(HaflerLab) Substudy Visit"].apply(lambda x: str(x).replace(" ", "") if " " in str(x) else x) #Erase all spaces in visit dates
            #current_dataframe["(HaflerLab) Substudy Visit"].apply(lambda x: "PRE07" if "PRE7" in str(x) else x) #Cast PRE7 visits as PRE07
            current_dataframe["(HaflerLab) Substudy Visit"] = current_dataframe["(HaflerLab) Substudy Visit"].replace("PRE7", "PRE07")#.astype(str).str.
            current_dataframe["(HaflerLab) Substudy Visit"].fillna("No Visit Specified", inplace=True) #Catch times when substudy visit is empty
            return current_dataframe
        except Exception:
            raise Exception(f"The input dataframe has column names {current_dataframe.columns}, while it should have the following names: {output_columns}")

 

def export_dataframe(input_dataframe: pandas.DataFrame, style:str="Freezer_Works_Import", output_filename:str=None, row_offset: Union[None,int]=None, column_offset: Union[None,int]=None) -> pandas.DataFrame:
    """Expects a dataframe in FW-import sytle, minus any headers or indices. Can either write it to a CSV for import into FW, or can generate a sample map CSV for use in the Hafler Lab sample map format. """
    
    if output_filename == None:
        output_filename=f"TEST_{style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" #.csv extension is appended later, once sample type is determined

    if style == "Freezer_Works_Import":
        #input_dataframe.to_csv(output_filepath, header=False, index=False) #To import into freezerworks the header and indices must be discarded
        return input_dataframe
    elif style == "Sample_Map":
        input_dataframe["Internal Date"] = pandas.to_datetime(input_dataframe["Sample Collection Date"], format='%m/%d/%y')
        input_dataframe_sorted = input_dataframe.sort_values(by=["Internal Date", "(Neuro) Patient ID"], ascending=[True, True])
        serum_Sample_Map_dataframe=pandas.DataFrame()#(columns="Column 1")
        pbmc_Sample_Map_dataframe=pandas.DataFrame()
        serum_aliquots = pandas.Series()
        pbmc_aliquots = pandas.Series()
        for index, row in input_dataframe_sorted.iterrows():
            logging.debug(f"row is: {row} and index is: {index}")
            #Extract Relevant information
            #Patient ID
            patient_id = row["(Neuro) Patient ID"]
            logging.debug(f"This is patient_id: {patient_id}")
            #Timepoint
            timepoint = row["(HaflerLab) Substudy Visit"]
            logging.debug(f"This is timepoint: {timepoint}")
            #sample collection date
            date = row["Sample Collection Date"]
            logging.debug(f"This is date: {date}")
            #current amount
            current_amount = str(row["Current Amount"])
            logging.debug(f"This is current_amount: {current_amount}")
            #aliquot UOM
            aliquot_uom = row["Aliquot UOM"]
            logging.debug(f"This is aliquot_uom: {aliquot_uom}")
        
            entry_string = patient_id+timepoint+" "+date+" "+current_amount+aliquot_uom  
            logging.debug(f"This is entry_string: {entry_string}")
        
            
            if row["Aliquot Type"] == "PBMC":
        
                #add to PBMC Sample Series
                new_series = pandas.Series(entry_string)
                logging.debug(f"new_series is: {new_series}")
                pbmc_aliquots = pandas.concat([pbmc_aliquots, new_series])
                logging.debug(f"pbmc_aliquots is: {pbmc_aliquots}")
                #turn row into dataframe and transpose
                #then add to map
                #then,
                #maybe in here check to see if series length is 10, then write to dataframe, then reset?
                if len(pbmc_aliquots) == 10:
                    pbmc_aliquots = pandas.DataFrame(pbmc_aliquots)
                    pbmc_aliquots = pbmc_aliquots.transpose()
                    pbmc_Sample_Map_dataframe = pandas.concat([pbmc_Sample_Map_dataframe, pbmc_aliquots], ignore_index=True)
                    logging.debug(f"pbmc_Sample_Map_dataframe is: {pbmc_Sample_Map_dataframe}")
                    #now, reset pbmc_aliquots so it doesn't mess up the next version of the loop
                    pbmc_aliquots = pandas.Series()
            if row["Aliquot Type"] == "Serum":
        
                #add to serum Sample Series
                new_series = pandas.Series(entry_string)
                logging.debug(f"new_series is: {new_series}")
                serum_aliquots = pandas.concat([serum_aliquots, new_series])
                logging.debug(f"serum_aliquots is: {serum_aliquots}")
                #turn row into dataframe and transpose
                #then add to map
                #then,
                #maybe in here check to see if series length is 10, then write to dataframe, then reset?
                if len(serum_aliquots) == 10:
                    serum_aliquots = pandas.DataFrame(serum_aliquots)
                    serum_aliquots = serum_aliquots.transpose()
                    serum_Sample_Map_dataframe = pandas.concat([serum_Sample_Map_dataframe, serum_aliquots], ignore_index=True) #indexing error that I will have to address later
                    logging.debug(f"serum_Sample_Map_dataframe is: {serum_Sample_Map_dataframe}")
                    #now, reset serum_aliquots so it doesn't mess up the next version of the loop
                    serum_aliquots = pandas.Series()
        

        #Code to handle when the final row has less than 10 aliquots, in which case it will need padding with an empty string
        serum_aliquot_length_difference = 10-len(serum_aliquots)
        if serum_aliquot_length_difference > 0: #Checking if any difference exists
            extra_spaces = pandas.Series([" "] * serum_aliquot_length_difference)
            serum_aliquots = pandas.concat([serum_aliquots, extra_spaces], ignore_index=True)
        serum_aliquots = pandas.DataFrame(serum_aliquots)
        serum_aliquots = serum_aliquots.transpose()
        serum_aliquots.columns=[0]*10 # Sets all column names to 0, which allows for concatenation with the rest of the sample map dataframe
        serum_Sample_Map_dataframe = pandas.concat([serum_Sample_Map_dataframe, serum_aliquots], ignore_index=True) #this needs to run one more time after the loop is over so that the remaining samples are added

        pbmc_aliquot_length_difference = 10-len(pbmc_aliquots)
        if pbmc_aliquot_length_difference > 0: #Checking if any difference exists
            extra_spaces = pandas.Series([" "] * pbmc_aliquot_length_difference)
            pbmc_aliquots = pandas.concat([pbmc_aliquots, extra_spaces], ignore_index=True)
        pbmc_aliquots = pandas.DataFrame(pbmc_aliquots)
        pbmc_aliquots = pbmc_aliquots.transpose()
        pbmc_aliquots.columns=[0]*10 # Sets all column names to 0, which allows for concatenation with the rest of the sample map dataframe
        pbmc_Sample_Map_dataframe = pandas.concat([pbmc_Sample_Map_dataframe, pbmc_aliquots], ignore_index=True) #this needs to run one more time after the loop is over so that the remaining samples are added
        
        #writing to outputfile
        #output_filename+="_serum.csv"
        #serum_Sample_Map_dataframe.to_csv(output_filepath+output_filename, header=False, index=False)
        #output_filename=output_filename[:-10] #remove last 10 chars, which was the previous ending
        #output_filename+="_pbmc.csv"
        #pbmc_Sample_Map_dataframe.to_csv(output_filepath+output_filename, header=False, index=False)
        return serum_Sample_Map_dataframe, pbmc_Sample_Map_dataframe

    elif style == "Patient_Report":
        patient_input_dataframe = input_dataframe
        # Initialize counts and placeholders
        serum_count = 0
        pbmc_count = 0
        tumor_oct_count = 0
        tumor_scrnaseq_count = 0
        previous_patient_id = None
        previous_visit_id = None

        # Placeholder for aggregated data
        patient_2D_array = []

        #sort dataframe by patient
        #convert row to appropriate datetime format
        patient_input_dataframe["Sample Collection Date"] = pandas.to_datetime(patient_input_dataframe["Sample Collection Date"])
        patient_input_dataframe=patient_input_dataframe.sort_values(by=["(Neuro) Patient ID", "Sample Collection Date"]) #has to be by sample collection date so OR and EOT appear in the right spot

        # Iterate over the DataFrame rows
        for idx, row in patient_input_dataframe.iterrows():
            # Extract current patient and visit IDs
            current_patient_id = row["(Neuro) Patient ID"]
            current_visit_day = row["(HaflerLab) Substudy Visit"]
            current_sample_collection_date = row["Sample Collection Date"]
            #print(f"Row is: {row}, Current Patient ID is: {current_patient_id}, Current Visit Day is: {current_visit_day}, and Sample Collection Date is: {current_sample_collection_date}")

            # Reset counts for a new patient or visit
            if (current_patient_id != previous_patient_id) or (current_visit_day != previous_visit_id):
                #Append data for this row only if we switch patients - so we have one entry for each patient-visit combo
                if previous_patient_id is not None: #Don't append until we have patient data to append
                    patient_2D_array.append([
                        previous_patient_id,
                        previous_visit_id,
                        previous_sample_collection_date,
                        serum_count,
                        pbmc_count,
                        tumor_oct_count,
                        tumor_scrnaseq_count
                    ])
                #reset variables after writing to array
                serum_count = 0
                pbmc_count = 0
                tumor_oct_count = 0
                tumor_scrnaseq_count = 0


            # Increment counts based on aliquot type
            if row["Aliquot Type"] == "Serum":
                serum_count += 1
            elif row["Aliquot Type"] == "PBMC":
                pbmc_count += 1
            elif row["Aliquot Type"] == "Tumor in OCT":
                tumor_oct_count += 1
            elif row["Aliquot Type"] == "Tumor in BamBanker":
                tumor_scrnaseq_count += 1
            # Update previous patient and visit IDs
            previous_patient_id = current_patient_id
            previous_visit_id = current_visit_day
            previous_sample_collection_date=current_sample_collection_date


        #ENSURE FINAL ROW IS APPENDED!
        patient_2D_array.append([
            previous_patient_id,
            previous_visit_id,
            previous_sample_collection_date,
            serum_count,
            pbmc_count,
            tumor_oct_count,
            tumor_scrnaseq_count
        ])


        

        # Convert patient_2D_array to DataFrame
        columns = ["(Neuro) Patient ID", "(HaflerLab) Substudy Visit", "Sample Collection Date",
                "Serum Count", "PBMC Count", "Tumor in OCT Count", "Sc-RNAseq Tumor Count"]
        patient_report_df = pandas.DataFrame(patient_2D_array, columns=columns)

        # Set MultiIndex for hierarchical structure
        patient_report_df.set_index(["(Neuro) Patient ID", "(HaflerLab) Substudy Visit"], inplace=True)

        # Save DataFrame to CSV
        #output_path = f"../data/exports/patient_report_dataframe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return patient_report_df
    else:
        raise Exception("Invalid Style Given.")
    
def convert_df_to_csv(df, show_index):
    output = io.BytesIO()
    df.to_csv(output, index=show_index) #False for Freezerworks Export and True for Patient Report
    return output.getvalue()
    
######## ADD/MODIFY SAMPLE PAGE #########
def generate_ascii_aliquot_id(patient_id, visit, sample_type, volume, aliquot_index=0):#need some way to keep track of and incrememnt aliquot index
    id_string = f"{patient_id}{visit}{sample_type}{volume}"
    ascii_id = ''.join(str(ord(char)) for char in id_string)
    aliquot_id = f"{ascii_id}.{aliquot_index}"
    return aliquot_id


#################### PLOTTING FUNCTIONS ###############
######### VIEW PATIENT PAGE ##########
# def plot_patient_samples_and_amounts(df, patient_id, visit_col, aliquot_col, amount_col):
#     patient_df = df[df['(Neuro) Patient ID'] == patient_id].copy()
#     patient_df[visit_col] = patient_df[visit_col].str.strip()

#     sample_counts = (
#         patient_df.groupby([visit_col, aliquot_col])
#         .size()
#         .reset_index(name='Sample Count')
#     )

#     fig_samples = px.bar(
#         sample_counts,
#         x=visit_col,
#         y='Sample Count',
#         color=aliquot_col,
#         title=f'Sample Count per Visit for Patient {patient_id}',
#         barmode='stack'
#     )

#     current_amounts = (
#         patient_df.groupby([visit_col, aliquot_col])[amount_col]
#         .sum()
#         .reset_index()
#     )

#     fig_amounts = px.bar(
#         current_amounts,
#         x=visit_col,
#         y=amount_col,
#         color=aliquot_col,
#         title=f'Current Amount per Visit for Patient {patient_id}',
#         barmode='stack'
#     )

#     return fig_samples, fig_amounts
def plot_patient_samples_and_amounts(df, patient_id, visit_col, aliquot_col, amount_col, barmode='group'):
    # Subset for the specific patient
    patient_df = df#[df['(Neuro) Patient ID'] == patient_id].copy()
    patient_df[visit_col] = patient_df[visit_col].str.strip()

    # Define the visit order (this should match your project’s visit order convention)
    visit_order = ['PRE14', 'PRE10', 'PRE07', 'OR', 'V00', 'V01', 'V02', 'V03', 'V04', 
                   'V05', 'V06', 'V07', 'V08', 'V09', 'V10', 'EOT']

    # Filter down to just the visits that actually exist in this patient's data
    actual_visits = patient_df[visit_col].unique().tolist()
    ordered_visits = [v for v in visit_order if v in actual_visits]
    extra_visits = [v for v in actual_visits if v not in visit_order]
    final_order = ordered_visits + sorted(extra_visits)

    # Apply categorical ordering
    patient_df[visit_col] = pandas.Categorical(patient_df[visit_col], categories=final_order, ordered=True)

    # Sample count plot (number of rows per aliquot per visit)
    sample_counts = (
        patient_df.groupby([visit_col, aliquot_col])
        .size()
        .reset_index(name='Sample Count')
    )

    fig_samples = px.bar(
        sample_counts,
        x=visit_col,
        y='Sample Count',
        color=aliquot_col,
        title=f'Sample Count per Visit for Patient {patient_id}',
        barmode=barmode
    )
    fig_samples.update_xaxes(categoryorder='array', categoryarray=final_order)

    # Total amount plot (sum of aliquot amounts per visit)
    current_amounts = (
        patient_df.groupby([visit_col, aliquot_col])[amount_col]
        .sum()
        .reset_index()
    )

    fig_amounts = px.bar(
        current_amounts,
        x=visit_col,
        y=amount_col,
        color=aliquot_col,
        title=f'Current Amount per Visit for Patient {patient_id}',
        barmode=barmode
    )
    fig_amounts.update_xaxes(categoryorder='array', categoryarray=final_order)

    return fig_samples, fig_amounts





######### SUMMARY PAGE ##########
# def sort_patient_visits(df: pandas.DataFrame, visit_column_name:str, eot_label):
#     all_visits = df[visit_column_name].str.upper()  # Ensure all visit labels are uppercase
#     all_visits = df[visit_column_name].str.replace(" ","")  #remove all spaces from name

#     def visit_sort_key(visit):
#         # Special cases
#         special_cases = {
#             'ARC': -5,
#             'PRETRIAL': -4,
#             'PRE-TRIAL': -4,
#             'PRE14': -3,
#             'PRE10': -2,
#             'PRE7': -1,
#             'PRE07': -1,
#             'PRE0': 0,
#             'OR(PRE)': -0.5,
#             'OR':0,
#             'OR(POST)': 0,
#             'SURG': 0,
#             'POD1': 9998,  # Second to last
#             eot_label: 9999    # Last entry
#         }
#         if visit in special_cases:
#             return special_cases[visit]

#         #In this order to ensure exactly one match
#         #print(f"visit is: {visit}")
#         day_specific_match = re.match(r"V(\d+)D(\d+)", visit)
#         if day_specific_match:
#             print(f" The day specific match assigns a key value of: {int(day_specific_match.group(1))+ ((int(day_specific_match.group(2))-1)/100)} on input {visit}")
#             return (int(day_specific_match.group(1))+ ((int(day_specific_match.group(2))-1)/100)) #Will create a slightly higher key value for pts where the day isn't 1. Unless there are over 100 days in a visit, but this won't happen
#         standard_visit_match = re.match(r"V(\d+)", visit)
#         # Handle standard visit formats (e.g., V01D01)
#         if standard_visit_match: #Cannot be elif since the standard_visit_match check happens after the if block (to ensure it's not checked on samples with V01D01, for example)
#             return int(standard_visit_match.group(1))
#         # Handle day specific visit formats (e.g., V01D01)
#         else:
#             # Catch-all for unexpected formats
#             #print(f"This is our unexpected vist {visit}")
#             return float('inf')

#     # Sort and return
#     sorted_visits = sorted(all_visits, key=visit_sort_key)
#     print(f"New sorting function: sorted_visits is: {sorted_visits}")
#     df["visit_column_name_seed"] = sorted_visits
#     #df[visit_column_name] = pandas.Categorical(df[visit_column_name], categories= df["visit_column_name_seed"], ordered=True) #Forces ordering this way.

#     return df




# def sort_patient_visits(df: pandas.DataFrame, visit_column_name:str, eot_label):
#     all_visits = df[visit_column_name].str.upper()  # Ensure all visit labels are uppercase
#     all_visits = df[visit_column_name].str.replace(" ","")  #remove all spaces from name

#     def visit_sort_key(visit):
#         # Special cases
#         special_cases = {
#             'ARC': -5,
#             'PRETRIAL': -4,
#             'PRE-TRIAL': -4,
#             'PRE14': -3,
#             'PRE10': -2,
#             'PRE7': -1,
#             'PRE07': -1,
#             'PRE0': 0,
#             'OR(PRE)': -0.5,
#             'OR':0,
#             'OR(POST)': 0,
#             'SURG': 0,
#             'POD1': 9998,  # Second to last
#             eot_label: 9999    # Last entry
#         }
#         if visit in special_cases:
#             return special_cases[visit]

#         #In this order to ensure exactly one match
#         #print(f"visit is: {visit}")
#         day_specific_match = re.match(r"V(\d+)D(\d+)", visit)
#         if day_specific_match:
#             print(f" The day specific match assigns a key value of: {int(day_specific_match.group(1))+ ((int(day_specific_match.group(2))-1)/100)} on input {visit}")
#             return (int(day_specific_match.group(1))+ ((int(day_specific_match.group(2))-1)/100)) #Will create a slightly higher key value for pts where the day isn't 1. Unless there are over 100 days in a visit, but this won't happen
#         standard_visit_match = re.match(r"V(\d+)", visit)
#         # Handle standard visit formats (e.g., V01D01)
#         if standard_visit_match: #Cannot be elif since the standard_visit_match check happens after the if block (to ensure it's not checked on samples with V01D01, for example)
#             return int(standard_visit_match.group(1))
#         # Handle day specific visit formats (e.g., V01D01)
#         else:
#             # Catch-all for unexpected formats
#             #print(f"This is our unexpected vist {visit}")
#             return float('inf')

#     # Sort and return
#     sorted_visits = sorted(all_visits, key=visit_sort_key)
#     print(f"New sorting function: sorted_visits is: {sorted_visits}")
#     df["visit_column_name_seed"] = sorted_visits
#     #df[visit_column_name] = pandas.Categorical(df[visit_column_name], categories= df["visit_column_name_seed"], ordered=True) #Forces ordering this way.

#     return df
def sort_patient_visits(df: pandas.DataFrame, visit_column_name: str, eot_label: str):
    print(f"The type of df at the start of sort_patient_visits is: {type(df)}")
    df[visit_column_name] = df[visit_column_name].str.upper().str.replace(" ", "")  # Clean visit labels

    def visit_sort_key(visit):
        special_cases = {
            'ARC': -5, 'PRETRIAL': -4, 'PRE-TRIAL': -4, 'PRE14': -3, 'PRE10': -2,
            'PRE7': -1, 'PRE07': -1, 'PRE0': 0, 'OR(PRE)': -0.5, 'OR': 0, 'OR(POST)': 0, 'POSTOP':0,
            'SURG': 0, 'POD1': 9998, eot_label: 9999
        }
        if visit in special_cases:
            return special_cases[visit]

        day_specific_match = re.match(r"V(\d+)D(\d+)", visit)
        if day_specific_match:
            return int(day_specific_match.group(1)) + ((int(day_specific_match.group(2)) - 1) / 100)

        standard_visit_match = re.match(r"V(\d+)", visit)
        if standard_visit_match:
            return int(standard_visit_match.group(1))

        return float('inf')  # Catch-all

    # **Sort entire dataframe based on computed visit order**
    df["visit_column_name_seed"] = df[visit_column_name].apply(visit_sort_key)
    df = df.sort_values(by="visit_column_name_seed").drop(columns=["visit_column_name_seed"])
    df = df.reset_index(drop=True)#drop old indexes
    return df


def plot_patient_retention(df, patient_col, visit_col):
    # Clean up the visit column — extra spaces are the enemy
    #df[visit_col] = df[visit_col].str.strip() #Attempting seeing how this without the strip
    eot_label = 'EOT'

    #Effectively old sorting function
    # # Define your standard visit order
    # base_order = ['PRE14', 'PRE10', 'PRE07', 'OR', 'V00', 'V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07', 'V08', 'V09', 'V10']


    # # Identify what's actually in the data
    # actual_visits = df[visit_col].unique().tolist()
    # #print("This is actual_visits in the plot_patient_Retention function: ", actual_visits)

    # # Split visits into:
    # # - standard ones (already in your order list)
    # # - unexpected ones (we'll just sort alphabetically)
    # standard_visits = [visit for visit in base_order if visit in actual_visits]
    # extra_visits = [visit for visit in actual_visits if visit not in base_order and visit != eot_label]

    # # Build final visit order: standard + unexpected (sorted) + EOT at the end if present
    # #print(f"These are the extra visits {extra_visits} And here they are as a string: {str(extra_visits)}, and here they are sorted: {sorted(str(extra_visits))}")
    # final_order = standard_visits + sorted((extra_visits)) #Will soon make a custom sorting function
    # if eot_label in actual_visits:
    #     final_order.append(eot_label)

    # # Check for debugging if needed
    # print("Visit order being used in the OLD FUNCTION FOR plot patient retention:", final_order)

    # # Force the visit column to obey this exact order
    # df[visit_col] = pandas.Categorical(df[visit_col], categories=final_order, ordered=True)







    #new sorting function
    df = sort_patient_vists(df, "(HaflerLab) Substudy Visit", eot_label)


    #Compute retention from first visit
    first_visit = 'PRE14'  # Adjust if needed
    patient_count_initial = df[df[visit_col] == first_visit][patient_col].nunique()

    retention = (
        df.groupby(visit_col)[patient_col]
        .nunique()
        .reset_index()
        .rename(columns={patient_col: 'Patient Count'})
    )
    retention['Retention %'] = (retention['Patient Count'] / patient_count_initial) * 100

    fig = px.bar(
        retention,
        x=visit_col,
        y='Retention %',
        title='Patient Retention Over Substudy Visits'
    )
    return fig

# def plot_samples_by_visit(df: pandas.DataFrame, visit_order_df:pandas.DataFrame, visit_col: str, patient_col: str, title: str = None):
#     # Clean up the visit column — extra spaces are the enemy
#     df[visit_col] = df[visit_col].str.strip()

#     # Define your standard visit order
#     # base_order = ['PRE14', 'PRE10', 'PRE07', 'OR', 'V00', 'V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07', 'V08', 'V09', 'V10']
#     # # Identify what's actually in the data
#     # actual_visits = df[visit_col].unique().tolist()

#     # # Split visits into:
#     # # - standard ones (already in your order list)
#     # # - unexpected ones (we'll just sort alphabetically)
#     # standard_visits = [visit for visit in base_order if visit in actual_visits]
#     # extra_visits = [visit for visit in actual_visits if visit not in base_order and visit != eot_label]

#     # # Build final visit order: standard + unexpected (sorted) + EOT at the end if present
#     # final_order = standard_visits + sorted(extra_visits)
#     # if eot_label in actual_visits:
#     #     final_order.append(eot_label)

#     # # Check for debugging if needed
#     # print("Visit order being used in samples by visit:", final_order)

#     # # Force the visit column to obey this exact order
#     # df[visit_col] = pandas.Categorical(df[visit_col], categories=final_order, ordered=True)

#     #df = sort_patient_vists(df, "(HaflerLab) Substudy Visit", eot_label) #Old sorting method - will need to sort extra 

#     #new sort: use the order in the visit dataframe

#     # Now count and sort
#     sample_counts = df.groupby([visit_col, patient_col], as_index=False).size().rename(columns={'size': 'Sample Count'})

#     # Plot
#     fig = px.bar(
#         sample_counts,
#         x=visit_col,
#         y='Sample Count',
#         color=patient_col,
#         barmode='stack',
#         title=title or "Samples by Substudy Visit, Colored by Patient"
#     )

#     return fig
def plot_samples_by_visit(df: pandas.DataFrame, visit_order_df: pandas.DataFrame, visit_col: str, patient_col: str, title: str = None):
    # Clean up the visit column — extra spaces are the enemy
    df[visit_col] = df[visit_col].str.strip()

    # Merge to get the correct visit order
    df = df.merge(
        visit_order_df[[visit_col, "Order"]], 
        on=visit_col, 
        how="left"
    )

    # Group and count samples, ensuring correct aggregation
    sample_counts = df.groupby([visit_col, patient_col], as_index=False).size().rename(columns={'size': 'Sample Count'})

    # Sort by visit order
    sample_counts = sample_counts.sort_values(by="Order").drop(columns=["Order"])

    # Reset index
    sample_counts = sample_counts.reset_index(drop=True)

    # Plot
    fig = px.bar(
        sample_counts,
        x=visit_col,
        y='Sample Count',
        color=patient_col,
        barmode='stack',
        title=title or "Samples by Substudy Visit, Colored by Patient"
    )

    return fig


# def plot_aliquot_amount_over_visits(df, aliquot_type, visit_col, patient_col, amount_col):
#     df = df[df['YCCI_Sample Type'] == aliquot_type].copy()
#     df[visit_col] = df[visit_col].str.strip()

#     amount_by_visit = (
#         df.groupby([visit_col, patient_col])[amount_col]
#         .sum()
#         .reset_index()
#     )

#     fig = px.bar(
#         amount_by_visit,
#         x=visit_col,
#         y=amount_col,
#         color=patient_col,
#         barmode='stack',
#         title=f'{aliquot_type} Amount by Visit (Colored by Patient)'
#     )
#     return fig
def plot_aliquot_amount_over_visits(df, aliquot_type, visit_col, patient_col, amount_col):
    df = df[df['YCCI_Sample Type'] == aliquot_type].copy()
    df[visit_col] = df[visit_col].str.strip()

    # Aggregate in case you have multiple rows per patient per visit (like multiple tubes collected)
    amount_by_visit = (
        df.groupby([visit_col, patient_col])[amount_col]
        .sum()
        .reset_index()
    )

    fig = px.line(
        amount_by_visit,
        x=visit_col,
        y=amount_col,
        color=patient_col,
        markers=True,
        title=f'{aliquot_type} Amount by Visit (Line Plot by Patient)'
    )

    # Optional: Force the x-axis order to match your visit sorting logic (PRE14, PRE10, ..., EOT)
    visit_order = [
        'ARC', 'PRETRIAL','PRE14', 'PRE10', 'PRE07', 'OR', 
        'V00', 'V01', 'V02', 'V03', 'V04', 
        'V05', 'V06', 'V07', 'V08', 'V09', 'V10', 'EOT'
    ]
    fig.update_xaxes(categoryorder='array', categoryarray=visit_order)

    fig.update_layout(xaxis_title="Substudy Visit", yaxis_title=f"Amount ({aliquot_type})")

    return fig