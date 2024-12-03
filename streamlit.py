import pandas as pd
import streamlit as st
import plotly.express as px

# Streamlit app title
st.title("Healthcare Data Visualization Dashboard")

# Sidebar for file upload
uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    # Extract sheet names
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    year_filter = st.sidebar.multiselect("Select Years (Sheets)", options=sheet_names, default=sheet_names)

    if year_filter:
        # Load data for selected sheets
        all_data = []
        for sheet in year_filter:
            sheet_data = pd.read_excel(uploaded_file, sheet_name=sheet)
            sheet_data["Year"] = sheet  # Add Year column from sheet name
            all_data.append(sheet_data)
        filtered_data = pd.concat(all_data, ignore_index=True)

        # Sidebar: State selection
        if "state_abbreviation" in filtered_data.columns:
            state_filter = st.sidebar.selectbox(
                "Select a State",
                options=filtered_data["state_abbreviation"].unique()
            )
            filtered_data = filtered_data[filtered_data["state_abbreviation"] == state_filter]

        # Sidebar: County selection
        if "name" in filtered_data.columns:
            county_filter = st.sidebar.multiselect(
                "Select Counties",
                options=filtered_data["name"].unique(),
                default=filtered_data["name"].unique()
            )
            filtered_data = filtered_data[filtered_data["name"].isin(county_filter)]

        if "name" not in filtered_data.columns:
             st.error("The dataset does not contain a 'name' column for counties.")
             st.stop()

        # Sidebar: Metric selection
             available_metrics = [col for col in filtered_data.columns if col not in ["Year", "state_abbreviation", "name"]]
             metric_filter = st.sidebar.selectbox("Select a Metric", options=available_metrics)

        if not filtered_data.empty:
            # Define available metrics after ensuring filtered_data is valid
            available_metrics = [col for col in filtered_data.columns if col not in ["Year", "state_abbreviation", "name"]]
            if available_metrics:
                metric_filter = st.sidebar.selectbox("Select a Metric", options=available_metrics)
            else:
                st.warning("No valid metrics are available in the dataset.")
                st.stop()

            if metric_filter:
                #Proceed with visualization
                st.write(f"Selected Metric: {metric_filter}")
            else:
                st.warning("Please select a valid metric.")
        else:
            st.warning9("No data available for the selected filters.")     

        if metric_filter:
            # Bar Chart: Aggregate values by county
            st.subheader(f"Bar Chart of {metric_filter} by County")
            bar_chart_data = filtered_data.groupby("name")[metric_filter].sum().reset_index()
            fig_bar = px.bar(
                bar_chart_data,
                x="name",
                y=metric_filter,
                title=f"{metric_filter} by County",
                labels={"name": "County", metric_filter: "Value"}
            )
            st.plotly_chart(fig_bar)

            # Line Chart: Trend over time
            st.subheader(f"Trend Graph of {metric_filter} Over Time")
            #trend_data = filtered_data.groupby(["Year", "name"])[metric_filter].sum().reset_index()
            fig_trend = px.line(
                filtered_data,
                x="Year",
                y=metric_filter,
                color="name",
                title=f"Trend of {metric_filter} Over Time",
                markers=True,
                animation_frame="Year"
            )
            st.plotly_chart(fig_trend)

            # Heatmap: Metric values across counties and years
            st.subheader(f"Heatmap of {metric_filter} by Year and County")
            heatmap_data = filtered_data.pivot_table(index="Year", columns="name", values=metric_filter)
            fig_heatmap = px.imshow(
                heatmap_data,
                color_continuous_scale="Viridis",
                title=f"Heatmap of {metric_filter} by Year and County",
                labels={"x": "County", "y": "Year", "color": metric_filter}
            )
            st.plotly_chart(fig_heatmap)
        else:
            st.warning("No data available for the selected filters. Please adjust your selections.")
    else:
        st.warning("Please select at least one year (sheet).") 
else:
    st.warning("Please upload an Excel file.")
