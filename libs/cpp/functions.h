#pragma once
#include <vector>
#include <stack>
#include <cmath>

const int SIZE = 128;

struct DistanceResult {
    std::vector<double> nearest_neighbor_distance;
    std::vector<double> edge_to_edge_distance;
    double mean_nnd = 0.0;
    double mean_edd = 0.0;
};


struct ObjectResult {
    int volume;
    double centrX;
    double centrY;
    double centrZ;
};

struct GrainBoundaries {
    int length;
    std::vector<double> posX;
    std::vector<double> posY;
    std::vector<double> posZ;
};

struct Bubbles_Grains_Distances {
    std::vector<double> bubCentr2grainCentr;
    std::vector<double> bubCentr2grainBound;
    std::vector<double> bubEdge2grainCentr;
    std::vector<double> bubEdge2grainBound;
    double mean_bcgc = 0.0;
    double mean_bcgb = 0.0;
    double mean_begc = 0.0;
    double mean_begb = 0.0;
};


struct BubRad_DistFromGrCentr {
    std::vector<double> dist;
    std::vector<double> radius;
    std::vector<double> dist_gc;
    std::vector<double> rad_gc;
};


struct calc_result {
    int count = 0;
    std::vector<double> list_volume;
    std::vector<double> list_surface;
    std::vector<double> list_radius;
    std::vector<double> list_spheric;
    std::vector<double> list_centerX;
    std::vector<double> list_centerY;
    std::vector<double> list_centerZ;
    double Rp = 0;
    double Np = 0;
    double Vp = 0;
    double Sph = 0;
};


template<int SIZE>
    struct calcPrecipitate3d {
        typedef double data_arr[SIZE][SIZE][SIZE];
        typedef int cluster_arr[SIZE][SIZE][SIZE];
        int size;

        calc_result calcPrecipitate(const double *linearData, double p, int sz, int min_n, int max_n);

        int get(int i);
        ObjectResult fill(int i, int j, int k, int c, double p, data_arr arr_a, cluster_arr arr_b);
        void init_arrays(const double *linearData, data_arr arr_a, cluster_arr arr_b);
    };

template<int SIZE>
int calcPrecipitate3d<SIZE>::get(int i) {
    int result;
    if (i >= size) result = 0;
    else if (i < 0) result = size - 1;
    else result = i;
    return (result);
}

template<int SIZE>
ObjectResult calcPrecipitate3d<SIZE>::fill(int i, int j, int k, int c, double p, data_arr arr_a, cluster_arr arr_b) {
    struct neighbor {
        int i, j, k;
    };

    ObjectResult result;

    std::stack<neighbor> st;

    neighbor delta[6] = {
            {1,  0,  0},
            {-1, 0,  0},
            {0,  1,  0},
            {0,  -1, 0},
            {0,  0,  1},
            {0,  0,  -1},
    };

    int vol, ti, tj, tk;
    vol = 0;
    double sx = 0.0, sy = 0.0, sz = 0.0;
    double cx = 0.0, cy = 0.0, cz = 0.0;

    st.push({i, j, k});
    do {
        neighbor cur = st.top();
        st.pop();

        arr_b[cur.i][cur.j][cur.k] = c;
        vol++;

        double theta_x = 2.0 * M_PI * cur.i / size;
        double theta_y = 2.0 * M_PI * cur.j / size;
        double theta_z = 2.0 * M_PI * cur.k / size;

        cx += cos(theta_x);
        sx += sin(theta_x);

        cy += cos(theta_y);
        sy += sin(theta_y);

        cz += cos(theta_z);
        sz += sin(theta_z);

        for (auto &a: delta) {
            ti = get(cur.i + a.i);
            tj = get(cur.j + a.j);
            tk = get(cur.k + a.k);
            if ((arr_a[ti][tj][tk] >= p) && (arr_b[ti][tj][tk] == 0)) {
                arr_b[ti][tj][tk] = -1;
                st.push({ti, tj, tk});
            }
        }
    } while (!st.empty());
    double theta_cx = atan2(sx, cx);
    double theta_cy = atan2(sy, cy);
    double theta_cz = atan2(sz, cz);

    if (theta_cx < 0) theta_cx += 2.0 * M_PI;
    if (theta_cy < 0) theta_cy += 2.0 * M_PI;
    if (theta_cz < 0) theta_cz += 2.0 * M_PI;

    result.volume = vol;
    result.centrX = size * theta_cx / (2.0 * M_PI);
    result.centrY = size * theta_cy / (2.0 * M_PI);
    result.centrZ = size * theta_cz / (2.0 * M_PI);

    return(result);
}

template<int SIZE>
void calcPrecipitate3d<SIZE>::init_arrays(const double *linearData, data_arr arr_a, cluster_arr arr_b) {
    for (int k = 0; k < size; k++)
        for (int j = 0; j < size; j++) {
            for (int i = 0; i < size; i++) {
                arr_a[i][j][k] = linearData[i + size * j + size * size * k];
                arr_b[i][j][k] = 0;
            }
        }
}

template<int SIZE>
calc_result calcPrecipitate3d<SIZE>::calcPrecipitate(const double *linearData, double p, int sz, int min_n, int max_n) {
	size = sz;
	auto arr_a = new data_arr;
    auto arr_b = new cluster_arr;

    init_arrays(linearData, arr_a, arr_b);
    int c_cnt = 0;
    int vol;
    double radius;
    double surface;
    double spheric;
    double volSum = 0.0;
    double radiusSum = 0.0;
    double sphericSum = 0.0;
    int index = 0;
    calc_result res;
    ObjectResult res_bulb;

    for (int k = 0; k < size; k++)
        for (int j = 0; j < size; j++) {
            for (int i = 0; i < size; i++) {
                if ((arr_a[i][j][k] >= p) && (arr_b[i][j][k] == 0)) {
                    c_cnt++;
                    res_bulb = fill(i, j, k, c_cnt, p, arr_a, arr_b);
                    vol = res_bulb.volume;
                    if ((vol < min_n ) || (vol > max_n)) {
                        c_cnt--;
                        arr_b[i][j][k] = -1;
                    } else {
                        res.list_volume.push_back(vol);
                        res.list_centerX.push_back(res_bulb.centrX);
                        res.list_centerY.push_back(res_bulb.centrY);
                        res.list_centerZ.push_back(res_bulb.centrZ);
                        radius = pow(3.0 * vol / (4.0 * M_PI), 1.0 / 3.0);
                        res.list_radius.push_back(radius);
                        surface = 4.0 * M_PI * radius * radius;
                        res.list_surface.push_back(surface);
                        spheric = (3.0 * vol) / (surface * radius);
                        res.list_spheric.push_back(spheric);
                        radiusSum += radius;
                        sphericSum += spheric;
                        volSum += vol;
                        index ++;
                    }
                }
            }
        }
    delete arr_a;
    delete arr_b;
    res.count = c_cnt;
    if (c_cnt != 0)
    {
        res.Rp = radiusSum / c_cnt;
        res.Np = 1.0 * c_cnt;
        res.Vp = volSum / c_cnt;
        res.Sph = sphericSum / c_cnt;
    }
    return res;
}

DistanceResult computeDistances(int N, const calc_result& resBulb);

Bubbles_Grains_Distances computeBubblGrainDist(
    int N,
    const calc_result& resBulb,
    const calc_result& resGrain,
    const GrainBoundaries& resBound
);
GrainBoundaries makeGB(const double *Data, int M, double p);
BubRad_DistFromGrCentr calc_bubblesSize_on_distance(
    int N,
    int NGrains,
    const calc_result& resBulb,
    const calc_result& resGrain,
    int bins
);


