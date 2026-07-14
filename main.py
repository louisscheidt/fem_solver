import os,sys
import shutil
import importlib.util

def import_temp_files():
    """
    Read the temp files where the python files have been copied and import them dynamically.
    From Claude code.
    """
    cur_dir = os.path.dirname(os.path.abspath('_'))+'/'
    tmp_dir = "Temp_files/"

    temp_dir = cur_dir + tmp_dir
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

def main():
    modules = import_temp_files()

    model = modules["Model"].Model()
    model.initialize()

    elem = modules[f"Element_{model.elem_type}"].Element(model)
    material = modules[f"{model.mat_routine}"].Material(model)
    solver = modules[f"Solver_explicit"].Solver(model) #a modifier pour parametrer entre explicite et implicite
    resolution = modules[f"Calc_Fint_explicit"].Internal_forces(model,elem,material) #a modifier pour parametrer entre explicite et implicite

    # read inp again and setup BC
    # 6) solve
    # 7) post-treatment
    return

if __name__ == "__main__":
    main()