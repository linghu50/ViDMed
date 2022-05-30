import pandas as pd
df = pd.read_csv('T2DM-numBMI.csv')
for i in range(df.shape[0]):
    if df.loc[i, 'Household_income'] in [0, 1]:
        df.loc[i, 'Household_income'] = 0
    elif df.loc[i, 'Household_income'] in [2, 3]:
        df.loc[i, 'Household_income'] = 1
    else:
        df.loc[i, 'Household_income'] = 2
df.to_csv('T2DM-3income.csv',index=False)