import io
import yfinance as yf #Imports Yahoo Finance
import pandas as pd # Imports pandas for working with tabular data
import streamlit as st # Imports Streamlit for web UI
from matplotlib import pyplot as plt

#Code has minimal changes based on raw code, in just GUI code
def out_graph_surf(ticker_str,w,h):
    try:
        stock = yf.Ticker(ticker_str)
        hist = stock.history(period="5y")['Close']

        if hist.empty:
            raise ValueError("No data")

        fig, ax = plt.subplots(figsize=(w/100,h/100),dpi=100)
        fig.patch.set_facecolor((0,0,0))
        ax.set_facecolor((0/256,0/256,0/256)) #Matplotlib uses decimals between 0 & 1 rather than 0 to 256
        ax.plot(hist.index, hist.values,color='white',linewidth=0.5)

        ax.set_title(f"{ticker_str.upper()} : Stock Performance",color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig #Returns to be outputted in web app

    except:
        return None

#Actual Content -->
def Convert(uncoverted_num): #Function to round and convert huge numbers to more understandable formats
    num_abs = abs(uncoverted_num) #Removes direction, only keeps magnitude
    if num_abs < 1000000:
        return (f"{(uncoverted_num):.2f}")
    elif num_abs < 1000000000:
        return(f"{(uncoverted_num/1000000):.2f} million")
    elif num_abs < 1000000000000:
        return(f"{(uncoverted_num/1000000000):.2f} billion")
    else:
        return(f"{(uncoverted_num/1000000000000):.2f} trillion")
def WACC(ticker_str): #Automatically creates a WACC

    ticker_wacc = yf.Ticker(ticker_str) #Saves the ticker as a local variable for the WACC function

    i_state = ticker_wacc.incomestmt  #Saves income statement
    i_state = i_state.T.fillna(0)  # Saves the income statement as a table & replaces NaN with 0
    equ_val_wacc = ticker_wacc.info.get("marketCap",0) #Saves market cap
    total_debt = ticker_wacc.info.get("totalDebt",0) #Saves total debt
    weight_of_equ = equ_val_wacc/(total_debt + equ_val_wacc) #Saves the weight of equity
    risk_free_r = (yf.Ticker("^TNX")).history(period='1d')['Close'].iloc[0] / 100 #Saves risk-free rate (10 year US treasury yield)
    cost_of_equ = risk_free_r + (0.05 * ticker_wacc.info.get("beta",1.0)) #Adds risk-free rate to beta multiplied by market risk premium (assumed to be 0.05)
    weight_of_debt = total_debt/(total_debt + equ_val_wacc) #Saves the weight of debt
    cost_of_debt = abs(i_state.get('Interest Expense',0).iloc[0])/total_debt #Retrieves magnitude of interest expense (as it is sometimes reported negative) and divides it by total debt
    tax_r = i_state.get('Tax Provision').iloc[0] / i_state.get('Pretax Income').iloc[0] #Calculates tax rate by dividing tax provision by pre-tax income
    wacc = weight_of_equ * cost_of_equ + weight_of_debt * cost_of_debt * (1-tax_r) #(Percent of Equity/Weight of Equity x Cost of Equity) + (Percent of debt/Weight of debt x Cost of debt x (1 - tax rate))

    return(wacc)
def DCF(proj_time_1,growth_r_1,p_growth_r_1,wacc_2,ebit_1, ebitda_1, ncwc_1_a, ncwc_1_b, cap_ex_1, tax_1, c_share_p, s_out_1, total_cash_1, total_debt_1, ticker_str):

    mega_string =""
    #Initialises lists
    cap_ex_2 = [cap_ex_1]
    ebit_2 = [ebit_1]
    ebitda_2 = [ebitda_1]
    tax_2 = [tax_1]

    ncwc_b = [ncwc_1_b]
    ncwc_c = []

    fcf = []

    d_a = [(ebitda_2[0] - ebit_2[0])] #Initialised depreciation & amortization

    # Makes statistics the correct format
    growth_r_1 = float(growth_r_1)/100
    p_growth_r_1 = float(p_growth_r_1)/100
    present_value = []

    #Calculates NCWC change from this year to last
    ncwc_c.append(ncwc_b[0] - ncwc_1_a)

    fcf.append(ebit_2[0] - tax_2[0] + cap_ex_2[0] - ncwc_c[0] + d_a[0]) #Calculates current FCF
    present_value.append(fcf[0])

    for i in range(1, int(proj_time_1) + 1): #Calculates all future FCFs for the given projection period
        ebit_2.append(ebit_2[i - 1] * (1 + growth_r_1))

        ncwc_b.append((ncwc_b[i-1] / ebit_2[i-1]) * ebit_2[i]) #Calculates the ncwc balance for the given year
        ncwc_c.append(ncwc_b[i] - ncwc_b[i-1]) #Calculates the year-on-year change in ncwc
        d_a.append(d_a[i - 1] * (1 + growth_r_1))
        cap_ex_2.append(cap_ex_2[i-1]* (1 + growth_r_1))
        tax_2.append((tax_2[0] / ebit_2[0]) * ebit_2[i])

        fcf.append(ebit_2[i] - tax_2[i] + cap_ex_2[i] - ncwc_c[i] + d_a[i]) #Free cash flow calculation
        present_value.append(fcf[i]/((1+wacc_2)**i)) # Calculates present value using discount factor


    term_value = (fcf[int(proj_time_1)]*(1+p_growth_r_1))/(wacc_2-p_growth_r_1) #Calculates terminal value
    ent_val = (term_value/(1+wacc_2)**int(proj_time_1)) + sum(present_value[1:]) #Calculates projected enterprise value

    equ_val = ent_val + total_cash_1 - total_debt_1 #Calculates equity value

    dis_stock_p = equ_val/s_out_1
    mega_string += (f"Terminal Value: {Convert(term_value)}\nImplied Enterprise Value: {Convert(ent_val)}\nImplied Equity Value: {Convert(equ_val)}   ")

    val_percent = (dis_stock_p-c_share_p)/c_share_p*100 #Calcuates the percentage under/overvaluation between current and target stock price

    if dis_stock_p > c_share_p:
        mega_string += (f"\nTarget Price:{Convert(dis_stock_p)}    Current Share Price: {Convert(c_share_p)}\n{ticker_str} is undervalued by {Convert(val_percent)}%")
    else:
        mega_string += (f"\nTarget Price: {Convert(dis_stock_p)}    Current Share Price: {Convert(c_share_p)}\n{ticker_str} is overvalued by {Convert(-val_percent)}%")

    mega_string += f"   WACC = {Convert(100*wacc_2)}%"

    return (mega_string) #Returns the answers
def FMajor(ticker_str,proj_time_0,growth_r_0,p_growth_r_0,wacc_1):
    ticker_2 = yf.Ticker(ticker_str)  # Defines the stock
    print("Accessing balance sheet, income & cash flow statements from Yahoo Finance.")  # Notifies the user the progress of the calculations

    b_sheet = ticker_2.balance_sheet  # aves the balance sheet
    b_sheet = b_sheet.T.fillna(0)  #Saves the balance sheet as a table & replaces NaN with 0
    c_flow = ticker_2.cashflow  #Saves cash flow statement
    c_flow = c_flow.T.fillna(0)  #Saves the cash flow statement as a table & replaces NaN with 0
    i_state = ticker_2.incomestmt  #Saves income statement
    i_state = i_state.T.fillna(0)  #Saves the income statement as a table & replaces NaN with 0

    ebit_0 = i_state.get("EBIT") #Retrieves EBIT
    ebitda_0 = i_state.get("EBITDA") #Retrieves EBITDA
    cap_ex_0 = c_flow.get('Capital Expenditure') #Retrieves capex
    tax_0 = i_state.get('Tax Provision') #Retrieves tax provision

    ncwc = ((b_sheet.get('Total Current Assets', 0) - b_sheet.get('Cash And Cash Equivalents', 0) -
             b_sheet.get('Other Short Term Investments', 0)) - (b_sheet.get('Total Current Liabilities', 0) -
             b_sheet.get('Current Debt And Capital Lease Obligation',0) -
             b_sheet.get('Current Debt',0)))  # Non-cash working capital calculation

    stock_p_0 = (ticker_2.history(period="1d"))['Close'] #Retrieves stock price by checking the most recent closing price
    total_cash_0 = (ticker_2.info).get('totalCash',0) #Retrieves total cash
    total_debt_0 = (ticker_2.info).get('totalDebt',0) #Retrieves total debt
    s_out_0 = ticker_2.info.get('sharesOutstanding',0) #Retrieves the number of outstanding shares
    #If there is missing elements from balance sheet of three items above, they will be automatically set to 0

    return DCF(proj_time_0,growth_r_0,p_growth_r_0,wacc_1,ebit_0.iloc[0], ebitda_0.iloc[0], ncwc.iloc[1], ncwc.iloc[0], cap_ex_0.iloc[0], tax_0.iloc[0], stock_p_0.iloc[0],s_out_0, total_cash_0, total_debt_0,ticker_str)  # Calls the DCF
# <-- Actual Content

#GUI Code
st.set_page_config(page_title="DCF | Modelling Tool")

# Replaces the saved_Text_Data list with Streamlit inputs
text_0 = st.text_input("Ticker", value="AAPL")
text_1 = st.text_input("Projection Time", value="5")
text_2 = st.text_input("Growth Rate", value="5")
text_3 = st.text_input("Perpetuity Growth Rate", value="2")
text_4 = st.text_input("Enter WACC or Leave Empty", value="")

if st.button("Press to Output"):
    try:
        if (text_4 == "" or text_4 == "Enter WACC or Leave Empty"):  # If the user enters a WACC, the program will not calculate one itself
            wacc_val = WACC(text_0.upper())
        else:
            wacc_val = float(text_4)/100

        out_ans = FMajor(text_0.upper(), text_1, text_2, text_3, wacc_val)

        st.text(out_ans)

        graph_surf = out_graph_surf(text_0.upper(), 420, 350)
        if graph_surf is not None:
            st.pyplot(graph_surf)

    except Exception as e:
        st.error(f"The error is: {e}")