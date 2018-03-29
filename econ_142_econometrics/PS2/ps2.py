###########################################
# Load Libraries
###########################################

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt


###########################################
# Read Data
###########################################

# Data file
data = 'mf_firms.out'

# Data types
col_dtypes = {
    'gvkey': int,
    'year': int,
    'Y': float,
    'K': float,
    'L': float,
    'M': float,
    'VA': float,
    'i': float,
    'naics_4digit': int
}

# read data
df = pd.read_csv(data,
                 dtype=col_dtypes,
                 na_values='',
                 engine='c',
                 sep='\t',
                 encoding='utf-8')

# drop observations with negative VA
df = df[df.VA > 0]

# create variables
df['constant'] = 1
df['logY'] = np.log(df.Y)
df['logK'] = np.log(df.K)
df['logL'] = np.log(df.L)
df['logM'] = np.log(df.M)
df['logVA'] = np.log(df.VA)
df['logK_sq'] = df.logK ** 2
df['i_sq'] = df.i ** 2
df['logK_i'] = df.logK * df.i


##################################
# Question 1
##################################

# Manufacturing firms
df = df[(df.naics_4digit // 100).isin([31, 32, 33])]
print(f"Number of firm-year observations: {len(df)}")
print(f"Number of distinct firms: {df.gvkey.nunique()}")

# 2014 observations
df_2014 = df[df.year == 2014]
print(f"Aggregate total sales: {df_2014.Y.sum()}")
print(f"Aggregate number of workers hired: {df_2014.L.sum()}")

# average, sd and by percentile
df_2014[['Y', 'K', 'L', 'M', 'i']].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])


#######################################
# Question 2
#######################################

# OLS
reg = smf.ols('logY ~ logK + logL + logM', data=df_2014).fit(cov_type='HC3')
reg.summary()

# test constant returns to scale
reg.t_test('logK + logL + logM = 1')

# OLS with sector dummy variables
reg2 = smf.ols('logY ~ logK + logL + logM + C(naics_4digit)', data=df_2014).fit(cov_type='HC3')
reg2.summary()

# test constant returns to scale
reg2.t_test('logK + logL + logM = 1')


########################################
# Question 3
########################################

# 2013 and 2014 data
df_1314 = df[df.year.isin([2013, 2014])]

# unique gvkey in 2013 and 2014 data
gvkey_1314 = pd.Series(df_1314.gvkey.unique())

# gvkey that has both 2013 and 2014 observations
gvkey_complete_1314 = df_1314.groupby('gvkey')\
                                     .size()\
                                     .reset_index()\
                                     .rename(columns={0: 'size'})\
                                     .query('size == 2')\
                                     .gvkey

# restrict our dataset to those with complete data
df_1314 = df_1314[df_1314.gvkey.isin(gvkey_complete_1314)]

print(f"Number of dropped firms: {len(gvkey_1314[np.logical_not(gvkey_1314.isin(gvkey_complete_1314))])}")

# transform into first difference
df_1314[['dlogY', 'dlogK', 'dlogL', 'dlogM']] = df_1314\
    .sort_values(by='year')\
    .groupby(['gvkey'])[['logY', 'logK', 'logL', 'logM']]\
    .diff(1)

# OLS
reg = smf.ols('dlogY ~ dlogK + dlogL + dlogM', data=df_1314).fit(cov_type='HC3')
reg.summary()

# test constant returns to scale
reg.t_test('dlogK + dlogL + dlogM = 1')

# OLS with dummy variables
reg2 = smf.ols('dlogY ~ dlogK + dlogL + dlogM + C(naics_4digit)', data=df_1314).fit(cov_type='HC3')
reg2.summary()

# test constant returns to scale
reg2.t_test('dlogK + dlogL + dlogM = 1')


##########################################
# Question 4
#########################################

# Part 1
# 2013 data
df_2013 = df[(df.year == 2013) & (df.gvkey.isin(gvkey_complete_1314))]

# Regression
reg = smf.ols('logVA ~ logK + i + logK_sq + i_sq + logK_i + logL', data=df_2013).fit(cov_type='HC3')
reg.summary()

# Part 2
df_2013['phi'] = np.matmul(df_2013[['constant', 'logK', 'i', 'logK_sq', 'i_sq', 'logK_i']],
                           np.transpose(reg.params[:-1]))
b_hat = reg.params[-1]

# Part 3
df_2014 = df[(df.year == 2014) & (df.gvkey.isin(gvkey_complete_1314))].merge(df_2013[['gvkey', 'phi', 'logK']],
                                                                             on='gvkey', how='left',
                                                                             suffixes=('_2014', '_2013'))
reg2 = smf.ols('logVA - b_hat * logL ~ logK_2014 + phi + logK_2013',
               data=df_2014).fit(cov_type='HC3')
reg2.summary()


###############################################
# Question 5
###############################################

df_2014['A'] = df_2014['VA'] / df_2014['K'] ** reg2.params[1] / df_2014['L'] ** b_hat

df_2014.A.describe()

plt.figure()
df_2014.A.plot.hist(bins=100)


###############################################
# Question 6
##############################################

df_2014['S'] = df_2014.VA / df_2014.VA.mean()
df_2014['S_A'] = df_2014.S * df_2014.A

print(f"E[A_t]: {df_2014.A.mean()}")
print(f"Var[A_t]: {df_2014.A.var()}")
print(f"beta: {(df_2014.S_A.mean() - df_2014.A.mean()) / df_2014.A.var()}")
print(f"beta * Var[A_t] = {df_2014.S_A.mean() - df_2014.A.mean()}")

