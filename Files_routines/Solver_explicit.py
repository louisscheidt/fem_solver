from numpy import matmul

class Solver:
    def __init__(self,model):
        self.model = model
        
        
    def retrieve_elem_data(self):
        Mi = self.model.get_inverse_mass_matrix()
        Fint = self.model.get_internal_effort()
        Fext = self.model.get_external_effort()
        V_half_last = self.model.get_last_V_half()
        U_last = self.model.get_last_U()

        return Mi,Fint,Fext,V_half_last,U_last

    def solve(self):
        Mi,Fint,Fext,V_half_last,U_last = retrieve_elem_data()
        dt = self.model.dt
        dt_last = self.model.dt_last

        A = matmul(Mi,(Fext-Fint))
        V_half = V_half_last + 0.5*A*(self.dt+self.dt_last)
        U = U_last + V_half*self.dt
        V = V_half + 0.5*self.dt*A

        self.model.update_nodal_state(A,V_half,V,U)
        return

