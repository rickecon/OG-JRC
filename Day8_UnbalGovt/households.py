'''
------------------------------------------------------------------------
This module contains the functions that generate the variables
associated with households' optimization in the steady-state or in the
transition path of the overlapping generations model with S-period lived
agents and endogenous labor supply from Chapter 7 of the OG textbook.

This Python module imports the following module(s): None

This Python module defines the following function(s):
    get_cons()
    MU_c_stitch()
    MDU_n_stitch()
    get_n_s()
    get_n_errors()
    get_b_errors()
    bn_solve()
    FOC_savings()
    FOC_labor()
    get_cnb_vecs()
    c1_bSp1err()
------------------------------------------------------------------------
'''
# Import packages
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os

'''
------------------------------------------------------------------------
    Functions
------------------------------------------------------------------------
'''


def get_cons(r, w, b, b_sp1, n, x, tax_params):
    '''
    --------------------------------------------------------------------
    Calculate household consumption given prices, labor supply, current
    wealth, and savings
    --------------------------------------------------------------------
    INPUTS:
    r          = scalar or (p,) vector, current interest rate or time path of
                 interest rates over remaining life periods
    w          = scalar or (p,) vector, current wage or time path of wages
                 over remaining life periods
    b          = scalar or (p,) vector, current period wealth or time path of
                 current period wealths over remaining life periods
    b_sp1      = scalar or (p,) vector, savings for next period or time path
                 of savings for next period over remaining life periods
    n          = scalar or (p,) vector, current labor supply or time path of
                 labor supply over remaining life periods
    x          = scalar or (p,) vector, lump sum transfer to household
    tax_params = length 3 tuple, (tau_l, ta_k, tau_c)
    tau_l      = scalar, labor income tax rate
    tau_k      = scalar, capital income tax rate
    tau_c      = scalar, corporate income tax rate

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION: None

    OBJECTS CREATED WITHIN FUNCTION:
    cons = scalar or (p,) vector, current consumption or time path of
           consumption over remaining life periods

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: cons
    --------------------------------------------------------------------
    '''
    tau_l, tau_k, tau_c = tax_params
    cons = ((1 + r) * b) + (w * n) - b_sp1 + x - r*b*tau_k - w*n*tau_l

    return cons


def MU_c_stitch(cvec, sigma, graph=False):
    '''
    --------------------------------------------------------------------
    Generate marginal utility(ies) of consumption with CRRA consumption
    utility and stitched function at lower bound such that the new
    hybrid function is defined over all consumption on the real
    line but the function has similar properties to the Inada condition.

    u'(c) = c ** (-sigma) if c >= epsilon
          = g'(c) = 2 * b2 * c + b1 if c < epsilon

        such that g'(epsilon) = u'(epsilon)
        and g''(epsilon) = u''(epsilon)

        u(c) = (c ** (1 - sigma) - 1) / (1 - sigma)
        g(c) = b2 * (c ** 2) + b1 * c + b0
    --------------------------------------------------------------------
    INPUTS:
    cvec  = scalar or (p,) vector, individual consumption value or
            lifetime consumption over p consecutive periods
    sigma = scalar >= 1, coefficient of relative risk aversion for CRRA
            utility function: (c**(1-sigma) - 1) / (1 - sigma)
    graph = boolean, =True if want plot of stitched marginal utility of
            consumption function

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION: None

    OBJECTS CREATED WITHIN FUNCTION:
    epsilon    = scalar > 0, positive value close to zero
    c_s        = scalar, individual consumption
    c_s_cnstr  = boolean, =True if c_s < epsilon
    b1         = scalar, intercept value in linear marginal utility
    b2         = scalar, slope coefficient in linear marginal utility
    MU_c       = scalar or (p,) vector, marginal utility of consumption
                 or vector of marginal utilities of consumption
    p          = integer >= 1, number of periods remaining in lifetime
    cvec_cnstr = (p,) boolean vector, =True for values of cvec < epsilon

    FILES CREATED BY THIS FUNCTION:
        MU_c_stitched.png

    RETURNS: MU_c
    --------------------------------------------------------------------
    '''
    epsilon = 0.0001
    if np.ndim(cvec) == 0:
        c_s = cvec
        c_s_cnstr = c_s < epsilon
        if c_s_cnstr:
            b2 = (-sigma * (epsilon ** (-sigma - 1))) / 2
            b1 = (epsilon ** (-sigma)) - 2 * b2 * epsilon
            MU_c = 2 * b2 * c_s + b1
        else:
            MU_c = c_s ** (-sigma)
    elif np.ndim(cvec) == 1:
        p = cvec.shape[0]
        cvec_cnstr = cvec < epsilon
        MU_c = np.zeros(p)
        MU_c[~cvec_cnstr] = cvec[~cvec_cnstr] ** (-sigma)
        b2 = (-sigma * (epsilon ** (-sigma - 1))) / 2
        b1 = (epsilon ** (-sigma)) - 2 * b2 * epsilon
        MU_c[cvec_cnstr] = 2 * b2 * cvec[cvec_cnstr] + b1

    if graph:
        '''
        ----------------------------------------------------------------
        cur_path    = string, path name of current directory
        output_fldr = string, folder in current path to save files
        output_dir  = string, total path of images folder
        output_path = string, path of file name of figure to be saved
        cvec_CRRA   = (1000,) vector, support of c including values
                      between 0 and epsilon
        MU_CRRA     = (1000,) vector, CRRA marginal utility of
                      consumption
        cvec_stitch = (500,) vector, stitched support of consumption
                      including negative values up to epsilon
        MU_stitch   = (500,) vector, stitched marginal utility of
                      consumption
        ----------------------------------------------------------------
        '''
        # Create directory if images directory does not already exist
        cur_path = os.path.split(os.path.abspath(__file__))[0]
        output_fldr = "images"
        output_dir = os.path.join(cur_path, output_fldr)
        if not os.access(output_dir, os.F_OK):
            os.makedirs(output_dir)

        # Plot steady-state consumption and savings distributions
        cvec_CRRA = np.linspace(epsilon / 2, epsilon * 3, 1000)
        MU_CRRA = cvec_CRRA ** (-sigma)
        cvec_stitch = np.linspace(-0.00005, epsilon, 500)
        MU_stitch = 2 * b2 * cvec_stitch + b1
        fig, ax = plt.subplots()
        plt.plot(cvec_CRRA, MU_CRRA, ls='solid', label='$u\'(c)$: CRRA')
        plt.plot(cvec_stitch, MU_stitch, ls='dashed', color='red',
                 label='$g\'(c)$: stitched')
        # for the minor ticks, use no labels; default NullFormatter
        minorLocator = MultipleLocator(1)
        ax.xaxis.set_minor_locator(minorLocator)
        plt.grid(b=True, which='major', color='0.65', linestyle='-')
        plt.title('Marginal utility of consumption with stitched ' +
                  'function', fontsize=14)
        plt.xlabel(r'Consumption $c$')
        plt.ylabel(r'Marginal utility $u\'(c)$')
        plt.xlim((-0.00005, epsilon * 3))
        # plt.ylim((-1.0, 1.15 * (b_ss.max())))
        plt.legend(loc='upper right')
        output_path = os.path.join(output_dir, "MU_c_stitched")
        plt.savefig(output_path)
        # plt.show()

    return MU_c


def MDU_n_stitch(nvec, params, graph=False):
    '''
    --------------------------------------------------------------------
    Generate marginal disutility(ies) of labor with elliptical
    disutility of labor function and stitched functions at lower bound
    and upper bound of labor supply such that the new hybrid function is
    defined over all labor supply on the real line but the function has
    similar properties to the Inada conditions at the upper and lower
    bounds.

    v'(n) = (b / l_tilde) * ((n / l_tilde) ** (upsilon - 1)) *
            ((1 - ((n / l_tilde) ** upsilon)) ** ((1-upsilon)/upsilon))
            if n >= eps_low <= n <= eps_high
          = g_low'(n)  = 2 * b2 * n + b1 if n < eps_low
          = g_high'(n) = 2 * d2 * n + d1 if n > eps_high

        such that g_low'(eps_low) = u'(eps_low)
        and g_low''(eps_low) = u''(eps_low)
        and g_high'(eps_high) = u'(eps_high)
        and g_high''(eps_high) = u''(eps_high)

        v(n) = -b *(1 - ((n/l_tilde) ** upsilon)) ** (1/upsilon)
        g_low(n)  = b2 * (n ** 2) + b1 * n + b0
        g_high(n) = d2 * (n ** 2) + d1 * n + d0
    --------------------------------------------------------------------
    INPUTS:
    nvec   = scalar or (p,) vector, labor supply value or labor supply
             values over remaining periods of lifetime
    params = length 3 tuple, (l_tilde, b_ellip, upsilon)
    graph  = Boolean, =True if want plot of stitched marginal disutility
             of labor function

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION: None

    OBJECTS CREATED WITHIN FUNCTION:
    l_tilde       = scalar > 0, time endowment for each agent each per
    b_ellip       = scalar > 0, scale parameter for elliptical utility
                    of leisure function
    upsilon       = scalar > 1, shape parameter for elliptical utility
                    of leisure function
    eps_low       = scalar > 0, positive value close to zero
    eps_high      = scalar > 0, positive value just less than l_tilde
    n_s           = scalar, individual labor supply
    n_s_low       = boolean, =True for n_s < eps_low
    n_s_high      = boolean, =True for n_s > eps_high
    n_s_uncstr    = boolean, =True for n_s >= eps_low and
                    n_s <= eps_high
    MDU_n         = scalar or (p,) vector, marginal disutility or
                    marginal utilities of labor supply
    b1            = scalar, intercept value in linear marginal
                    disutility of labor at lower bound
    b2            = scalar, slope coefficient in linear marginal
                    disutility of labor at lower bound
    d1            = scalar, intercept value in linear marginal
                    disutility of labor at upper bound
    d2            = scalar, slope coefficient in linear marginal
                    disutility of labor at upper bound
    p             = integer >= 1, number of periods remaining in life
    nvec_s_low    = boolean, =True for n_s < eps_low
    nvec_s_high   = boolean, =True for n_s > eps_high
    nvec_s_uncstr = boolean, =True for n_s >= eps_low and
                    n_s <= eps_high

    FILES CREATED BY THIS FUNCTION:
        MDU_n_stitched.png

    RETURNS: MDU_n
    --------------------------------------------------------------------
    '''
    l_tilde, b_ellip, upsilon = params
    eps_low = 0.000001
    eps_high = l_tilde - 0.000001
    # This if is for when nvec is a scalar
    if np.ndim(nvec) == 0:
        n_s = nvec
        n_s_low = n_s < eps_low
        n_s_high = n_s > eps_high
        n_s_uncstr = (n_s >= eps_low) and (n_s <= eps_high)
        if n_s_uncstr:
            MDU_n = \
                ((b_ellip / l_tilde) * ((n_s / l_tilde) **
                 (upsilon - 1)) * ((1 - ((n_s / l_tilde) ** upsilon)) **
                 ((1 - upsilon) / upsilon)))
        elif n_s_low:
            b2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) *
                  (upsilon - 1) * (eps_low ** (upsilon - 2)) *
                  ((1 - ((eps_low / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) *
                  (1 + ((eps_low / l_tilde) ** upsilon) *
                  ((1 - ((eps_low / l_tilde) ** upsilon)) ** (-1))))
            b1 = ((b_ellip / l_tilde) * ((eps_low / l_tilde) **
                  (upsilon - 1)) *
                  ((1 - ((eps_low / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) - (2 * b2 * eps_low))
            MDU_n = 2 * b2 * n_s + b1
        elif n_s_high:
            d2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) *
                  (upsilon - 1) * (eps_high ** (upsilon - 2)) *
                  ((1 - ((eps_high / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) *
                  (1 + ((eps_high / l_tilde) ** upsilon) *
                  ((1 - ((eps_high / l_tilde) ** upsilon)) ** (-1))))
            d1 = ((b_ellip / l_tilde) * ((eps_high / l_tilde) **
                  (upsilon - 1)) *
                  ((1 - ((eps_high / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) - (2 * d2 * eps_high))
            MDU_n = 2 * d2 * n_s + d1
    # This if is for when nvec is a one-dimensional vector
    elif np.ndim(nvec) == 1:
        p = nvec.shape[0]
        nvec_low = nvec < eps_low
        nvec_high = nvec > eps_high
        nvec_uncstr = np.logical_and(~nvec_low, ~nvec_high)
        MDU_n = np.zeros(p)
        MDU_n[nvec_uncstr] = (
            (b_ellip / l_tilde) *
            ((nvec[nvec_uncstr] / l_tilde) ** (upsilon - 1)) *
            ((1 - ((nvec[nvec_uncstr] / l_tilde) ** upsilon)) **
             ((1 - upsilon) / upsilon)))
        b2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) * (upsilon - 1) *
              (eps_low ** (upsilon - 2)) *
              ((1 - ((eps_low / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) *
              (1 + ((eps_low / l_tilde) ** upsilon) *
              ((1 - ((eps_low / l_tilde) ** upsilon)) ** (-1))))
        b1 = ((b_ellip / l_tilde) * ((eps_low / l_tilde) **
              (upsilon - 1)) *
              ((1 - ((eps_low / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) - (2 * b2 * eps_low))
        MDU_n[nvec_low] = 2 * b2 * nvec[nvec_low] + b1
        d2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) * (upsilon - 1) *
              (eps_high ** (upsilon - 2)) *
              ((1 - ((eps_high / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) *
              (1 + ((eps_high / l_tilde) ** upsilon) *
              ((1 - ((eps_high / l_tilde) ** upsilon)) ** (-1))))
        d1 = ((b_ellip / l_tilde) * ((eps_high / l_tilde) **
              (upsilon - 1)) *
              ((1 - ((eps_high / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) - (2 * d2 * eps_high))
        MDU_n[nvec_high] = 2 * d2 * nvec[nvec_high] + d1

    if graph:
        '''
        ----------------------------------------------------------------
        cur_path    = string, path name of current directory
        output_fldr = string, folder in current path to save files
        output_dir  = string, total path of images folder
        output_path = string, path of file name of figure to be saved
        nvec_ellip  = (1000,) vector, support of n including values
                      between 0 and eps_low and between eps_high and
                      l_tilde
        MU_CRRA     = (1000,) vector, CRRA marginal utility of
                      consumption
        cvec_stitch = (500,) vector, stitched support of consumption
                      including negative values up to epsilon
        MU_stitch   = (500,) vector, stitched marginal utility of
                      consumption
        ----------------------------------------------------------------
        '''
        # Create directory if images directory does not already exist
        cur_path = os.path.split(os.path.abspath(__file__))[0]
        output_fldr = "images"
        output_dir = os.path.join(cur_path, output_fldr)
        if not os.access(output_dir, os.F_OK):
            os.makedirs(output_dir)

        # Plot steady-state consumption and savings distributions
        nvec_ellip = np.linspace(eps_low / 2, eps_high +
                                 ((l_tilde - eps_high) / 5), 1000)
        MDU_ellip = (
            (b_ellip / l_tilde) *
            ((nvec_ellip / l_tilde) ** (upsilon - 1)) *
            ((1 - ((nvec_ellip / l_tilde) ** upsilon)) **
             ((1 - upsilon) / upsilon)))
        n_stitch_low = np.linspace(-0.05, eps_low, 500)
        MDU_stitch_low = 2 * b2 * n_stitch_low + b1
        n_stitch_high = np.linspace(eps_high, l_tilde + 0.000005, 500)
        MDU_stitch_high = 2 * d2 * n_stitch_high + d1
        fig, ax = plt.subplots()
        plt.plot(nvec_ellip, MDU_ellip, ls='solid', color='black',
                 label='$v\'(n)$: Elliptical')
        plt.plot(n_stitch_low, MDU_stitch_low, ls='dashed', color='red',
                 label='$g\'(n)$: low stitched')
        plt.plot(n_stitch_high, MDU_stitch_high, ls='dotted',
                 color='blue', label='$g\'(n)$: high stitched')
        # for the minor ticks, use no labels; default NullFormatter
        minorLocator = MultipleLocator(1)
        ax.xaxis.set_minor_locator(minorLocator)
        plt.grid(b=True, which='major', color='0.65', linestyle='-')
        plt.title('Marginal utility of consumption with stitched ' +
                  'function', fontsize=14)
        plt.xlabel(r'Labor $n$')
        plt.ylabel(r'Marginal disutility $v\'(n)$')
        plt.xlim((-0.05, l_tilde + 0.01))
        # plt.ylim((-1.0, 1.15 * (b_ss.max())))
        plt.legend(loc='upper left')
        output_path = os.path.join(output_dir, "MDU_n_stitched")
        plt.savefig(output_path)
        # plt.show()

    return MDU_n



def get_n_errors(nvec, args):
    '''
    --------------------------------------------------------------------
    Generates vector of static Euler errors that characterize the
    optimal lifetime labor supply decision. Because this function is
    used for solving for lifetime decisions in both the steady-state and
    in the transition path, lifetimes will be of varying length.
    Lifetimes in the steady-state will be S periods. Lifetimes in the
    transition path will be p in [2, S] periods
    --------------------------------------------------------------------
    INPUTS:
    params    = length 6 tuple,
                (sigma, l_tilde, chi_n_vec, b_ellip, upsilon)
    sigma     = scalar > 0, coefficient of relative risk aversion
    l_tilde   = scalar > 0, time endowment of each agent in each period
    chi_n_vec = (p,) vector, values for chi^n_p
    b_ellip   = scalar > 0, fitted value of b for elliptical disutility
                of labor
    upsilon   = scalar > 1, fitted value of upsilon for elliptical
                disutility of labor
    tau_l     = scalar, labor income tax rate
    w         = scalar > 0 or (p,) vector, steady-state wage or time
                path of wage
    cvec      = (p,) vector, distribution of consumption by age c_p
    nvec      = (p,) vector, distribution of labor supply by age n_p
    n_low     = (p,) Boolean vector, =True if n_p<=0 for given nvec
    n_high    = (p,) Boolean vector, =True if n_p>=l_tilde for given
                nvec
    diff      = Boolean, =True if use simple difference Euler errors.
                Use percent difference errors otherwise.

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        MU_c_stitch()
        MDU_n_stitch()

    OBJECTS CREATED WITHIN FUNCTION:
    mu_c     = (p,) vector, marginal utility of consumption
    mu_n     = (p,) vector, marginal utility of labor supply
    n_errors = (p,) vector, Euler errors characterizing optimal labor
               supply nvec

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: n_errors
    --------------------------------------------------------------------
    '''
    w, cvec, sigma, l_tilde, chi_n_vec, b_ellip, upsilon, tau_l, diff = args
    mu_c = MU_c_stitch(cvec, sigma)
    mdun_params = (l_tilde, b_ellip, upsilon)
    mdu_n = MDU_n_stitch(nvec, mdun_params)
    if diff:
        n_errors = ((1-tau_l)*w * mu_c) - chi_n_vec * mdu_n
    else:
        n_errors = (((1-tau_l)*w * mu_c) / (chi_n_vec * mdu_n)) - 1

    return n_errors


def get_b_errors(params, r, cvec, diff):
    '''
    --------------------------------------------------------------------
    Generates vector of dynamic Euler errors that characterize the
    optimal lifetime savings decision. Because this function is used for
    solving for lifetime decisions in both the steady-state and in the
    transition path, lifetimes will be of varying length. Lifetimes in
    the steady-state will be S periods. Lifetimes in the transition path
    will be p in [2, S] periods
    --------------------------------------------------------------------
    INPUTS:
    params  = length 3 tuple, (beta, sigma, tau_k)
    beta    = scalar in (0,1), discount factor
    sigma   = scalar > 0, coefficient of relative risk aversion
    tau_k   = scalar, capital income tax rate
    r       = scalar > 0 or (p,) vector, steady-state interest rate or
              time path of interest rates
    cvec    = (p,) vector, distribution of consumption by age c_p
    diff    = boolean, =True if use simple difference Euler
              errors. Use percent difference errors otherwise.

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        MU_c_stitch()

    OBJECTS CREATED WITHIN FUNCTION:
    mu_c     = (p-1,) vector, marginal utility of current consumption
    mu_cp1   = (p-1,) vector, marginal utility of next period consumpt'n
    b_errors = (p-1,) vector, Euler errors characterizing optimal
               savings bvec

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: b_errors
    --------------------------------------------------------------------
    '''
    beta, sigma, tau_k = params
    mu_c = MU_c_stitch(cvec[:-1], sigma)
    mu_cp1 = MU_c_stitch(cvec[1:], sigma)
    if diff:
        b_errors = (beta * (1 + (1-tau_k)*r) * mu_cp1) - mu_c
    else:
        b_errors = ((beta * (1 + (1-tau_k)*r) * mu_cp1) / mu_c) - 1

    return b_errors


def bn_solve(guesses, *args):
    '''
    --------------------------------------------------------------------
    Finds the euler errors for certain b and n, one ability type at a time.
    --------------------------------------------------------------------
    INPUTS:
    guesses = (2S-1,) vector, initial guesses for b and n
    params  = length 12 tuple, r, w, x, S, beta, sigma, l_tilde, b_ellip,
              upsilon, chi_n_vec, tax_params , diff

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        FOC_savings()
        FOC_labor()

    OBJECTS CREATED WITHIN FUNCTION:
    r         = scalar, real interest rate
    w         = scalar, real wage rate
    S         = integer in [3, 80], number of periods an individual
                lives
    beta      = scalar in (0,1), discount factor for each model per
    sigma     = scalar > 0, coefficient of relative risk aversion
    l_tilde   = scalar > 0, time endowment for each agent each period
    b_ellip   = scalar > 0, fitted value of b for elliptical
                disutility of labor
    upsilon   = scalar > 1, fitted value of upsilon for elliptical
                disutility of labor
    chi_n_vec = (S,) vector, values for chi^n_s
    diff      = boolean, =True if use simple difference Euler
                errors. Use percent difference errors otherwise.


    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        FOC_savings()
        FOC_labor()

    OBJECTS CREATED WITHIN FUNCTION:
    b_guess   = (S,) vector, initial guess at household savings
    n_guess   = (S,) vector, initial guess at household labor supply
    b_s       = (S,) vector, wealth enter period with
    b_splus1  = (S,) vector, household savings
    b_params  = length 6 tuple, parameters passed to FOC_savings()
    error1    = (S,) vector, errors from FOC for savings
    n_params  = length 9 tuple, parameters passt to FOC_labor()
    error2    = (S,) vector, errors from FOC for labor supply

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: 2S-1 length list of error1 and error2
    --------------------------------------------------------------------
    '''
    (r, w, x, S, beta, sigma, l_tilde, b_ellip, upsilon, chi_n_vec,
        tax_params, diff) = args
    tau_l, tau_k, tau_c = tax_params
    b_guess = np.append(np.array(guesses[:S - 1]), 0.0)
    n_guess = np.array(guesses[S - 1:])
    b_s = np.array([0] + list(b_guess[:-1]))
    b_splus1 = b_guess

    cons = get_cons(r, w, b_s, b_splus1, n_guess, x, tax_params)
    b_params = (beta, sigma, tau_k)
    error1 = get_b_errors(b_params, r, cons, diff)

    n_args = (w, cons, sigma, l_tilde, chi_n_vec, b_ellip, upsilon, tau_l, diff)
    error2 = get_n_errors(n_guess, n_args)

    return list(error1.flatten()) + list(error2.flatten())





def get_cnb_vecs(c_init, rpath, wpath, xpath, params):
    '''
    --------------------------------------------------------------------
    Generate lifetime consumption vector for individual given a guess
    for initial consumption c_{S-p+1}, initial wealth b_{S-p+1}, a path
    for interest rates, wages, and parameters beta and sigma using
    household first order equations

    c_{s+1,t+1} = c_{s,t} * ([beta * (1 + r_{t+1})] ** (1 / sigma))

    w_t * (c_{s,t} ** (-sigma)) = chi_n_s * g'(n_{s,t})
    --------------------------------------------------------------------
    INPUTS:
    c_init = scalar > 0, consumption in initial period of lifetime c_{S-p+1}
    rpath  = (p,) vector, path of interest rates over lifetime
    wpath  = (p,) vector, path of wages over lifetime
    xpath  = (p,) vector, path of transfers over lifetime
    params = length 8 tuple, (b_init, beta, sigma, l_tilde, b_ellip,
             upsilon, chi_n_vec, diff)

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        get_n_s()

    OBJECTS CREATED WITHIN FUNCTION:
    b_init    = scalar, initial wealth b_{S-p+1}
    beta      = scalar in (0, 1), discount factor
    sigma     = scalar >= 1, coefficient of relative risk aversion
    b_ellip   = scalar > 0, fitted value of b for elliptical disutility
                of labor
    l_tilde   = scalar > 0, per-period time endowment for every agent
    upsilon   = scalar > 1, fitted value of upsilon for elliptical
                disutility of labor
    chi_n_vec = (p,) vector, values for chi^n_s over remaining lifetime
    diff      = boolean, =True if simple difference Euler error,
                otherwise percent deviation Euler error
    p         = integer >= 1, number of periods remaining in a
                household's life
    cvec      = (p,) vector, household lifetime consumption given c1
    nvec      = (p,) vector, household lifetime labor supply given c1
    bvec      = (p,) vector, household lifetime savings given c_{S-p+1}
                and b_{S-p+1} where b1=0
    per       = integer >= 1, index of period number
    n_args    = length 8 tuple, (c_s, w_t, sigma, l_tilde, chi_n_s,
                b_ellip, upsilon, diff)
    n_options = length 1 dict, options for opt.root(get_n_s,...)
    result_n  = results object, solution from opt.root(get_n_s,...)
    b_Sp1     = scalar, savings after the last period of life. Should be
                zero in equilibrium

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: cvec, nvec, bvec, b_Sp1
    --------------------------------------------------------------------
    '''
    (b_init, beta, sigma, l_tilde, b_ellip, upsilon, chi_n_vec, tax_params,
        diff) = params
    tau_l, tau_k, tau_c = tax_params
    p = rpath.shape[0]
    cvec = np.zeros(p)
    nvec = np.zeros(p)
    bvec = np.zeros(p)
    for per in range(p):
        if per == 0:
            bvec[per] = b_init
            cvec[per] = c_init
        else:
            bvec[per] = ((1 + rpath[per - 1]) * bvec[per - 1] +
                         wpath[per - 1] * nvec[per - 1] - cvec[per - 1]
                         + xpath[per-1]
                         - tau_k*rpath[per - 1]*bvec[per - 1]
                         - tau_l*wpath[per-1]*nvec[per-1])
            cvec[per] = cvec[per - 1] * ((beta * (1 + (1-tau_k)*rpath[per])) **
                                         (1 / sigma))
        n_options = {'maxiter': 500}
        n_args = [wpath[per], cvec[per], sigma, l_tilde, chi_n_vec[per],
                  b_ellip, upsilon, tau_l, diff]
        result_n = \
            opt.root(get_n_errors, l_tilde / 2, args=(n_args),
                     method='lm', tol=1e-14, options=(n_options))

        nvec[per] = result_n.x


    b_Sp1 = ((1 + rpath[-1]) * bvec[-1] + wpath[-1] * nvec[-1] - cvec[-1]
             + xpath[per-1] - tau_k*rpath[-1]*bvec[-1]
             - tau_l*wpath[-1]*nvec[-1])

    return cvec, nvec, bvec, b_Sp1


def c1_bSp1err(c_init, *args):
    '''
    --------------------------------------------------------------------
    Given value for c1, as well as w and r, solve for household
    lifetime decisions c_{s,t}, n_{s,t}, and b_{s+1,t+1}, and return
    implied savings for period after last period of life b_{S+1}. This
    savings amount b_{S+1} should be zero in equilibrium.
    --------------------------------------------------------------------
    INPUTS:
    c_init = scalar > 0, assumed initial period consumption for
             individual
    args   = length 10 tuple, (b_init, beta, sigma, l_tilde, b_ellip,
             upsilon, chi_n_vec, rpath, wpath, diff)

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        get_cnb_vecs()

    OBJECTS CREATED WITHIN FUNCTION:
    beta      = scalar in (0, 1), discount factor
    sigma     = scalar >= 1, coefficient of relative risk aversion
    b_ellip   = scalar > 0, fitted value of b for elliptical disutility
                of labor
    l_tilde   = scalar > 0, per-period time endowment for every agent
    upsilon   = scalar > 1, fitted value of upsilon for elliptical
                disutility of labor
    chi_n_vec = (p,) vector, values for chi^n_s for remaining lifetime
    rpath     = (p,) vector, path of interest rates over remaining life
    wpath     = (p,) vector, path of wages over remaining lifetime
    diff      = boolean, =True if simple difference Euler errors,
                otherwise percent deviation Euler errors
    cnb_args  = length 8 tuple, args to pass into get_cnb_vecs()
    cvec      = (p,) vector, household lifetime consumption given c1
    nvec      = (p,) vector, household lifetime labor supply given c1
    bvec      = (p,) vector, household lifetime savings given c1
                (b_{S-p+1}, b_{S-p+2}, ...bS) where b1=0
    b_Sp1     = scalar, residual amount left for individual savings in
                period after last period of life based on c_{S-p+1},
                Euler equations, and budget constraints. b_Sp1 should be
                zero in equilibrium

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: b_Sp1
    --------------------------------------------------------------------
    '''
    (b_init, beta, sigma, l_tilde, b_ellip, upsilon, chi_n_vec, tax_params,
        xpath, rpath, wpath, diff) = args
    cnb_args = (b_init, beta, sigma, l_tilde, b_ellip, upsilon,
                chi_n_vec, tax_params, diff)
    cvec, nvec, bvec, b_Sp1 = get_cnb_vecs(c_init, rpath, wpath, xpath,
                                           cnb_args)

    return b_Sp1
