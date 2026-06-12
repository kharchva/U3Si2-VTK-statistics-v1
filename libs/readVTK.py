import pyvista as pv
import numpy as np
from skimage.measure import marching_cubes
import plotly.graph_objects as go


class VTKReader:
    def __init__(self, filename):
        self.filename = filename
        self.mesh = None
        self.dataset_type = None

    def read(self):
        self.mesh = pv.read(self.filename)
        self.dataset_type = type(self.mesh).__name__
        return self

    def info(self):
        m = self.mesh
        print("File:", self.filename)
        print("Type:", self.dataset_type)
        print("Points:", m.n_points)
        print("Cells:", m.n_cells)
        if hasattr(m, "dimensions"):
            print("Dimensions:", tuple(m.dimensions))
        if hasattr(m, "spacing"):
            print("Spacing:", tuple(m.spacing))
        print("Point arrays:")
        for name in m.point_data.keys():
            print("   ", name, m.point_data[name].shape)
        print("Cell arrays:")
        for name in m.cell_data.keys():
            print("   ", name, m.cell_data[name].shape)

    def get_dimensions(self):
        m = self.mesh
        if hasattr(m, "dimensions"):
            return tuple(m.dimensions)
        return None

    def get_spacing(self):
        m = self.mesh
        if hasattr(m, "spacing"):
            return tuple(m.spacing)
        return (1.0, 1.0, 1.0)

    def get_origin(self):
        m = self.mesh
        if hasattr(m, "origin"):
            return tuple(m.origin)
        return (0.0, 0.0, 0.0)

    def get_array_names(self):
        return list(self.mesh.point_data.keys())

    def get_scalar_field(self,
                         name=None,
                         association="point"):
        if association == "point":
            arrays = self.mesh.point_data
        else:
            arrays = self.mesh.cell_data
        if name is None:
            name = list(arrays.keys())[0]
        data = np.asarray(arrays[name])
        dims = self.get_dimensions()
        if dims is None:
            raise ValueError(
                "Dataset has no dimensions."
            )
        Nx, Ny, Nz = dims
        field = data.reshape(
            (Nx, Ny, Nz),
            order="F"
        )
        return field

    def get_vector_field(self,
                         name=None):
        arrays = self.mesh.point_data
        if name is None:
            name = list(arrays.keys())[0]
        data = np.asarray(arrays[name])
        dims = self.get_dimensions()
        Nx, Ny, Nz = dims
        return data.reshape(
            (Nx, Ny, Nz, 3),
            order="F"
        )

    def to_dict(self):
        return {
            "filename": self.filename,
            "dataset_type": self.dataset_type,
            "dimensions": self.get_dimensions(),
            "spacing": self.get_spacing(),
            "origin": self.get_origin(),
            "point_data": {
                k: np.asarray(v)
                for k, v
                in self.mesh.point_data.items()
            },
            "cell_data": {
                k: np.asarray(v)
                for k, v
                in self.mesh.cell_data.items()
            }
        }


def readdatafromVTK(fname):
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False,
                                     suffix=".vtk") as tmp:
        tmp.write(fname.getbuffer())
        path = tmp.name

    reader = (
                VTKReader(path)
                .read()
            )
    data = reader.get_scalar_field()
    Nx, Ny, Nz = reader.get_dimensions()
    return Nx, Ny, Nz, data, fname.name

#
# if __name__ == "__main__":
#
#     start = time.perf_counter()
#
#     name1 = "Chi_FD57392E17_f05T700noGr.vtk"
#     reader = (
#         VTKReader(name1)
#         .read()
#     )
#     reader.info()
#     Nx, Ny, Nz = reader.get_dimensions()
#     field_3d1 = reader.get_scalar_field()
#     fig1 = show_VTK_case2(field_3d1, Nx, Ny, Nz, 0.9)
#     fig1.show()
#
#     end = time.perf_counter()
#     print(f"Time: {end - start:.6f} s")

