# The Author of this code is Aditya Phadnis
# importing required modules
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# setting page config
st.set_page_config(page_title="Budget Tracker", layout='centered')

# Use existing csv
st.title("Personal Budget Tracker")

uploaded_file = st.file_uploader("Upload your budget CSV", type="csv")

@st.cache_data

def load_data(file):
    df = pd.read_csv(file)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['category'] = df['category'].str.strip().str.lower()
    return df.dropna(subset = ['date', 'amount'])

def create_pdf(total, category_summary, month):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"Budget Summary - {month}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Spent: ${total:.2f}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt="Spending by Category:", ln=True)
    
    for category, amount in category_summary.items():
        pdf.cell(200, 10, txt=f"{category.title()}: ${amount:.2f}", ln=True)

    # Generate PDF as string and encode it to bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes



if uploaded_file:
    df = load_data(uploaded_file)

    # Date Filter
    st.sidebar.header("Filter")
    months = df['date'].dt.to_period('M').astype(str).unique()
    selected_month = st.sidebar.selectbox("Select Month", sorted(months), index=0)

    filtered_df = df[df['date'].dt.to_period('M').astype(str) == selected_month]

    st.subheader(f"Summary for {selected_month}")
    total = filtered_df['amount'].sum()
    st.metric("Total Spent", f"${total: .2f}")

    # Category-wise Spending
    st.subheader("Spending by Category")
    category_summary = filtered_df.groupby('category')['amount'].sum().sort_values(ascending = False)
    st.bar_chart(category_summary)

    # Export as csv
    st.subheader("Export Options")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name=f"filtered_data_{selected_month}.csv",
        mime='text/csv',
    )

    # Export as PDF
    pdf_bytes = create_pdf(total, category_summary, selected_month)
    st.download_button("📄 Download PDF", pdf_bytes, "budget_summary.pdf", "application/pdf")

    # Monthly Spending Chart
    st.subheader("Monthly Spending Trend")
    
    monthly_summary = (
        df.groupby(df['date'].dt.to_period('M'))['amount']
        .sum()
        .sort_index()
    )
    monthly_summary.index = monthly_summary.index.astype(str)

    fig, ax = plt.subplots()
    monthly_summary.plot(kind='line', marker='o', ax=ax)
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Spent ($)")
    ax.set_title("Monthly Spending Trend")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    # Income vs Expense Chart
    st.subheader("🧾 Income vs Expense")

    # Categorize based on sign of amount
    income = df[df['amount'] > 0]['amount'].sum()
    expense = abs(df[df['amount'] < 0]['amount'].sum())
    balance = income - expense

    # Show metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Income", f"${income:.2f}")
    col2.metric("Expense", f"${expense:.2f}")
    col3.metric("Net Balance", f"${balance:.2f}", delta=f"{(income - expense):.2f}")

    # Bar chart comparison
    st.subheader("💡 Income vs Expense Overview")

    bar_df = pd.DataFrame({
        'Type': ['Income', 'Expense'],
        'Amount': [income, expense]
    })

    fig2, ax2 = plt.subplots()
    colors = ['green', 'red']
    ax2.bar(bar_df['Type'], bar_df['Amount'], color=colors)
    ax2.set_ylabel("Amount ($)")
    ax2.set_title("Income vs Expense")
    st.pyplot(fig2)


    # Show Raw Data
    with st.expander("Show Raw Data"):
        st.dataframe(filtered_df)

else:
    st.info("Please upload your csv file to begin.")


