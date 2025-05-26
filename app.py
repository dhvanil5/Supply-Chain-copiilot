import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import simpy
import random
import numpy as np

# --- Styling ---
st.set_page_config(page_title="Smart Supply Chain Simulator", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
        background-color: #121212;
        color: #f0f0f0;
    }
    h1, h2, h3, h4 {
        font-weight: bold;
        font-size: 18px;
    }
    .markdown-text-container {
        font-size: 14px;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)
sns.set_theme(style="darkgrid", palette="mako")
plt.style.use("dark_background")

# --- Simulation Class ---
class AdvancedDeliverySimulator:
    def __init__(self, env, orders_df, return_rate, delay_min, delay_max):
        self.env = env
        self.orders = orders_df
        self.log = []
        self.return_rate = return_rate / 100
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.cumulative_profit = 0
        self.total_stock_used = 0
        self.initial_stock = 10000
        self.current_stock = self.initial_stock
        self.stockouts = 0
        self.daily_stock_levels = {}

    def simulate_order(self, row):
        order_id = row['Order Id']
        base_delay = random.randint(self.delay_min, self.delay_max)
        quantity = row['Order Item Quantity']
        unit_price = row['Product Price']
        base_profit = row['Order Profit Per Order']

        delivery_type = random.choices(['Standard', 'Express', 'Same-Day'], weights=[0.6, 0.3, 0.1])[0]
        multiplier = {'Standard': 1.0, 'Express': 0.8, 'Same-Day': 0.5}
        adjusted_delay = int(base_delay * multiplier[delivery_type])

        yield self.env.timeout(adjusted_delay)

        is_returned = random.random() < self.return_rate
        delay_penalty = -5 * max(0, adjusted_delay - base_delay)
        final_status = "Delivered"
        final_profit = base_profit + delay_penalty

        if self.current_stock < quantity:
            self.stockouts += 1
            final_status = "Stockout"
            final_profit = 0
            quantity = 0
        else:
            self.current_stock -= quantity
            self.total_stock_used += quantity

        if is_returned and final_status == "Delivered":
            final_status = "Returned"
            final_profit = -abs(final_profit)

        self.cumulative_profit += final_profit

        self.daily_stock_levels[self.env.now] = self.current_stock

        self.log.append({
            "Sim Time": self.env.now,
            "Order Id": order_id,
            "Delivery Type": delivery_type,
            "Status": final_status,
            "Profit": final_profit,
            "Delay Days": adjusted_delay,
            "Cumulative Profit": self.cumulative_profit,
            "Holding Cost": quantity * adjusted_delay * 0.2,
            "Stock Used": quantity,
            "Remaining Stock": self.current_stock
        })

    def run(self):
        processes = [self.env.process(self.simulate_order(row)) for _, row in self.orders.iterrows()]
        for p in processes:
            yield p

# --- Streamlit UI ---
st.title("Smart Supply Chain CoPilot")

st.sidebar.header("Simulation Controls")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df['Days for shipping (real)'] = pd.to_numeric(df['Days for shipping (real)'], errors='coerce')
    df['Order Profit Per Order'] = pd.to_numeric(df['Order Profit Per Order'], errors='coerce')
    df['Order Item Quantity'] = pd.to_numeric(df['Order Item Quantity'], errors='coerce')
    df['Product Price'] = pd.to_numeric(df['Product Price'], errors='coerce')
    df = df.dropna(subset=['Days for shipping (real)', 'Order Profit Per Order', 'Order Id'])

    num_orders = st.sidebar.slider("Number of Orders", 100, min(100000, len(df)), 1000, step=100)
    return_rate = st.sidebar.slider("Return Rate (%)", 0, 50, 10)
    delay_min = st.sidebar.slider("Minimum Delay (Days)", 1, 5, 2)
    delay_max = st.sidebar.slider("Maximum Delay (Days)", 5, 15, 10)

    if st.sidebar.button("Run Simulation"):
        sample_orders = df.sample(num_orders).reset_index(drop=True)
        env = simpy.Environment()
        sim = AdvancedDeliverySimulator(env, sample_orders, return_rate, delay_min, delay_max)
        env.process(sim.run())
        env.run()
        result_df = pd.DataFrame(sim.log)

        # --- Metrics ---
        st.header("📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Profit ($)", f"{sim.cumulative_profit:,.2f}")
        with col2:
            delivered = result_df[result_df["Status"] == "Delivered"]
            st.metric("Successful Deliveries (%)", f"{len(delivered) / num_orders * 100:.2f}%")
        with col3:
            returned = result_df[result_df["Status"] == "Returned"]
            st.metric("Returns (%)", f"{len(returned) / num_orders * 100:.2f}%")
        with col4:
            st.metric("Stockouts", sim.stockouts)

        # --- Dataset Summary ---
        st.header("📂 Dataset Summary")
        st.markdown("<p style='font-size:14px;'>Essential characteristics of your order data:</p>", unsafe_allow_html=True)
        st.dataframe(df.describe()[['Order Profit Per Order', 'Order Item Quantity', 'Product Price']].round(2))

        # --- Safety Stock & ROP ---
        st.header("📦 Safety Stock & Reorder Analysis")
        daily_usage = result_df.groupby("Sim Time")["Stock Used"].sum()
        lead_time = (delay_min + delay_max) / 2
        avg_daily_usage = daily_usage.mean()
        std_dev_usage = daily_usage.std()
        safety_stock = std_dev_usage * np.sqrt(lead_time)
        reorder_point = (avg_daily_usage * lead_time) + safety_stock

        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("Avg Daily Usage", f"{avg_daily_usage:.2f} units")
        with col6:
            st.metric("Safety Stock", f"{safety_stock:.0f} units")
        with col7:
            st.metric("Reorder Point", f"{reorder_point:.0f} units")

        st.markdown("<p style='font-size:14px;'>Visualizing stock levels across the simulation vs calculated reorder point.</p>", unsafe_allow_html=True)
        fig_stock = plt.figure(figsize=(12, 5))
        stock_series = pd.Series(sim.daily_stock_levels).sort_index()
        stock_series.plot(label="Stock Level", color='cyan')
        plt.axhline(y=reorder_point, color='red', linestyle='--', label="Reorder Point")
        plt.axhline(y=safety_stock, color='orange', linestyle='--', label="Safety Stock")
        plt.xlabel("Simulation Time (Days)")
        plt.ylabel("Stock Level")
        plt.legend()
        st.pyplot(fig_stock)

        if stock_series.min() <= reorder_point:
            st.warning("⚠️ Stock level dipped below the reorder point. Replenishment needed!")

        # --- Visual Insights ---
        st.header("📈 Visual Insights")

        st.subheader("Cumulative Profit Over Time")
        fig1 = plt.figure(figsize=(12, 5))
        sns.lineplot(data=result_df, x="Sim Time", y="Cumulative Profit", color='#76D7C4', linewidth=2.5)
        st.pyplot(fig1)

        st.subheader("Sales Volume Over Time")
        fig2 = plt.figure(figsize=(12, 5))
        sns.histplot(data=result_df, x="Sim Time", bins=30, kde=True, color='#85C1E9')
        st.pyplot(fig2)

        st.subheader("Profit Distribution by Delivery Type")
        fig3 = plt.figure(figsize=(10, 5))
        sns.violinplot(x="Delivery Type", y="Profit", data=result_df, inner="quartile", palette="magma")
        st.pyplot(fig3)

        st.subheader("Inventory Holding Cost Distribution")
        fig4 = plt.figure(figsize=(10, 5))
        sns.histplot(result_df["Holding Cost"], kde=True, bins=30, color='#F1948A')
        st.pyplot(fig4)

        st.subheader("Delay vs Profit Heatmap")
        fig5 = plt.figure(figsize=(10, 6))
        sns.histplot(data=result_df, x="Delay Days", y="Profit", bins=30, cmap="viridis")
        st.pyplot(fig5)

        st.subheader("Delivery Status Breakdown")
        fig6 = plt.figure(figsize=(8, 4))
        sns.countplot(data=result_df, x="Status", palette="Set2")
        st.pyplot(fig6)

        st.subheader("Total Stock Used vs Initial Stock")
        fig7 = plt.figure(figsize=(8, 5))
        stock_data = pd.DataFrame({
            "Stock": ["Initial", "Used", "Remaining"],
            "Units": [sim.initial_stock, sim.total_stock_used, sim.current_stock]
        })
        sns.barplot(data=stock_data, x="Stock", y="Units", palette="crest")
        st.pyplot(fig7)

else:
    st.info("Upload a CSV file using the sidebar to start the simulation.")
