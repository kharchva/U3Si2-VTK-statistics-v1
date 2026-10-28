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
from libs.stlit import show_dependence_on_distance
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
    "threshold_vaac": None,
    "bubShape": None,
    "grShape": None,
    "gasShape": None,
    "vacShape": None,
    "bubNx": None,
    "bubNy": None,
    "bubNz": None,
    "grNx": None,
    "grNy": None,
    "grNz": None,
    "gasNx": None,
    "gasNy": None,
    "gasNz": None,
    "vacNx": None,
    "vacNy": None,
    "vacNz": None
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
if "set_par" not in st.session_state:
    st.session_state.set_par = False

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

    colc1, colc2 = st.columns(2)

    with colc1:
        M = st.selectbox(
            "Size in grids",
            options=[32, 64, 128, 256],
            index=2  # за замовчуванням буде 128
        )
    with colc2:
        scale = st.number_input("Scale [nm]", value=5, min_value=1, step=1)

    if M != st.session_state.M or scale != st.session_state.scale:
        st.session_state.set_par = False

    if st.button("⚙️ Set parameters", width='stretch'):
        st.session_state.set_par = True
        st.session_state.M = M
        st.session_state.scale = scale
        st.session_state.size_cm = M * scale * 1E-7
        st.session_state.vol_cm3 = (M * scale * 1E-7) ** 3

        if "dmin" not in st.session_state:
            st.session_state["dmin"] = {}
            st.session_state["dmin"].update(
                {name: 0 for name in dictBinsDists}
            )

        if "dmax" not in st.session_state:
            st.session_state["dmax"] = {}
            st.session_state["dmax"].update(
                {name: int(M*scale/2) for name in dictBinsDists}
            )
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<a href="http://iap.sumy.org/viewdep/en/?id=36&schemeid=51" target="_blank">'
            'M<sub>3</sub>TREC<sub>s</sub></a>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(' © 2026')

st.set_page_config(page_title="U3Si2 statistics", layout="wide", initial_sidebar_state="expanded")

if st.session_state.set_par:
    col01, col02 = st.columns([1, 5], gap="large")
    with col01:
        st.image("figs/photo_2026-06-09_14-53-28.jpg")
    with col02:
        st.title("Statistical analysis ")
        st.header("of grains and gas-bubbles in $U_3Si_2$")

    top_tabs = st.tabs([
        f"💨 **Dynamics of bubbles formation**",
        f"🫧 **Gas bubbles**",
        f"🧊 **Grain structure**",
        f"📐 **Statistics of bubbles in grains**",
        f"🔬 **Bubbles microstructure**"
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
        st.header(f"🧊 Grain structure:")
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
        st.header(f"📐 Statistics of bubbles in grains:")
        show_results_bubbles_in_grains()
        if st.session_state["results_bubbles_in_grains"] is not None:
            st.subheader(f"📈 Graphical results")
            tabs_bubbles_in_grains = st.tabs([
                f"📊 **Bubble center -- Grain center**",
                f"📊 **Bubble center -- Grain boundary**",
                f"📊 **Bubble edge -- Grain center**",
                f"📊 **Bubble edge -- Grain boundary**"
            ])
            with tabs_bubbles_in_grains[0]:
                st.markdown("**Normalized distribution of nearest distances between bubble center and grain center**")
                show_dependence_on_distance("bub_center_grain_center_dist", "green")
                st.divider()
                st.markdown("**Dependence of the number density of bubbles on distance between bubble center and grain center**")
                show_dependence_on_distance("bub_center_grain_center_numdens", "green")
                st.divider()
                st.markdown("**Dependence of the radius of bubbles on distance between bubble center and grain center**")
                show_dependence_on_distance("bub_center_grain_center_radius", "green")
                st.divider()
                st.markdown("**Dependence of the swelling on distance between bubble center and grain center**")
                show_dependence_on_distance("bub_center_grain_center_swelling", "green")
                st.divider()
                st.markdown("**Dependence of the porosity on distance between bubble center and grain center**")
                show_dependence_on_distance("bub_center_grain_center_porosity", "green")

            with tabs_bubbles_in_grains[1]:
                st.markdown("**Normalized distribution of nearest distances between bubble center and grain boundary**")
                show_dependence_on_distance("bub_center_grain_bound_dist", "green")
                st.divider()
                st.markdown("**Dependence of the number density of bubbles on distance between bubble center and grain boundary**")
                show_dependence_on_distance("bub_center_grain_bound_numdens", "green")
                st.divider()
                st.markdown("**Dependence of the radius of bubbles on distance between bbubble center and grain boundary**")
                show_dependence_on_distance("bub_center_grain_bound_radius", "green")
                st.divider()
                st.markdown("**Dependence of the swelling on distance between bubble center and grain boundary**")
                show_dependence_on_distance("bub_center_grain_bound_swelling", "green")
                st.divider()
                st.markdown("**Dependence of the porosity on distance between bubble center and grain boundary**")
                show_dependence_on_distance("bub_center_grain_bound_porosity", "green")

            with tabs_bubbles_in_grains[2]:
                st.markdown("**Normalized distribution of nearest distances between edge of bubble and grain center**")
                show_dependence_on_distance("bub_edge_grain_center_dist", "green")
                st.divider()
                st.markdown("**Dependence of the number density of bubbles on distance between edge of bubble and grain center**")
                show_dependence_on_distance("bub_edge_grain_center_numdens", "green")
                st.divider()
                st.markdown("**Dependence of the radius of bubbles on distance between edge of bubble and grain center**")
                show_dependence_on_distance("bub_edge_grain_center_radius", "green")
                st.divider()
                st.markdown("**Dependence of the swelling on distance between edge of bubble and grain center**")
                show_dependence_on_distance("bub_edge_grain_center_swelling", "green")
                st.divider()
                st.markdown("**Dependence of the porosity on distance between edge of bubble and grain center**")
                show_dependence_on_distance("bub_edge_grain_center_porosity", "green")

            with tabs_bubbles_in_grains[3]:
                st.markdown("**Normalized distribution of nearest distances between edge of bubble and grain boundary**")
                show_dependence_on_distance("bub_edge_grain_bound_dist", "green")
                st.divider()
                st.markdown("**Dependence of the number density of bubbles on distance between edge of bubble and grain boundary**")
                show_dependence_on_distance("bub_edge_grain_bound_numdens", "green")
                st.divider()
                st.markdown("**Dependence of the radius of bubbles on distance between edge of bubble and grain boundary**")
                show_dependence_on_distance("bub_edge_grain_bound_radius", "green")
                st.divider()
                st.markdown("**Dependence of the swelling on distance between edge of bubble and grain boundary**")
                show_dependence_on_distance("bub_edge_grain_bound_swelling", "green")
                st.divider()
                st.markdown("**Dependence of the porosity on distance between edge of bubble and grain boundary**")
                show_dependence_on_distance("bub_edge_grain_bound_porosity", "green")


            # with tabs_bubbles_in_grains[2]:
            #     st.markdown("**Dependence of the mean size of bubbles on a distance between bubbles and grain center**")
            #     show_meanBubSize_on_distGrainCenter("bubRad_vs_distGrCentr")

    with top_tabs[4]:
        st.header(f"🔬 **Bubbles microstructure**")
        colbubs, colgrns = st.columns(2)
        with colbubs:
            if st.session_state.BubblesFileName is not None:
                st.success(f"**Bubbles file name:**\n\n {st.session_state.BubblesFileName}")
                if st.session_state.bubShape != st.session_state.grShape:
                    st.warning(f"Dimension is ({st.session_state.bubNx}, {st.session_state.bubNy}, {st.session_state.bubNz})")
            else:
                st.warning("File with bubbles was not downloaded")
        with colgrns:
            if st.session_state.GrainsFileName is not None:
                st.success(f"**Grains file name:**\n\n {st.session_state.GrainsFileName}")
                if st.session_state.grShape != st.session_state.bubShape:
                    st.warning(f"Dimension is ({st.session_state.grNx}, {st.session_state.grNy}, {st.session_state.grNz})")
            else:
                st.warning("File with grains was not downloaded")

        colcg, colcv = st.columns(2)
        with colcg:
            show_results_gas_in_bubbles()
        with colcv:
            show_results_vac_in_bubbles()

else:
    st.image("figs/titul2.jpg", width='stretch')




