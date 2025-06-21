# Create a streamlit application in CORTEX_AI_DB and paste this code in the editor
# Import python packages from Package List.txt before proceeding.

import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import plotly.express as px
from PIL import Image
import io
    

session = get_active_session()

st.set_page_config(layout="wide")

st.markdown("""<style>
            button[data-testid="stBaseButton-secondary"] p {
                font-size: 20px;
                font-weight: 500;
            }
            button[data-testid="stBaseButton-secondary"] {
                background-color: #00008B; /* Green */
                color: white;
                padding: 8px 24px;
                border: none;
                border-radius: 24px;
                /*font-size: 50px;*/
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            button[data-testid="stBaseButton-secondary"]:hover {
                background-color: #80BFFF; /* Slightly darker green */
                transform: scale(1.05); /* Slight zoom effect */
            }
            /* Style when the button is clicked (active) */
            button[data-testid="stBaseButton-secondary"]:active {
                background-color: #0059B3; /* Darker green */
                transform: scale(0.98); /* Slight shrink effect */
                box-shadow: 0 5px #666; 
            }
 
</style>""", unsafe_allow_html=True)

co1, co2 = st.columns([0.27, 0.73])
with co2:
    st.title("AI - Powered Quality Control")

lss = st.selectbox("Part Types", [None, 'All', 'Good', 'Defective'])

if lss == 'All':

    dat = session.sql("SELECT * FROM PARTS_STATUS_CLASSIFICATION;").collect()
    df = pd.DataFrame(dat)
    st.dataframe(df, hide_index=True)
    
    # Loop over pairs of images
    for i in range(0, len(df), 2):
        c1, c2 = st.columns([0.5, 0.5])  # New row of two columns
    
        for idx, col in enumerate([c1, c2]):
            if i + idx < len(df):
                file_name = df['FILE_NAME'].iloc[i + idx]
    
                with col:
                    # Read image from Snowflake stage
                    image_bytes = session.file.get_stream(
                        f"@cortex_ai_db.public.PARTS_STAGE/{file_name}", decompress=False
                    ).read()
    
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.image(image_bytes, width=400)
                    st.markdown("</div>", unsafe_allow_html=True)
    
                    # Filter df and display details
                    df_filtered = df[df['FILE_NAME'] == file_name]
                    st.write(f" ##### Part Type : {df_filtered['PART_TYPE'].values[0]}")
                    st.write(f" ##### Part Status : {df_filtered['PART_STATUS'].values[0]}")
                    st.write(f" ##### Defect Summary : {df_filtered['DEFECT_SUMMARY'].values[0]}")
    
                    label = file_name.replace('.jpg', '').replace('.JPG', '')
    
                    if st.button(f" Escalate {label}", key=f"All_{i + idx}"):
                        part_type = df_filtered['PART_TYPE'].values[0]
                        extracted_dt = df_filtered['EXTRACTION_DTTM'].values[0]
                        part_status = df_filtered['PART_STATUS'].values[0]
                        defect_summary = df_filtered['DEFECT_SUMMARY'].values[0]
    
                        # Check if the file_name already exists
                        exists = session.sql(f"""
                            SELECT 1 FROM parts_for_escalation WHERE FILE_NAME = '{file_name}' LIMIT 1
                        """).collect()
    
                        if exists:
                            st.info("Part already escalated")
                        else:
                            # Insert the new row
                            session.sql(f"""
                                INSERT INTO parts_for_escalation (FILE_NAME, EXTRACTION_DTTM, PART_TYPE, PART_STATUS, DEFECT_SUMMARY)
                                VALUES ('{file_name}', '{extracted_dt}', '{part_type}', '{part_status}', '{defect_summary}')
                            """).collect()
                            st.success("Part submitted to escalation table")
    
        # Add vertical space between each row
        st.markdown("<br><hr><br>", unsafe_allow_html=True)


    summary = df['PART_STATUS'].value_counts().reset_index()
    summary.columns = ['PART_STATUS', 'COUNT']
    
    # Step 2: Plot pie chart
    fig = px.pie(summary, 
                 names='PART_STATUS', 
                 values='COUNT', 
                 title='Count of Parts by Type')
    
    # Step 3: Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


    type = st.selectbox('Part Status', [None, 'Good', 'Defective'])

    if type != None:
        summary1 = df[df['PART_STATUS'] == type]
        summary1 = summary1['PART_TYPE'].value_counts().reset_index()
        summary1.columns = ['PART_TYPE', 'COUNT']
        
        # Create Bar chart
        fig1 = px.bar(summary1,
            x='PART_TYPE',  
            y='COUNT',    
            color='PART_TYPE',
            title=f'Part Type and Status Breakdown for {type} parts',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        # Display in Streamlit
        st.plotly_chart(fig1, use_container_width=True)
                    
            

if lss == 'Good':
    
    dat1 = session.sql(f" SELECT * FROM PARTS_STATUS_CLASSIFICATION WHERE PART_STATUS = '{lss}';").collect()
    df1 = pd.DataFrame(dat1)
    st.dataframe(df1, hide_index=True)
    
    # Loop over pairs of images
    for i in range(0, len(df1), 2):
        c1, c2 = st.columns([0.5, 0.5])  # New row of two columns
    
        for idx, col in enumerate([c1, c2]):
            if i + idx < len(df1):
                file_name = df1['FILE_NAME'].iloc[i + idx]
    
                with col:
                    # Read image from Snowflake stage
                    image = session.file.get_stream(f"@cortex_ai_db.public.PARTS_STAGE/{file_name}", decompress=False).read()
                    
                    # Display image
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.image(image, width=300)
            
                    # Filter df and display part type
                    df_filtered = df1[df1['FILE_NAME'] == file_name]
                    st.write(f" ##### Part Type : {df_filtered['PART_TYPE'].values[0]}")
                    st.write(f" ##### Part Status : {df_filtered['PART_STATUS'].values[0]}")
                    st.write(f" ##### Defect Summary : {df_filtered['DEFECT_SUMMARY'].values[0]}")
        
                    st.markdown("</div>", unsafe_allow_html=True)
        
                    label = file_name.replace('.jpg', '').replace('.JPG', '')
                    if st.button(f"Escalate {label}"):
                        part_type = df_filtered['PART_TYPE'].values[0]
                        extracted_dt = df_filtered['EXTRACTION_DTTM'].values[0]
                        part_status = df_filtered['PART_STATUS'].values[0]
                        defect_summary = df_filtered['DEFECT_SUMMARY'].values[0]
                        file_name = i  # already defined in loop
            
                        # Check if the file_name already exists
                        exists = session.sql(f"""
                            SELECT 1 FROM parts_for_escalation WHERE FILE_NAME = '{file_name}' LIMIT 1
                        """).collect()
                    
                        if exists:
                            st.info("Part already escalated")
                        else:
                            # Insert the new row
                            session.sql(f"""
                                INSERT INTO parts_for_escalation (FILE_NAME, EXTRACTION_DTTM, PART_TYPE, PART_STATUS, DEFECT_SUMMARY)
                                VALUES ('{file_name}', '{extracted_dt}', '{part_type}', '{part_status}', '{defect_summary}')
                            """).collect()
                            st.success("Part submitted to escalation table")
        # Add vertical space between each row
        st.markdown("<br><hr><br>", unsafe_allow_html=True)

if lss == 'Defective':
    
    dat2 = session.sql(f" SELECT * FROM PARTS_STATUS_CLASSIFICATION WHERE PART_STATUS = '{lss}';").collect()
    df2 = pd.DataFrame(dat2)
    st.dataframe(df2, hide_index=True)
    
    # Loop over pairs of images
    for i in range(0, len(df2), 2):
        c1, c2 = st.columns([0.5, 0.5])  # New row of two columns
    
        for idx, col in enumerate([c1, c2]):
            if i + idx < len(df2):
                file_name = df2['FILE_NAME'].iloc[i + idx]
            
                with col:
                    # Read image from Snowflake stage
                    image = session.file.get_stream(f"@cortex_ai_db.public.PARTS_STAGE/{file_name}", decompress=False).read()
                    
                    # Display image
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.image(image, width=300)
            
                    # Filter df and display part type
                    df_filtered = df2[df2['FILE_NAME'] == file_name]
                    st.write(f" ##### Part Type : {df_filtered['PART_TYPE'].values[0]}")
                    st.write(f" ##### Part Status : {df_filtered['PART_STATUS'].values[0]}")
                    st.write(f" ##### Defect Summary : {df_filtered['DEFECT_SUMMARY'].values[0]}")
            
                    st.markdown("</div>", unsafe_allow_html=True)
        
                    label = file_name.replace('.jpg', '').replace('.JPG', '')
                    if st.button(f"Escalate {label}", key=f'Bad_{i + idx}'):
                        part_type = df_filtered['PART_TYPE'].values[0]
                        extracted_dt = df_filtered['EXTRACTION_DTTM'].values[0]
                        part_status = df_filtered['PART_STATUS'].values[0]
                        defect_summary = df_filtered['DEFECT_SUMMARY'].values[0]
                        file_name = i  # already defined in loop
            
                        # Check if the file_name already exists
                        exists = session.sql(f"""
                            SELECT 1 FROM parts_for_escalation WHERE FILE_NAME = '{file_name}' LIMIT 1
                        """).collect()
                    
                        if exists:
                            st.info("Part already escalated")
                        else:
                            # Insert the new row
                            session.sql(f"""
                                INSERT INTO parts_for_escalation (FILE_NAME, EXTRACTION_DTTM, PART_TYPE, PART_STATUS, DEFECT_SUMMARY)
                                VALUES ('{file_name}', '{extracted_dt}', '{part_type}', '{part_status}', '{defect_summary}')
                            """).collect()
                            st.success("Part submitted to escalation table")

        # Add vertical space between each row
        st.markdown("<br><hr><br>", unsafe_allow_html=True)