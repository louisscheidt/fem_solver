from numpy import zeros
import sys,os

class Model:
    def __init__(self,mesh):
        self.mesh = mesh

        self.elem_type = None

        self.table_coord = None
        self.table_connect = None

        self.mcrd = None #dim
        self.nelem = None #nbr elem in the mesh
        self.nnode = None #node per elem (only 1 type of elem allowed)
        self.ndofel = None #nbr of dof per elem
        self.nnode_tot = None #nbr of nodes in the mesh
        self.ndofel_tot = None #nbr of dofs in the mesh
        self.nsvars = None #nbr of state variables (stress, strain, plastic strain, porosity, damage, ...)
        self.nprops = None #nbr of material properties
        self.ntens = None #size of vectorized 2nd order tensor (e.g. 3x3 symetric stress tensor -> ntens = 6)
        self.ndef = None #nbr of lines of the B_matrix
        self.n_GP = None #nbr of gauss points per element
        self.ndi = None

        self.svars = None
        self.props = None

        self.Fext = None
        self.Fint = None

        self.U = None
        self.U_last = None

        self.V = None
        self.V_last = None

        self.A = None

        self.tens_vars = 3 #stress,dstran,dplas

        self.dt = None
        self.dt_last = 0.


    def initialize(self):
        self.elem_type = self.mesh.elem_type

        self.table_coord = self.mesh.table_coord
        self.table_connect = self.mesh.table_connect

        self.mcrd = self.mesh.mcrd
        self.ndi = self.mcrd
        self.nelem = self.mesh.nelem
        self.nnode = self.mesh.nnode
        self.nnode_tot = self.mesh.nnode_tot
        self.ndofel = self.mesh.ndofel
        self.ndofel_tot = self.mesh.ndofel_tot

        #a modifier dans le future, devrait être gere au niveau de l'element
        self.n_GP = self.mesh.n_GP
        self.ntens = self.mesh.ntens
        self.ndef = self.mesh.ndef

        self.init_svars()
        self.init_props()

        self.Fext = zeros([self.ndofel_tot,1])
        self.Fint = zeros([self.ndofel_tot,1])

        self.U = zeros([self.ndofel_tot,1])
        self.U_last = zeros([self.ndofel_tot,1])

        self.V = zeros([self.ndofel_tot,1])
        self.V_last = zeros([self.ndofel_tot,1])

        self.A = zeros([self.ndofel_tot,1])
        return

    def init_svars(self):
        nvars = None

        abs_dir = os.path.dirname(os.path.abspath('_'))+'/'
        dir_tmp = "Temp_files/"
        file = "PARAM_MODEL"
        file_path = abs_dir+dir_tmp+file
        if not os.path.exists(file_path):
            print(f"Error - File {file} not found.")
            sys.exit()

        with open(file_path,"r") as f:
            data = f.readlines()

        while True:
            if data[-1] == "":
                del(data[-1])
            else:
                break

        nlines = len(data)
        if nlines == 0:
            print(f"Error - The file {file} seems empty.")
            sys.exit()

        nline = 0
        while nline < nlines:
            line = data[nline]
            if nvars == None:
                if line.startswith("nvars"):
                    line = line.split(":")
                    nvars = int(line[-1])

            nline += 1

        self.nsvars = int(self.ntens*self.tens_vars + nvars)
        self.svars = zeros([(self.n_GP + 1)*self.nsvars])
        return


    def init_props(self):
        abs_dir = os.path.dirname(os.path.abspath('_'))+'/'
        dir_tmp = "Temp_files/"
        file = "PARAM_MATERIAU"
        file_path = abs_dir+dir_tmp+file
        if not os.path.exists(file_path):
            print(f"Error - File {file} not found.")
            sys.exit()

        with open(file_path,"r") as f:
            data = f.readlines()

        while True:
            if data[-1] == "":
                del(data[-1])
            else:
                break

        nlines = len(data)
        if nlines == 0:
            print(f"Error - The file {file} seems empty.")
            sys.exit()

        self.nprops = len(data)
        array_props = zeros([self.nprops])
        for i,j in enumerate(data):
            try:
                line = j.split(":")
                array_props[i] = float(line[-1])
            except:
                print(f"Error - Problem while reading the {file} file.")
                sys.exit()

        self.props = array_props
        return


    def apply_load(self):
        """
        lecture de fichiers préalablement écris et modification des vecteurs initiaux
        """
        return

    def retrieve_nodal_state_elem(self,jelem):
        jelem = jelem - 1 #python compte à partir de 0

        U = zeros([self.ndofel,1])
        U_last = zeros([self.ndofel,1])

        V = zeros([self.ndofel,1])
        V_last = zeros([self.ndofel,1])

        A = zeros([self.ndofel,1])

        Fext = zeros([self.ndofel,1])
        Fint = zeros([self.ndofel,1])

        for i in range(self.nnode):
            node = self.table_coord[jelem,i] - 1 #python compte à partir de 0
            indice1 = node*self.ndofel

            for j in range(self.nodel):
                indice2 = indice1 + j
                U = self.U[indice2,0]
                U_last = self.U_last[indice2,0]

                V = self.V[indice2,0]
                V_last = self.V_last[indice2,0]

                A = self.A[indice2,0]

                Fext = self.Fext[indice2,0]
                Fint = self.Fint[indice2,0]

        return U,U_last,V,V_last,A,Fext,Fint

        def update_nodal_state(self,jelem):
            
            return

        def get_dt(self):

            return