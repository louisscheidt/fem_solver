import os,sys
import shutil
import importlib.util

def get_input():
    abs_dir = os.path.dirname(os.path.abspath('_'))+'/'
    file_dir = abs_dir + "Files_input/"

    file_name = str(sys.argv[1])
    if not os.path.exists(file_dir+file_name):
        print(f"Error - Input file {file_name} not found.")
        sys.exit()
    else:
        extension = file_name.split(".")[-1]

        obj = file_dir+file_name
        target = abs_dir+f"input_file.{extension}"
        shutil.copy(obj,target)

    return target

def import_temp_files(temp_dir):
    """
    Read the temp files where the python files have been copied and import them dynamically.
    From Claude code.
    """

    modules = {}
    for filename in os.listdir(temp_dir):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            filepath = os.path.join(temp_dir, filename)

            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            modules[module_name] = module
    return modules

def create_tmp_dir():
    abs_dir = os.path.dirname(os.path.abspath('_'))+'/'
    tmp_dir = "Temp_files/"
    sim_data_dir = "Sim_data/"
    routines_dir = "Files_routines/"
    param_dir = "Files_parameters/"

    """
    remove old dir and create new ones
    """
    if os.path.isdir(abs_dir+tmp_dir):
        shutil.rmtree(abs_dir+tmp_dir)

    os.mkdir(abs_dir+tmp_dir)

    if os.path.isdir(abs_dir+sim_data_dir):
        shutil.rmtree(abs_dir+sim_data_dir)

    os.mkdir(abs_dir+sim_data_dir)

    """
    Put the param files in temp dir
    """
    param_files = [file for file in os.listdir(abs_dir+param_dir)]
    for i,j in enumerate(param_files):
        j = j.split("/")[-1]
        if not os.path.exists(abs_dir+param_dir+j):
            print("Error - File {j} not found.")
            sys.exit()
        else:
            obj = abs_dir+param_dir+j
            target = abs_dir+tmp_dir+j
            shutil.copy(obj,target)

    """
    Check the matrial law to use
    """
    with open(abs_dir+tmp_dir+"PARAM_MODEL") as f:
        data = f.readlines()

    nlines = len(data)
    nline = 0
    while nline<nlines:
        if data[nline].startswith("material"):
            ind_mat = int(data[nline].split(":")[-1])
            break
        
        nline += 1


    """
    Put the routines in temp dir
    """
    mat_dic = {
        "1": ("Loi_materiau_elastique"),
    }

    routine_files = ["Model.py","Meshing.py","Solver_explicite.py","Calcul_efforts_interieurs.py"]
    routine_files.append(mat_dic[str(ind_mat)]+".py")

    for i,j in enumerate(routine_files):
        if not os.path.exists(abs_dir+routines_dir+j):
            print(f"Error - File {j} not found.")
            sys.exit()
        else:
            obj = abs_dir+routines_dir+j
            target = abs_dir+tmp_dir+j
            shutil.copy(obj,target)

    modules = import_temp_files(abs_dir+tmp_dir)

    return modules,mat_dic[str(ind_mat)]


def initialize_mesh(modules,input_file):
    abs_dir = os.path.dirname(os.path.abspath('_'))+'/'
    tmp_dir = "Temp_files/"
    routines_dir = "Files_routines/"

    elem_dic = {
        "C2D4" : ("Element_C2D4.py"),
    }

    mesh = modules["Meshing"].Mesh(input_file)
    mesh.get_mesh_data()

    elem_file = elem_dic[mesh.elem_type]
    if not os.path.exists(abs_dir+routines_dir+elem_file):
        print("Error - File {elem_file} not found.")
        sys.exit()
    else:
        obj = abs_dir+routines_dir+elem_file
        target = abs_dir+tmp_dir+elem_file
        shutil.copy(obj,target)

    modules = import_temp_files(abs_dir+tmp_dir)

    return mesh,modules


def initialize_modules(modules,mesh,loi_mat):
    model = modules["Model"].Model(mesh)
    model.initialize()

    elem = modules[f"Element_{mesh.elem_type}"].Element(model)

    material = modules[loi_mat].Material(model)

    solver = modules["Solver_explicite"].Solver(model)

    eff_int = modules["Calcul_efforts_interieurs"].Internal_forces(model,elem,material)

    return model,elem,material,solver,eff_int

def main():
    # 1) get input file
    input_file = get_input()

    # 2) create temporary directories and files, and dynamically load 
    #   the module (except for the element one which is imported later)
    modules,loi_mat = create_tmp_dir()

    # 3) initialize the mesh, get the element type, put the right element subroutine in the temp dir, and import it
    mesh,modules = initialize_mesh(modules,input_file)

    # 4) Initialize model, element, material law, calc_fint, solver
    model,elem,material,solver,eff_int = initialize_modules(modules,mesh,loi_mat)

    # 5) apply CL
    # 6) solve
    # 7) post-treatment
    return

if __name__ == "__main__":
    main()