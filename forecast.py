# prophet_forecast.py
import pandas as pd
import streamlit as st
from prophet import Prophet
import holidays
import matplotlib.pyplot as plt

st.set_page_config(page_title="Demand Forecasting", layout="wide")
st.title("📈 Demand Forecasting with Prophet")

uploaded_file = st.file_uploader("Upload CSV with 'Order Date' and 'Order Item Quantity'", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")

    try:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df = df[['Order Date', 'Order Item Quantity']].dropna()
        df = df.rename(columns={"Order Date": "ds", "Order Item Quantity": "y"})
        df = df.groupby('ds').sum().reset_index()

        # Add holiday flag using India holidays (customize as needed)
        ind_holidays = holidays.India()
        df['holiday'] = df['ds'].apply(lambda x: 1 if x in ind_holidays else 0)

        # Prophet model with holidays as regressor
        m = Prophet()
        m.add_regressor('holiday')
        m.fit(df)

        future = m.make_future_dataframe(periods=30)
        future['holiday'] = future['ds'].apply(lambda x: 1 if x in ind_holidays else 0)

        forecast = m.predict(future)

        # Plot forecast
        st.subheader("Forecast Plot")
        fig1 = m.plot(forecast)
        st.pyplot(fig1)

        st.subheader("Forecast Components")
        fig2 = m.plot_components(forecast)
        st.pyplot(fig2)

        st.subheader("Forecasted Data")
        st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30).round(2))

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("Please upload a CSV file to begin forecasting.")
