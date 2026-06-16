from skimage.measure import marching_cubes
import plotly.graph_objects as go
import numpy as np


def clip_by_value(field_3d, threshold):
    mask = field_3d >= threshold

    x, y, z = np.where(mask)
    val = field_3d[mask]

    return x, y, z, val


def show_clip(field_3d, threshold):
    x, y, z = np.where(field_3d >= threshold)
    val = field_3d[x, y, z]

    # print("points:", len(x))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="markers",
            marker=dict(
                size=2,
                color=val,
                colorscale="Viridis",
            ),
        )
    )

    return fig


def add_cube_edges(fig, Nx, Ny, Nz):
    # 8 вершин куба
    p = [
        (0, 0, 0),
        (Nx, 0, 0),
        (Nx, Ny, 0),
        (0, Ny, 0),
        (0, 0, Nz),
        (Nx, 0, Nz),
        (Nx, Ny, Nz),
        (0, Ny, Nz),
    ]

    edges = [
        (0,1), (1,2), (2,3), (3,0),  # bottom
        (4,5), (5,6), (6,7), (7,4),  # top
        (0,4), (1,5), (2,6), (3,7)   # vertical
    ]

    for i, j in edges:
        fig.add_trace(
            go.Scatter3d(
                x=[p[i][0], p[j][0]],
                y=[p[i][1], p[j][1]],
                z=[p[i][2], p[j][2]],
                mode="lines",
                line=dict(color="black", width=4),
                showlegend=False
            )
        )

    return fig


def show_VTK(field_3d, threshold, color):
    verts, faces, normals, values = marching_cubes(
        field_3d,
        level=threshold
    )

    Nx, Ny, Nz = field_3d.shape

    fig = go.Figure()

    fig.add_trace(
        go.Mesh3d(
            x=verts[:, 0],
            y=verts[:, 1],
            z=verts[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color=color,
            opacity=1.0,
            showscale=False
        )
    )

    # 🔥 додаємо каркас куба
    fig = add_cube_edges(fig, Nx, Ny, Nz)

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    return fig


def show_two_VTK(field1, field2, th1, th2, color1, color2, opacity1=1.0, opacity2=1.0):
    fig = go.Figure()

    Nx, Ny, Nz = field1.shape

    # --- field 1 ---
    verts1, faces1, _, _ = marching_cubes(field1, level=th1)

    fig.add_trace(go.Mesh3d(
        x=verts1[:, 0],
        y=verts1[:, 1],
        z=verts1[:, 2],
        i=faces1[:, 0],
        j=faces1[:, 1],
        k=faces1[:, 2],
        color=color1,
        opacity=opacity1,
        name="field1"
    ))

    # --- field 2 ---
    verts2, faces2, _, _ = marching_cubes(field2, level=th2)

    fig.add_trace(go.Mesh3d(
        x=verts2[:, 0],
        y=verts2[:, 1],
        z=verts2[:, 2],
        i=faces2[:, 0],
        j=faces2[:, 1],
        k=faces2[:, 2],
        color=color2,
        opacity=opacity2,
        name="field2"
    ))

    # cube frame
    fig = add_cube_edges(fig, Nx, Ny, Nz)

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    return fig


def show_three_VTK(field1, field2, field3, th1, th2, th3, color1, color2, color3, opacity1=1.0, opacity2=1.0, opacity3=1.0):
    fig = go.Figure()

    Nx, Ny, Nz = field1.shape

    # --- field 1 ---
    verts1, faces1, _, _ = marching_cubes(field1, level=th1)

    fig.add_trace(go.Mesh3d(
        x=verts1[:, 0],
        y=verts1[:, 1],
        z=verts1[:, 2],
        i=faces1[:, 0],
        j=faces1[:, 1],
        k=faces1[:, 2],
        color=color1,
        opacity=opacity1,
        name="field1"
    ))

    # --- field 2 ---
    verts2, faces2, _, _ = marching_cubes(field2, level=th2)

    fig.add_trace(go.Mesh3d(
        x=verts2[:, 0],
        y=verts2[:, 1],
        z=verts2[:, 2],
        i=faces2[:, 0],
        j=faces2[:, 1],
        k=faces2[:, 2],
        color=color2,
        opacity=opacity2,
        name="field2"
    ))

    # --- field 3 ---
    verts3, faces3, _, _ = marching_cubes(field3, level=th3)

    fig.add_trace(go.Mesh3d(
        x=verts3[:, 0],
        y=verts3[:, 1],
        z=verts3[:, 2],
        i=faces3[:, 0],
        j=faces3[:, 1],
        k=faces3[:, 2],
        color=color3,
        opacity=opacity3,
        name="field3"
    ))

    # cube frame
    fig = add_cube_edges(fig, Nx, Ny, Nz)

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    return fig


def show_surface_field(field_3d, colorscale="RdBu_r"):
    Nx, Ny, Nz = field_3d.shape

    def plane(x, y, z, c):
        return x, y, z, c

    X = []
    Y = []
    Z = []
    C = []

    # --- 6 граней куба ---

    # z = 0
    x, y = np.meshgrid(np.arange(Nx), np.arange(Ny), indexing="ij")
    z = np.zeros_like(x)
    X.append(x); Y.append(y); Z.append(z); C.append(field_3d[:, :, 0])

    # z = Nz-1
    z = np.full_like(x, Nz-1)
    X.append(x); Y.append(y); Z.append(z); C.append(field_3d[:, :, Nz-1])

    # y = 0
    x, z = np.meshgrid(np.arange(Nx), np.arange(Nz), indexing="ij")
    y = np.zeros_like(x)
    X.append(x); Y.append(y); Z.append(z); C.append(field_3d[:, 0, :])

    # y = Ny-1
    y = np.full_like(x, Ny-1)
    X.append(x); Y.append(y); Z.append(z); C.append(field_3d[:, Ny-1, :])

    # x = 0
    y, z = np.meshgrid(np.arange(Ny), np.arange(Nz), indexing="ij")
    x = np.zeros_like(y)
    X.append(x); Y.append(y); Z.append(z); C.append(field_3d[0, :, :])

    # x = Nx-1
    x = np.full_like(y, Nx-1)
    X.append(x); Y.append(y); Z.append(z); C.append(field_3d[Nx-1, :, :])

    fig = go.Figure()

    for x, y, z, c in zip(X, Y, Z, C):
        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                surfacecolor=c,
                colorscale=colorscale,
                showscale=False,
                opacity=1.0,
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    return fig
