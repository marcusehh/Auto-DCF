import yfinance as yf #Imports Yahoo Finance
import pandas as pd # Imports pandas for working with tabular data


def Convert(uncoverted_num): #Function to round and convert huge numbers to more understandable formats
    num_abs = abs(uncoverted_num)
    if num_abs < 1000000:
        return (f"{(uncoverted_num):.2f}")
    elif num_abs < 1000000000:
        return(f"{(uncoverted_num/1000000):.2f} million")
    elif num_abs < 1000000000000:
        return(f"{(uncoverted_num/1000000000):.2f} billion")
    else:
        return(f"{(uncoverted_num/1000000000000):.2f} trillion")

def WACC(): #Automatically creates a WACC
    wacc_ans = input("Will you input WACC manually?").strip().lower() #Removes capitalisation and whitespaces as well as taking an input for whether or not the user wants to input their own WACC
    if (wacc_ans != "yes"):
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

        print(f"WACC: {Convert(wacc*100)}%") #Outputs WACC
        return(wacc)
    else:
        return input("Enter WACC:") #The user will manually input the WACC

def DCF(ebit_1, ebitda_1, ncwc_1_a, ncwc_1_b, cap_ex_1, tax_1, c_share_p, s_out_1, total_cash_1, total_debt_1):

    #Initialises lists
    cap_ex_2 = [cap_ex_1]
    ebit_2 = [ebit_1]
    ebitda_2 = [ebitda_1]
    tax_2 = [tax_1]

    ncwc_b = [ncwc_1_b]
    ncwc_c = []
    fcf = []

    d_a = [(ebitda_2[0] - ebit_2[0])]

    proj_time = input("Enter projection time: ")
    growth_r = input("Enter Growth Rate: ") #Input Growth Rate
    p_growth_r = input("Enter Perpetuity Growth Rate: ") # Input P Growth Rate
    wacc = WACC() #Calls WACC function to enable the user to either manually or automatically have a WACC used for the DCF

    # Makes statistics the correct format
    growth_r = float(growth_r)/100
    p_growth_r = float(p_growth_r)/100
    present_value = []

    #Calculates NCWC change from this year to last
    ncwc_c.append(ncwc_b[0] - ncwc_1_a)

    fcf.append(ebit_2[0] - tax_2[0] + cap_ex_2[0] - ncwc_c[0] + d_a[0]) #Calculates current FCF
    present_value.append(fcf[0])

    for i in range(1, int(proj_time) + 1): #Calculates all future FCFs for the given projection period
        ebit_2.append(ebit_2[i - 1] * (1 + growth_r))

        ncwc_b.append((ncwc_b[i-1] / ebit_2[i-1]) * ebit_2[i]) #Calculates the ncwc balance for the given year
        ncwc_c.append(ncwc_b[i] - ncwc_b[i-1]) #Calculates the year-on-year change in ncwc
        d_a.append(d_a[i - 1] * (1 + growth_r))
        cap_ex_2.append(cap_ex_2[i-1]* (1 + growth_r))
        tax_2.append((tax_2[0] / ebit_2[0]) * ebit_2[i])

        fcf.append(ebit_2[i] - tax_2[i] + cap_ex_2[i] - ncwc_c[i] + d_a[i]) #Free cash flow calculation
        present_value.append(fcf[i]/((1+wacc)**i)) # Calculates present value using discount factor


    term_value = (fcf[int(proj_time)]*(1+p_growth_r))/(wacc-p_growth_r) #Calculates terminal value
    ent_val = (term_value/(1+wacc)**int(proj_time)) + sum(present_value[1:]) #Calculates projected enterprise value

    equ_val = ent_val + total_cash_1 - total_debt_1 #Calculates equity value

    dis_stock_p = equ_val/s_out_1
    print(f"Terminal Value: {Convert(term_value)}    Implied Enterprise Value: {Convert(ent_val)}     Implied Equity Value: {Convert(equ_val)}")

    val_percent = (dis_stock_p-c_share_p)/c_share_p*100 #Calcuates the percentage under/overvaluation between current and target stock price

    if dis_stock_p > c_share_p:
        print(f"Target Price: {Convert(dis_stock_p)}   Current Share Price: {Convert(c_share_p)}    {ticker_str} is undervalued by {Convert(val_percent)}%")
    else:
        print(f"Target Price: {Convert(dis_stock_p)}   Current Share Price: {Convert(c_share_p)}    {ticker_str} is overvalued by {Convert(-val_percent)}%")
def FMajor(ticker_0):
    ticker_2 = yf.Ticker(ticker_0)  # Defines the stock
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

    DCF(ebit_0.iloc[0], ebitda_0.iloc[0], ncwc.iloc[1], ncwc.iloc[0], cap_ex_0.iloc[0], tax_0.iloc[0], stock_p_0.iloc[0],s_out_0, total_cash_0, total_debt_0)  # Calls the DCF

#Main Code
ticker_str = input("Enter ticker:") #Input ticker - Is string global variable to be used in output of DCF

FMajor(ticker_str) #Calls the major function, with DCF inside

input("Press any key to exit") #Keeps the program open until the user is finished.