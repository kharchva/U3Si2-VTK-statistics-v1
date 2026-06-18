import streamlit as st

from libs.functions import dictBinsBubbles
from libs.functions import dictBinsGrains
from libs.functions import dictBinsDists

from libs.stlit import show_results_bubbles
from libs.stlit import show_results_grains
from libs.stlit import show_results_bubbles_in_grains
from libs.stlit import show_results_gas_in_bubbles
from libs.stlit import show_results_vac_in_bubbles
from libs.stlit import show_results_fission_dependencies
from libs.stlit import show_distribution
from libs.stlit import show_meanBubSize_on_distGrainCenter


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
    "threshold_grains": None,
    "gas3d": None,
    "vac3d": None,
    "GasFileName": None,
    "VacFileName": None,
    "threshold_gas": None,
    "threshold_vaac": None

}


for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


if "M" not in st.session_state:
    st.session_state.M = None
if "scale" not in st.session_state:
    st.session_state.scale = None
if "size_cm" not in st.session_state:
    st.session_state.size_cm = None
if "vol_cm3" not in st.session_state:
    st.session_state.vol_cm3 = None


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


with st.sidebar:
    st.image("figs/m3trex.png")
    st.divider()
    st.header("Parameters")
    M = st.number_input("Size in grids", value=128, min_value=32, step=32)
    scale = st.number_input("Scale [nm]", value=10, min_value=1, step=1)

    st.session_state.M = M
    st.session_state.scale = scale
    st.session_state.size_cm = M * scale * 1E-7
    st.session_state.vol_cm3 = (M * scale * 1E-7) ** 3

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

st.set_page_config(page_title="U3Si2 statistics", layout="wide", initial_sidebar_state="expanded")

col01, col02 = st.columns([2, 5], gap="large")
with col01:
    st.image("figs/photo_2026-06-09_14-53-28.jpg")
with col02:
    st.title("Statistical analysis ")
    st.header("of grains and gas-bubbles in $U_3Si_2$")

top_tabs = st.tabs([
    f"💨 **Dynamics of bubbles formation**",
    f"🫧 **Gas bubbles**",
    f"🔷 **Grain structure**",
    f"🧪 **Bubbles microstructure**",
    f"🧊 **Bubbles inside grains**"
])

with top_tabs[0]:
    st.header(f"💨 **Dynamics of bubbles formation**")
    show_results_fission_dependencies()


with top_tabs[1]:
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


with top_tabs[2]:
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


with top_tabs[3]:
    st.header(f"🧪 **Bubbles microstructure**")
    colbubs, colgrns = st.columns(2)
    with colbubs:
        if st.session_state.BubblesFileName is not None:
            st.success(f"**Bubbles file name:** {st.session_state.BubblesFileName}")
        else:
            st.warning("File with bubbles was not downloaded")
    with colgrns:
        if st.session_state.GrainsFileName is not None:
            st.success(f"**Grains file name:** {st.session_state.GrainsFileName}")
        else:
            st.warning("File with grains was not downloaded")

    colcg, colcv = st.columns(2)
    with colcg:
        show_results_gas_in_bubbles()
    with colcv:
        show_results_vac_in_bubbles()


with top_tabs[4]:
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




