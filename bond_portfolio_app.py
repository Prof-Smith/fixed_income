
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Expanded bond dataset with fictitious company names
bond_data = pd.DataFrame({
    "Company": [
        "Alpha Corp", "Beta Industries", "Gamma Ltd", "Delta Holdings", "Epsilon Inc",
        "Zeta Group", "Eta Enterprises", "Theta Co", "Iota Partners", "Kappa Systems"
    ],
    "Bond ID": [f"B{i+1}" for i in range(10)],
    "Coupon Rate (%)": [5.0, 3.5, 6.0, 4.0, 7.0, 5.5, 4.5, 6.5, 3.0, 5.2],
    "Maturity (Years)": [5, 10, 3, 7, 8, 6, 4, 9, 2, 5],
    "Price ($)": [980, 1020, 950, 1000, 970, 990, 985, 1010, 960, 995],
    "Face Value ($)": [1000]*10,
    "Rating": ["AAA", "BBB", "AA", "A", "BB", "BBB", "AA", "A", "AAA", "BBB"]
})

st.title("Bond Portfolio Simulation")

st.subheader("Available Bonds")
st.dataframe(bond_data)

st.markdown("""
### Investment Challenge
Select at least **five bonds** to construct a portfolio that aims to achieve a **target duration between 4 and 6 years**.
""")

selected_bonds = st.multiselect("Choose bonds to include in your portfolio:", bond_data["Bond ID"])
portfolio = bond_data[bond_data["Bond ID"].isin(selected_bonds)]

if len(selected_bonds) < 5:
    st.warning("Please select at least five bonds to proceed with the simulation.")

if len(selected_bonds) >= 5:
    st.subheader("Selected Portfolio")
    st.dataframe(portfolio)

    def calculate_ytm(price, face_value, coupon_rate, maturity):
        annual_coupon = coupon_rate * face_value / 100
        return (annual_coupon + (face_value - price) / maturity) / ((face_value + price) / 2) * 100

    portfolio["YTM (%)"] = portfolio.apply(lambda row: calculate_ytm(row["Price ($)"], row["Face Value ($)"], row["Coupon Rate (%)"], row["Maturity (Years)"]), axis=1)

    st.markdown("""
    ### Understanding Yield to Maturity (YTM)
    Yield to Maturity is the total return anticipated on a bond if held until it matures. It accounts for all coupon payments and the difference between the purchase price and face value.
    """)

    def calculate_duration(price, face_value, coupon_rate, maturity):
        c = coupon_rate * face_value / 100
        y = calculate_ytm(price, face_value, coupon_rate, maturity) / 100
        duration = sum([(t * c / (1 + y)**t) for t in range(1, maturity + 1)]) + (maturity * face_value / (1 + y)**maturity)
        return duration / price

    portfolio["Duration"] = portfolio.apply(lambda row: calculate_duration(row["Price ($)"], row["Face Value ($)"], row["Coupon Rate (%)"], row["Maturity (Years)"]), axis=1)

    portfolio["Market Value"] = portfolio["Price ($)"]
    total_value = portfolio["Market Value"].sum()
    portfolio["Weight"] = portfolio["Market Value"] / total_value
    portfolio_duration = (portfolio["Weight"] * portfolio["Duration"]).sum()

    st.subheader("Portfolio Metrics")
    st.dataframe(portfolio[["Company", "Bond ID", "YTM (%)", "Duration"]])
    st.markdown(f"**Portfolio Duration (Weighted Average):** {portfolio_duration:.2f} years")

    st.markdown("""
    ### Understanding Duration
    Duration measures a bond's sensitivity to interest rate changes. It represents the weighted average time to receive the bond's cash flows. Longer duration means higher sensitivity.
    """)

    fig_duration = px.bar(portfolio, x="Bond ID", y="Duration", color="Company", title="Duration of Selected Bonds")
    st.plotly_chart(fig_duration)

    rate_change = st.slider("Simulate interest rate change (%):", -2.0, 2.0, 0.0, 0.1)
    st.write(f"Interest rate change: {rate_change}%")

    def calculate_convexity(price, face_value, coupon_rate, maturity):
        c = coupon_rate * face_value / 100
        y = calculate_ytm(price, face_value, coupon_rate, maturity) / 100
        convexity = sum([(t * (t + 1) * c / (1 + y)**(t + 2)) for t in range(1, maturity + 1)]) + (maturity * (maturity + 1) * face_value / (1 + y)**(maturity + 2))
        return convexity / price / 100

    portfolio["Convexity"] = portfolio.apply(lambda row: calculate_convexity(row["Price ($)"], row["Face Value ($)"], row["Coupon Rate (%)"], row["Maturity (Years)"]), axis=1)

    st.markdown("""
    ### Understanding Convexity
    Convexity is a measure of how the duration of a bond changes as interest rates change. It reflects the curvature in the price-yield relationship of a bond. 
    Bonds with higher convexity are less affected by interest rate changes and provide more accurate estimates of price changes for large shifts in rates.
    """)

    fig_convexity = px.bar(portfolio, x="Bond ID", y="Convexity", color="Company", title="Convexity of Selected Bonds")
    st.plotly_chart(fig_convexity)

    portfolio["Price Change (%)"] = -portfolio["Duration"] * rate_change + 0.5 * portfolio["Convexity"] * (rate_change**2)
    portfolio["New Price ($)"] = portfolio["Price ($)"] * (1 + portfolio["Price Change (%)"] / 100)

    st.subheader("Simulated Portfolio Performance")
    st.dataframe(portfolio[["Bond ID", "Price ($)", "New Price ($)", "Price Change (%)"]])
else:
    st.info("Select at least five bonds to view portfolio metrics and simulations.")
