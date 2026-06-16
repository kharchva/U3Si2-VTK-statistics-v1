import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import io
import zipfile
from scipy.optimize import curve_fit
from scipy import stats
from scipy.optimize import least_squares


plt.rcParams.update({
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'axes.titlesize': 16,
    'legend.fontsize': 12
})


def MR_distrib(x, c0, a, xc):
    term1 = c0 * x**a
    term2 = np.exp(
        -3 * xc**4 / ((xc**3 + 3) * (xc - x))
    )
    power1 = 2 + 3 * xc * (xc**3 + 6) / (xc**3 + 3)**2
    term3 = (xc - x)**power1
    power2 = 1 + 27 / (xc**3 + 3)**2
    term4 = (x + 3 / xc**2)**power2
    return term1 * term2 / (term3 * term4)


def residuals(params, x, y):
    c0, a, xc = params
    y_model = MR_distrib(x, c0, a, xc)
    return y_model - y


def LSW_distrib(x):
    return (
        (4/9) * x * x
        * (3 / (3 + x))**(7/3)
        * (1.5 / (1.5 - x))**(11/3)
        * np.exp(x / (x - 1.5))
    )


def gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))


def lognormal(x, A, shape, scale):
    return A * stats.lognorm.pdf(x, shape, scale=scale)


def calc_distribution_from_data(data, fname, nbins, type, area_cm3):
    if type == "dist":
        counts, bin_edges = np.histogram(data, bins=nbins, density=True)
        y = counts
    else:
        counts, bin_edges = np.histogram(data, bins=nbins, density=False)
        y = counts / area_cm3
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]
    x = bin_centers
    # y = counts
    # x_ax = np.linspace(data.min(), data.max(), 200)
    x_ax = np.linspace(0, data.max(), 200)

    if nbins > 2:
        try:
            p0 = [max(y), np.mean(x), np.std(x)]
            params_gauss, _ = curve_fit(gaussian, x, y, p0=p0)
            A_gauss, mu_gauss, sigma_gauss = params_gauss
            y_gauss_fit = gaussian(x, A_gauss, mu_gauss, sigma_gauss)
            # --- R^2 для Gaussian ---
            ss_res_gauss = np.sum((y - y_gauss_fit) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2_gauss = 1 - ss_res_gauss / ss_tot
            y_gauss_fit = gaussian(x_ax, A_gauss, mu_gauss, sigma_gauss)
            # ax_h.plot(x_ax, y_gauss_fit, 'r-', lw=2, label=f'Gaussian fit, R²={r2_gauss:.4f}')
            gauss_fit_ok = True
        except RuntimeError:
            # st.warning("Gaussian fit не зійшовся.")
            gauss_fit_ok = False
            y_gauss_fit = np.zeros_like(x_ax)
            r2_gauss = 0

        try:
            p0_ln = [max(y), 0.5, np.mean(x)]
            params_ln, _ = curve_fit(lognormal, x, y, p0=p0_ln)
            A_ln, shape_ln, scale_ln = params_ln
            y_ln_fit = lognormal(x, A_ln, shape_ln, scale_ln)
            # --- R^2 для Log-normal ---
            ss_res_ln = np.sum((y - y_ln_fit) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2_ln = 1 - ss_res_ln / ss_tot
            y_ln_fit = lognormal(x_ax, A_ln, shape_ln, scale_ln)
            # ax_h.plot(x_ax, y_ln_fit, 'b-', lw=2, label=f'Log-normal fit, R²={r2_ln:.4f}')
            ln_fit_ok = True
        except RuntimeError:
            # st.warning("Log-Normal fit не зійшовся.")
            ln_fit_ok = False
            y_ln_fit = np.zeros_like(x_ax)
            r2_ln = 0

###################################################################
        MR_fit_ok = False
        y_MR_fit = np.zeros_like(x_ax)
        r2_MR = 0
        if fname == "size_bubbles_mean_dist" or fname == "size_grains_mean_dist":
            try:
                p0 = [300.0, 1.0, max(x) * 1.1]  # початкові оцінки
                params_MR, _ = curve_fit(MR_distrib,
                                         x, y,
                                         p0=p0,
                                         bounds=(
                        [0, -np.inf, max(x)],  # xc > max(x)
                        [np.inf, np.inf, np.inf]
                    ),
                    maxfev=100000)
                c0_fit, a_fit, xc_fit = params_MR

                # x0 = [
                #     300.0,  # c0
                #     1.0,  # a
                #     max(x) * 1.5  # xc (ВАЖЛИВО: трохи правіше за дані)
                # ]
                #
                # result = least_squares(
                #     residuals,
                #     x0,
                #     args=(x, y),
                #     max_nfev=20000
                # )
                #
                # c0_fit, a_fit, xc_fit = result.x

                y_MR_fit = MR_distrib(x, c0_fit, a_fit, xc_fit)
                # --- R^2 для MR ---
                ss_res_MR = np.sum((y - y_MR_fit) ** 2)
                ss_tot = np.sum((y - np.mean(y)) ** 2)
                r2_MR = 1 - ss_res_MR / ss_tot
                y_MR_fit = MR_distrib(x_ax, c0_fit, a_fit, xc_fit)
                MR_fit_ok = True
            except RuntimeError:
                # st.warning("Log-Normal fit не зійшовся.")
                MR_fit_ok = False
                y_MR_fit = np.zeros_like(x_ax)
                r2_MR = 0
###################################################################

    else:
        gauss_fit_ok = False
        y_gauss_fit = np.zeros_like(x_ax)
        r2_gauss = 0
        ln_fit_ok = False
        y_ln_fit = np.zeros_like(x_ax)
        r2_ln = 0
        MR_fit_ok = False
        y_MR_fit = np.zeros_like(x_ax)
        r2_MR = 0

###################################################################
    x_axLSW = np.linspace(0, 1.499, 200)
    if fname == "size_bubbles_mean_dist" or fname == "size_grains_mean_dist":
        # y_LSW_fit = LSW_distrib(x)
        # # --- R^2 для LSW ---
        # ss_res_LSW = np.sum((y - y_LSW_fit) ** 2)
        # ss_tot = np.sum((y - np.mean(y)) ** 2)
        # r2_LSW = 1 - ss_res_LSW / ss_tot
        y_LSW_fit = LSW_distrib(x_axLSW)
        LSW_fit_ok = True
    else:
        LSW_fit_ok = False
        y_LSW_fit = np.zeros_like(x_axLSW)
        # r2_LSW = 0

###################################################################

    datasets = {
        f"data_{fname}.txt": [(i, val) for i, val in enumerate(data)],
        f"histogram_{fname}.txt": list(zip(x, y)),
        f"gaussian_fit_{fname}.txt": list(zip(x_ax, y_gauss_fit)),
        f"lognormal_fit_{fname}.txt": list(zip(x_ax, y_ln_fit))
        # f"MR_fit_{fname}.txt": list(zip(x_ax, y_MR_fit)),
        # f"LSW_distribution_{fname}.txt": list(zip(x_ax, y_LSW_fit)),
    }
    if fname == "size_bubbles_mean_dist" or fname == "size_grains_mean_dist":
        datasets[f"MR_fit_{fname}.txt"] = list(zip(x_ax, y_MR_fit))
        datasets[f"LSW_distribution_{fname}.txt"] = list(zip(x_axLSW, y_LSW_fit))

    dict4return = {
        "x": x,
        "y": y,
        "x_ax": x_ax,
        "gauss_fit_ok": gauss_fit_ok,
        "y_gauss_fit": y_gauss_fit,
        "r2_gauss": r2_gauss,
        "ln_fit_ok": ln_fit_ok,
        "y_ln_fit": y_ln_fit,
        "r2_ln": r2_ln,
        "MR_fit_ok": MR_fit_ok,
        "y_MR_fit": y_MR_fit,
        "r2_MR": r2_MR,
        "LSW_fit_ok": LSW_fit_ok,
        "y_LSW_fit": y_LSW_fit,
        # "r2_LSW": r2_LSW,
        "bin_width": bin_width,
        # "datasets": datasets,
        "mean": data.mean(),
        # "fname": fname,
        "data": data,
        "type": type
                   }
    return dict4return, datasets

#
# @st.cache_data(
#     show_spinner=False,
#     hash_funcs={np.ndarray: lambda x: x.tobytes()}
# )
# def make_figure_distribution_png(dict_with_data, colorbins, xlabel, ylabel,
#                                     show_gaus, show_logn, show_MR, show_LSW, show_mean, mean,
#                                  min_x=None, max_x=None):
#     x = dict_with_data["x"]
#     y = dict_with_data["y"]
#     x_ax = dict_with_data["x_ax"]
#     gauss_fit_ok = dict_with_data["gauss_fit_ok"]
#     y_gs = dict_with_data["y_gauss_fit"]
#     r2gs = dict_with_data["r2_gauss"]
#     ln_fit_ok = dict_with_data["ln_fit_ok"]
#     y_ln = dict_with_data["y_ln_fit"]
#     r2ln = dict_with_data["r2_ln"]
#
#     MR_fit_ok = dict_with_data["MR_fit_ok"]
#     y_MR = dict_with_data["y_MR_fit"]
#     r2MR = dict_with_data["r2_MR"]
#
#     LSW_fit_ok = dict_with_data["LSW_fit_ok"]
#     y_LSW = dict_with_data["y_LSW_fit"]
#     r2LSW = dict_with_data["r2_LSW"]
#
#     bin_width = dict_with_data["bin_width"]
#
#     fig_fit, ax_fit = plt.subplots(figsize=(10, 5))
#     ax_fit.bar(x, y, width=bin_width * 0.8, color=colorbins, edgecolor='black', alpha=0.5, label="Data")
#     if gauss_fit_ok and show_gaus:
#         ax_fit.plot(x_ax, y_gs, 'r-', lw=2, label=f'Gaussian fit, R²={r2gs:.4f}')
#     if ln_fit_ok and show_logn:
#         ax_fit.plot(x_ax, y_ln, 'b-', lw=2, label=f'Log-normal fit, R²={r2ln:.4f}')
#     if MR_fit_ok and show_MR:
#         ax_fit.plot(x_ax, y_MR, 'g-', lw=2, label=f'MR fit, R²={r2MR:.4f}')
#     if LSW_fit_ok and show_LSW:
#         # ax_fit.plot(x_ax, y_LSW, 'y-', lw=2, label=f'LSW distribution, R²={r2LSW:.4f}')
#         ax_fit.plot(x_ax, y_LSW, 'y-', lw=2, label=f'LSW distribution')
#     if show_mean:
#         ax_fit.axvline(mean, color='black', linestyle='--', linewidth=2)
#     ax_fit.set_xlabel(xlabel)
#     ax_fit.set_ylabel(ylabel)
#     lines, labels = ax_fit.get_legend_handles_labels()
#     ax_fit.legend(lines[::-1], labels[::-1])
#
#     xmin, xmax = ax_fit.get_xlim()
#     if min_x is not None:
#         xmin = max(min_x, xmin)
#     if max_x is not None:
#         xmax = max_x
#     ax_fit.set_xlim(xmin, xmax)
#
#     fig_fit.tight_layout()
#     buf = io.BytesIO()
#     fig_fit.savefig(buf, format="png")
#     plt.close(fig_fit)
#     return buf.getvalue()
#
#
#
#
#
#
