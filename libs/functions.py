import libs.functions_cpp_v2 as cpp
import numpy as np
import pandas as pd
import io
import zipfile
from libs.readVTK import readdatafromVTK
from libs.paraview import show_VTK
from libs.paraview import show_two_VTK
from libs.paraview import show_surface_field
from libs.distributions import calc_distribution_from_data


def calc_bulbes(BubblesFileName, threshold_bubbles, M, nbins, scale, vol_cm3):
    Nx, Ny, Nz, bubbles3d, fnameBulbs = readdatafromVTK(BubblesFileName)
    bubbles1d = bubbles3d.reshape(Nx * Ny * Nz)
    figBulbs = show_VTK(bubbles3d, Nx, Ny, Nz, threshold_bubbles, "blue")
    resBulbs = cpp.calc_precipitate(bubbles1d, threshold_bubbles, M)

    data_size = np.array(resBulbs.list_radius) * scale
    fname_size = "size_bubbles_dist"
    dictBulbs_size_dist, dataBulbs_size_dist = calc_distribution_from_data(
        data_size, fname_size, nbins, "dist", vol_cm3)

    fname_size_dens = "size_bubbles_dens"
    dictBulbs_size_dens, dataBulbs_size_dens = calc_distribution_from_data(
        data_size, fname_size_dens, nbins, "dens", vol_cm3)

    data_size_mean = np.array(resBulbs.list_radius) / resBulbs.Rp

    fname_size_mean_dist = "size_bubbles_mean_dist"
    dictBulbs_size_mean_dist, dataBulbs_size_mean_dist = calc_distribution_from_data(
        data_size_mean, fname_size_mean_dist, nbins, "dist", vol_cm3)

    fname_size_mean_dens = "size_bubbles_mean_dens"
    dictBulbs_size_mean_dens, dataBulbs_size_mean_dens = calc_distribution_from_data(
        data_size_mean, fname_size_mean_dens, nbins, "dens", vol_cm3)

    resDists = cpp.compute_distances(M, resBulbs)

    data_nn_dist = np.array(resDists.nearest_neighbor_distance) * scale
    fname_nn_dist = "nn_dist_bubbles"
    dictBulbs_nn_dist, dataBulbs_nn_dist = calc_distribution_from_data(
        data_nn_dist, fname_nn_dist, nbins, "dist", vol_cm3)

    data_edge_dist = np.array(resDists.edge_to_edge_distance) * scale
    fname_edge_dist = "edge_dist_bubbles"
    dictBulbs_edge_dist, dataBulbs_edge_dist = calc_distribution_from_data(
        data_edge_dist, fname_edge_dist, nbins, "dist", vol_cm3)

    bulbs_dict = {
        fname_size: dictBulbs_size_dist,
        fname_size_dens: dictBulbs_size_dens,
        fname_size_mean_dist: dictBulbs_size_mean_dist,
        fname_size_mean_dens: dictBulbs_size_mean_dens,
        fname_nn_dist: dictBulbs_nn_dist,
        fname_edge_dist: dictBulbs_edge_dist
    }
    bulbs_data = {
        fname_size: dataBulbs_size_dist,
        fname_size_dens: dataBulbs_size_dens,
        fname_size_mean_dist: dataBulbs_size_mean_dist,
        fname_size_mean_dens: dataBulbs_size_mean_dens,
        fname_nn_dist: dataBulbs_nn_dist,
        fname_edge_dist: dataBulbs_edge_dist
    }

    dfBulbs = pd.DataFrame({
        "Parameter": ["Mean radius", "Number density", "Center-to-center distance", "Edge-to-edge distance"],
        "Value": [
            resBulbs.Rp * scale,
            resBulbs.count / vol_cm3 * 1E-14,
            resDists.mean_nnd * scale,
            resDists.mean_edd * scale
        ],
        "Dimension": ["[nm]", "[cm⁻³] (×10¹⁴)", "[nm]", "[nm]"]
    })
    dfBulbs_pivot = dfBulbs.set_index("Parameter")

    results_bulbs = {
        "df_bulbs": dfBulbs_pivot,
        "fig_bulbs": figBulbs,
        "res_bulbs": resBulbs,
        "fname_bulbs": fnameBulbs,
        "res_bubbles3d": bubbles3d,
        "dict": bulbs_dict,
        "data": bulbs_data
    }

    return results_bulbs


def calc_grains(GrainsFileName, threshold_grains, M, nbins, scale, vol_cm3):
    Nx, Ny, Nz, grains3d, fnameGrains = readdatafromVTK(GrainsFileName)
    grains1d = grains3d.reshape(Nx * Ny * Nz)
    figGrains = show_surface_field(grains3d)
    resGrains = cpp.calc_precipitate(grains1d, threshold_grains, M)

    data_size = np.array(resGrains.list_radius) * scale

    fname_size_dist = "size_grains_dist"
    dictGrains_size_dist, dataGrains_size_dist = calc_distribution_from_data(
        data_size, fname_size_dist, nbins, "dist", vol_cm3)

    fname_size_dens = "size_grains_dens"
    dictGrains_size_dens, dataGrains_size_dens = calc_distribution_from_data(
        data_size, fname_size_dens, nbins, "dens", vol_cm3)

    data_size_mean = np.array(resGrains.list_radius) / resGrains.Rp

    fname_size_mean_dist = "size_grains_mean_dist"
    dictGrains_size_mean_dist, dataGrains_size_mean_dist = calc_distribution_from_data(
        data_size_mean, fname_size_mean_dist, nbins, "dist", vol_cm3)

    fname_size_mean_dens = "size_grains_mean_dens"
    dictGrains_size_mean_dens, dataGrains_size_mean_dens = calc_distribution_from_data(
        data_size_mean, fname_size_mean_dens, nbins, "dens", vol_cm3)

    grains_dict = {
        fname_size_dist: dictGrains_size_dist,
        fname_size_dens: dictGrains_size_dens,
        fname_size_mean_dist: dictGrains_size_mean_dist,
        fname_size_mean_dens: dictGrains_size_mean_dens
    }

    grains_data = {
        fname_size_dist: dataGrains_size_dist,
        fname_size_dens: dataGrains_size_dens,
        fname_size_mean_dist: dataGrains_size_mean_dist,
        fname_size_mean_dens: dataGrains_size_mean_dens
    }

    dfGrains = pd.DataFrame({
        "Parameter": ["Mean size", "Number density"],
        "Value": [
            resGrains.Rp * scale,
            resGrains.count / vol_cm3 * 1E-12
        ],
        "Dimension": ["[nm]", "[cm⁻³] (×10¹²)"]
    })
    dfGrains_pivot = dfGrains.set_index("Parameter")

    num_of_grains_for_calc = sum(r > resGrains.Rp for r in resGrains.list_radius)

    results_grains = {
        "num_of_grains_for_calc": num_of_grains_for_calc,
        "df_grains": dfGrains_pivot,
        "fig_grains": figGrains,
        "res_grains": resGrains,
        "fname_grains": fnameGrains,
        "res_grains1d":  grains1d,
        "res_grains3d": grains3d,
        "dict": grains_dict,
        "data": grains_data
    }

    return results_grains


def calc_bubbles_in_grains(res_gr, res_bub, thr_gr, thr_bub, M, nbins, scale, vol_cm3):
    resGrains = res_gr["res_grains"]
    resBulbs = res_bub["res_bulbs"]
    grains1d = res_gr["res_grains1d"]
    grains3d = res_gr["res_grains3d"]
    bubbles3d = res_bub["res_bubbles3d"]
    figBulbsGrains = show_two_VTK(
        grains3d,
        bubbles3d,
        M, M, M,
        thr_gr,
        thr_bub,
        "orange",
        "blue"
    )
    resBound = cpp.make_gb(grains1d, M, thr_gr)
    resBubGrDist = cpp.compute_bubble_grain_dist(M, resBulbs, resGrains, resBound)

    data_bcgc_dist = np.array(resBubGrDist.bubCentr2grainCentr) * scale
    fname_bcgc_dist = "bub_center_grain_center_dist"
    dictBulbs_bcgc_dist, dataBulbs_bcgc_dist = calc_distribution_from_data(
        data_bcgc_dist, fname_bcgc_dist, nbins, "dist", vol_cm3)

    data_bcgb_dist = np.array(resBubGrDist.bubCentr2grainBound) * scale
    fname_bcgb_dist = "bub_center_grain_bound_dist"
    dictBulbs_bcgb_dist, dataBulbs_bcgb_dist = calc_distribution_from_data(
        data_bcgb_dist, fname_bcgb_dist, nbins, "dist", vol_cm3)

    data_begc_dist = np.array(resBubGrDist.bubEdge2grainCentr) * scale
    fname_begc_dist = "bub_edge_grain_center_dist"
    dictBulbs_begc_dist, dataBulbs_begc_dist = calc_distribution_from_data(
        data_begc_dist, fname_begc_dist, nbins, "dist", vol_cm3)

    data_begb_dist = np.array(resBubGrDist.bubEdge2grainBound) * scale
    fname_begb_dist = "bub_edge_grain_bound_dist"
    dictBulbs_begb_dist, dataBulbs_begb_dist = calc_distribution_from_data(
        data_begb_dist, fname_begb_dist, nbins, "dist", vol_cm3)

    bubbles_in_grains_dict = {
        fname_bcgc_dist: dictBulbs_bcgc_dist,
        fname_bcgb_dist: dictBulbs_bcgb_dist,
        fname_begc_dist: dictBulbs_begc_dist,
        fname_begb_dist: dictBulbs_begb_dist
    }

    bubbles_in_grains_data = {
        fname_bcgc_dist: dataBulbs_bcgc_dist,
        fname_bcgb_dist: dataBulbs_bcgb_dist,
        fname_begc_dist: dataBulbs_begc_dist,
        fname_begb_dist: dataBulbs_begb_dist
    }

    dfBubsGrains = pd.DataFrame({
        "Parameter": ["Mean nearest distance bubble-center to grain-center",
                      "Mean nearest distance bubble-edge to grain-center",
                      "Mean nearest distance bubble-center to grain-boundary",
                      "Mean nearest distance bubble-edge to grain-boundary"],
        "Value": [
            resBubGrDist.mean_bcgc * scale,
            resBubGrDist.mean_begc * scale,
            resBubGrDist.mean_bcgb * scale,
            resBubGrDist.mean_begb * scale
        ],
        "Dimension": ["[nm]", "[nm]", "[nm]", "[nm]"]
    })
    dfBubsGrains_pivot = dfBubsGrains.set_index("Parameter")

    results_bubbles_in_grains = {
        "df_bubingrains": dfBubsGrains_pivot,
        "fig_bulbsgrains": figBulbsGrains,
        "res_dist_bulbs_grains": resBubGrDist,
        "dict": bubbles_in_grains_dict,
        "data": bubbles_in_grains_data
    }

    return results_bubbles_in_grains


def calc_bubbleRadius_on_dist_grainCenter(M, grains, bubbles, num_of_grains, num_of_bins, scale, fname):
    resBulb = bubbles["res_bulbs"]
    resGrain = grains["res_grains"]

    resBubRad_vs_distGrCenter = cpp.calc_bubbles_size_on_distance(
        M, num_of_grains, resBulb, resGrain, num_of_bins)

    dist = np.asarray(resBubRad_vs_distGrCenter.dist)
    radius = np.asarray(resBubRad_vs_distGrCenter.radius)
    idx = np.argsort(dist)
    dist = dist[idx]
    radius = radius[idx]
    dist_all = dist * scale
    rad_all = radius * scale
    dist_av = np.asarray(resBubRad_vs_distGrCenter.dist_gc) * scale
    rad_av = np.asarray(resBubRad_vs_distGrCenter.rad_gc) * scale

    dict_to_return = {
        "dist_to_grCentr": dist_all,
        "bubbleRadius": rad_all,
        "dist_to_grCentr_bins": dist_av,
        "mean_bubbleRadius": rad_av
    }

    datasets = {
        f"{fname}_all.txt": list(zip(dist_all, rad_all)),
        f"{fname}_average_{num_of_bins}.txt": list(zip(dist_av, rad_av))
    }

    return dict_to_return, datasets


dictXlable = {
    "size_bubbles_dist": "Bubbles radius Rb [nm]",
    "size_bubbles_dens": "Bubbles radius Rb [nm]",
    "size_bubbles_mean_dist": "Bubbles radius Rb / ⟨Rb⟩",
    "size_bubbles_mean_dens": "Bubbles radius Rb / ⟨Rb⟩",
    "nn_dist_bubbles": "Nearest center-to-center distance between bubbles [nm]",
    "edge_dist_bubbles": "Nearest edge-to-edge distance between bubbles [nm]",
    "size_grains_dist": "Grain size Rg [nm]",
    "size_grains_dens": "Grain size Rg [nm]",
    "size_grains_mean_dist": "Grain size Rg / ⟨Rg⟩",
    "size_grains_mean_dens": "Grain size Rg / ⟨Rg⟩",
    "bub_center_grain_center_dist": "Nearest distance from bubble center to grain center [nm]",
    "bub_center_grain_bound_dist": "Nearest distance from bubble center to grain boundary [nm]",
    "bub_edge_grain_center_dist": "Nearest distance from bubble edge to grain center [nm]",
    "bub_edge_grain_bound_dist": "Nearest distance from bubble edge to grain boundary [nm]"
}

dictYlable = {
    "size_bubbles_dist": "Normalized distribution",
    "size_bubbles_dens": "Number density of bubbles [cm⁻³]",
    "size_bubbles_mean_dist": "Normalized distribution",
    "size_bubbles_mean_dens": "Number density of bubbles [cm⁻³]",
    "nn_dist_bubbles": "Normalized distribution",
    "edge_dist_bubbles": "Normalized distribution",
    "size_grains_dist": "Normalized distribution",
    "size_grains_dens": "Number density of grains [cm⁻³]",
    "size_grains_mean_dist": "Normalized distribution",
    "size_grains_mean_dens": "Number density of grains [cm⁻³]",
    "bub_center_grain_center_dist": "Normalized distribution",
    "bub_center_grain_bound_dist": "Normalized distribution",
    "bub_edge_grain_center_dist": "Normalized distribution",
    "bub_edge_grain_bound_dist": "Normalized distribution"
}


def fig_labels(fname):
    return dictXlable[fname], dictYlable[fname]


def make_zip_from_dict(data_dict, fig=None, fig_name="figure.png"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Додаємо текстові файли
        for file_name, data_list in data_dict.items():
            txt_io = io.StringIO()
            for row in data_list:
                txt_io.write("\t".join(f"{val:.6f}" for val in row) + "\n")
            txt_io.seek(0)
            zf.writestr(file_name, txt_io.getvalue())

        # Додаємо фігуру, якщо вона є
        if fig is not None:
            zf.writestr(fig_name, fig)
            # img_io = io.BytesIO()
            # fig.savefig(img_io, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
            # img_io.seek(0)
            # zf.writestr(fig_name, img_io.getvalue())

    zip_buffer.seek(0)
    return zip_buffer


