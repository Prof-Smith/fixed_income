
import streamlit as st
import pandas as pd
import numpy as np

# Sample bond data
bond_data = pd.DataFrame({
    "Bond ID": ["B1", "B2", "B3", "B4"],
    "Coupon Rate (%)": [5.0, 3.5, 6.0, 4.0],
    "Maturity (Years)": [5, 10, 3, 7],
    "Price ($)": [980, 1020, 950, 1000],
    "Face Value ($)": [1000, 1000, 1000, 1000],
    "Rating": ["AAA", "BBB", "AA", "A"]
})

# Streamlit UI
st.title("Bond Portfolio Simulation")
st.write("Select bonds to add to your portfolio and simulate market scenarios.")

selected_bonds = st.multiselect("Choose bonds to include in your portfolio:", bond_data["Bond ID"])
portfolio = bond_data[bond_data["Bond ID"].isin(selected_bonds)]

if not portfolio.empty:
    st.subheader("Selected Portfolio")
    st.dataframe(portfolio)

    # Calculate YTM (simplified approximation)
    def calculate_ytm(price, face_value, coupon_rate, maturity):
        annual_coupon = coupon_rate * face_value / 100
        return (annual_coupon + (face_value - price) / maturity) / ((face_value + price) / 2) * 100

    portfolio["YTM (%)"] = portfolio.apply(lambda row: calculate_ytm(row["Price ($)"], row["Face Value ($)"], row["Coupon Rate (%)"], row["Maturity (Years)"]), axis=1)

    # Duration (Macaulay approximation)
    def calculate_duration(price, face_value, coupon_rate, maturity):
        c = coupon_rate * face_value / 100
        y = calculate_ytm(price, face_value, coupon_rate, maturity) / 100
        duration = sum([(t * c / (1 + y)**t) for t in range(1, maturity + 1)]) + (maturity * face_value / (1 + y)**maturity)
        return duration / price

    portfolio["Duration"] = portfolio.apply(lambda row: calculate_duration(row["Price ($)"], row["Face Value ($)"], row["Coupon Rate (%)"], row["Maturity (Years)"]), axis=1)

    # Convexity (simplified)
    def calculate_convexity(price, face_value, coupon_rate, maturity):
        c = coupon_rate * face_value / 100
        y = calculate_ytm(price, face_value, coupon_rate, maturity) / 100
        convexity = sum([(t * (t + 1) * c / (1 + y)**(t + 2)) for t in range(1, maturity + 1)]) + (maturity * (maturity + 1) * face_value / (1 + y)**(maturity + 2))
        return convexity / price

    portfolio["Convexity"] = portfolio.apply(lambda row: calculate_convexity(row["Price ($)"], row["Face Value ($)"], row["Coupon Rate (%)"], row["Maturity (Years)"]), axis=1)

    st.subheader("Portfolio Metrics")
    st.dataframe(portfolio[["Bond ID", "YTM (%)", "Duration", "Convexity"]])

    # Simulate interest rate change
    rate_change = st.slider("Simulate interest rate change (%):", -2.0, 2.0, 0.0, 0.1)
    st.write(f"Interest rate change: {rate_change}%")

    portfolio["Price Change (%)"] = -portfolio["Duration"] * rate_change + 0.5 * portfolio["Convexity"] * (rate_change**2)
    portfolio["New Price ($)"] = portfolio["Price ($)"] * (1 + portfolio["Price Change (%)"] / 100)

    st.subheader("Simulated Portfolio Performance")
    st.dataframe(portfolio[["Bond ID", "Price ($)", "New Price ($)", "Price Change (%)"]])
else:
    st.info("Please select at least one bond to view portfolio metrics and simulations.")
