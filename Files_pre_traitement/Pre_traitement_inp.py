import os,sys
from numpy import zeros,shape,arange,asarray
import shutil

class Pre_treatment():
    def __init__(self,file):
        self.file = file
        self.extension = "inp"
        self.dir = os.path.dirname(os.path.abspath('_'))+'/'
        self.input_dir = "Files_input/"
        self.tmp_dir = "Temp_files/"
        self.sim_data_dir = "Sim_data/"
        self.routines_dir = "Files_routines/"
        self.param_dir = "Files_parameters/"
        self.file_model = "PARAM_MODEL"
        self.file_table_coord = "Coordinates_table"
        self.file_table_connect = "connectivities_table"
        self.file_node_sets = "node_sets"
        self.file_BC = "boundary_conditions"
        self.file_path = None

        self.routines = ["Model.py","Solver_explicit.py","Calc_Fint_explicit.py"]
        self.mat_routine = None

        self.supported_elem = ["C2D4"]
        self.dic_elem = { #key: element type, values: (dim,ngp)
            "C2D4" : (2,4),
        }

        self.dic_material_law = { #key: index material lax, values : (file name correponding to the routine,nprops,ntens_vars,nvars)
            1 : ("Loi_materiau_elastique",3,2,0)
        }

        self.nBC = None
        self.bc_dic = {} #key:number of the BC, values:(type of BC,node set, array containing the applied direction,amplitude for each direction)
        self.nNode_set = None
        self.node_sets_dic = {} #key: set name, values: array of nodes

        self.table_coord = None
        self.table_connect = None

        self.elem_type = None
        self.n_GP = None

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

        return

    def pre_treatment(self):
        self.check_file()

        self.create_temp_dir()

        with open(self.file_path,"r") as f:
            data = f.readlines()

        while True:
            if data[-1] == "":
                del(data[-1])
            else:
                break

        self.get_coord_table(data)
        self.get_connect_table(data)

        self.read_param_files()

        self.add_routines()

        self.get_BC()

        self.write_data()

        return

    def check_file(self):
        extension = self.file.split(".")[-1]
        if extension != self.extension:
            print(f"Error - The input file is not an .{self.extension} file.")
            sys.exit()
        
        file_path = self.dir + self.input_dir + self.file
        if not os.path.exists(file_path):
            print(f"Error - Mesh file {self.file} not found.")
            sys.exit()

        self.file_path = file_path

        return

    def get_coord_table(self,data):
        passage = 0
        for nline,line in enumerate(data):
            if passage == 0 and line.startswith("*Part,"):
                passage = 1
            elif passage == 1 and line.startswith("*Node"):
                passage = 2
                istart = nline + 1
            elif passage == 2 and line.startswith("*Element"):
                passage = 3
                iend = nline - 1
                break

        if passage != 3:
            print("Error - Something went wrong while parsing the inp for nodes.")
            sys.exit()
        
        nnode_tot = iend - istart + 1
        table_coord = zeros([nnode_tot,4])

        for i in range(istart,iend+1):
            indice = i-istart
            line = data[i].split(",")
            if i == istart:
                ncoord_inp = len(line)
            for j in range(ncoord_inp):
                table_coord[indice,j] = float(line[j])

        self.nnode_tot = nnode_tot
        self.table_coord = table_coord
        
        return

    def get_connect_table(self,data):
        passage = 0
        for nline,line in enumerate(data):
            if passage == 0 and line.startswith("*Part,"):
                passage = 1
            elif passage == 1 and line.startswith("*Element,"):
                passage = 2
                istart = nline + 1
                if "type=" in line:
                    elem_type = line.split("=")[-1]
                    elem_type = elem_type.strip()
                else:
                    print("Error - The element type was not found while parsing the inp.")
                    sys.exit()

            elif passage == 2 and line.startswith("*"):
                passage = 3
                iend = nline - 1
                break

        if passage != 3:
            print("Error - Something went wrong while parsing the inp for elements.")
            sys.exit()

        nnode = len(data[istart].split(",")) - 1
        
        nelem = iend - istart + 1
        table_connect = zeros([nelem,nnode+1])
        for i in range(istart,iend+1):
            indice = i-istart
            line = data[i].split(",")
            for j in range(nnode+1):
                table_connect[indice,j] = int(line[j])

        self.nnode = nnode
        self.nelem = nelem
        self.table_connect = table_connect

        if elem_type in self.supported_elem:
            dim,n_gp = self.dic_elem[elem_type]

            self.elem_type = elem_type
            self.dim = dim
            self.mcrd = dim
            self.ndofel = int(dim*nnode)
            self.ndofel_tot = int(dim*self.nnode_tot)

            self.ndi = dim
            self.n_GP = n_gp

            if dim == 1:
                self.nshr = 0
            elif dim == 2:
                self.nshr = 1
            elif dim == 3:
                self.nshr = 3
            else:
                print(f"Error - Something went wrong, the dimension is equal {dim}")

            self.ntens = self.ndi + self.nshr

        else:
            print(f"Error - The element type {elem_type} is not supported.")
            print(f"Supported elements : {self.supported_elem}.")
            sys.exit()
        
        return

    def create_temp_dir(self):
        dir_path = self.dir+self.tmp_dir
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

        os.mkdir(dir_path)

        dir_path = self.dir+self.sim_data_dir
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

        os.mkdir(dir_path)

        param_files = [file for file in os.listdir(self.dir+self.param_dir)]
        for i,j in enumerate(param_files):
            j = j.split("/")[-1]
            if not os.path.exists(self.dir+self.param_dir+j):
                print("Error - File {j} not found.")
                sys.exit()
            else:
                obj = self.dir+self.param_dir+j
                target = self.dir+self.tmp_dir+j
                shutil.copy(obj,target)

        obj = self.file_path
        target = self.dir + self.tmp_dir + f"Fichier_traite.{self.extension}"
        shutil.copy(obj,target)

        return

    def read_param_files(self):
        file_path = self.dir + self.param_dir + self.file_model
        with open(file_path,"r") as f:
            data = f.readlines()

        while True:
            if data[-1] == "":
                del(data[-1])
            else:
                break

        nlines = len(data)
        nline = 0
        flag = 0
        while nline < nlines:
            line = data[nline]
            if line.startswith("material_law"):
                index_mat = int(line.split(":")[-1])
                flag = 1
                nline = nlines
            nline += 1

        if flag == 0:
            print("Error - Something went wrong while parsong the "
            f"{self.file_model} file for the material law.")
            sys.exit()

        self.mat_routine,self.nprops,ntens_var,nvars = self.dic_material_law[index_mat]

        self.nsvars = int(self.ntens*ntens_var + nvars)
        return

    def add_routines(self):
        self.routines.append(self.mat_routine+".py")
        self.routines.append(f"Element_{self.elem_type}.py")

        routines_path = self.dir + self.routines_dir
        tmp_path = self.dir + self.tmp_dir
        for i,j in enumerate(self.routines):
            if not os.path.exists(routines_path+j):
                print(f"Error - Routine file {j} not found.")
                sys.exit()
            
            obj = routines_path + j
            target = tmp_path + j
            shutil.copy(obj,target)
        return

    def write_data(self):
        towrite = []
        towrite.append("Material : "+str(self.mat_routine)+"\n")
        towrite.append("Element : "+str(self.elem_type)+"\n")
        towrite.append("dim : "+str(self.dim)+"\n")
        towrite.append("mcrd : "+str(self.mcrd)+"\n")
        towrite.append("nnode : "+str(self.nnode)+"\n")
        towrite.append("nnode_tot : "+str(self.nnode_tot)+"\n")
        towrite.append("nelem : "+str(self.nelem)+"\n")
        towrite.append("ndofel : "+str(self.ndofel)+"\n")
        towrite.append("ndofel_tot : "+str(self.ndofel_tot)+"\n")
        towrite.append("nprops : "+str(self.nprops)+"\n")
        towrite.append("ndi : "+str(self.ndi)+"\n")
        towrite.append("nshr : "+str(self.nshr)+"\n")
        towrite.append("ntens : "+str(self.ntens)+"\n")
        towrite.append("nsvars : "+str(self.nsvars)+"\n")
        towrite.append("n_GP : "+str(self.n_GP)+"\n")

        file_path = self.dir + self.tmp_dir + self.file_model
        with open(file_path,"w") as f:
            f.writelines(towrite)
        
        #Cordinnates table
        towrite = []
        for i in range(self.nnode_tot):
            for j in range(shape(self.table_coord)[1]):
                towrite.append(str(self.table_coord[i,j])+" ")
            towrite.append("\n")

        file_path = self.dir + self.tmp_dir + self.file_table_coord
        with open(file_path,"x") as f:
            f.writelines(towrite)

        #Connectivities table
        towrite = []
        for i in range(self.nelem):
            for j in range(self.nnode+1):
                towrite.append(str(int(self.table_connect[i,j]))+" ")
            towrite.append("\n")

        file_path = self.dir + self.tmp_dir + self.file_table_connect
        with open(file_path,"x") as f:
            f.writelines(towrite)

        #node sets
        towrite = []
        for key in self.node_sets_dic:
            set_name = key
            nodes_set = self.node_sets_dic[set_name]
            towrite.append(set_name + " : ")
            for node in nodes_set:
                towrite.append(str(node) + " ")
            towrite.append("\n")

        file_path = self.dir + self.tmp_dir + self.file_node_sets
        with open(file_path,"x") as f:
            f.writelines(towrite)

        #BC
        towrite = []
        for key in self.bc_dic:
            BC_type,node_set_BC,dofs_BC,amplitude_BC = self.bc_dic[key]
            towrite.append(BC_type + " : " + node_set_BC + ", ")
            for value in dofs_BC:
                towrite.append(str(value) + " ")
            towrite[-1] = towrite[-1][:-1] + ", "
            for value in amplitude_BC:
                towrite.append(str(value) + " ")
            towrite[-1] = towrite[-1][:-1] + '\n'

        file_path = self.dir + self.tmp_dir + self.file_BC
        with open(file_path,"x") as f:
            f.writelines(towrite)

        return

    def get_BC(self):
        with open(self.file_path,"r") as f:
            data = f.readlines()

        nlines = len(data)
        nBC = 0

        for nline,line in enumerate(data):
            flag = 1
            if line.startswith("*Boundary"):
                if "type=" not in line:
                    print("Error - Something went wrong while parsing the"
                    f" {self.file_path} for the boundary conditions")
                    sys.exit()
                boundary_type = line.split("type=")[-1].split(",")[0].strip().replace("\n","")
                direction = []
                amplitude = []
                index_tmp = 1
                while True:
                    line_tmp = data[nline+index_tmp]
                    if line_tmp.startswith("*"):
                        break
                    else:
                        values_tmp = line_tmp.split(",")
                        set_bc = values_tmp[0]
                        if values_tmp[1].strip() != values_tmp[2].strip():
                            print("Error - Node inclusivity in Abaqus inp is not supported yet "
                            "when declaring boundary conditions. Write a separate line for each dof")
                            sys.exit()
                        if int(float(values_tmp[1])) <= 3:
                            direction.append(int(float(values_tmp[1])))
                            if len(values_tmp) >= 4:
                                amplitude.append(float(values_tmp[3]))
                            else:
                                amplitude.append(0)
                        index_tmp += 1

            elif line.startswith("*Cload"):
                values_tmp = data[nline-1].split("Type:")[-1].split(",")[0]
                boundary_type = "CONCENTRATED FORCE"
                if values_tmp.strip() != "Concentrated force":
                    print("Error - Concentrated force are supported for external forces so far.")
                    sys.exit()
                direction = []
                amplitude = []
                index_tmp = 1
                while True:
                    line_tmp = data[nline+index_tmp]
                    if line_tmp.startswith("*"):
                        break
                    else:
                        values_tmp = line_tmp.split(",")
                        set_bc = values_tmp[0]
                        direction.append(int(float(values_tmp[1])))
                        amplitude.append(float(values_tmp[2]))

                    index_tmp += 1

            else:
                flag = 0

            if flag == 1:
                nBC += 1
                self.bc_dic.update({nBC: (boundary_type,set_bc,direction,amplitude)})

        if nBC == 0:
            print("Error - No boundary condition found.")
            sys.exit()

        self.nBC = nBC

        self.check_BC_sets(data)
        return

    def check_BC_sets(self,data):
        done_sets = []
        nNode_set = 0
        for BC in range(self.nBC):
            set_name = self.bc_dic[BC+1][1]

            if set_name not in done_sets:
                index_tmp = next((i for i,line in enumerate(data) if 
                f"*Nset, nset={set_name}" in line), None)

                if index_tmp is not None:
                    line_tmp = data[index_tmp]

                    if "generate" in line_tmp:
                        values = data[index_tmp+1].split(",")
                        first_node = int(float(values[0]))
                        last_node = int(float(values[1]))
                        inc_node = int(float(values[2]))
                        nodes_set = arange(first_node,last_node+1,inc_node)

                    else:
                        nodes_set = []
                        line_set = ""
                        index_nodes = index_tmp + 1
                        while True:
                            line_nodes = data[index_nodes]
                            if line_nodes.startswith("*"):
                                break
                            else:
                                if index_nodes == index_tmp + 1:
                                    line_set = line_set + line_nodes.replace(" ","").replace("\n","")
                                else:
                                    line_set = line_set + "," + line_nodes.replace(" ","").replace("\n","")
                                index_nodes += 1

                        nodes = line_set.split(",")
                        for i,j in enumerate(nodes):
                            nodes_set.append(int(float(j.strip())))
                        nodes_set = asarray(nodes_set)

                    nNode_set += 1
                    self.node_sets_dic.update({set_name: (nodes_set)})
                    done_sets.append(set_name)
                else:
                    print(f"Error - The node set {self.bc_dic[str(BC+1)][1]} was not found while "
                    "parsing the input file.")

        self.nNode_set = nNode_set
        return

file = str(sys.argv[1])
obj = Pre_treatment(file)
obj.pre_treatment()