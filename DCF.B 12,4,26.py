import yfinance as yf #Imports Yahoo Finance
import pandas as pd # Imports pandas for working with tabular data
import pygame, sys
from pygame.locals import *

def inp_box (screen,x,y,w,h,text,font_size=20):

    inp_rect = pygame.Rect(x,y,w,h)
    pygame.draw.rect(screen,(128,128,128),inp_rect)

    out_colour = (255,255,255) if inp_rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
    pygame.draw.rect(screen,out_colour,inp_rect,3)

    draw_text(text, pygame.font.SysFont("Arial",font_size),x+5,y+5)  # Draw text on the input_box
    return inp_rect

def ui (screen,mainClock):
    text = ["Ticker","Projection Time","Growth Rate","Perpetuity Growth Rate","Enter WACC or Leave Empty","Press to Output"] #List for text inputs
    active_box = None

    while 0<1: #This code will always run
        screen.fill((0,0,0)) #Makes the screen black

        rect = [inp_box(screen,50,100,200,50,text[0]),
                inp_box(screen,270,100,200,50,text[1]),
                inp_box(screen,50,170,200,50,text[2]),
                inp_box(screen,270,170,200,50,text[3]),
                inp_box(screen,50,240,250,50,text[4]),
                inp_box(screen,50,310,420,100,text[5],font_size=16)] #Initalises all squares

        for event in pygame.event.get():
            if event.type == QUIT:  # Closes the program if the user clicks out
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN: #Checks whether anything has been inputted
                for i in range(len(rect)):
                    if (rect[i].collidepoint(event.pos)):  # Active is validated if the mouse touching the input button
                        active_box = i
                        if (i==5): #Duplicated
                            try:
                                pygame.display.update()
                                if (text[5] == "Enter WACC or Leave Empty"):
                                    wacc_val = WACC(text[0])
                                else:
                                    wacc_val = text[4]
                                out_ans = FMajor(text[0], text[1], text[2], text[3], wacc_val)
                                text[5] = out_ans
                            except:
                                pygame.display.update()
                                text[5] = "Invalid Input"
                        else:
                            text[i] = ""

            if event.type == KEYDOWN and active_box is not None:  # If a key is being inputted
                if event.key == K_RETURN: #Duplicated

                    try:
                        pygame.display.update()
                        wacc_val = WACC(text[0])
                        out_ans = FMajor(text[0], text[1], text[2], text[3], wacc_val)
                        text[5] = out_ans
                    except:
                        pygame.display.update()
                        text[5] = "Invalid Input"

                elif (active_box != 5):
                    if event.key == K_BACKSPACE:
                        text[active_box] = text[active_box][:-1]
                    else:
                        text[active_box] += event.unicode

        pygame.display.update()

        mainClock.tick(30)

def draw_text (text,font,x,y): #No clue mate, ACC for drawing text at this location
    textobj = font.render(text,1,(255,255,255))
    textrect = textobj.get_rect()
    textrect.topleft = (x,y)
    screen.blit(textobj,textrect)

#Actual Content -->
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

    d_a = [(ebitda_2[0] - ebit_2[0])]

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
    mega_string += (f"Terminal Value: {Convert(term_value)}    Implied Enterprise Value: {Convert(ent_val)}\nImplied Equity Value: {Convert(equ_val)}   ")

    val_percent = (dis_stock_p-c_share_p)/c_share_p*100 #Calcuates the percentage under/overvaluation between current and target stock price

    if dis_stock_p > c_share_p:
        mega_string += (f"Target Price: {Convert(dis_stock_p)}\nCurrent Share Price: {Convert(c_share_p)}    {ticker_str} is undervalued by {Convert(val_percent)}%")
    else:
        mega_string += (f"Target Price: {Convert(dis_stock_p)}\nCurrent Share Price: {Convert(c_share_p)}    {ticker_str} is overvalued by {Convert(-val_percent)}%")

    mega_string += f"\nWACC = {Convert(100*wacc_2)}%"

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


#GUI Code
pygame.init()
pygame.display.set_caption("DCF Analysis")
screen = pygame.display.set_mode((500, 500))
mainClock = pygame.time.Clock()

ui(screen,mainClock)

"""
results = ui(screen,mainClock)

proj_time_str = results[1]
growth_r_str = results[2]
p_growth_r_str = results[3]
wacc_0 = results[4]
if wacc_0 == "WACC":
wacc_0 = WACC() #Saves the WACC
else:
    wacc_0 = float(wacc_0)

#Main Code
ticker_str = input("Enter ticker:") #Input ticker - Is string global variable to be used in output of DCF
proj_time_str = input("Enter projection time: ")
growth_r_str = input("Enter Growth Rate: ") #Input Growth Rate
p_growth_r_str = input("Enter Perpetuity Growth Rate: ") # Input P Growth Rate
wacc_0 = WACC() #Calls WACC function to enable the user to either manually or automatically have a WACC used for the DCF


FMajor(ticker_str,proj_time_str,growth_r_str,p_growth_r_str,wacc_0) #Calls the major function, with DCF inside
"""p