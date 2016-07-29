Statistical method used
=======================

1. For calculating 95% confidence intervals of percent control relative to the control response (frequently used in data-pivot visualizations), variance is calculated from both groups using a Fisher Information Matrix, assuming independent normal distributions.

2. For confidence intervals on individual dose-response animal-bioassay datasets:

   - For continuous data, intervals are calculated using a two-tailed t-test, assuming a 95% confidence interval
   - For dichotomous data, intervals are calculated using the inverse standard normal cumulative distribution function evaluated at :math:`1-\alpha/2`, using a two-sided 95% confidence interval.
