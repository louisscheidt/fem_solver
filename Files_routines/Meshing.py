import os,sys
import meshio

class Mesh:
    def __init__(self,file):
        self.mesh_file = file
        self.extension = None

        self.mcrd = None
        self.nnode = None
        self.nelem = None
        self.nnode_tot = None
        self.elem_type = None
        self.order = None
        self.ndofel = None
        self.ndofel_tot = None
        self.n_GP = None
        self.ndef = None
        self.ntens = None

        self.table_coord = None
        self.table_connect = None

        self.supported_formats = ('msh')

    def get_mesh_data(self):
        self.check_file()
        if self.extension == "msh":
            self.get_data_gmsh_mesh()
        return

    def check_file(self):
        file_path = self.mesh_file

        if not os.path.exists(file_path):
            print(f"Error - Mesh file {self.mesh_file} not found.")
            sys.exit()
        else:
            extension = self.mesh_file.split(".")[-1]
            if extension not in self.supported_formats:
                print("Error - The mesh file format is not yet supported.\n"
                f"Supported mesh file formats : {self.supported_formats}")
            else:
                self.extension = extension
        return

    def get_data_gmsh_mesh(self):
        """
        Assumes that there is only 1 type of element in the mesh
        """

        dim_2d = {"triangle": 2, "triangle6": 2, "quad": 2, "quad8": 2, "quad9": 2}
        dim_3d = {"tetra": 3, "hexahedron": 3, "wedge": 3, "pyramid": 3}

        file_path = self.mesh_file

        mesh = meshio.read(file_path)

        cell_block = next(cb for cb in mesh.cells if cb.type in {**dim_2d, **dim_3d})
        elem_type = cell_block.type

        dimension = {**dim_2d, **dim_3d}[elem_type]
        self.mcrd = int(dimension)

        shape = elem_type.rstrip("0123456789") if elem_type[-1].isdigit() else elem_type

        order = "quadratic" if any(c.isdigit() for c in elem_type) else "linear"
        if order == "linear":
            self.order = 1
        elif order == "quadratic":
            self.order = 2
        else:
            print("Error - Only linear or quadratic elements supported.")
            sys.exit()
        
        coords = mesh.points[:, :dimension]
        
        connectivity = cell_block.data

        self.nelem = connectivity.shape[0]
        self.nnode_tot = coords.shape[0]
        self.nnode = connectivity.shape[1]

        self.ndofel = int(self.nnode*self.mcrd)
        self.ndofel_tot = int(self.nnode_tot*self.mcrd)

        self.elem_type = "C"+str(self.mcrd)+"D"+str(int(self.nnode*self.order))

        self.table_coord = coords
        self.table_connect = connectivity

        if self.elem_type == "C2D4":
            self.n_GP = 4
            self.ntens = 3
            self.ndef = 3
        elif self.elem_type == "C2D3":
            self.n_GP = 3
            self.ntens = 3
            self.ndef = 3
        return