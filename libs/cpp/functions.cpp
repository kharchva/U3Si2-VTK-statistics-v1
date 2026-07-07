#include "functions.h"
#include <algorithm>
#include <limits>


double pbc_dist(double dx, double dy, double dz, double L)
{
    dx = fabs(dx);
    dy = fabs(dy);
    dz = fabs(dz);

    dx = std::min(dx, L - dx);
    dy = std::min(dy, L - dy);
    dz = std::min(dz, L - dz);

    return sqrt(dx*dx + dy*dy + dz*dz);
}

DistanceResult computeDistances(int N,
        const calc_result& resBulb)
{
    int count = resBulb.count;
    std::vector<double> centerX = resBulb.list_centerX;
    std::vector<double> centerY = resBulb.list_centerY;
    std::vector<double> centerZ = resBulb.list_centerZ;
    std::vector<double> radius = resBulb.list_radius;

    DistanceResult res;

    res.nearest_neighbor_distance.resize(count, 0.0);
    res.edge_to_edge_distance.resize(count, 0.0);

    double L = (double)N;
    int min_j = 0;
    for (int i = 0; i < count; i++)
    {
        double minDist = std::numeric_limits<double>::max();
        int min_j = -1;

        for (int j = 0; j < count; j++)
        {
            if (i == j) continue;

            double dx = centerX[i] - centerX[j];
            double dy = centerY[i] - centerY[j];
            double dz = centerZ[i] - centerZ[j];

            double d = pbc_dist(dx, dy, dz, L);
            if (d < (radius[i] + radius[j])) continue;
            if (d < minDist)
            {
                minDist = d;
                min_j = j;
            }
        }

        res.nearest_neighbor_distance[i] = minDist;

        double ed = minDist - (radius[i] + radius[min_j]);
        res.edge_to_edge_distance[i] = ed;

        res.mean_nnd += minDist;
        res.mean_edd += ed;
    }
    if (count > 0)
    {
        res.mean_nnd /= count;
        res.mean_edd /= count;
    }

    return res;
}

Bubbles_Grains_Distances computeBubblGrainDist(int N,
        const calc_result& resBulb,
        const calc_result& resGrain,
        const GrainBoundaries& resBound)
{
    Bubbles_Grains_Distances res;

    std::vector<double> cBx = resBulb.list_centerX;
    std::vector<double> cBy = resBulb.list_centerY;
    std::vector<double> cBz = resBulb.list_centerZ;
    std::vector<double> rB = resBulb.list_radius;
    int nB = resBulb.count;
    std::vector<double> cGx = resGrain.list_centerX;
    std::vector<double> cGy = resGrain.list_centerY;
    std::vector<double> cGz = resGrain.list_centerZ;
    std::vector<double> rG = resGrain.list_radius;
    int nG = resGrain.count;
    std::vector<double> GBx = resBound.posX;
    std::vector<double> GBy = resBound.posY;
    std::vector<double> GBz = resBound.posZ;
    int nGB = resBound.length;
    res.bubCentr2grainBound.resize(nB, 0.0);
    res.bubCentr2grainCentr.resize(nB, 0.0);
    res.bubEdge2grainBound.resize(nB, 0.0);
    res.bubEdge2grainCentr.resize(nB, 0.0);

    double L = (double)N;
    for (int i = 0; i < nB; i++)
    {
        double minDist = std::numeric_limits<double>::max();
        for (int j = 0; j < nG; j++)
        {
            double dx = cBx[i] - cGx[j];
            double dy = cBy[i] - cGy[j];
            double dz = cBz[i] - cGz[j];

            double d = pbc_dist(dx, dy, dz, L);
            if (d < minDist)
                minDist = d;
        }
        res.bubCentr2grainCentr[i] = minDist;
        res.bubEdge2grainCentr[i] = minDist - rB[i];
        res.mean_bcgc += minDist;
        res.mean_begc += minDist - rB[i];

        double minDistGB = std::numeric_limits<double>::max();
        for (int j = 0; j < nGB; j++)
        {
            double dx = cBx[i] - GBx[j];
            double dy = cBy[i] - GBy[j];
            double dz = cBz[i] - GBz[j];

            double d = pbc_dist(dx, dy, dz, L);
            if (d < minDistGB)
                minDistGB = d;
        }
        res.bubCentr2grainBound[i] = minDistGB;
        res.bubEdge2grainBound[i] = minDistGB - rB[i];
        res.mean_bcgb += minDistGB;
        res.mean_begb += minDistGB - rB[i];
    }
    if (nB > 0)
    {
        res.mean_bcgb /= nB;
        res.mean_bcgc /= nB;
        res.mean_begb /= nB;
        res.mean_begc /= nB;
    }
    return res;
}


GrainBoundaries makeGB(const double *Data, int M, double p)
{
    GrainBoundaries res_gb;
    int num = 0;
    for (int k = 0; k < M; k++)
    for (int j = 0; j < M; j++)
    for (int i = 0; i < M; i++)
    {
        int idx = i + M*j + M*M*k;
        if (Data[idx] < p)
        {
            res_gb.posX.push_back(i);
            res_gb.posY.push_back(j);
            res_gb.posZ.push_back(k);
            num++;
        }
    }
    res_gb.length = num;
    return res_gb;
}


BubRad_DistFromGrCentr calc_bubblesSize_on_distance(int N, int NGrains,
        const calc_result& resBulb,
        const calc_result& resGrain,
        int bins)
{
    std::vector<double> cBx = resBulb.list_centerX;
    std::vector<double> cBy = resBulb.list_centerY;
    std::vector<double> cBz = resBulb.list_centerZ;
    std::vector<double> rB = resBulb.list_radius;
    int nB = resBulb.count;
    std::vector<double> cGx = resGrain.list_centerX;
    std::vector<double> cGy = resGrain.list_centerY;
    std::vector<double> cGz = resGrain.list_centerZ;
    std::vector<double> rG = resGrain.list_radius;

    /////////////////////////////////////////////////////////////////

    int n = rG.size();

    // Створюємо індекси
    std::vector<int> idx(n);
    for (int i = 0; i < n; ++i)
        idx[i] = i;

    // Сортуємо індекси за спаданням rG
    std::sort(idx.begin(), idx.end(),
        [&](int i, int j) {
            return rG[i] > rG[j];
        });

    // Створюємо нові відсортовані вектори
    std::vector<double> cGx_sorted(n);
    std::vector<double> cGy_sorted(n);
    std::vector<double> cGz_sorted(n);
    std::vector<double> rG_sorted(n);

    for (int i = 0; i < n; ++i)
    {
        cGx_sorted[i] = cGx[idx[i]];
        cGy_sorted[i] = cGy[idx[i]];
        cGz_sorted[i] = cGz[idx[i]];
        rG_sorted[i]  = rG[idx[i]];
    }

    // За потреби замінюємо оригінальні
    cGx = cGx_sorted;
    cGy = cGy_sorted;
    cGz = cGz_sorted;
    rG  = rG_sorted;

    /////////////////////////////////////////////////////////////////

//    int nG = resGrain.count;
    int nG = NGrains;
    double L = (double)N;
    int num = 0;
    std::vector<double> dist;
    std::vector<double> radius;

    for(int j = 0; j < nG; j ++)
    {
        for(int i = 0; i < nB; i++)
        {
            double dx = cBx[i] - cGx[j];
            double dy = cBy[i] - cGy[j];
            double dz = cBz[i] - cGz[j];
            double d = pbc_dist(dx, dy, dz, L);
            if (d < rG[j] / 2.0)
            {
                dist.push_back(d);
                radius.push_back(rB[i]);
                num ++;
            }
        }
    }

    std::vector<double> dist_gc;
    std::vector<double> rad_gc;

    auto [minIt1, maxIt1] = std::minmax_element(
            dist.begin(),
            dist.end()
        );

    double min_bc2gc = *minIt1;
    double max_bc2gc = *maxIt1;

    double delta_bc2gc = (max_bc2gc - min_bc2gc) / bins;
    double cur_d, Rmean;
    int Nb;
    for(int i = 0; i < bins; i ++)
    {
        cur_d = min_bc2gc + i * delta_bc2gc;
        Rmean = 0.0;
        Nb = 0;
        for(int j = 0; j < num; j++)
        {
            if ( (dist[j] >= cur_d) && (dist[j] < cur_d + delta_bc2gc) )
            {
                Rmean += radius[j];
                Nb ++;
            }
        }
//        if (Nb > 0) Rmean /= Nb;
//        else Rmean = 0.0;
//        double d = cur_d + delta_bc2gc / 2.0;
//        dist_gc.push_back(d);
//        rad_gc.push_back(Rmean);

        if (Nb > 0)
        {
            Rmean /= Nb;
            double d = cur_d + delta_bc2gc / 2.0;
            dist_gc.push_back(d);
            rad_gc.push_back(Rmean);
        }
    }


    BubRad_DistFromGrCentr res;
    res.dist = dist;
    res.radius = radius;
    res.dist_gc = dist_gc;
    res.rad_gc = rad_gc;
    return res;

}

