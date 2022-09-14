# Statistical methods

All statistical methods are documented in the source code, which is publicly available. <https://github.com/shapiromatron/hawc>.  If you're interested in locating a particular method and have troubles navigating the source code, please contact us and we can help.

## Bioassay

- For single dose-response confidence intervals displayed on the dose-response plot:
   - For continuous data, 95% confidence intervals are calculated using a two-tailed t-test (eg., <https://hawcproject.org/ani/endpoint/1/>)
   - For dichotomous data, intervals are calculated using the inverse standard normal cumulative distribution function evaluated at $1-\alpha/2$, using a two-sided 95% confidence interval (eg., <https://hawcproject.org/ani/endpoint/30/>)

- For calculating percent control relative to the control response (in data-pivot, eg., <https://hawcproject.org/summary/data-pivot/assessment/1/feature-example-percent-difference/>):
    - 95% confidence intervals are calculated using a Fisher Information Matrix, assuming independent normal distributions
    - This statistic assumes that first dose-group is control, and all other dose-groups are compared to control
    - Calculation of confidence intervals requires the following:
        - The endpoint dataset must provide variance measures (i.e. standard deviation or standard error)
        - The control mean value must not be equal to zero (cannot divide by zero)
        - The n for each dose-group must be provided, including control
    - A detailed description is available: [CI description](./appendix-a-ci.md)

## In-vitro

- For single dose-response confidence intervals displayed on the dose-response plot:
   - same as continuous methods for bioassay data, as described above

- For calculating percent control relative to the control response (in data-pivot):
    - same as methods for bioassay data, as described above

## Epidemiology (v1)

- For confidence intervals on epidemiology result-datasets
    - If 95% confidence intervals are entered, they are presented (eg., <https://hawcproject.org/epi/result/98/>)
    - If 95% confidence intervals are not entered, and the response is a normal distribution with a SD or SE:
        - 95% confidence intervals are calculated using a two-tailed t-test (eg., <https://hawcproject.org/epi/result/1445/>)

- For calculating percent control relative to the control response (in data-pivot):
    - same as methods for bioassay data, as described above
    - The control group is determined by the following rules:
        - If 0 groups are marked control (using comparison-set groups), the first group will be chosen as control
        - If 1 groups is marked control (using comparison-set groups), the first group will be chosen as control
        - If ≥ 2 groups are marked control (using comparison-set groups), a random control group will be chosen for control for all calculations
