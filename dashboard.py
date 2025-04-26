import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Freshdesk Tickets Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load the data
@st.cache_data
def load_data():
    with open('freshdesk_tickets6.json', 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Convert timestamp strings to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['due_by'] = pd.to_datetime(df['due_by'])
    return df

# Main title
st.title("📊 Freshdesk Tickets Dashboard")

try:
    # Load the data
    df = load_data()
    
    # Top level metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", len(df))
    with col2:
        st.metric("Open Tickets", len(df[df['status'] == 2]))
    with col3:
        st.metric("Escalated Tickets", df['is_escalated'].sum())
    with col4:
        st.metric("Average Response Time (days)", 
                 round((df['updated_at'] - df['created_at']).mean().total_seconds() / (24*60*60), 2))

    # Create two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        # Ticket Status Distribution
        status_counts = df['status'].value_counts()
        status_map = {2: "Open", 3: "Pending", 4: "Resolved", 5: "Closed"}
        fig_status = px.pie(
            values=status_counts.values,
            names=[status_map.get(x, f"Status {x}") for x in status_counts.index],
            title="Ticket Status Distribution"
        )
        st.plotly_chart(fig_status)

        # Tickets by Priority
        priority_map = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}
        priority_counts = df['priority'].value_counts()
        fig_priority = px.bar(
            x=[priority_map.get(x, f"Priority {x}") for x in priority_counts.index],
            y=priority_counts.values,
            title="Tickets by Priority",
            labels={'x': 'Priority', 'y': 'Number of Tickets'}
        )
        st.plotly_chart(fig_priority)

    with col2:
        # Tickets by Source
        source_counts = df['source'].value_counts()
        source_map = {1: "Email", 2: "Portal", 3: "Phone", 7: "Chat", 9: "Feedback Widget"}
        fig_source = px.pie(
            values=source_counts.values,
            names=[source_map.get(x, f"Source {x}") for x in source_counts.index],
            title="Ticket Source Distribution"
        )
        st.plotly_chart(fig_source)

        # Tickets Created Over Time
        df_time = df.set_index('created_at').resample('D')['subject'].count().reset_index()
        fig_timeline = px.line(
            df_time,
            x='created_at',
            y='subject',
            title="Tickets Created Over Time",
            labels={'subject': 'Number of Tickets', 'created_at': 'Date'}
        )
        st.plotly_chart(fig_timeline)

    # Ticket Details
    st.header("📝 Ticket Details")
    st.dataframe(
        df[['subject', 'status', 'priority', 'created_at', 'is_escalated']]
        .sort_values('created_at', ascending=False)
        .head(10)
    )

except Exception as e:
    st.error(f"An error occurred while loading the dashboard: {str(e)}")
    st.info("Please make sure the 'freshdesk_tickets6.json' file is in the same directory as this script.")