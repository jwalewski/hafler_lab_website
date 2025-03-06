import streamlit
import pandas
import FreezerWorksScripts #Loads in custom functions from previous code
import plotly.express as px

# App title
streamlit.title("Hafler Lab Patient Sample Tracker")

# Sidebar Controls
with streamlit.sidebar:
    streamlit.header("Data Management")
    uploaded_file = streamlit.file_uploader("Upload Sample Data (CSV)")
    if streamlit.button("Download Processed Data"):
        streamlit.success("Feature not implemented yet (but will trigger export logic)")






#################### DATA UPLOADING #################

# Load data
if uploaded_file:
    #current_dataframe = pd.read_csv(uploaded_file)
    #all of the logic for handling the imports goes here

    #Temporary hardcoding of parameters
    import_style="DF" #DF is first to be implemented                         #Implemented options are "DF", "SF", "Freezer_Works_Import", and "Freezer_Works_Export"
    export_style="Patient_Report" #Implemented options are "Freezer_Works_Import", "Sample_Map", "Patient_Report"
    output_filepath="../data/exports/"
    output_filename=f"TEST_{export_style}.csv" #Can be left blank as well
    row_offset=1 #should only be 1 right now #Determines which row will be the column names of the pandas dataframe. Should be 1 for DF, 0 for FW Export
    #

    current_dataframe = FreezerWorksScripts.read_file("",uploaded_file, import_style, row_offset) #Building upon the FreezerWorksScripts repo I already have. The "" at the start is for the filepath - streamlit just loads the file into memory, so there's no actual path now
    #I'll get the documentation to appear nomally soon, but in the meantime:
    #def read_file(input_dataframe_filepath: str, input_data_filename:str, import_style:str, row_offset:Union[int, None]=None) -> pandas.DataFrame:
    #

else:
    streamlit.warning("Upload a CSV to get started via the left side bar.")
    streamlit.stop()



####################### TABS ####################


# Tabs for different actions
#               In here, this will be new, interactive development should people be interested in adding samples/correcting anything in the meantime
#               Remember, at this stage curent_dataframe should always be in a FW style format so that I don't have to rewrite everything depending on any "style" of dataframe
search_view_tab, add_edit_sample_tab, summary_stats_tab = streamlit.tabs(["🔍 Search & View", "➕ Add/Edit Sample", "📊 Summary Stats"])

with search_view_tab:
    #(df, patient_id, visit_col, aliquot_col, amount_col):
    patient_id_column_name= "(Neuro) Patient ID"
    visit_column_name= "(HaflerLab) Substudy Visit"
    aliquot_type_column_name= "Aliquot Type"
    current_amount_column_name= "Current Amount"
    streamlit.subheader("Search Samples")
    search_term = streamlit.text_input("Search by (Neuro) Patient ID, Sample ID, etc.")
    if search_term:
        results = current_dataframe[current_dataframe.apply(lambda row: search_term.lower() in row.to_string().lower(), axis=1)]
        streamlit.dataframe(results)
        plot1,plot2 = FreezerWorksScripts.plot_patient_samples_and_amounts(results,patient_id_column_name,visit_column_name,aliquot_type_column_name,current_amount_column_name)
        streamlit.plotly_chart(plot1)
        streamlit.plotly_chart(plot2)
    else:
        streamlit.dataframe(current_dataframe)

with add_edit_sample_tab:
    # streamlit.subheader("Add or Edit Sample")
    # with streamlit.form("sample_form"):
    #     selected_patient_id = streamlit.text_input("Patient ID")
    #     selected_visit = streamlit.text_input("Substudy Visit")
    #     selected_collection_date = streamlit.date_input("Collection Date")
    #     selected_sample_type = streamlit.selectbox("Sample Type", ["Blood", "Tumor", "Other"])
    #     selected_volume = streamlit.selectbox("Volume")
    #     submit_button = streamlit.form_submit_button("Add/Update Sample")
    #     if streamlit.button("Generate Aliquot ID"):
    #         new_id = FreezerWorksScripts.generate_ascii_aliquot_id(
    #         patient_id=selected_patient_id,
    #         visit=selected_visit,
    #         sample_type=selected_sample_type,
    #         volume=selected_volume,
    #     aliquot_index=0  # or some logic to find the next available index for this sample
    # )
    #     streamlit.write(f"Generated Aliquot ID: {new_id}")

    #     if submit_button:
    #         new_sample = {"Patient ID": selected_patient_id, "Sample ID": selected_visit, "Collection Date": selected_collection_date, "Sample Type": selected_sample_type}
    #         current_dataframe = pandas.concat([current_dataframe, pandas.DataFrame([new_sample])], ignore_index=True)
    #         streamlit.success("Sample added/updated!")
# Form for actual sample submission
    with streamlit.form("sample_form"):
        selected_patient_id = streamlit.text_input("Patient ID")
        selected_visit = streamlit.text_input("Substudy Visit")
        selected_collection_date = streamlit.date_input("Collection Date")
        selected_sample_type = streamlit.selectbox("Sample Type", ["Blood", "Tumor", "Other"])
        selected_volume = streamlit.text_input("Volume. To be marked as ##mL")

        submit_button = streamlit.form_submit_button("Add/Update Sample")

    if streamlit.button("Generate Aliquot ID (Optional)"):
        new_id = FreezerWorksScripts.generate_ascii_aliquot_id(
            patient_id=selected_patient_id,
            visit=selected_visit,
            sample_type=selected_sample_type,
            volume=selected_volume,
            aliquot_index=0
        )
        streamlit.write(f"Generated Aliquot ID: {new_id}")

    if submit_button:
        new_sample = {
            "Patient ID": selected_patient_id,
            "Sample ID": selected_visit,
            "Collection Date": selected_collection_date,
            "Sample Type": selected_sample_type,
        }
        current_dataframe = pandas.concat([current_dataframe, pandas.DataFrame([new_sample])], ignore_index=True)
        streamlit.success("Sample added/updated!")

with summary_stats_tab:
    streamlit.subheader("Summary Statistics")
    streamlit.write(f"Total Patients: {current_dataframe['(Neuro) Patient ID'].nunique()}")
    #streamlit.bar_chart(current_dataframe['YCCI_Sample Type'].value_counts()) #To implement: For input CSVs that contain more than one patient site, I can scrape the site from (Neuro) patient ID and make a pie chart and/or stacked bar plots of varying days with colors representing the sites
    streamlit.write(f"Total Samples: {len(current_dataframe)}")
    streamlit.bar_chart(current_dataframe['YCCI_Sample Type'].value_counts())
    streamlit.write(f"Total Aliquots: {len(current_dataframe)}")
    streamlit.bar_chart(current_dataframe['Aliquot Type'].value_counts())


    #Cool idea for future: Have this instead be where buttons appear depending on the columns
    #   Example: have it so user plot "sample type" by "collection date" (both selectable)

    #Create arr of strings from columns
    #For each: make button
    #have two sets, one for independent and one for dependent
    #add an optinal third set for color
    #lastly, add a button so user can choose bar or line chart



    #Plot of Patients by Substudy Visit
    streamlit.plotly_chart(FreezerWorksScripts.plot_samples_by_visit(current_dataframe, "(HaflerLab) Substudy Visit", "(Neuro) Patient ID"))

    #Plot of Percent of Patients retained
    streamlit.plotly_chart(FreezerWorksScripts.plot_patient_retention(current_dataframe, "(Neuro) Patient ID", "(HaflerLab) Substudy Visit"))

    with streamlit.form("Visualize Current Amounts For a Given Aliquot Type"):
        selected_aliquot_type = streamlit.text_input("Type the Aliquot Type you wish to use. Currently, this is only relevant for 'PBMC'")
        submit_button = streamlit.form_submit_button("Submit Aliquot Type")
    #Plot of Current Amount For an Aliquot
    streamlit.plotly_chart(FreezerWorksScripts.plot_aliquot_amount_over_visits(current_dataframe, selected_aliquot_type, "(HaflerLab) Substudy Visit","(Neuro) Patient ID","Current Amount")) #visit_col, patient_col, amount_col
    #                                           NOTE: This doesn't work right now, but I think it's due to the fact that the dataframe might not have a "Current Amount". Will require debugging.


##################### EXPORTS #########################


# Optional: Save updated data back to file (could be hooked to sidebar button)
# current_dataframe.to_csv("updated_samples.csv", index=False)

FreezerWorksScripts.export_dataframe(current_dataframe)