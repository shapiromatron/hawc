# Appendix A: Estimating the variance of a ratio of means

Or, a Normal-Theory Derivation of an Estimator of the Sampling Variance for a Ratio of Means.

## Introduction

A maximum likelihood method is used to find a formula for the variance of the ratio of the means from two independent samples of normally distributed data. The method defines the ratio as a transformation of the means then finds the variance matrix of the transformed parameters. Note that this method transforms parameters of distributions, not random variables. The method uses the inverse of the variance matrix of parameters, known as Fisher’s information matrix.

The method is not used very much, because in general the algebra is prohibitive. For this reason also, it is hard to find a single reference that contains the work below. The method works in this case, because the starting point is two independent normally distributed samples, and the ratio transformation is pretty simple. Transformations of maximum likelihood estimators (MLEs) (in this case, the mean and variance estimators for normal distributions) are again maximum likelihood estimators [eg, Cox and Hinkley, p. 287]. Thus, the variance estimate for the ratio of means this method produces is a maximum likelihood estimator if the MLEs for the normal means and variances are used. Note the MLEs for normal mean and variance for a sample $\{x_1, x_2, ..., x_n\}$ are $\hat{\mu} = \bar{x}$ and $\hat{\sigma^2} = \frac{1}{n}\sum_i(x_i - \bar{x})^2$.

One may note that the 2nd formula above is not the usual textbook estimator of variance.  The latter is usually denoted $s^2$ and has an $n – 1$ in the denominator where the formula above has $n$, i.e., uses the "degrees of freedom." The two estimators will converge with a modest amount of data. We will revisit this distinction below. Maximum likelihood estimators have nice asymptotic properties. For example, the asymptotic distribution is normal around the true value of the parameter (here the ratio) with confidence intervals constructed using the variance estimate with Gaussian critical values. For example, the 95% confidence interval can be computed by subtracting from the observed ratio of means (for lower bound) and adding (for upper bound), the quantity $Z_{0.975} * SE$, where $SE$ is the standard error (as derived here) and $Z_{0.975}$ is the 97.5th percentile of the standard normal distribution, around 1.96.

## Method

The normal distribution, denoted by $N(x|\mu,\sigma^2)$, has 2 parameters. To find the information matrix of a normal sample of $n$ observations, start with the log of the likelihood function and calculate the partial derivative with respect to each of the parameters. If the sample $x$ has $n$ observations, the log-likelihood function can be calculated from the likelihood function to look like

$$
\ln N ( \vec{x} | \mu, \sigma^2) = \sum_{i=1}^{n}\ln\left[f\left(x_i | \mu , \sigma ^ { 2 } \right) \right] = - \frac { n } { 2 } \ln ( 2 \pi ) - \frac { n } { 2 } \ln \sigma ^ { 2 } - \frac { 1 } { 2 \sigma ^ { 2 } } \sum _ { i = 1 } ^ { n } \left( x _ { i } - \mu \right) ^ { 2 }
$$

The vector of first derivatives wrt the two parameters is known as the Fisher score for the normal distribution:

$$
\left[ \begin{array} { c } { g _ { 1 } } \\ { g _ { 2 } } \end{array} \right] = \left[ \begin{array} { c } { \frac { \partial } { \partial \mu } \ln N ( \vec { x } | \mu , \sigma ^ { 2 } ) } \\ { \frac { \partial } { \partial \sigma ^ { 2 } } \ln N ( \vec { x } | \mu , \sigma ^ { 2 } ) } \end{array} \right] = \left[ \begin{array} { c } { \frac { 1 } { \sigma ^ { 2 } } \sum _ { i = 1 } ^ { n } \left( x _ { i } - \mu \right) } \\ { - \frac { n } { 2 \sigma ^ { 2 } } + \frac { 1 } { 2 \sigma ^ { 4 } } \sum _ { i = 1 } ^ { n } \left( x _ { i } - \mu \right) ^ { 2 } } \end{array} \right]
$$

To get the information matrix, calculate the matrix $\left[\begin{array}{l}{g_1} \\ {g_2} \end{array} \right] \left[ \begin{array}{l l}{g_1} & {g_2} \end{array} \right]$, and take the expected value. The result can be found in references [eg Lehman, p. 126] and is equal to $\left[ \begin{array} { c c } { \frac { n } { \sigma ^ { 2 } } } & { 0 } \\ { 0 } & { \frac { n } { 2 \sigma ^ { 4 } } } \end{array} \right]$.

The inverse of this matrix is the variance matrix for the two parameters. To estimate the variance of the ratio of the means of two independent normal samples, we start with a 4x4 block diagonal matrix.

$$
F = \left[ \begin{array} { c c c c } { \frac { n _ { 1 } } { \sigma _ { 1 } ^ { 2 } } } & { 0 } & { 0 } & { 0 } \\ { 0 } & { \frac { n _ { 1 } } { 2 \sigma _ { 1 } ^ { 2 } } } & { 0 } & { 0 } \\ { 0 } & { 0 } & { \frac { n _ { 2 } } { \sigma _ { 2 } ^ { 2 } } } & { 0 } \\ { 0 } & { 0 } & { 0 } & { \frac { n _ { 2 } } { 2 \sigma _ { 2 } ^ { 2 } } } \end{array} \right]
$$

We define the following transformations of the four parameters:

$$
\begin{array} { l } { \theta _ { 1 } \leftarrow h _ { 1 } \left( \mu _ { 1 } , \mu _ { 2 } , \sigma _ { 1 } ^ { 2 } , \sigma _ { 2 } ^ { 2 } \right) = \mu _ { 1 } } \\ { \theta _ { 2 } \leftarrow h _ { 2 } \left( \mu _ { 1 } , \mu _ { 2 } , \sigma _ { 1 } ^ { 2 } , \sigma _ { 2 } ^ { 2 } \right) = \sigma _ { 1 } ^ { 2 } } \\ { \theta _ { 3 } \leftarrow h _ { 3 } \left( \mu _ { 1 } , \mu _ { 2 } , \sigma _ { 1 } ^ { 2 } , \sigma _ { 2 } ^ { 2 } \right) = \frac { \mu _ { 2 } } { \mu _ { 1 } } } \\ { \theta _ { 4 } \leftarrow h _ { 4 } \left( \mu _ { 1 } , \mu _ { 2 } , \sigma _ { 1 } ^ { 2 } , \sigma _ { 2 } ^ { 2 } \right) = \sigma _ { 2 } ^ { 2 } } \end{array}
$$

The Jacobian of the transformation is given by the partial derivatives of the inverses of the above functions. For example, $h_1^{-1}(\theta_1) = \mu_1 = \sigma_1$ and $h_3^{-1}(\theta_1,\theta_3)=\theta_1 * \theta_3 = \mu_2$. Then

$$
J = \frac { \partial h ^ { - 1 } } { \partial \theta } = \left[ \begin{array} { c c c c } { 1 } & { 0 } & { 0 } & { 0 } \\ { 0 } & { 1 } & { 0 } & { 0 } \\ { \theta _ { 3 } } & { 0 } & { \theta _ { 1 } } & { 0 } \\ { 0 } & { 0 } & { 0 } & { 1 } \end{array} \right]
$$

The Fisher information matrix for the transformed parameters is given by $I=J^TFJ$ where $F$ is written in terms of the new parameters (Cox and Hinkley, page 130):

$$
I = \left[ \begin{array} { c c c c } { \frac { n _ { 1 } } { \theta _ { 2 } } + \frac { n _ { 2 } \theta _ { 3 } ^ { 2 } } { \theta _ { 4 } } } & { 0 } & { \frac { n _ { 2 } \theta _ { 3 } \theta _ { 1 } } { \theta _ { 4 } } } & { 0 } \\ { 0 } & { \frac { n _ { 1 } } { 2 \theta _ { 2 } ^ { 2 } } } & { 0 } & { 0 } \\ { \frac { n _ { 2 } \theta _ { 3 } \theta _ { 1 } } { \theta _ { 4 } } } & { 0 } & { \frac { n _ { 2 } } { \theta _ { 4 } } } & { 0 } \\ { 0 } & { 0 } & { 0 } & { \frac { n _ { 2 } } { 2 \theta _ { 4 } ^ { 2 } } } \end{array} \right]
$$

The inverse of this matrix gives the estimated variance of the maximum likelihood estimate of the transformed variables.

$$
I ^ { - 1 } = \left[ \begin{array} { c c c c } { \frac { \theta _ { 2 } } { n _ { 1 } } } & { 0 } & { \frac { - \theta _ { 3 } \theta _ { 2 } } { n _ { 1 } \theta _ { 1 } } } & { 0 } \\ { 0 } & { \frac { 2 \theta _ { 2 } ^ { 2 } } { n _ { 1 } } } & { 0 } & { 0 } \\ { \frac { - \theta _ { 3 } \theta _ { 2 } } { n _ { 1 } \theta _ { 1 } } } & { 0 } & { \frac { 1 } { \theta _ { 1 } ^ { 2 } } \left( \frac { \theta _ { 4 } } { n _ { 2 } } + \frac { \theta _ { 3 } ^ { 2 } \theta _ { 2 } } { n _ { 1 } } \right) } & { 0 } \\ { 0 } & { 0 } & { 0 } & { \frac { 2 \theta _ { 4 } ^ { 2 } } { n _ { 2 } } } \end{array} \right]
$$

Therefore the estimate of variance of the variance of $\theta_3$ is given by

$$
\frac { 1 } { \theta _ { 1 } ^ { 2 } } \left( \frac { \theta _ { 4 } } { n _ { 2 } } + \frac { \theta _ { 3 } ^ { 2 } \theta _ { 2 } } { n _ { 1 } } \right) = \frac { 1 } { \mu _ { 1 } ^ { 2 } } \left( \frac { \sigma _ { 2 } ^ { 2 } } { n _ { 2 } } + \frac { \mu _ { 2 } ^ { 2 } \sigma _ { 1 } ^ { 2 } } { n _ { 1 } \mu _ { 1 } ^ { 2 } } \right)
$$

To make use of this expression, four parameters (means and variances of normal distributions, for two treatment groups) have to be substituted with estimators. The use of maximum likelihood estimators (expressions given above) is appropriate. The approach is also expected to work if the variances are substituted with the "textbook" estimate mentioned above (the square of standard deviation as normally computed), which is an unbiased estimator regardless of normality. The current version of HAWC uses $s^2$, not the variance MLE.

This describes a standard error for a ratio of normal means (e.g., the treated group mean over the control mean). Biologists will frequently report the difference in means, as percentage of controls (a relative difference). The standard error for that will be the standard error just described (for a ratio of means), times 100 (accounting for conversion of the ratio to a percentage).

The formula is generally used with positive measurements. For example, inspection of the formula shows that the mean of the first sample cannot be "close" to zero. But "close" would be defined in terms of the corresponding standard deviation $\sigma_1$. If the standard deviation was large enough that the chance of negative values was appreciable given a normal distribution, probably the assumption of normality would be suspect, and a different approach should be used.

## References

1. Cox DR and Hinkley DV. (1974) Theoretical Statistics, Halsted Press, NY.
2. Lehmann EL. (1983) Theory of Point Estimation, Wiley Press, NY
