%matplotlib inline

# Load libraries
import numpy as np
import scipy as sp
import pandas as pd
import math
import matplotlib.pyplot as plt     # for plotting

import statsmodels.api as sm    # StatsModels

# StatsModels bug-fix
from scipy import stats
stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)

# Data file
data = 'math_10.out'

# Data types
col_dtypes = {
    'c10_zmath': float,
    'wgt10_math': float,
    'sat': int,
    'constant': int,
    'c08_zlang': float,
    'c08_zmath': float,
    'feeder_school': int,
    'm_id_pairs': int
}

# read csv
df = pd.read_csv(data,
                 dtype=col_dtypes,
                 na_values='',
                 engine='c',
                 sep='\t',
                 encoding='utf-8')

# Construct a list of all matched SAT-CEB village pairs in the dataset
included_pairs = sorted(df['m_id_pairs'].unique())

# Q1
# Form dummies for included matched SAT/CEB pairs
pair_dums = pd.get_dummies(df['m_id_pairs'].astype('category'),
                           prefix='mp')

# Concatenate matched pair dummies onto dataframe
df = pd.concat([df, pair_dums], axis=1)

# Q2
# Construct outcome vector, design matrix and test instrument inverse weights
Y = df['c08_zmath']     # outcome
test_wgt = 1. / df['wgt10_math']    # test instrument weights
X = df[['constant', 'sat']]     # design matrix

# omit last matched pair to avoid dummy variable trap
X = pd.concat([X, pair_dums.iloc[:, 0:-1]], axis=1)

# Compute weighted least squares fit
# NOTE: cluster-robust standard errors
wls = sm.WLS(Y, X, weights=test_wgt).fit(cov_type='cluster',
                                         cov_kwds={'groups': df['feeder_school']},
                                         use_t=True)
wls.summary()

# Q3
# now independent variable is c10_zmath
Y = df['c10_zmath']

# WLS
wls = sm.WLS(Y, X, weights=test_wgt).fit(cov_type='cluster',
                                         cov_kwds={'groups': df['feeder_school']},
                                         use_t=True)
wls.summary()

# Q4
# additional control for c08_zmath, c08_zlang
X = pd.concat([X, df[['c08_zmath', 'c08_zlang']]], axis=1)

# WLS
wls = sm.WLS(Y, X, weights=test_wgt).fit(cov_type='cluster',
                                         cov_kwds={'groups': df['feeder_school']},
                                         use_t=True)
wls.summary()

# Q5
# design matrix
X = pd.concat([df.constant,
               df.c08_zmath,
               df.c08_zlang,
               pair_dums.iloc[:, 0:-1]],
              axis=1)

# logistic regression
logit = sm.Logit(df['sat'], X)
logit_results = logit.fit()
logit_results.summary()

# Fitted propensity score values
df['propensity'] = logit_results.fittedvalues.apply(
    lambda v: math.exp(v) / (1 + math.exp(v))
)

# histogram
plt.figure()
df[df.sat == 0].propensity.plot.hist(histtype='step')
df[df.sat == 1].propensity.plot.hist(histtype='step')

# Q6
# IPW weights
df['ipw_weight'] = df.apply(
    lambda row: row.sat / row.propensity
                + (1 - row.sat) / (1 - row.propensity),
    axis=1
)

# Multiply weights by test_wgt
df.ipw_weight = test_wgt * df['ipw_weight']

# WLS
wls_ipw = sm.WLS(df['c10_zmath'],
                 df[['constant', 'sat']],
                 weights=df.ipw_weight).fit(cov_type='cluster',
                                            cov_kwds={'groups': df['feeder_school']},
                                            use_t=True)

wls_ipw.summary()