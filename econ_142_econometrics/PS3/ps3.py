###########################################
# Load Libraries
###########################################

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

from scipy.stats import norm


###########################################
# Read Data
###########################################

data = 'Brazil_1996PNAD.out'

# drop observations with 0 earnings
df = pd.read_csv(data, sep='\t', encoding='utf-8')\
    .query('MONTHLY_EARNINGS != 0')\
    .assign(log_earnings=lambda x: np.log(x.MONTHLY_EARNINGS))


###################################
# Question 1a
###################################

reg = smf.ols('log_earnings ~ YRSSCH + AgeInDays + np.power(AgeInDays, 2)', data=df).fit()
reg.summary()


###################################
# Question 1b
###################################

reg2 = smf.ols('log_earnings ~ C(YRSSCH) + AgeInDays + np.power(AgeInDays, 2) - 1', data=df).fit()
reg2.summary()


###################################
# Question 1c
###################################

# schooling years
x = np.arange(0, 15)

plt.figure()

# part a
p = reg.params
line_a, = plt.plot(x, p[0] + p[1] * x + p[2] * 40 + p[3] * 40 ** 2,
                  label='a')

# part b
p2 = reg2.params
line_b, = plt.plot(x, p2[x] + p2[16] * 40 + p2[17] * 40 ** 2,
                  label='b')

# plot
plt.legend(handles=[line_a, line_b])


###################################
# Question 1d
###################################

# YRSSCH == 0
plt.figure()
plt.hist(np.log(df[df.YRSSCH == 0].MONTHLY_EARNINGS), bins=30)

# YRSSCH == 8
plt.figure()
plt.hist(np.log(df[df.YRSSCH == 8].MONTHLY_EARNINGS), bins=30)

print(np.log(df[df.YRSSCH == 0].MONTHLY_EARNINGS).describe())
print(np.log(df[df.YRSSCH == 8].MONTHLY_EARNINGS).describe())

###################################
# Question 1e
###################################

# construct a new data frame
# filter for observations with age between 20 and 60
# assign observations to cells
# sort
df2 = df\
    .query('AgeInDays >= 20 & AgeInDays <= 60')\
    .assign(subcell=lambda x: (x.YRSSCH * 8 + np.minimum((x.AgeInDays - 20) // 5, 7)).astype('int'))\
    .sort_values(by=['subcell', 'log_earnings'], ascending=True)

# subcells with at least 30 observations
subcells_gte_30 = df2\
    .groupby('subcell')\
    .size().reset_index(name='size')\
    .query('size >= 30')

# compute quantiles
subcells_quantiles = df2\
    .query('subcell in @subcells_gte_30.subcell')\
    .groupby('subcell')\
    .log_earnings\
    .quantile([0.1, 0.25, 0.5, 0.75, 0.9])\
    .reset_index(name='value')\
    .rename(index=str, columns={'level_1': 'q'})

# confidence level
conf_level = 0.05

# compute N, l, j, k
subcells_quantiles = subcells_quantiles\
    .assign(N=lambda x: subcells_gte_30.loc[x.subcell, 'size'].values)\
    .assign(l=lambda x: norm.ppf(1 - conf_level / 2) * np.sqrt(x.N * x.q * (1 - x.q)))\
    .assign(j=lambda x: (np.maximum(1, np.floor(x.N * x.q - x.l)).astype('int')),
            k=lambda x: (np.minimum(x.N, np.ceil(x.N * x.q + x.l)).astype('int')))

# compute confidence intervals
subcells_quantiles['ci0'] = subcells_quantiles.apply(axis=1,
                                                     func=lambda x: df2[df2.subcell == x.subcell].log_earnings.iloc[int(x.j - 1)])
subcells_quantiles['ci1'] = subcells_quantiles.apply(axis=1,
                                                     func=lambda x: df2[df2.subcell == x.subcell].log_earnings.iloc[int(x.k - 1)])

# compute SE
subcells_quantiles = subcells_quantiles\
    .assign(se=lambda x: np.sqrt(x.N * (x.ci1 - x.ci0) ** 2 / 4 / (norm.ppf(1 - conf_level / 2) ** 2)))


###################################
# Question 1f
###################################

print(df.MONTHLY_EARNINGS.sample(10))

print(subcells_quantiles.query('se == 0').se)


###################################
# Question 1g
###################################

# compute weights
subcells_quantiles = subcells_quantiles\
    .query('se != 0')\
    .assign(p=lambda x: x.N / len(df2),
            YRSSCH=lambda x: x.subcell // 8,
            AgeInDays=lambda x: (x.subcell % 8) * 5 + 20 + 2.5)\
    .assign(w=lambda x: x.p / (x.se ** 2))

# run WLS for each quantile
reg_quantiles = []
for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
    this_subset = subcells_quantiles.query('q == @q')
    reg_quantiles.append(smf.wls('value ~ YRSSCH + AgeInDays + np.power(AgeInDays, 2)',
                                 data=this_subset,
                                 weights=this_subset.w).fit())

for reg in reg_quantiles:
    print(reg.params['YRSSCH'])


###################################
# Question 1i
###################################

# compute quantiles
subcells_quantiles2 = df2\
    .query('subcell in @subcells_gte_30.subcell')\
    .groupby('subcell')\
    .log_earnings\
    .quantile(np.arange(0.05, 0.96, 0.01))\
    .reset_index(name='value')\
    .rename(index=str, columns={'level_1': 'q'})

# confidence level
conf_level = 0.05

# compute N, l, j, k
subcells_quantiles2 = subcells_quantiles2\
    .assign(N=lambda x: subcells_gte_30.loc[x.subcell, 'size'].values)\
    .assign(l=lambda x: norm.ppf(1 - conf_level / 2) * np.sqrt(x.N * x.q * (1 - x.q)))\
    .assign(j=lambda x: (np.maximum(1, np.floor(x.N * x.q - x.l)).astype('int')),
            k=lambda x: (np.minimum(x.N, np.ceil(x.N * x.q + x.l)).astype('int')))

# compute confidence intervals
subcells_quantiles2['ci0'] = subcells_quantiles2.apply(axis=1,
                                                       func=lambda x: df2[df2.subcell == x.subcell].log_earnings.iloc[int(x.j - 1)])
subcells_quantiles2['ci1'] = subcells_quantiles2.apply(axis=1,
                                                       func=lambda x: df2[df2.subcell == x.subcell].log_earnings.iloc[int(x.k - 1)])

# compute SE
subcells_quantiles2 = subcells_quantiles2\
    .assign(se=lambda x: np.sqrt(x.N * (x.ci1 - x.ci0) ** 2 / 4 / (norm.ppf(1 - conf_level / 2) ** 2)))

# compute weights
subcells_quantiles2 = subcells_quantiles2\
    .query('se != 0')\
    .assign(p=lambda x: x.N / len(df2),
            YRSSCH=lambda x: x.subcell // 8,
            AgeInDays=lambda x: (x.subcell % 8) * 5 + 20 + 2.5)\
    .assign(w=lambda x: x.p / (x.se ** 2))

# run WLS, store coefficient on schooling and its SE
coefs = []
ses = []
for q in np.arange(0.05, 0.96, 0.01):
    this_subset = subcells_quantiles2.query('q == @q')
    this_reg = smf.wls('value ~ YRSSCH + AgeInDays + np.power(AgeInDays, 2)',
                       data=this_subset,
                       weights=this_subset.w).fit()
    coefs.append(this_reg.params['YRSSCH'])
    ses.append(this_reg.bse['YRSSCH'])

# construct a data frame with quantiles, coef on schooling, SE
reg_quantiles2 = pd.DataFrame({'q': np.arange(0.05, 0.96, 0.01),
                               'coef': coefs,
                               'se': ses})

# plot
x = np.arange(0.05, 0.96, 0.01)
plt.figure()
plt.plot(x, reg_quantiles2.coef[((x - 0.05) * 100).astype('int')])
plt.fill_between(x,
                 reg_quantiles2.coef[((x - 0.05) * 100).astype('int')] + norm.ppf(1 - conf_level / 2) * reg_quantiles2.se[((x - 0.05) * 100).astype('int')],
                 reg_quantiles2.coef[((x - 0.05) * 100).astype('int')] - norm.ppf(1 - conf_level / 2) * reg_quantiles2.se[((x - 0.05) * 100).astype('int')],
                 alpha=0.2)
