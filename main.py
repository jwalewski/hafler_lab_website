import streamlit
import pandas
import FreezerWorksScripts #Loads in custom functions from previous code
import plotly.express as px
from streamlit_sortables import sort_items
#Page Config Designs

streamlit.set_page_config(
    page_title="Hafler Lab Sample Tracker",  # Custom tab name
    page_icon="🧪",  # Custom emoji as favicon (or use a path to an image file) #"/path/to/file.png"
)


# App title
streamlit.title("Hafler Lab Sample Tracker")

# Sidebar Controls
with streamlit.sidebar:
    streamlit.header("Data Management")
    uploaded_df_file = streamlit.file_uploader("Upload Dana Farber Manifest (.csv ONLY)")
    uploaded_sf_file = streamlit.file_uploader("Upload UCSF Manifest (.csv ONLY)")
    uploaded_fw_file = streamlit.file_uploader("Upload Freezerworks Export (.csv in HaflerLab Export Format)")


#################### DATA UPLOADING #################

# Load data
if uploaded_df_file or uploaded_fw_file or uploaded_fw_file:
    #current_dataframe = pd.read_csv(uploaded_file)
    #all of the logic for handling the imports goes here

    #Temporary hardcoding of parameters
    if uploaded_df_file:
        import_style="DF" #DF is first to be implemented                         #Implemented options are "DF", "SF", "Freezer_Works_Import", and "Freezer_Works_Export"
        uploaded_file=uploaded_df_file
        row_offset=1 #Determines which row will be the column names of the pandas dataframe. Should be 1 for DF, 0 for FW Export
    elif uploaded_sf_file:
        import_style="SF"
        uploaded_file=uploaded_sf_file
        row_offset=0                                        #IMPORTANT: 1 or 0???
    elif uploaded_fw_file:
        import_style="Freezer_Works_Export"
        uploaded_file=uploaded_fw_file 
        row_offset=0 
    export_style="Patient_Report" #Implemented options are "Freezer_Works_Import", "Sample_Map", "Patient_Report"
    output_filepath="../data/exports/"
    output_filename=f"TEST_{export_style}.csv" #Can be left blank as well
    
    #

    current_dataframe = FreezerWorksScripts.read_file(uploaded_file, import_style, row_offset) #Building upon the FreezerWorksScripts repo I already have. The "" at the start is for the filepath - streamlit just loads the file into memory, so there's no actual path now
    #I'll get the documentation to appear nomally soon, but in the meantime:
    #def read_file(input_dataframe_filepath: str, input_data_filename:str, import_style:str, row_offset:Union[int, None]=None) -> pandas.DataFrame:
    #
    # Store processed data in session state
    streamlit.session_state.processed_df = current_dataframe
    patient_report_dataframe = FreezerWorksScripts.export_dataframe(streamlit.session_state.processed_df, style="Patient_Report") #Returns the dataframe in patient report format        
    streamlit.session_state.data_processed = True

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
        #Add in Patient Report Version below here
    else:
        streamlit.dataframe(current_dataframe)
        #Add in Patient Report Version below here
        streamlit.dataframe(patient_report_dataframe)

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
   
    #True summary stats
    streamlit.write(f"Total Patients: {current_dataframe['(Neuro) Patient ID'].nunique()}")
    #streamlit.bar_chart(current_dataframe['YCCI_Sample Type'].value_counts()) #To implement: For input CSVs that contain more than one patient site, I can scrape the site from (Neuro) patient ID and make a pie chart and/or stacked bar plots of varying days with colors representing the sites
    streamlit.write(f"Total Samples: {len(current_dataframe)}")
    streamlit.bar_chart(current_dataframe['YCCI_Sample Type'].value_counts())
    streamlit.write(f"Total Aliquots: {len(current_dataframe)}")
    streamlit.bar_chart(current_dataframe['Aliquot Type'].value_counts())


    # Extract unique visits from the main dataframe
    current_dataframe_visits = current_dataframe["(HaflerLab) Substudy Visit"].unique()
    current_dataframe_visits = pandas.DataFrame(current_dataframe_visits, columns=["(HaflerLab) Substudy Visit"])

    # Sort visits initially using FreezerWorksScripts
    current_dataframe_visits = FreezerWorksScripts.sort_patient_visits(current_dataframe_visits, "(HaflerLab) Substudy Visit", "EOT")

    streamlit.write("OPTIONAL: Drag and drop the visits in case the plotted order below is incorrect. ")
    # Display sortable drag-and-drop UI
    sorted_visits = sort_items(list(current_dataframe_visits["(HaflerLab) Substudy Visit"]), direction="vertical")

    # Save the new order into a dataframe
    visit_order_df = pandas.DataFrame({"(HaflerLab) Substudy Visit": sorted_visits, "Order": range(len(sorted_visits))})

    # Debugging: Show the user-defined order
    # streamlit.write("### User-Defined Visit Order:")
    # streamlit.dataframe(visit_order_df)

    # Aggregate sample counts per visit per patient
    grouped_df = current_dataframe.groupby(["(HaflerLab) Substudy Visit", "(Neuro) Patient ID"]).size().reset_index(name="Sample Count")

    # Merge with the visit order to enforce sorting
    grouped_df = grouped_df.merge(visit_order_df, on="(HaflerLab) Substudy Visit", how="left").sort_values("Order")

    ##Second test with CHATGPT
    # **FIX: Explicitly sort by "Order" before plotting**
    grouped_df = grouped_df.sort_values("Order")

    # Ensure x-axis categories match the user-defined order
    grouped_df["(HaflerLab) Substudy Visit"] = pandas.Categorical(
        grouped_df["(HaflerLab) Substudy Visit"],
        categories=sorted_visits,
        ordered=True
    )

    # # Debugging: Check aggregated DataFrame after sorting
    # streamlit.write("### Aggregated Sample Counts (Sorted):")
    # streamlit.dataframe(grouped_df)

    # Plot using the user-defined order
    fig = px.bar(
        grouped_df,
        x="Order",#"""(HaflerLab) Substudy Visit",  # Now this column is properly ordered
        y="Sample Count",
        color="(Neuro) Patient ID",
        barmode="stack",
        title="Samples by Substudy Visit, Colored by Patient",
        #text="(HaflerLab) Substudy Visit"  # Preserve original visit names as labels
        )

    # Update x-axis to display visit names instead of numeric order
    fig.update_xaxes(
        tickmode="array",
        tickvals=grouped_df["Order"], 
        ticktext=grouped_df["(HaflerLab) Substudy Visit"], 
    )
    streamlit.plotly_chart(fig)


    #Plot of sample type by Substudy Visit

    # Aggregate sample counts per visit per patient
    grouped_df = current_dataframe.groupby(["(HaflerLab) Substudy Visit", "YCCI_Sample Type"]).size().reset_index(name="Sample Count")

    # Merge with the visit order to enforce sorting
    grouped_df = grouped_df.merge(visit_order_df, on="(HaflerLab) Substudy Visit", how="left").sort_values("Order")

    ##Second test with CHATGPT
    # **FIX: Explicitly sort by "Order" before plotting**
    grouped_df = grouped_df.sort_values("Order")

    # Ensure x-axis categories match the user-defined order
    grouped_df["(HaflerLab) Substudy Visit"] = pandas.Categorical(
        grouped_df["(HaflerLab) Substudy Visit"],
        categories=sorted_visits,
        ordered=True
    )

    
    streamlit.write("Plot of Sample Type by (HaflerLab) Substudy Visit")
    fig = px.bar(
        grouped_df,
        x="Order",#"""(HaflerLab) Substudy Visit",  # Now this column is properly ordered
        y="Sample Count",
        color="YCCI_Sample Type",
        barmode="stack",
        title="Samples by Substudy Visit, Colored by YCCI_Sample Type",
        #text="(HaflerLab) Substudy Visit"  # Preserve original visit names as labels
        )

    # Update x-axis to display visit names instead of numeric order
    fig.update_xaxes(
        tickmode="array",
        tickvals=grouped_df["Order"], #When this is enabled ticks disappear entirely
        ticktext=grouped_df["(HaflerLab) Substudy Visit"],  #Only allows order ticks EVEN THOUGH I SPECIFY OTHERWISE
    )
    streamlit.plotly_chart(fig)

    #Plot of Aliquot type by Substudy Visit

    # Aggregate sample counts per visit per patient
    grouped_df = current_dataframe.groupby(["(HaflerLab) Substudy Visit", "Aliquot Type"]).size().reset_index(name="Sample Count")

    # Merge with the visit order to enforce sorting
    grouped_df = grouped_df.merge(visit_order_df, on="(HaflerLab) Substudy Visit", how="left").sort_values("Order")

    ##Second test with CHATGPT
    # **FIX: Explicitly sort by "Order" before plotting**
    grouped_df = grouped_df.sort_values("Order")

    # Ensure x-axis categories match the user-defined order
    grouped_df["(HaflerLab) Substudy Visit"] = pandas.Categorical(
        grouped_df["(HaflerLab) Substudy Visit"],
        categories=sorted_visits,
        ordered=True
    )

    
    streamlit.write("Plot of Sample Type by (HaflerLab) Substudy Visit")
    fig = px.bar(
        grouped_df,
        x="Order",#"""(HaflerLab) Substudy Visit",  # Now this column is properly ordered
        y="Sample Count",
        color="Aliquot Type",
        barmode="stack",
        title="Samples by Substudy Visit, Colored by Aliquot Type",
        #text="(HaflerLab) Substudy Visit"  # Preserve original visit names as labels
        )

    # Update x-axis to display visit names instead of numeric order
    fig.update_xaxes(
        tickmode="array",
        tickvals=grouped_df["Order"], 
        ticktext=grouped_df["(HaflerLab) Substudy Visit"], 
    )
    streamlit.plotly_chart(fig)





    ##Code below here isn't updated for summary stats page  

    #Plot of Percent of Patients retained
    # Group by visit & patient ID, then count unique patients per visit
    grouped_df = current_dataframe.groupby(["(HaflerLab) Substudy Visit"])["(Neuro) Patient ID"].nunique().reset_index(name="Patient Count")

    # Merge with visit order to enforce sorting
    grouped_df = grouped_df.merge(visit_order_df, on="(HaflerLab) Substudy Visit", how="left").sort_values("Order")

    # Get initial patient count (baseline for retention)
    initial_patient_count = grouped_df["Patient Count"].iloc[0]  # First visit's patient count

    # Calculate retention percentage
    grouped_df["Retention (%)"] = (grouped_df["Patient Count"] / initial_patient_count) * 100

    # Ensure x-axis categories match the user-defined order
    grouped_df["(HaflerLab) Substudy Visit"] = pandas.Categorical(
        grouped_df["(HaflerLab) Substudy Visit"],
        categories=sorted_visits,
        ordered=True
    )

    # Plot patient retention over time
    fig = px.line(
        grouped_df,
        x="Order",  # Enforce sorting
        y="Retention (%)",
        markers=True,  # Show data points
        title="Patient Retention by Substudy Visit",
    )

    # Update x-axis to display visit names instead of numeric order
    fig.update_xaxes(
        tickmode="array",
        tickvals=grouped_df["Order"], 
        ticktext=grouped_df["(HaflerLab) Substudy Visit"], 
    )

    streamlit.plotly_chart(fig)

    

    # with streamlit.form("Visualize Current Amounts For a Given Aliquot Type"):
    #     selected_aliquot_type = streamlit.text_input("Type the Aliquot Type you wish to use. Currently, this is only relevant for 'PBMC'")
    #     submit_button = streamlit.form_submit_button("Submit Aliquot Type")
    # #Plot of Current Amount For an Aliquot
    # streamlit.plotly_chart(FreezerWorksScripts.plot_aliquot_amount_over_visits(current_dataframe, selected_aliquot_type, "(HaflerLab) Substudy Visit","(Neuro) Patient ID","Current Amount")) #visit_col, patient_col, amount_col
    # #                                           NOTE: This doesn't work right now, but I think it's due to the fact that the dataframe might not have a "Current Amount". Will require debugging.



# User selects an aliquot type
with streamlit.form("Visualize Current Amounts For a Given Aliquot Type"):
    selected_aliquot_type = streamlit.text_input(f"Type the Aliquot Type you wish to use. Currently, this is only relevant for {str(current_dataframe['Aliquot Type'].unique())}")
    submit_button = streamlit.form_submit_button("Submit Aliquot Type")

# Filter dataframe based on user input
if selected_aliquot_type:
    filtered_df = current_dataframe[current_dataframe["Aliquot Type"] == selected_aliquot_type]
else:
    streamlit.warning("Please enter a valid aliquot type.")
    streamlit.stop()  # Prevents further execution if no valid input

# Group by patient and visit, summing "Current Amount"
grouped_df = filtered_df.groupby(["(HaflerLab) Substudy Visit", "(Neuro) Patient ID"])["Current Amount"].sum().reset_index()

# Merge with visit order to enforce sorting
grouped_df = grouped_df.merge(visit_order_df, on="(HaflerLab) Substudy Visit", how="left").sort_values("Order")

# Ensure x-axis categories match the user-defined order
grouped_df["(HaflerLab) Substudy Visit"] = pandas.Categorical(
    grouped_df["(HaflerLab) Substudy Visit"],
    categories=sorted_visits,
    ordered=True
)

# Plot stacked bar chart of remaining aliquots
fig = px.bar(
    grouped_df,
    x="Order",
    y="Current Amount",
    color="(Neuro) Patient ID",
    barmode="stack",
    title=f"Remaining {selected_aliquot_type} Aliquots by Substudy Visit and Patient"
)

# Update x-axis to display visit names instead of numeric order
fig.update_xaxes(
    tickmode="array",
    tickvals=grouped_df["Order"], 
    ticktext=grouped_df["(HaflerLab) Substudy Visit"], 
)

streamlit.plotly_chart(fig)












##################### EXPORTS #########################


# Optional: Save updated data back to file (could be hooked to sidebar button)
# current_dataframe.to_csv("updated_samples.csv", index=False)

# Second Sidebar Block: Download Section
with streamlit.sidebar:
    if streamlit.session_state.data_processed:

        streamlit.download_button(
            label="Download Processed CSV (For Freezerworks Import)",
            data=FreezerWorksScripts.convert_df_to_csv(streamlit.session_state.processed_df, False),
            file_name="processed_data.csv",
            mime="text/csv",
        )

        streamlit.download_button(
            label="Download Patient Report",
            data=FreezerWorksScripts.convert_df_to_csv(patient_report_dataframe, True),
            file_name="processed_data.csv",
            mime="text/csv",
        )