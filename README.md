# US Presidential Election Forecast

This repo contains code and analysis for forecasting 2020 US presidential election. 

### Methodology

Model inspired by this paper: http://www.stat.columbia.edu/~gelman/research/published/election15Feb.pdf
<br> and derives many functions from Joseph Richards' work: https://github.com/jwrichar/bayesian_election_forecasting

The model tries to estimate a posterior for statewise democratic-share based on past election results and polling data.

<br>

**Is polling fundamentally useful if done right?**<br>
Let's estimate the sampling variance of an average poll. In our data, we see that most polls are around 600-700 in size:

$SD = \sqrt {\dfrac {p_0(1-p_0)}{600}} = 0.02$

The small value of SD shows that variability due to sampling would be low enough to make the results informative. However, this assumes the polls were created by random sampling, which they are not.
<br><br>
For each state:

$p_0$: democratic share in the actual election. So if $p_0$ is more than 0.5 for a certain state, it means Democrats won that state <br>
$p_t$: the true proportion (in the given state) who intended to vote for the Democratic candidate, _t months_
before the election <br>
$\hat{p}_t$: denotes our estimate of $p_t$ from a preelection poll <br>
$p_{2016}$: democratic share of the given state in 2016 election

The goal is to estimate the posterior $p_0$ given $p_t$ and $p_{2016}$. We could also use older election results, but my model only used 2016.

** Assumptions **
 - $p_t$ has a normal distribution with mean $p_0$ and variance computed emiprically as a function of _months t_ before the election
 - $\hat{p}_t$ has a normal distribution with mean $p_t$ and variance a function of $p_t$ and $p_0$.<br>
 This assumes that CLT holds true for polling which is not the case. In practice $\hat{p}_t$ is an underestimate of survey error, given clustering, weighting, and other issues that depart from simple random sampling.
 
Our goal is to try and estimate $var(\hat{p_t}  | p_0)$<br><br>

$var(\hat{p_t} | p_0) = E (var(\hat{p_t} | p_t) | p_0) + var (E(\hat{p_t} | p_t) | p_0)$  ... law of total variance <br><br>
$= E(\dfrac{p_t(1-p_t)}{n} | p_0) + var (p_t | p_0)$      ... Assumes CLT on $\hat{p}_t$, which isn't true <br>

$= \dfrac{E(p_t| p_0)- E(p_t| p_0)^2)}{n} + var (p_t | p_0)$ <br>
$= \dfrac{p_0(1-p_0)}{n} + \dfrac{n-1}{n}var (p_t | p_0)$ <br>
$\sim \dfrac{p_0(1-p_0)}{n} + var (p_t | p_0)$ <br>

<br
This gives:<br>
Estimate of $$var(p_t | p_0) = var(\hat{p_t} | p_0) - \dfrac{p_0(1-p_0)}{n}$$

The first term is basically the variance of the polling data. Since we know p_0 for the last election and variance of polling data (for each month), we can compute the value of $var(p_t | p_0)$ as a function of t.

Empirically, $var(p_t | p_0)$ comes to be about $0:0002t$ using weighted least squares fitting (t is the number of months before election)

<br><br>
Final step: Posterior

$p_t|p_0 \sim N\Big( p_0,  \dfrac{p_0(1-p_0)}{n} + var (p_t | p_0) \Big)$

$p_0 | p_{2016} \sim N\Big( p_{2016}, var(p_0 | p_{2016})\Big)$

<br>
Now, 

$$var(p_t | p_0) \sim 0.0002t$$ <br>
$$var(p_0 | p_{2016})$$ can be estimated from historical elections  <br>
$$p_{2016}$$ is known  <br>

We use MCMC sampling to estimate the distribution of $p_0$ by using observed values of $p_t$ from polling data.
Please refer to the notebook for the implementation of this appraoch.
