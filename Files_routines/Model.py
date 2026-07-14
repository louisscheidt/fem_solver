from numpy import zeros
import sys,os

class Model:
    def __init__(self):
        self.dir = os.path.dirname(os.path.abspath('_'))+'/'
        self.tmp_dir = "Temp_files/"
        self.sim_data_dir = "Sim_data/"
        self.param_dir = "Files_parameters/"
        self.file_model = "PARAM_MODEL"
        self.file_table_coord = "Coordinates_table"
        self.file_table_connect = "connectivities_table"

        self.elem_type = None
        self.mat_routine = None

        self.table_coord = None
        self.table_connect = None

        self.dim = None 
        self.mcrd = None 
        self.nnode = None 
        self.nnode_tot = None 
        self.nelem = None 
        self.ndofel = None 
        self.ndofel_tot = None 

        self.nprops = None 
        self.ndi = None 
        self.nshr = None 
        self.ntens = None 
        self.nsvars = None
        self.n_GP = None

        self.svars = None
        self.props = None

        self.Fext = None
        self.Fint = None

        self.U = None
        self.U_last = None

        self.V = None
        self.V_last = None

        self.A = None

        self.dt = None
        self.dt_last = 0.


    def initialize(self):
        #Get param
        file_path = self.dir + self.tmp_dir + self.file_model
        with open(file_path,"r") as f:
            data = f.readlines()

        while True:
            if (data[-1]) == "":
                del(data[-1])
            else:
                break
        
        for i,j in enumerate(data):
            line = j.split(":")
            param = line[0].strip()
            value = line[1].strip()
            if param == "Material":
                self.mat_routine = value
            elif param == "Element":
                self.elem_type = value
            elif param == "dim":
                self.dim = int(value)
            elif param == "mcrd":
                self.mcrd = int(value)
            elif param == "nnode":
                self.nnode = int(value)
            elif param == "nnode_tot":
                self.nnode_tot = int(value)
            elif param == "nelem":
                self.nelem = int(value)
            elif param == "ndofel":
                self.ndofel = int(value)
            elif param == "ndofel_tot":
                self.ndofel_tot = int(value)
            elif param == "nprops":
                self.nprops = int(value)
            elif param == "ndi":
                self.ndi = int(value)
            elif param == "nshr":
                self.nshr = int(value)
            elif param == "ntens":
                self.ntens = int(value)
            elif param == "nsvars":
                self.nsvars = int(value)
            elif param == "n_GP":
                self.n_GP = int(value)

        #Get coord table
        file_path = self.dir + self.tmp_dir + self.file_table_coord
        with open(file_path,"r") as f:
            data = f.readlines()

        while True:
            if (data[-1]) == "":
                del(data[-1])
            else:
                break

        array_cord = zeros([self.nnode_tot,4])
        for i,j in enumerate(data):
            line = j.split()
            for k in range(4):
                array_cord[i,k] = int(float(line[k]))

        self.table_coord = array_cord

        #Get connect_tabel
        file_path = self.dir + self.tmp_dir + self.file_table_connect
        with open(file_path,"r") as f:
            data = f.readlines()

        while True:
            if (data[-1]) == "":
                del(data[-1])
            else:
                break

        array_connect = zeros([self.nelem,self.nnode+1])
        for i,j in enumerate(data):
            line = j.split()
            for k in range(self.nnode+1):
                array_connect[i,k] = int(float(line[k]))

        self.table_connect = array_connect

        #set up the rest
        self.nsvars = int(self.nsvars*self.n_GP)
        self.init_props()

        self.Fext = zeros([self.ndofel_tot,1])
        self.Fint = zeros([self.ndofel_tot,1])

        self.U = zeros([self.ndofel_tot,1])
        self.U_last = zeros([self.ndofel_tot,1])

        self.V = zeros([self.ndofel_tot,1])
        self.V_last = zeros([self.ndofel_tot,1])

        self.A = zeros([self.ndofel_tot,1])
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