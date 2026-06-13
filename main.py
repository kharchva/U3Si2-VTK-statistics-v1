import streamlit as st
from libs.distributions import calc_distribution_from_data
from libs.functions import calc_bulbes
from libs.functions import calc_grains
from libs.functions import calc_bubbles_in_grains
from libs.functions import calc_bubbleRadius_on_dist_grainCenter
from libs.functions import dictBinsBubbles
from libs.functions import dictBinsGrains
from libs.functions import dictBinsDists
from libs.functions import make_zip_from_dict
from libs.functions import fig_labels
from libs.functions import getdata
from libs.mkfigures import show_bulbes
from libs.mkfigures import show_grains
from libs.mkfigures import show_bubbles_in_grains
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
    "num_of_grains_to_calc": 2,
    "num_of_bins_to_show": 10,
    "num_of_grains": None,
    "bub3d": None,
    "gr3d": None,
    "BubblesFileName": None,
    "GrainsFileName": None,
    "threshold_bubbles": None,
    "threshold_grains": None
}


for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


if "numbins" not in st.session_state:
    st.session_state["numbins"] = {}
    st.session_state["numbins"].update(
        {name: st.session_state.bins for name in dictBinsBubbles}
    )
    st.session_state["numbins"].update(
        {name: st.session_state.bins for name in dictBinsGrains}
    )
    st.session_state["numbins"].update(
        {name: st.session_state.bins for name in dictBinsDists}
    )


def reset_bubbles():
    st.session_state.results_bubbles = None
    st.session_state.bub3d = None
    st.session_state.threshold_bubbles = None
    st.session_state.bubfname = None
    st.session_state.minv = None
    st.session_state.maxv = None
    st.session_state.BubblesFileName = None


def reset_grains():
    st.session_state.results_grains = None
    st.session_state.gr3d = None
    st.session_state.threshold_grains = None
    st.session_state.grfname = None
    st.session_state.minvg = None
    st.session_state.maxvg = None
    st.session_state.GrainsFileName = None


@st.fragment
def show_3D_bubbles():
    fig = show_bulbes(st.session_state.threshold_bubbles)
    st.plotly_chart(fig, use_container_width=True)


@st.fragment
def show_3D_grains():
    fig = show_grains()
    st.plotly_chart(fig, use_container_width=True)


@st.fragment
def show_3D_bubbles_in_grains():
    fig = show_bubbles_in_grains()
    st.plotly_chart(fig, use_container_width=True)


def show_results_bubbles():
    c11, c12 = st.columns(2)
    with c11:
        BubblesFileName = st.file_uploader(
            "Download bubbles file",
            type=["vtk"],
            key="bubble_uploader",
            on_change=reset_bubbles,
        )
        threshold_bubbles = st.number_input("Threshold for Bubbles",
                                            value=0.5,
                                            min_value=0.05,
                                            step=0.05,
                                            max_value=1.0)
        st.session_state.threshold_bubbles = threshold_bubbles
        if BubblesFileName is not None:
            st.session_state.BubblesFileName = BubblesFileName.name
            if st.session_state.bub3d is None:
                bub3d, bubfname = getdata(BubblesFileName)
                minv = bub3d.min()
                maxv = bub3d.max()
                st.session_state.bub3d = bub3d
                st.session_state.bubfname = bubfname
                st.session_state.minv = minv
                st.session_state.maxv = maxv

            st.success(
                f"Minimal value: **{st.session_state.minv:.2f}**\n\n"
                f"Maximal value: **{st.session_state.maxv:.2f}**"
            )
            if threshold_bubbles > st.session_state.maxv:
                st.warning(f"Threshold for bubbles is larger than maximal value\n\n"
                           f"Choose threshold between {st.session_state.minv:.2f} "
                           f"and {st.session_state.maxv:.2f} !!!")

        if st.session_state.bub3d is not None:
            if st.session_state.minv < threshold_bubbles < st.session_state.maxv:
                start_bub = st.button("▶️ Start calculations", key="button_bub")
                if start_bub:
                    results_bubbles = calc_bulbes(st.session_state.bub3d, st.session_state.bubfname,
                                                  st.session_state.threshold_bubbles,
                                                  st.session_state.M, st.session_state.bins,
                                                  st.session_state.scale, st.session_state.vol_cm3)
                    st.session_state["results_bubbles"] = results_bubbles
                if st.session_state["results_bubbles"] is not None:
                    st.session_state["numbins"].update(
                        {name: st.session_state.bins for name in dictBinsBubbles}
                    )
                    res_bub = st.session_state["results_bubbles"]
                    st.markdown(""" Bubbles statistics """)
                    table = res_bub["df_bulbs"]
                    st.dataframe(
                            table.style.format({"Value": "{:.1f}"}),
                            use_container_width=True
                        )

    with c12:
        if BubblesFileName is not None:
            if st.session_state.threshold_bubbles < st.session_state.maxv:
                show_3D_bubbles()



def show_results_grains():
    c11, c12 = st.columns(2)
    with c11:
        GrainsFileName = st.file_uploader(
            "Download grains file",
            type=["vtk"],
            key="grain_uploader",
            on_change=reset_grains,
        )
        threshold_grains = st.number_input("Threshold for Grains",
                                            value=0.9,
                                            min_value=0.05,
                                            step=0.05,
                                            max_value=1.0)
        st.session_state.threshold_grains = threshold_grains
        if GrainsFileName is not None:
            st.session_state.GrainsFileName = GrainsFileName.name
            if st.session_state.gr3d is None:
                gr3d, grfname = getdata(GrainsFileName)
                minvg = gr3d.min()
                maxvg = gr3d.max()
                st.session_state.gr3d = gr3d
                st.session_state.grfname = grfname
                st.session_state.minvg = minvg
                st.session_state.maxvg = maxvg

            st.success(
                f"Minimal value: **{st.session_state.minvg:.2f}**\n\n"
                f"Maximal value: **{st.session_state.maxvg:.2f}**"
            )
            if threshold_grains > st.session_state.maxvg:
                st.warning(f"Threshold for grains is larger than maximal value\n\n"
                           f"Choose threshold between {st.session_state.minvg:.2f} "
                           f"and {st.session_state.maxvg:.2f} !!!")

        if st.session_state.gr3d is not None:
            if st.session_state.minvg < threshold_grains < st.session_state.maxvg:
                start_gr = st.button("▶️ Start calculations", key="grain_bub")
                if start_gr:
                    results_grains = calc_grains(st.session_state.gr3d, st.session_state.grfname,
                                                  st.session_state.threshold_grains,
                                                  st.session_state.M, st.session_state.bins,
                                                  st.session_state.scale, st.session_state.vol_cm3)
                    st.session_state["results_grains"] = results_grains
                    st.session_state["num_of_grains"] = results_grains["num_of_grains_for_calc"]
                if st.session_state["results_grains"] is not None:
                    st.session_state["numbins"].update(
                        {name: st.session_state.bins for name in dictBinsGrains}
                    )
                    res_gr = st.session_state["results_grains"]
                    st.markdown(""" Grains statistics """)
                    table = res_gr["df_grains"]
                    st.dataframe(
                            table.style.format({"Value": "{:.1f}"}),
                            use_container_width=True
                        )

    with c12:
        if GrainsFileName is not None:
            if st.session_state.threshold_grains < st.session_state.maxvg:
                show_3D_grains()


def show_results_bubbles_in_grains():
    c31, c32 = st.columns(2)
    with c31:
        if st.session_state.BubblesFileName is not None:
            st.success(f"**Bubbles file name:**\n\n {st.session_state.BubblesFileName}")
        else:
            st.warning("File with bubbles was not downloaded")
        if st.session_state.results_bubbles is None:
            st.warning("Calculations of bubbles are needed")
    with c32:
        if st.session_state.GrainsFileName is not None:
            st.success(f"**Grains file name:**\n\n {st.session_state.GrainsFileName}")
        else:
            st.warning("File with grains was not downloaded")
        if st.session_state.results_grains is None:
            st.warning("Calculations of grains are needed")
    c33, c34 = st.columns(2)
    with c33:
        if st.session_state.results_grains is not None and st.session_state.results_bubbles is not None:
            start_bub_in_gr = st.button(
                "▶️ Start calculations",
                key="button_bubgr",
                disabled=(
                        st.session_state.get("results_grains") is None or
                        st.session_state.get("results_bubbles") is None
                )
            )
            if start_bub_in_gr:
                if st.session_state["results_grains"] is not None and st.session_state["results_bubbles"] is not None:
                    results_bubbles_in_grains = calc_bubbles_in_grains(
                        st.session_state["results_grains"], st.session_state["results_bubbles"],
                        st.session_state.threshold_grains, st.session_state.threshold_bubbles,
                        st.session_state.M, st.session_state.bins,
                        st.session_state.scale, st.session_state.vol_cm3)
                    st.session_state["results_bubbles_in_grains"] = results_bubbles_in_grains

    with c34:
        if st.session_state.BubblesFileName is not None and st.session_state.GrainsFileName is not None:
            show_3D_bubbles_in_grains()

    with c33:
        if st.session_state["results_bubbles_in_grains"] is not None:
            st.session_state["numbins"].update(
                {name: st.session_state.bins for name in dictBinsDists}
            )
            st.markdown(""" Distances between bubbles and grains """)
            res_bub_in_gr = st.session_state["results_bubbles_in_grains"]
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
    tab31bg, tab32bg = st.columns(2)
    with tab31bg:
        num_of_grains = st.slider("Number of grains for analysis", 1, Ngrains, curr_Ngrains, key=f"curr_Ngrains")
    with tab32bg:
        num_of_bins = st.slider("Number of bins for analysis", 2, 20, curr_Nbins, key=f"curr_Nbins")
    # with tab33bg:
    #     start_dud_gr_dist = st.button(f"🔄 Start calculations", key=f"start_dud_gr_dist")
########################################
    # if start_dud_gr_dist:
    if num_of_grains != curr_Ngrains:
        st.session_state.num_of_grains_to_calc = num_of_grains
    if num_of_bins != curr_Nbins:
        st.session_state.num_of_bins_to_show = num_of_bins
    grains = st.session_state["results_grains"]
    bubbles = st.session_state["results_bubbles"]
    results, datasets = calc_bubbleRadius_on_dist_grainCenter(
        st.session_state.M, grains, bubbles, num_of_grains, num_of_bins,
        st.session_state.scale, fname)
    st.session_state[fname]["dict"] = results
    st.session_state[fname]["data"] = datasets
###########################
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
    st.image("figs/m3trex.png")
    st.divider()
    st.header("Parameters")
    M = st.number_input("Size in grids", value=128, min_value=32, step=32)
    scale = st.number_input("Scale [nm]", value=10, min_value=1, step=1)
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("figs/logo.jpg")
    with col2:
        st.markdown(
            '<a href="http://iap.sumy.org/viewdep/en/?id=36&schemeid=51" target="_blank">'
            'M<sub>3</sub>TREC<sub>s</sub></a>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(' © 2026')

    if "M" not in st.session_state:
        st.session_state.M = M
    if "scale" not in st.session_state:
        st.session_state.scale = scale
    if "size_cm" not in st.session_state:
        st.session_state.size_cm = M * scale * 1E-7
    if "vol_cm3" not in st.session_state:
        st.session_state.vol_cm3 = (M * scale * 1E-7) ** 3


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
    st.header(f"🫧 Gas bubbles:")
    show_results_bubbles()
    if st.session_state["results_bubbles"] is not None:
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
    show_results_grains()
    if st.session_state["results_grains"] is not None:
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
    st.header(f"🧊 Bubbles inside Grains:")
    show_results_bubbles_in_grains()
    if st.session_state["results_bubbles_in_grains"] is not None:
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




