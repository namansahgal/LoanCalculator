import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def loan_repayment_calculator():
    st.set_page_config(page_title="Financial Planner for Master's Abroad", layout="wide")
    st.title("🎓 Loan Repayment and Financial Planner")

    # Currency selection
    currency_options = {"INR (₹)": "₹", "USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£"}
    currency_symbol = st.selectbox("Choose your currency:", options=list(currency_options.keys()), format_func=lambda x: x.split(" (")[0])
    currency = currency_options[currency_symbol]

    # Input fields
    st.sidebar.header("Input Parameters")
    tuition_fees = st.sidebar.number_input(f"Enter the total tuition fees ({currency}):", value=7500000.0, step=100000.0)
    interest_rate = st.sidebar.number_input("Enter the annual loan interest rate (in %):", value=10.0, step=0.1)
    salary = st.sidebar.number_input(f"Enter your expected annual salary after graduation ({currency}):", value=6000000.0, step=100000.0)
    grace_period = st.sidebar.number_input("Enter the grace period (in months):", value=12, step=1, min_value=0)
    loan_term = st.sidebar.number_input("Enter the loan term (in years):", value=10, step=1, min_value=1)
    salary_growth_rate = st.sidebar.number_input("Enter your expected annual salary increment rate (in %):", value=5.0, step=0.1)
    extra_payment = st.sidebar.number_input(f"Enter your expected annual extra payment towards the loan ({currency}):", value=50000.0, step=1000.0)
    allocation_percentage = st.sidebar.number_input("Enter the percentage of salary allocated for loan repayment (in %):", value=30.0, step=0.1) / 100

    if st.sidebar.button("Calculate"):
        # Calculations
        annual_interest_rate = interest_rate / 100
        monthly_interest_rate = annual_interest_rate / 12
        loan_amount = tuition_fees

        # Grace period interest accrual
        if grace_period > 0:
            accrued_interest = loan_amount * (monthly_interest_rate * grace_period)
            loan_amount += accrued_interest

        # Monthly EMI
        n = loan_term * 12
        emi = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**n) / ((1 + monthly_interest_rate)**n - 1)
        total_repayment = emi * n
        total_interest = total_repayment - tuition_fees

        # Detailed repayment schedule
        balance = loan_amount
        monthly_income = salary / 12
        months_to_repay = 0
        repayment_schedule = []

        while balance > 0:
            months_to_repay += 1
            allocation = monthly_income * allocation_percentage

            # Adjust for prepayment
            if months_to_repay % 12 == 0:  # Extra payment at the end of each year
                allocation += extra_payment

            # Apply interest and reduce balance
            interest_for_month = balance * monthly_interest_rate
            principal_payment = allocation - interest_for_month

            if principal_payment <= 0:
                st.error("Insufficient allocation for repayment. Loan balance will never reduce.")
                return

            balance -= principal_payment
            repayment_schedule.append({
                "Month": months_to_repay,
                "Monthly Payment": allocation,
                "Interest Paid": interest_for_month,
                "Principal Paid": principal_payment,
                "Remaining Balance": max(balance, 0),
            })

            # Annual salary growth
            if months_to_repay % 12 == 0:
                salary += salary * (salary_growth_rate / 100)
                monthly_income = salary / 12

            # Stop when balance is fully paid
            if balance <= 0:
                break

        # Final outputs
        years_to_repay = months_to_repay / 12
        repayment_df = pd.DataFrame(repayment_schedule)

        # Calculate amount saved and percentage of loan payment
        annual_savings = salary - 35000 - (12 * emi)
        percent_allocated_to_loan = (12 * emi) / salary * 100

        # Display results
        st.subheader("Loan Repayment Summary")
        col1, col2 = st.columns(2)
        col1.metric("Monthly EMI", f"{currency} {emi:.2f}")
        col1.metric("Total Repayment", f"{currency} {total_repayment:.2f}")
        col1.metric("Total Interest Paid", f"{currency} {total_interest:.2f}")
        col2.metric("Years to Repay Loan", f"{years_to_repay:.2f} years")
        col2.metric("Annual Savings", f"{currency} {annual_savings:.2f}")
        col2.metric("% Salary to Loan Payment", f"{percent_allocated_to_loan:.2f}%")

        # Visualization
        st.subheader("Repayment Schedule")

        # Line chart for balance reduction
        st.line_chart(repayment_df.set_index("Month")["Remaining Balance"], use_container_width=True, height=400)

        # Bar chart for payment breakdown
        repayment_df["Principal + Interest"] = repayment_df["Principal Paid"] + repayment_df["Interest Paid"]
        st.bar_chart(repayment_df.set_index("Month")[["Principal Paid", "Interest Paid"]], use_container_width=True, height=400)

        # Detailed repayment table
        st.subheader("Detailed Repayment Schedule")
        st.dataframe(repayment_df, use_container_width=True)

# To run the program dynamically, use Streamlit:
# 1. Save this file as `loan_calculator.py`.
# 2. Run `streamlit run loan_calculator.py` in the terminal.
loan_repayment_calculator()