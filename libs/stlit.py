import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

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
from libs.functions import parse_tab_file

# from libs.mkfigures import show_bulbes
# from libs.mkfigures import show_grains
# from libs.mkfigures import show_bubbles_in_grains

from libs.mkfigures import make_figure_distribution_png
from libs.mkfigures import make_figure_radius_on_distance_png
from libs.mkfigures import make_time_dependence_png

from libs.paraview import show_surface_field
from libs.paraview import show_VTK
from libs.paraview import show_two_VTK
from libs.paraview import show_three_VTK


color_options = [
    "Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Pink", "Brown", "Cyan",
    "Magenta", "Lime", "Navy", "Teal", "Olive", "Maroon", "Gold"]


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


def reset_gas():
    st.session_state.gas3d = None
    st.session_state.threshold_gas = None
    st.session_state.gasfname = None
    st.session_state.mincg = None
    st.session_state.maxcg = None
    st.session_state.GasFileName = None


def reset_vac():
    st.session_state.vac3d = None
    st.session_state.threshold_vac = None
    st.session_state.vacfname = None
    st.session_state.mincv = None
    st.session_state.maxcv = None
    st.session_state.VacFileName = None

@st.fragment
def show_surface(field):
    fig = show_surface_field(field)
    st.plotly_chart(fig, width="stretch")


@st.fragment
def show_clip(field, thr, color):
    # Nx, Ny, Nz = field.shape
    # if Nz < 2:
    #     field = np.repeat(field, 2, axis=2)   # тепер форма (Nx, Ny, 2)
    fig = show_VTK(field, thr, color)
    st.plotly_chart(fig, width="stretch")


@st.fragment
def show_clip2(field1, field2, thr1, thr2, color1, color2):
    fig = show_two_VTK(field1, field2, thr1, thr2, color1, color2, opacity1=1.0, opacity2=1.0)
    st.plotly_chart(fig, width="stretch")


def show_results_bubbles():
    c11, c12 = st.columns(2)
    c13, c14 = st.columns(2)
    c15, c16 = st.columns(2)
    with c11:
        BubblesFileName = st.file_uploader(
            "Download bubbles file",
            type=["vtk"],
            key="bubble_uploader",
            on_change=reset_bubbles,
        )
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

            with c12:
                col121, col122 = st.columns(2)
                with col121:
                    st.success(f"Minimal value: **{st.session_state.minv:.2f}**")
                with col122:
                    st.success(f"Maximal value: **{st.session_state.maxv:.2f}**")

                minv = float(st.session_state.minv)
                maxv = float(st.session_state.maxv)
                threshold_bubbles = st.number_input(
                    "Threshold for Gas-atoms",
                    value=minv + (maxv - minv) / 2,
                    min_value=minv,
                    step=(maxv - minv) / 100,
                    max_value=maxv
                )
                st.session_state.threshold_bubbles = threshold_bubbles

            with c13:
                show_surface(st.session_state.bub3d)
            with c14:
                cmap = plt.get_cmap("RdBu_r")
                color = cmap(threshold_bubbles)
                color = mcolors.to_hex(color)
                show_clip(st.session_state.bub3d, threshold_bubbles, color)
            with c15:
                # start_bub = st.button("▶️ Start calculations", key="button_bub")

                set_min_num_cells_bubbles = st.checkbox("Ignore small bubbles", value=False, key="small_bubbles")
                if set_min_num_cells_bubbles:
                    min_num_cells_bubbles = st.number_input(
                        "Minimal number of cells",
                        value=1,
                        min_value=1,
                        step=1,
                        max_value=st.session_state.M**3,
                        key="min_num_cells_bubbles"
                    )
                else:
                    min_num_cells_bubbles = 1
                set_max_num_cells_bubbles = st.checkbox("Ignore large bubbles", value=False, key="large_bubbles")
                if set_max_num_cells_bubbles:
                    max_num_cells_bubbles = st.number_input(
                        "Maximal number of cells",
                        value=st.session_state.M,
                        min_value=1,
                        step=1,
                        max_value=st.session_state.M**3,
                        key="max_num_cells_bubbles"
                    )
                else:
                    max_num_cells_bubbles = st.session_state.M**3
                start_bub = st.button("▶️ Start calculations", key="button_bub")
                if start_bub:
                    if max_num_cells_bubbles < min_num_cells_bubbles:
                        st.error("Maximal number of cells should be more than minimal number of cells !!!")
                    else:
                        results_bubbles = calc_bulbes(st.session_state.bub3d, st.session_state.bubfname,
                                                      st.session_state.threshold_bubbles,
                                                      st.session_state.M, st.session_state.bins,
                                                      st.session_state.scale, st.session_state.vol_cm3,
                                                      min_num_cells_bubbles, max_num_cells_bubbles)
                        st.session_state["results_bubbles"] = results_bubbles
                if st.session_state["results_bubbles"] is not None:
                    st.session_state["numbins"].update(
                        {name: st.session_state.bins for name in dictBinsBubbles}
                    )
                    res_bub = st.session_state["results_bubbles"]
                    with c16:
                        st.markdown(""" Bubbles statistics """)
                        table = res_bub["df_bulbs"]
                    #     st.dataframe(
                    #             table.style.format({"Value": "{:.1f}"}),
                    #             width="stretch"
                    # )
                        st.dataframe(
                            table.style.format({
                                "Value": lambda x: f"{int(x)}" if isinstance(x, int) or x.is_integer() else f"{x:.1f}"
                            }),
                            width="stretch"
                        )


def show_results_grains():
    c21, c22 = st.columns(2)
    c23, c24 = st.columns(2)
    c25, c26 = st.columns(2)
    with c21:
        GrainsFileName = st.file_uploader(
            "Download grains file",
            type=["vtk"],
            key="grain_uploader",
            on_change=reset_grains,
        )
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

            with c22:
                col221, col222 = st.columns(2)
                with col221:
                    st.success(f"Minimal value: **{st.session_state.minvg:.2f}**")
                with col222:
                    st.success(f"Maximal value: **{st.session_state.maxvg:.2f}**")

                minvg = float(st.session_state.minvg)
                maxvg = float(st.session_state.maxvg)
                threshold_grains = st.number_input(
                    "Threshold for Gas-atoms",
                    value=minvg + (maxvg - minvg) / 2,
                    min_value=minvg,
                    step=(maxvg - minvg) / 100,
                    max_value=maxvg
                )
                st.session_state.threshold_grains = threshold_grains

            with c23:
                show_surface(st.session_state.gr3d)
            with c24:
                cmap = plt.get_cmap("RdBu_r")
                color = cmap(threshold_grains)
                color = mcolors.to_hex(color)
                # show_clip(st.session_state.gr3d, threshold_grains, "orange")
                show_clip(st.session_state.gr3d, threshold_grains, color)
            with c25:
                set_min_num_cells_grains = st.checkbox("Ignore small grains", value=False, key="small_grains")
                if set_min_num_cells_grains:
                    min_num_cells_grains = st.number_input(
                        "Minimal number of cells",
                        value=1,
                        min_value=1,
                        step=1,
                        max_value=st.session_state.M**3,
                        key="min_num_cells_grains"
                    )
                else:
                    min_num_cells_grains = 1
                set_max_num_cells_grains = st.checkbox("Ignore large grains", value=False, key="large_grains")
                if set_max_num_cells_grains:
                    max_num_cells_grains = st.number_input(
                        "Maximal number of cells",
                        value=st.session_state.M,
                        min_value=1,
                        step=1,
                        max_value=st.session_state.M**3,
                        key="max_num_cells_grains"
                    )
                else:
                    max_num_cells_grains = st.session_state.M**3

                start_gr = st.button("▶️ Start calculations", key="button_gr")
                if start_gr:
                    if max_num_cells_grains < min_num_cells_grains:
                        st.error("Maximal number of cells should be more than minimal number of cells !!!")
                    else:
                        results_grains = calc_grains(st.session_state.gr3d, st.session_state.grfname,
                                                      st.session_state.threshold_grains,
                                                      st.session_state.M, st.session_state.bins,
                                                      st.session_state.scale, st.session_state.vol_cm3,
                                                     min_num_cells_grains, max_num_cells_grains)
                        st.session_state["results_grains"] = results_grains
                        st.session_state["num_of_grains"] = results_grains["num_of_grains_for_calc"]
                if st.session_state["results_grains"] is not None:
                    st.session_state["numbins"].update(
                        {name: st.session_state.bins for name in dictBinsGrains}
                    )
                    res_gr = st.session_state["results_grains"]
                    with c26:
                        st.markdown(""" Grains statistics """)
                        table = res_gr["df_grains"]
                        # st.dataframe(
                        #     table.style.format({"Value": "{:.1f}"}),
                        #     width="stretch"
                        # )
                        st.dataframe(
                            table.style.format({
                                "Value": lambda x: f"{int(x)}" if isinstance(x, int) or x.is_integer() else f"{x:.1f}"
                            }),
                            width="stretch"
                        )


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
            col_cl1, col_cl2 = st.columns(2)
            with col_cl1:
                colorgr = st.selectbox("Color for Grains", list(color_options), index=5)
            with col_cl2:
                colorbub = st.selectbox("Color for Bubbles", list(color_options), index=12)
            show_clip2(st.session_state.gr3d, st.session_state.bub3d,
                       st.session_state.threshold_grains, st.session_state.threshold_bubbles,
                       colorgr, colorbub)

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
                width="stretch"
            )


@st.fragment
def show_results_gas_in_bubbles():
    st.subheader("***Gas atoms in Bubbles***")
    GasFileName = st.file_uploader(
        "Download gas-atoms file",
        type=["vtk"],
        key="gas_uploader",
        on_change=reset_gas,
    )


    if GasFileName is not None:
        st.session_state.GasFileName = GasFileName.name
        if st.session_state.gas3d is None:
            gas3d, gasfname = getdata(GasFileName)
            mincg = gas3d.min()
            maxcg = gas3d.max()
            st.session_state.gas3d = gas3d
            st.session_state.gasfname = gasfname
            st.session_state.mincg = mincg
            st.session_state.maxcg = maxcg

        colming, colmaxg = st.columns(2)
        with colming:
            st.success(f"Minimal value: **{st.session_state.mincg:.2f}**")
        with colmaxg:
            st.success(f"Maximal value: **{st.session_state.maxcg:.2f}**")

        st.markdown("**Gas-atoms field parameters**")
        colgas1, colgas2 = st.columns(2)
        with colgas1:
            mincg = float(st.session_state.mincg)
            maxcg = float(st.session_state.maxcg)
            threshold_gas = st.number_input(
                "Threshold for Gas-atoms",
                value=mincg + (maxcg - mincg) / 2,
                min_value=mincg,
                step=(maxcg - mincg) / 100,
                max_value=maxcg
            )
            st.session_state.threshold_gas = threshold_gas
        with colgas2:
            color_gas = st.selectbox("Color for Gas-atoms field", list(color_options), index=0)

        if st.session_state.BubblesFileName is not None:
            st.markdown("**Bubbles field parameters**")
            colbub1, colbub2 = st.columns(2)
            with colbub1:
                opacity_bub = st.slider("Opacity for Bubbles field", 0.0, 1.0, 0.5, key="gasinbub_op")
            with colbub2:
                color_bub = st.selectbox("Color for Bubbles field", list(color_options), index=12, key="gasinbub_col")

        show_gr = False
        if st.session_state.GrainsFileName is not None:
            st.markdown("**Grains field parameters**")
            colgr1, colgr2 = st.columns(2)
            with colgr1:
                show_gr = st.checkbox("Show Grain boundaries", value=False, key="gasinbub_showgb")
            with colgr2:
                color_gr = st.selectbox("Color for Grains field", list(color_options), index=5,
                                             key="gasinbubgr_col")

        if st.session_state.BubblesFileName is not None and show_gr:
            fig = show_three_VTK(st.session_state.gr3d, st.session_state.bub3d, st.session_state.gas3d,
                               st.session_state.threshold_grains, st.session_state.threshold_bubbles, st.session_state.threshold_gas,
                               color_gr, color_bub, color_gas, opacity1=1.0, opacity2=opacity_bub, opacity3=1.0)
        elif st.session_state.BubblesFileName is not None and not show_gr:
            fig = show_two_VTK(st.session_state.bub3d, st.session_state.gas3d,
                               st.session_state.threshold_bubbles, st.session_state.threshold_gas,
                               color_bub, color_gas, opacity1=opacity_bub, opacity2=1.0)
        elif st.session_state.BubblesFileName is None and show_gr:
            fig = show_two_VTK(st.session_state.gr3d, st.session_state.gas3d,
                               st.session_state.threshold_grains, st.session_state.threshold_gas,
                               color_gr, color_gas, opacity1=1.0, opacity2=1.0)
        else:
            fig = show_VTK(st.session_state.gas3d, st.session_state.threshold_gas, color_gas)
        st.plotly_chart(fig, width="stretch")


@st.fragment
def show_results_vac_in_bubbles():
    st.subheader("***Vacancies in Bubbles***")
    VacFileName = st.file_uploader(
        "Download vacancies file",
        type=["vtk"],
        key="vac_uploader",
        on_change=reset_vac,
    )
    if VacFileName is not None:
        st.session_state.VacFileName = VacFileName.name
        if st.session_state.vac3d is None:
            vac3d, vacfname = getdata(VacFileName)
            mincv = vac3d.min()
            maxcv = vac3d.max()
            st.session_state.vac3d = vac3d
            st.session_state.vacfname = vacfname
            st.session_state.mincv = mincv
            st.session_state.maxcv = maxcv

        colminv, colmaxv = st.columns(2)
        with colminv:
            st.success(f"Minimal value: **{st.session_state.mincv:.2f}**")
        with colmaxv:
            st.success(f"Maximal value: **{st.session_state.maxcv:.2f}**")

        st.markdown("**Vacancies field parameters**")
        colvac1, colvac2 = st.columns(2)
        with colvac1:
            mincv = float(st.session_state.mincv)
            maxcv = float(st.session_state.maxcv)
            threshold_vac = st.number_input(
                "Threshold for Vacancies",
                value=mincv + (maxcv - mincv) / 2,
                min_value=mincv,
                step=(maxcv - mincv) / 100,
                max_value=maxcv
            )
            st.session_state.threshold_vac = threshold_vac
        with colvac2:
            color_vac = st.selectbox("Color for Vacancies field", list(color_options), index=2)

        if st.session_state.BubblesFileName is not None:
            st.markdown("**Bubbles field parameters**")
            colbub1, colbub2 = st.columns(2)
            with colbub1:
                opacity_bub = st.slider("Opacity for Bubbles field", 0.0, 1.0, 0.5, key="vacinbub_op")
            with colbub2:
                color_bub = st.selectbox("Color for Bubbles field", list(color_options), index=12, key="vacinbub_col")

        show_gr = False
        if st.session_state.GrainsFileName is not None:
            st.markdown("**Grains field parameters**")
            colgr1, colgr2 = st.columns(2)
            with colgr1:
                show_gr = st.checkbox("Show Grain boundaries", value=False, key="vacinbub_showgb")
            with colgr2:
                color_gr = st.selectbox("Color for Grains field", list(color_options), index=5,
                                             key="vacinbubgr_col")

        if st.session_state.BubblesFileName is not None and show_gr:
            fig = show_three_VTK(st.session_state.gr3d, st.session_state.bub3d, st.session_state.vac3d,
                               st.session_state.threshold_grains, st.session_state.threshold_bubbles, st.session_state.threshold_vac,
                               color_gr, color_bub, color_vac, opacity1=1.0, opacity2=opacity_bub, opacity3=1.0)
        elif st.session_state.BubblesFileName is not None and not show_gr:
            fig = show_two_VTK(st.session_state.bub3d, st.session_state.vac3d,
                               st.session_state.threshold_bubbles, st.session_state.threshold_vac,
                               color_bub, color_vac, opacity1=opacity_bub, opacity2=1.0)
        elif st.session_state.BubblesFileName is None and show_gr:
            fig = show_two_VTK(st.session_state.gr3d, st.session_state.vac3d,
                               st.session_state.threshold_grains, st.session_state.threshold_vac,
                               color_gr, color_vac, opacity1=1.0, opacity2=1.0)
        else:
            fig = show_VTK(st.session_state.vac3d, st.session_state.threshold_vac, color_vac)
        st.plotly_chart(fig, width="stretch")


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
    # r2LSW = distribs["r2_LSW"]

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
                disabled=(not LSW_ok)
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

    st.image(fig, width="stretch")

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
    grains = st.session_state["results_grains"]
    bubbles = st.session_state["results_bubbles"]
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
    # grains = st.session_state["results_grains"]
    # bubbles = st.session_state["results_bubbles"]
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
        st.image(fig_rd, width="stretch")

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

@st.fragment
def show_results_fission_dependencies():

    dataFileName = st.file_uploader(
        "Download data-file",
        type=["txt", "dat"],
        key="data_uploader",
        # on_change=reset_gas,
    )

    if dataFileName:
        st.subheader(f"📈 Graphical results")
        text_rows, data_columns, num_columns = parse_tab_file(dataFileName)
        num_of_text_rows = len(text_rows)
        for j in range(len(text_rows)):
            if len(text_rows[j]) < num_columns:
                delta = num_columns - len(text_rows[j])
                for i in range(delta):
                    text_rows[j].append("")

        digits = len(str(int(data_columns[0][-1]))) - 1

        curve = [False] * (num_columns - 1)
        colData1, colData2 = st.columns([5, 1])
        with colData2:
            st.divider()
            st.markdown("**Select dependence:**")
            for i in range(num_columns - 1):
                curve[i] = st.checkbox(f"{text_rows[0][i + 1]}({text_rows[0][0]})", value=(i == 0))
            st.divider()
            log_x = st.checkbox("Log-scale x-axis")
            divide_x = st.checkbox("Divide by factor x-axis")
            if divide_x:
                power = st.number_input(
                    "Enter a power a for 10^a",
                    value=digits,
                    min_value=17,
                    max_value=22,
                    step=17
                )
                divider = 10 ** power
                for i in range(len(data_columns[0])):
                    data_columns[0][i] /= divider
            log_y = st.checkbox("Log-scale y-axis")
            st.divider()

        with colData1:
            fig_time = make_time_dependence_png(text_rows, data_columns, num_columns,
                                 curve, log_x, log_y, color_options)
            st.image(fig_time, width="stretch")
        with colData2:
            st.download_button(
                label="📥 Download plot as PNG",
                data=fig_time,
                file_name=f"{dataFileName.name}.png",
                mime="image/png"
            )
        # print(f"len(text_rows) = {len(text_rows)}")
        # print(f"len(text_rows[0]) = {len(text_rows[0])}")
        # print(f"len(text_rows[1]) = {len(text_rows[1])}")
        # print("Text rows:")
        # for row in text_rows:
        #     print(row)
        # print("\nData columns:")
        # for i, col in enumerate(data_columns):
        #     print(f"Column {i}: {col[:5]} ...")  # показати перші 5 значень
