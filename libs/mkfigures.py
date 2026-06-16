import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import io


plt.rcParams.update({
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'axes.titlesize': 16,
    'legend.fontsize': 12
})


# def show_surface(field):
#     return show_surface_field(field)
#
#
# def show_clip(field, thr, color):
#     return show_VTK(field, thr, color)
#
#
# def show_two_clips(field1, field2, thr1, thr2, color1, color2):
#     return show_two_VTK(field1, field2, thr1, thr2, color1, color2)


# # @st.cache_data(
# #     show_spinner=False,
# #     hash_funcs={np.ndarray: lambda x: x.tobytes()}
# # )
# def show_bulbes(thr):
#     figBulbs = show_VTK(st.session_state.bub3d, thr, "blue")
#     return figBulbs
#
#
# # @st.cache_data(
# #     show_spinner=False,
# #     hash_funcs={np.ndarray: lambda x: x.tobytes()}
# # )
# def show_grains():
#     figGrains = show_surface_field(st.session_state.gr3d)
#     return figGrains
#
#
# # @st.cache_data(
# #     show_spinner=False,
# #     hash_funcs={np.ndarray: lambda x: x.tobytes()}
# # )
# def show_bubbles_in_grains():
#     figBubGrains = show_two_VTK(
#                 st.session_state.gr3d,
#                 st.session_state.bub3d,
#                 st.session_state.threshold_grains,
#                 st.session_state.threshold_bubbles,
#                 "orange",
#                 "blue"
#             )
#     return figBubGrains


@st.cache_data(
    show_spinner=False,
    hash_funcs={np.ndarray: lambda x: x.tobytes()}
)
def make_figure_radius_on_distance_png(dict_with_data):
    x_all = dict_with_data["dist_to_grCentr"]
    y_all = dict_with_data["bubbleRadius"]
    x = dict_with_data["dist_to_grCentr_bins"]
    y = dict_with_data["mean_bubbleRadius"]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_all, y_all, marker='s', linestyle='', color='r', lw=2, ms=8, mfc='none', label="All data")
    ax.plot(x, y, marker='o', linestyle='-', color='b', lw=2, ms=8, label="Average data")
    ax.set_xlabel("Distance from bubble center to grain center [nm]")
    ax.set_ylabel("Bubble radius [nm]")
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines[::-1], labels[::-1])

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()


@st.cache_data(
    show_spinner=False,
    hash_funcs={np.ndarray: lambda x: x.tobytes()}
)
def make_figure_distribution_png(dict_with_data, colorbins, xlabel, ylabel,
                                    show_gaus, show_logn, show_MR, show_LSW, show_mean, mean,
                                 min_x=None, max_x=None):
    x = dict_with_data["x"]
    y = dict_with_data["y"]
    x_ax = dict_with_data["x_ax"]
    gauss_fit_ok = dict_with_data["gauss_fit_ok"]
    y_gs = dict_with_data["y_gauss_fit"]
    r2gs = dict_with_data["r2_gauss"]
    ln_fit_ok = dict_with_data["ln_fit_ok"]
    y_ln = dict_with_data["y_ln_fit"]
    r2ln = dict_with_data["r2_ln"]

    MR_fit_ok = dict_with_data["MR_fit_ok"]
    y_MR = dict_with_data["y_MR_fit"]
    r2MR = dict_with_data["r2_MR"]

    LSW_fit_ok = dict_with_data["LSW_fit_ok"]
    y_LSW = dict_with_data["y_LSW_fit"]
    # r2LSW = dict_with_data["r2_LSW"]

    bin_width = dict_with_data["bin_width"]

    fig_fit, ax_fit = plt.subplots(figsize=(10, 5))
    ax_fit.bar(x, y, width=bin_width * 0.8, color=colorbins, edgecolor='black', alpha=0.5, label="Data")
    if gauss_fit_ok and show_gaus:
        ax_fit.plot(x_ax, y_gs, 'r-', lw=2, label=f'Gaussian fit, R²={r2gs:.4f}')
    if ln_fit_ok and show_logn:
        ax_fit.plot(x_ax, y_ln, 'b-', lw=2, label=f'Log-normal fit, R²={r2ln:.4f}')
    if MR_fit_ok and show_MR:
        ax_fit.plot(x_ax, y_MR, 'g-', lw=2, label=f'MR fit, R²={r2MR:.4f}')
    if LSW_fit_ok and show_LSW:
        # ax_fit.plot(x_ax, y_LSW, 'y-', lw=2, label=f'LSW distribution, R²={r2LSW:.4f}')
        ax_fit.plot(x_ax, y_LSW, 'y-', lw=2, label=f'LSW distribution')
    if show_mean:
        ax_fit.axvline(mean, color='black', linestyle='--', linewidth=2)
    ax_fit.set_xlabel(xlabel)
    ax_fit.set_ylabel(ylabel)
    lines, labels = ax_fit.get_legend_handles_labels()
    ax_fit.legend(lines[::-1], labels[::-1])

    xmin, xmax = ax_fit.get_xlim()
    if min_x is not None:
        xmin = max(min_x, xmin)
    if max_x is not None:
        xmax = max_x
    ax_fit.set_xlim(xmin, xmax)

    fig_fit.tight_layout()
    buf = io.BytesIO()
    fig_fit.savefig(buf, format="png")
    plt.close(fig_fit)
    return buf.getvalue()


@st.cache_data(
    show_spinner=False,
    hash_funcs={np.ndarray: lambda x: x.tobytes()}
)
def make_time_dependence_png(text, data, n_cols, curves, log_x, log_y, colors):
    fig_fit, ax_fit = plt.subplots(figsize=(10, 5))
    ax_fit.set_xlabel(f"{text[0][0]} {text[1][0]}")
    ylabel = ""
    for i in range (n_cols - 1):
        if curves[i]:
            ylabel += f", {text[0][i+1]}"
            ax_fit.plot(data[0], data[i+1], color=colors[i], lw=2, label=f"{text[0][i+1]} {text[1][i+1]}")
    ylabel = ylabel.lstrip(", ")
    ax_fit.set_ylabel(ylabel)
    if log_x:
        ax_fit.set_xscale("log")  # логарифмічна шкала по X
    if log_y:
        ax_fit.set_yscale("log")  # логарифмічна шкала по
    lines, labels = ax_fit.get_legend_handles_labels()
    ax_fit.legend(lines[::-1], labels[::-1])

    fig_fit.tight_layout()
    buf = io.BytesIO()
    fig_fit.savefig(buf, format="png")
    plt.close(fig_fit)
    return buf.getvalue()
