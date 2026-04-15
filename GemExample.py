import yfinance as yf
import pandas as pd
import pygame, sys
from pygame.locals import *


# --- 1. THE PYGAME INTERFACE ---
def user_interface(screen, font, mainClock):
    current_state = "menu"  # Our State Machine starts here
    user_text = ""
    input_rect = pygame.Rect(50, 180, 200, 40)
    active = False

    # This will hold our final math results to draw on screen
    final_results = {}

    running = True
    while running:
        screen.fill((30, 30, 30))  # Dark gray background

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    # If in Menu State, check the red button
                    if current_state == "menu":
                        button_1 = pygame.Rect(50, 100, 200, 50)
                        if button_1.collidepoint(mx, my):
                            current_state = "input"  # Move to text box state!

                    # If in Input State, check the text box
                    elif current_state == "input":
                        if input_rect.collidepoint(event.pos):
                            active = True
                        else:
                            active = False

            if event.type == KEYDOWN:
                if current_state == "input" and active:
                    if event.key == K_RETURN:
                        # User pressed Enter! Move to loading state.
                        current_state = "loading"
                    elif event.key == K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode.upper()  # Force uppercase for tickers

        # --- DRAWING BASED ON STATE ---
        if current_state == "menu":
            draw_text('MAIN MENU - Click to Start', font, (255, 255, 255), screen, 50, 50)
            button_1 = pygame.Rect(50, 100, 200, 50)
            pygame.draw.rect(screen, (255, 0, 0), button_1)
            draw_text('Start Analysis', font, (255, 255, 255), screen, 85, 115)

        elif current_state == "input":
            draw_text('Enter Ticker Symbol (e.g., AAPL) and press ENTER:', font, (255, 255, 255), screen, 50, 140)

            # Draw Text Box
            color = (0, 150, 255) if active else (100, 100, 100)
            pygame.draw.rect(screen, color, input_rect, 2)

            # Draw Typed Text
            text_surface = font.render(user_text, True, (255, 255, 255))
            screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            input_rect.w = max(200, text_surface.get_width() + 10)

        elif current_state == "loading":
            draw_text(f'Downloading Yahoo Finance data for {user_text}...', font, (255, 255, 0), screen, 50, 200)
            pygame.display.update()  # Force the screen to draw the loading text

            # Run the math! (This freezes the screen for a second)
            final_results = FMajor(user_text)

            # Math is done, move to results!
            current_state = "results"

        elif current_state == "results":
            draw_text(f"--- Results for {user_text} ---", font, (0, 255, 0), screen, 50, 50)
            draw_text(f"Terminal Value: ${final_results['term_val']}", font, (255, 255, 255), screen, 50, 100)
            draw_text(f"Enterprise Value: ${final_results['ent_val']}", font, (255, 255, 255), screen, 50, 140)
            draw_text(f"Equity Value: ${final_results['equ_val']}", font, (255, 255, 255), screen, 50, 180)
            draw_text(f"Current Share Price: ${final_results['current_price']}", font, (255, 255, 255), screen, 50, 240)
            draw_text(f"Target DCF Price: ${final_results['target_price']}", font, (0, 255, 255), screen, 50, 280)

            # Valuation text
            val_text = f"Undervalued by {final_results['percent']}%" if final_results[
                'is_undervalued'] else f"Overvalued by {-final_results['percent']}%"
            val_color = (0, 255, 0) if final_results['is_undervalued'] else (255, 0, 0)
            draw_text(val_text, font, val_color, screen, 50, 320)

        pygame.display.update()
        mainClock.tick(60)


def draw_text(text, font, colour, surface, x, y):
    textobj = font.render(text, 1, colour)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


# --- 2. THE MATH LOGIC ---
def Convert(uncoverted_num):
    num_abs = abs(uncoverted_num)
    if num_abs < 1000000:
        return (f"{(uncoverted_num):.2f}")
    elif num_abs < 1000000000:
        return (f"{(uncoverted_num / 1000000):.2f} M")
    elif num_abs < 1000000000000:
        return (f"{(uncoverted_num / 1000000000):.2f} B")
    else:
        return (f"{(uncoverted_num / 1000000000000):.2f} T")


def WACC(ticker_str):
    # Hardcoded to automatic for Pygame demo
    ticker_wacc = yf.Ticker(ticker_str)
    i_state = ticker_wacc.incomestmt.T.fillna(0)
    equ_val_wacc = ticker_wacc.info.get("marketCap", 0)
    total_debt = ticker_wacc.info.get("totalDebt", 0)
    weight_of_equ = equ_val_wacc / (total_debt + equ_val_wacc)
    risk_free_r = (yf.Ticker("^TNX")).history(period='1d')['Close'].iloc[0] / 100
    cost_of_equ = risk_free_r + (0.05 * ticker_wacc.info.get("beta", 1.0))
    weight_of_debt = total_debt / (total_debt + equ_val_wacc)
    cost_of_debt = abs(i_state.get('Interest Expense', 0).iloc[0]) / total_debt
    tax_r = i_state.get('Tax Provision').iloc[0] / i_state.get('Pretax Income').iloc[0]
    wacc = weight_of_equ * cost_of_equ + weight_of_debt * cost_of_debt * (1 - tax_r)
    return wacc


def DCF(ticker_str, ebit_1, ebitda_1, ncwc_1_a, ncwc_1_b, cap_ex_1, tax_1, c_share_p, s_out_1, total_cash_1,
        total_debt_1):
    cap_ex_2 = [cap_ex_1]
    ebit_2 = [ebit_1]
    ebitda_2 = [ebitda_1]
    tax_2 = [tax_1]
    ncwc_b = [ncwc_1_b]
    ncwc_c = []
    fcf = []
    d_a = [(ebitda_2[0] - ebit_2[0])]

    # Hardcoded inputs for Pygame demo
    proj_time = 5
    growth_r = 0.05
    p_growth_r = 0.025
    wacc = WACC(ticker_str)

    present_value = []
    ncwc_c.append(ncwc_b[0] - ncwc_1_a)
    fcf.append(ebit_2[0] - tax_2[0] + cap_ex_2[0] - ncwc_c[0] + d_a[0])
    present_value.append(fcf[0])

    for i in range(1, proj_time + 1):
        ebit_2.append(ebit_2[i - 1] * (1 + growth_r))
        ncwc_b.append((ncwc_b[i - 1] / ebit_2[i - 1]) * ebit_2[i])
        ncwc_c.append(ncwc_b[i] - ncwc_b[i - 1])
        d_a.append(d_a[i - 1] * (1 + growth_r))
        cap_ex_2.append(cap_ex_2[i - 1] * (1 + growth_r))
        tax_2.append((tax_2[0] / ebit_2[0]) * ebit_2[i])
        fcf.append(ebit_2[i] - tax_2[i] + cap_ex_2[i] - ncwc_c[i] + d_a[i])
        present_value.append(fcf[i] / ((1 + wacc) ** i))

    term_value = (fcf[proj_time] * (1 + p_growth_r)) / (wacc - p_growth_r)
    ent_val = (term_value / (1 + wacc) ** proj_time) + sum(present_value[1:])
    equ_val = ent_val + total_cash_1 - total_debt_1
    dis_stock_p = equ_val / s_out_1
    val_percent = (dis_stock_p - c_share_p) / c_share_p * 100

    # Instead of printing, we return a dictionary of results to the Pygame UI!
    return {
        "term_val": Convert(term_value),
        "ent_val": Convert(ent_val),
        "equ_val": Convert(equ_val),
        "current_price": Convert(c_share_p),
        "target_price": Convert(dis_stock_p),
        "percent": Convert(abs(val_percent)),
        "is_undervalued": dis_stock_p > c_share_p
    }


def FMajor(ticker_0):
    ticker_2 = yf.Ticker(ticker_0)
    b_sheet = ticker_2.balance_sheet.T.fillna(0)
    c_flow = ticker_2.cashflow.T.fillna(0)
    i_state = ticker_2.incomestmt.T.fillna(0)

    ebit_0 = i_state.get("EBIT")
    ebitda_0 = i_state.get("EBITDA")
    cap_ex_0 = c_flow.get('Capital Expenditure')
    tax_0 = i_state.get('Tax Provision')

    ncwc = ((b_sheet.get('Total Current Assets', 0) - b_sheet.get('Cash And Cash Equivalents', 0) -
             b_sheet.get('Other Short Term Investments', 0)) - (b_sheet.get('Total Current Liabilities', 0) -
                                                                b_sheet.get('Current Debt And Capital Lease Obligation',
                                                                            0) -
                                                                b_sheet.get('Current Debt', 0)))

    stock_p_0 = (ticker_2.history(period="1d"))['Close']
    total_cash_0 = (ticker_2.info).get('totalCash', 0)
    total_debt_0 = (ticker_2.info).get('totalDebt', 0)
    s_out_0 = ticker_2.info.get('sharesOutstanding', 0)

    # Return the dictionary all the way back to the Pygame loop
    return DCF(ticker_0, ebit_0.iloc[0], ebitda_0.iloc[0], ncwc.iloc[1], ncwc.iloc[0], cap_ex_0.iloc[0], tax_0.iloc[0],
               stock_p_0.iloc[0], s_out_0, total_cash_0, total_debt_0)


# --- 3. START THE PROGRAM ---
if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Financial Analysis Pro")
    screen = pygame.display.set_mode((500, 500), 0, 32)
    font = pygame.font.SysFont("Arial", 20)
    mainClock = pygame.time.Clock()

    user_interface(screen, font, mainClock)