#include "functions.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

calc_result calc_precipitate_wrapper(
    py::array_t<double,
                py::array::c_style |
                py::array::forcecast> arr,
    double threshold, int M, int min_n, int max_n)
{
    auto buf = arr.request();
    const double* ptr = static_cast<const double*>(buf.ptr);
    calcPrecipitate3d<SIZE> solver;
    return solver.calcPrecipitate(ptr, threshold, M, min_n, max_n);
}


DistanceResult compute_distances_wrapper(int M,
        const calc_result& res)
{
    return computeDistances(M, res);
}


GrainBoundaries make_gb_wrapper(py::array_t<double, py::array::c_style | py::array::forcecast> data,
                           int M,
                           double p)
{
    auto buf = data.request();
    return makeGB(static_cast<const double*>(buf.ptr), M, p);
}


Bubbles_Grains_Distances
compute_bubble_grain_dist_wrapper(
        int M,
        const calc_result& bulbs,
        const calc_result& grains,
        const GrainBoundaries& gb)
{
    return computeBubblGrainDist(M, bulbs, grains, gb);
}


BubRad_DistFromGrCentr
calc_bubbles_size_on_distance_wrapper(
        int M,
        int Ngrains,
        const calc_result& bulbs,
        const calc_result& grains,
        int bins)
{
    return calc_bubblesSize_on_distance(M, Ngrains, bulbs, grains, bins);
}


PYBIND11_MODULE(functions_cpp_v2, m)
{
    m.doc() = "Fast C++ routines for 3D microstructure analysis";
    py::class_<calc_result>(m,"CalcResult")
        .def(py::init<>())
        .def_readwrite("count",&calc_result::count)
        .def_readwrite("list_volume",&calc_result::list_volume)
        .def_readwrite("list_surface",&calc_result::list_surface)
        .def_readwrite("list_radius",&calc_result::list_radius)
        .def_readwrite("list_spheric",&calc_result::list_spheric)
        .def_readwrite("list_centerX",&calc_result::list_centerX)
        .def_readwrite("list_centerY",&calc_result::list_centerY)
        .def_readwrite("list_centerZ",&calc_result::list_centerZ)
        .def_readwrite("Rp",&calc_result::Rp)
        .def_readwrite("Np",&calc_result::Np)
        .def_readwrite("Vp",&calc_result::Vp)
        .def_readwrite("Sph",&calc_result::Sph);

    py::class_<DistanceResult>(m,"DistanceResult")
        .def(py::init<>())
        .def_readwrite("nearest_neighbor_distance",&DistanceResult::nearest_neighbor_distance)
        .def_readwrite("edge_to_edge_distance",&DistanceResult::edge_to_edge_distance)
        .def_readwrite("mean_nnd",&DistanceResult::mean_nnd)
        .def_readwrite("mean_edd",&DistanceResult::mean_edd);

    py::class_<GrainBoundaries>(m,"GrainBoundaries")
        .def(py::init<>())
        .def_readwrite("length",&GrainBoundaries::length)
        .def_readwrite("posX",&GrainBoundaries::posX)
        .def_readwrite("posY",&GrainBoundaries::posY)
        .def_readwrite("posZ",&GrainBoundaries::posZ);

    py::class_<Bubbles_Grains_Distances>(m,"BubblesGrainsDistances")
        .def(py::init<>())
        .def_readwrite("bubCentr2grainCentr",&Bubbles_Grains_Distances::bubCentr2grainCentr)
        .def_readwrite("bubCentr2grainBound",&Bubbles_Grains_Distances::bubCentr2grainBound)
        .def_readwrite("bubEdge2grainCentr",&Bubbles_Grains_Distances::bubEdge2grainCentr)
        .def_readwrite("bubEdge2grainBound",&Bubbles_Grains_Distances::bubEdge2grainBound)
        .def_readwrite("mean_bcgc",&Bubbles_Grains_Distances::mean_bcgc)
        .def_readwrite("mean_bcgb",&Bubbles_Grains_Distances::mean_bcgb)
        .def_readwrite("mean_begc",&Bubbles_Grains_Distances::mean_begc)
        .def_readwrite("mean_begb",&Bubbles_Grains_Distances::mean_begb);

    py::class_<BubRad_DistFromGrCentr>(m,"BubRadDistFromGrCentr")
        .def(py::init<>())
        .def_readwrite("dist",&BubRad_DistFromGrCentr::dist)
        .def_readwrite("radius",&BubRad_DistFromGrCentr::radius)
        .def_readwrite("dist_gc",&BubRad_DistFromGrCentr::dist_gc)
        .def_readwrite("rad_gc",&BubRad_DistFromGrCentr::rad_gc);


    m.def("make_gb", &make_gb_wrapper,py::arg("data"),py::arg("M"),py::arg("p"));
    m.def("calc_precipitate",&calc_precipitate_wrapper);
    m.def("compute_distances",&compute_distances_wrapper);
    m.def("compute_bubble_grain_dist",&compute_bubble_grain_dist_wrapper);
    m.def("calc_bubbles_size_on_distance",&calc_bubbles_size_on_distance_wrapper);

}
