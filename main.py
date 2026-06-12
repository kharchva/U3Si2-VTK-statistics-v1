import streamlit as st
from libs.distributions import calc_distribution_from_data
from libs.functions import calc_bulbes
from libs.functions import calc_grains
from libs.functions import calc_bubbles_in_grains
from libs.functions import calc_bubbleRadius_on_dist_grainCenter
from libs.functions import dictXlable
from libs.functions import make_zip_from_dict
from libs.functions import fig_labels
from libs.mkfigures import make_figure_distribution_png
from libs.mkfigures import make_figure_radius_on_distance_png

DEFAULT_STATE = {
    "res_dist_bulbs_grains": None,
    "res_dist_bulbs": None,
    "res_boundaries": None,
    "res_grains": None,
    "res_bulbs": None,
    "fig_grains": None,
    "fig_bulbs": None,
    "calc_bulbs_done": False,
    "df_bulbs": None,
    "fname_bulbs": None,
    "calc_grains_done": False,
    "df_grains": None,
    "fname_grains": None,
    "res_grains1d": None,
    "res_bubbles3d": None,
    "res_grains3d": None,
    "df_bubingrains": None,
    "fig_bubingrains": None,
    "calc_dist_bulbs_grains_done": False,
    "bins": 15,
    "results_bubbles": None,
    "results_grains": None,
    "results_bubbles_in_grains": None,
    "vol_cm3": None,
    "num_of_grains_to_calc": 2,
    "num_of_bins_to_show": 10,
    "num_of_grains": None
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "numbins" not in st.session_state:
    st.session_state["numbins"] = {
        name: st.session_state.bins for name in dictXlable
    }


@st.fragment
def show_results_bubbles():
    c13, c14 = st.columns(2)
    res_bub = st.session_state["results_bubbles"]
    with c13:
        fig = res_bub["fig_bulbs"]
        st.plotly_chart(fig, use_container_width=True)
    with c14:
        st.markdown(""" Bubbles statistics """)
        table = res_bub["df_bulbs"]
        st.dataframe(
            table.style.format({"Value": "{:.1f}"}),
            use_container_width=True
        )


@st.fragment
def show_results_grains():
    if st.session_state["results_grains"] is not None:
        res_gr = st.session_state["results_grains"]
        with c23:
            fig = res_gr["fig_grains"]
            st.plotly_chart(fig, use_container_width=True)
        with c24:
            st.markdown(""" Grains statistics """)
            table = res_gr["df_grains"]
            st.dataframe(
                table.style.format({"Value": "{:.1f}"}),
                use_container_width=True
            )


@st.fragment
def show_results_bubbles_in_grains():
    if st.session_state["results_bubbles_in_grains"] is not None:
        res_bub_in_gr = st.session_state["results_bubbles_in_grains"]
        with c34:
            fig = res_bub_in_gr["fig_bulbsgrains"]
            st.plotly_chart(fig, use_container_width=True)
        with c35:
            st.markdown(""" Distances between bubbles and grains """)
            table = res_bub_in_gr["df_bubingrains"]
            st.dataframe(
                table.style.format({"Value": "{:.1f}"}),
                use_container_width=True
            )


@st.fragment
def show_distribution(results_name, fname, color):
    res = st.session_state[results_name]
    all_distribs = res["dict"]
    all_datasets = res["data"]
    distribs = all_distribs[fname]
    datasets = all_datasets[fname]
    gaus_ok = distribs["gauss_fit_ok"]
    logn_ok = distribs["ln_fit_ok"]
    MR_ok = distribs["MR_fit_ok"]
    LSW_ok = distribs["LSW_fit_ok"]

    r2ln = distribs["r2_ln"]
    r2gaus = distribs["r2_gauss"]
    r2MR = distribs["r2_MR"]
    r2LSW = distribs["r2_LSW"]

    mean_val = distribs["mean"]
    # fname = distribs["fname"]
    type = distribs["type"]
    area_cm3 = st.session_state["vol_cm3"]

    col_gaus, col_ln, col_MR, col_LSW, col_mean = st.columns(5)
    with col_gaus:
        show_gaus = st.checkbox(
            "Show Gaussian fit",
            key=f"show_gaus_{fname}",
            disabled=(not gaus_ok or r2gaus < 0)
        )

    with col_ln:
        show_logn = st.checkbox(
            "Show Log-normal fit",
            key=f"show_logn_{fname}",
            disabled=(not logn_ok or r2ln < 0)
        )


    if fname == "size_bubbles_mean_dist" or fname == "size_grains_mean_dist":
        with col_MR:
            show_MR = st.checkbox(
                "Show MR fit",
                key=f"show_MR_{fname}",
                disabled=(not MR_ok or r2MR < 0)
            )
        with col_LSW:
            show_LSW = st.checkbox(
                "Show LSW distribution",
                key=f"show_LSW_{fname}",
                disabled=(not LSW_ok or r2LSW < 0)
            )
    else:
        show_LSW = None
        show_MR = None

    with col_mean:
        show_mean = st.checkbox(
            "Show mean value",
            key=f"show_mean_{fname}"
        )

    curr_bins = st.session_state.numbins[fname]
    tab01h, tab02h = st.columns(2)
    with tab01h:
        new_bins = st.slider("Number of bins for distribution", 2, 2 * st.session_state.bins, curr_bins, key=f"nbins_{fname}")
    with tab02h:
        recalc = st.button(f"🔄 Recalculate distribution", key=f"recalc_{fname}")

    if recalc:
        if new_bins != curr_bins:
            st.session_state.numbins[fname] = new_bins
            data = distribs["data"]
            distribs, datasets = calc_distribution_from_data(
                data, fname, new_bins, type, area_cm3)
            st.session_state[results_name]["dict"][fname] = distribs
            st.session_state[results_name]["data"][fname] = datasets

    xlabel, ylabel = fig_labels(fname)

    fig = make_figure_distribution_png(
        distribs, color, xlabel, ylabel,
        show_gaus, show_logn, show_MR, show_LSW, show_mean, mean_val,
        min_x=0.0
    )

    st.image(fig, use_container_width=True)

    if not gaus_ok or r2gaus < 0:
        st.warning("Gaussian fit was not found")
    if not logn_ok or r2ln < 0:
        st.warning("Log-normal fit was not found")
    if fname == "size_bubbles_mean_dist" or fname == "size_grains_mean_dist":
        if not MR_ok or r2MR < 0:
            st.warning("MR fit was not found")

    fig_fname = f"fig_{fname}.png"
    zip_fname = f"{fname}_analysis.zip"
    st.session_state[f"zip_{fname}_ready"] = False
    zip_data = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            f"📦 Make ZIP arxiv with data",
            key=f"mk_zip_{fname}"
        ):
            zip_data = make_zip_from_dict(datasets, fig, fig_fname)
            st.session_state[f"zip_{fname}"] = zip_data
            st.session_state[f"zip_{fname}_ready"] = True

    with col2:
        if st.session_state.get(f"zip_{fname}_ready", False):
            st.download_button(
                label=f"💾 Download data in ZIP format",
                data=st.session_state[f"zip_{fname}"],
                file_name=zip_fname,
                mime="application/zip"
            )


@st.fragment
def show_meanBubSize_on_distGrainCenter(fname):
    # fname = "bubRad_vs_distGrCentr"
    if fname not in st.session_state or st.session_state[fname] is None:
        st.session_state[fname] = {
            "dict": None,
            "data": None
        }
    curr_Ngrains = st.session_state.num_of_grains_to_calc
    Ngrains = st.session_state.num_of_grains
    curr_Nbins = st.session_state.num_of_bins_to_show
    tab31bg, tab32bg, tab33bg = st.columns(3)
    with tab31bg:
        num_of_grains = st.slider("Number of grains for analysis", 1, Ngrains, curr_Ngrains, key=f"curr_Ngrains")
    with tab32bg:
        num_of_bins = st.slider("Number of bins for analysis", 2, 20, curr_Nbins, key=f"curr_Nbins")
    with tab33bg:
        start_dud_gr_dist = st.button(f"🔄 Start calculations", key=f"start_dud_gr_dist")

    if start_dud_gr_dist:
        if num_of_grains != curr_Ngrains:
            st.session_state.num_of_grains_to_calc = num_of_grains
        if num_of_bins != curr_Nbins:
            st.session_state.num_of_bins_to_show = num_of_bins
        grains = st.session_state["results_grains"]
        bubbles = st.session_state["results_bubbles"]
        results, datasets = calc_bubbleRadius_on_dist_grainCenter(
            M, grains, bubbles, num_of_grains, num_of_bins, scale, fname)
        st.session_state[fname]["dict"] = results
        st.session_state[fname]["data"] = datasets

    res = st.session_state[fname]
    if res["dict"] is not None and res["data"] is not None:
        results = res["dict"]
        datasets = res["data"]

        fig_rd = make_figure_radius_on_distance_png(results)
        st.image(fig_rd, use_container_width=True)

        fig_fname = f"fig_{fname}.png"
        zip_fname = f"{fname}_analysis.zip"
        st.session_state[f"zip_{fname}_ready"] = False
        zip_data = None

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                    f"📦 Make ZIP arxiv with data",
                    key=f"mk_zip_{fname}"
            ):
                zip_data = make_zip_from_dict(datasets, fig_rd, fig_fname)
                st.session_state[f"zip_{fname}"] = zip_data
                st.session_state[f"zip_{fname}_ready"] = True

        with col2:
            if st.session_state.get(f"zip_{fname}_ready", False):
                st.download_button(
                    label=f"💾 Download data in ZIP format",
                    data=st.session_state[f"zip_{fname}"],
                    file_name=zip_fname,
                    mime="application/zip"
                )


with st.sidebar:
    st.header("Parameters")
    M = st.number_input("Size in grids", value=128, min_value=32, step=32)
    scale = st.number_input("Scale [nm]", value=10, min_value=1, step=1)
    threshold_bubbles = st.number_input("Threshold for Bubbles", value=0.5, min_value=0.05, step=0.05, max_value=0.95)
    threshold_grains = st.number_input("Threshold for gains", value=0.9, min_value=0.05, step=0.05, max_value=0.95)
    nbins = st.session_state["bins"]
    size_cm = M * scale * 1E-7
    vol_cm3 = size_cm ** 3
    st.session_state["vol_cm3"] = vol_cm3

# start_dud_gr_dist = None

st.set_page_config(page_title="U3Si2 statistics", layout="wide", initial_sidebar_state="expanded")

col01, col02 = st.columns([2, 5], gap="large")
with col01:
    st.image("figs/photo_2026-06-09_14-53-28.jpg")
with col02:
    st.title("Statistical analysis ")
    st.header("of grains and gas-bubbles in $U_3Si_2$")

top_tabs = st.tabs([
    f"🫧 **Gas bubbles**",
    f"🔷 **Grain structure**",
    f"🧊 **Bubbles inside grains**"
])

with top_tabs[0]:
    st.header(f"🫧 Bubbles statistics:")
    c11, c12 = st.columns(2)
    with c11:
        BubblesFileName = st.file_uploader("Download bubbles file", type=["vtk"])
    with c12:
        start_bub = st.button("▶️ Start calculations", key="button_bub")
    if st.session_state["results_bubbles"] is not None:
        show_results_bubbles()
        st.subheader(f"📈 Graphical results")
        tabs_bubbles = st.tabs([
            f"📊 **Normalized size-distribution**",
            f"📊 **Number density (radius)**",
            f"📊 **Nearest distances**"
        ])
        with tabs_bubbles[0]:
            st.markdown("**Normalized distribution of bubbles over sizes (equivalent radius)**")
            show_distribution("results_bubbles", "size_bubbles_dist", "blue")
            st.divider()
            st.markdown(
                "**Normalized distribution of bubbles over reduced sizes "
                "($R_b / \\langle R_b \\rangle$)**"
            )
            show_distribution("results_bubbles", "size_bubbles_mean_dist", "blue")
        with tabs_bubbles[1]:
            st.markdown("**Dependence of the bubbles number density on the bubbles size (equivalent radius)**")
            show_distribution("results_bubbles", "size_bubbles_dens", "blue")
            st.divider()
            st.markdown(
                "**Dependence of the bubbles number density on the reduced bubbles size "
                "($R_b / \\langle R_b \\rangle$)**"
            )
            show_distribution("results_bubbles", "size_bubbles_mean_dens", "blue")
        with tabs_bubbles[2]:
            st.markdown("**Normalized distribution of nearest distances between bubbles centers**")
            show_distribution("results_bubbles", "nn_dist_bubbles", "blue")
            st.divider()
            st.markdown("**Normalized distribution of nearest distances between edges of bubbles**")
            show_distribution("results_bubbles", "edge_dist_bubbles", "blue")

with top_tabs[1]:
    st.header(f"🔷 Grain structure:")
    c21, c22 = st.columns(2)
    with c21:
        GrainsFileName = st.file_uploader("Download grains file", type=["vtk"])
    with c22:
        start_gr = st.button("▶️ Start calculations", key="button_gr")
    c23, c24 = st.columns(2)
    if st.session_state["results_grains"] is not None:
        show_results_grains()
        st.subheader(f"📈 Graphical results")
        tabs_grains = st.tabs([
            f"📊 **Normalized size-distribution**",
            f"📊 **Number density (radius)**"
        ])
        with tabs_grains[0]:
            st.markdown("**Normalized distribution of grains over sizes (equivalent radius)**")
            show_distribution("results_grains", "size_grains_dist", "orange")
            st.divider()
            st.markdown(
                "**Normalized distribution of grains over reduced sizes "
                "($R_g / \\langle R_g \\rangle$)**"
            )
            show_distribution("results_grains", "size_grains_mean_dist", "orange")
        with tabs_grains[1]:
            st.markdown("**Dependence of the grains number density on the grains size (equivalent radius)**")
            show_distribution("results_grains", "size_grains_dens", "orange")
            st.divider()
            st.markdown(
                "**Dependence of the grains number density on the reduced grains size "
                "($R_g / \\langle R_g \\rangle$)**"
            )
            show_distribution("results_grains", "size_grains_mean_dens", "orange")

with top_tabs[2]:
    st.header(f"🧊 Bubbles in Grains:")
    c31, c32, c33 = st.columns(3)
    with c31:
        if BubblesFileName:
            st.success(f"**Bubbles file name:** {BubblesFileName.name}")
        else:
            st.warning("File with bubbles was not downloaded")
    with c32:
        if GrainsFileName:
            st.success(f"**Grains file name:** {GrainsFileName.name}")
        else:
            st.warning("File with grains was not downloaded")
    with c33:
        start_bub_in_gr = st.button(
            "▶️ Start calculations",
            key="button_bubgr",
            disabled=(
                    st.session_state.get("results_grains") is None or
                    st.session_state.get("results_bubbles") is None
            )
        )
    c34, c35 = st.columns(2)
    if st.session_state["results_bubbles_in_grains"] is not None:
        show_results_bubbles_in_grains()
        st.subheader(f"📈 Graphical results")
        tabs_bubbles_in_grains = st.tabs([
            f"📊 **Distance to Grain center**",
            f"📊 **Distance to Grain boundary**",
            f"📉 **Bubbles size VS distance from grain center**"
        ])
        with tabs_bubbles_in_grains[0]:
            st.markdown("**Normalized distribution of nearest distances between bubbles center and grains center**")
            show_distribution("results_bubbles_in_grains", "bub_center_grain_center_dist", "green")
            st.divider()
            st.markdown("**Normalized distribution of nearest distances between edges of bubbles and grain center**")
            show_distribution("results_bubbles_in_grains", "bub_edge_grain_center_dist", "green")
        with tabs_bubbles_in_grains[1]:
            st.markdown("**Normalized distribution of nearest distances between bubbles center and grains boundary**")
            show_distribution("results_bubbles_in_grains", "bub_center_grain_bound_dist", "green")
            st.divider()
            st.markdown("**Normalized distribution of nearest distances between edges of bubbles and grain boundary**")
            show_distribution("results_bubbles_in_grains", "bub_edge_grain_bound_dist", "green")
        with tabs_bubbles_in_grains[2]:
            st.markdown("**Dependence of the mean size of bubbles on a distance between bubbles and grain center**")
            show_meanBubSize_on_distGrainCenter("bubRad_vs_distGrCentr")


if start_bub:
    if BubblesFileName:
        results_bubbles = calc_bulbes(BubblesFileName, threshold_bubbles, M, nbins, scale, vol_cm3)
        st.session_state["results_bubbles"] = results_bubbles
        st.rerun()
    else:
        with c12:
            st.warning("File was not downloaded")


if start_gr:
    if GrainsFileName:
        results_grains = calc_grains(GrainsFileName, threshold_grains, M, nbins, scale, vol_cm3)
        st.session_state["results_grains"] = results_grains
        st.session_state["num_of_grains"] = results_grains["num_of_grains_for_calc"]
        st.rerun()
    else:
        with c22:
            st.warning("File was not downloaded")


if start_bub_in_gr:
    if st.session_state["results_grains"] is not None and st.session_state["results_bubbles"] is not None:
        results_bubbles_in_grains = calc_bubbles_in_grains(
            st.session_state["results_grains"], st.session_state["results_bubbles"],
            threshold_grains, threshold_bubbles, M, nbins, scale, vol_cm3)
        st.session_state["results_bubbles_in_grains"] = results_bubbles_in_grains
        st.rerun()




