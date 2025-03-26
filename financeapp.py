#import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page title and layout
st.set_page_config(page_title="MyFinance Toolkit", layout="centered")

def main():
    """Main function to control the app navigation."""
    st.title("MyFinance Toolkit")
    st.sidebar.header("Navigation")
    app_mode = st.sidebar.radio("Select Tool", ["Budget Tracker", "Loan Calculator"])

    if app_mode == "Budget Tracker":
        budget_tracker()
    else:
        loan_calculator()

def budget_tracker():
    """Budget Tracker Tool"""
    st.header("📊 Monthly Budget Tracker")

    # Initialize session state for transactions
    if "transactions" not in st.session_state:
        st.session_state.transactions = pd.DataFrame(columns=["Date", "Category", "Amount", "Type"])

    # Input form for transactions
    with st.form("transaction_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Transport", "Housing", "Entertainment", "Utilities", "Other"])
        amount = st.number_input("Amount ($)", min_value=0.01)
        trans_type = st.radio("Type", ["Income", "Expense"])

        if st.form_submit_button("Add Transaction"):
            new_trans = pd.DataFrame([{
                "Date": date,
                "Category": category,
                "Amount": amount if trans_type == "Income" else -amount,
                "Type": trans_type
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, new_trans], ignore_index=True)
            st.success("Transaction added!")

    # Display transactions
    if not st.session_state.transactions.empty:
        st.subheader("📜 Your Transactions")
        st.dataframe(st.session_state.transactions.style.applymap(
            lambda x: "color: green" if x > 0 else "color: red",
            subset=["Amount"]
        ))

        st.subheader("📈 Financial Summary")
        summary = st.session_state.transactions.groupby("Type")["Amount"].sum()
        net_balance = summary.sum()

        col1, col2 = st.columns(2)
        col1.metric("Total Income", f"${summary.get('Income', 0):,.2f}")
        col1.metric("Total Expenses", f"${-summary.get('Expense', 0):,.2f}")
        col2.metric("Net Balance", f"${net_balance:,.2f}", delta_color="inverse")

        # Expense Breakdown Pie Chart
        expenses = st.session_state.transactions[st.session_state.transactions["Type"] == "Expense"]
        if not expenses.empty:
            fig, ax = plt.subplots()
            expenses.groupby("Category")["Amount"].sum().plot(kind="pie", autopct="%1.1f%%", ax=ax)
            ax.set_title("Expense Breakdown")
            st.pyplot(fig)
    else:
        st.info("No transactions yet. Add your first transaction above.")

def loan_calculator():
    """Loan Calculator Tool"""
    st.header("🏦 Loan Calculator")

    col1, col2 = st.columns(2)
    principal = col1.number_input("Loan Amount ($)", min_value=100, value=10000)
    interest_rate = col2.slider("Annual Interest Rate (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.1)

    col1, col2 = st.columns(2)
    years = col1.slider("Loan Term (years)", min_value=1, max_value=30, value=5)
    payment_freq = col2.selectbox("Payment Frequency", ["Monthly", "Quarterly", "Yearly"])

    # Payment Calculation
    freq_map = {"Monthly": 12, "Quarterly": 4, "Yearly": 1}
    periods_per_year = freq_map[payment_freq]
    total_payments = years * periods_per_year
    periodic_rate = interest_rate / 100 / periods_per_year

    payment = principal * (periodic_rate * (1 + periodic_rate) ** total_payments) / (
        (1 + periodic_rate) ** total_payments - 1
    )

    # Display results
    st.subheader("💰 Payment Details")
    cols = st.columns(3)
    cols[0].metric(f"{payment_freq} Payment", f"${payment:,.2f}")
    cols[1].metric("Total Payments", f"${payment * total_payments:,.2f}")
    cols[2].metric("Total Interest", f"${payment * total_payments - principal:,.2f}")

if __name__ == "__main__":
    main()
