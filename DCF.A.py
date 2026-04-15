def DCF(ebit_temp, ebitda_temp, ncwc_temp, cap_ex_temp, tax_temp, wacc_temp, c_equ_val, growth_r_temp, p_growth_r_temp, c_share_p, t_c_l, t_c_a):
    cap_ex = []
    cap_ex.append(cap_ex_temp)
    ebit = []
    ebit.append(ebit_temp)
    ebitda = []
    ebitda.append(ebitda_temp)
    tax = []
    tax.append(tax_temp)

    ncwc_b = []
    ncwc_c = []
    fcf = []

    d_a = (ebitda[0] - ebit[0])

    wacc = wacc_temp/100
    growth_r = growth_r_temp/100
    p_growth_r = p_growth_r_temp/100
    present_value = []

    #Calculates current NCWC (total current liabilities - total current assets) & change from this year to last
    ncwc_b.append(t_c_l - t_c_a)
    ncwc_c.append(ncwc_b[0] - ncwc_temp)

    proj_time = input("How many years into the future would you like to project?")

    fcf.append(ebit[0] - tax[0] - cap_ex[0] - ncwc_c[0] + d_a) #Calculates current FCF
    present_value.append(fcf[0])

    for i in range(1, int(proj_time) + 1): #Calculates all future FCFs for the given projection period

        ebit.append(ebit[i - 1] * (1 + growth_r))

        ncwc_b.append((ncwc_b[i-1] / ebit[i-1]) * ebit[i]) #Calculates the ncwc balance for the given year
        ncwc_c.append(ncwc_b[i] - ncwc_b[i-1]) #Calculates the year-on-year change in ncwc
        cap_ex.append(cap_ex[i-1]* (1 + growth_r))
        tax.append((tax[0] / ebit[0]) * ebit[i])

        fcf.append(ebit[i] - tax[i] - cap_ex[i] - ncwc_c[i] + d_a) #Free cash flow calculation
        present_value.append(fcf[i]/((1+wacc)**i)) # Calculates present value using discount factor


    term_value = (fcf[int(proj_time)]*(1+p_growth_r))/(wacc-p_growth_r) #Calculates terminal value
    ent_val = (term_value/(1+wacc)**int(proj_time)) + sum(present_value[1:]) #Calculates projected enterprise value
    '''equ_val = ent_val - total_debt + cash #Calculates market cap from subtracting short & long term (total) debt and adding cash & cash equivalents
    '''
    return (fcf, present_value, term_value, ent_val) #, equ_val

print(DCF(982000,1375000,391000,119000,137000,7.10,1,5.00,2.50,77.43,318000,887000))