from numpy import matmul,zeros

class Internal_forces:
    def __init__(self,model,elem,material):
        self.model = model
        self.elem = elem
        self.material = material

        self.Cl = self.material.Cl

    def Calc_DSTRAN(self,i_GP,jelem,B_mat):
        """
        petite def
        """
        U,U_last = self.model.retrieve_nodal_state_elem(jelem)[0,1]
        dU = U - U_last

        DSTRAN = matmul(B_mat,dU)
        return DSTRAN

    def Calc_bulk_viscosity(self,DSTRAN,Le):
        eps_kk = 0.
        for i in range(self.model.NDI):
            eps_kk = eps_kk + DSTRAN(i)

        pbv1 = self.model.bv1*self.model.props[0]*self.Cl*self.Le*eps_kk

        if eps_kk > 0:
            pbv2 = 0
            xi = self.model.bv1
        else:
            pbv2 = self.model.props[0]*(self.model.bv2*self.Le*eps_kk)**2
            xi = self.model.bv1 - (self.model.bv2**2)*(self.Le/self.Cl)*eps_kk

        q_bulk = pbv2 - pbv1
        return q_bulk,xi

    def Calc_Fint(self,jelem):
        Fint = zeros([self.model.ndofel,1])

        B_mat_cent,detJ_cent = self.elem.Calc_Bmatrix(jelem,0,centroid=True)

        wgt = self.elem.get_wgt_GP(0,centroid=True)
        mes_elem = detJ_cent*wgt

        Le = self.elem.Calc_Le(B_mat_cent,detJ_cent,wgt_GP,mes_elem)

        for i_GP in range(self.elem.n_GP):
            
            wgt = self.elem.get_wgt_GP(i_GP,centroid=False)

            B_mat,detJ = self.elem.Calc_Bmatrix(jelem,i_GP,centroid=False)

            B_mat_bar = self.elem.Calc_B_bar(B_mat,B_mat_cent)

            DSTRAN = self.Calc_DSTRAN(i_GP,jelem,B_mat_bar)
            STRESS = self.material.integration_material(i_GP,DSTRAN,jelem)
            q_bulk,xi = self.Calc_bulk_viscosity(DSTRAN,Le)

            for i in range(self.model.NDI):
                STRESS[i] = STRESS[i] - q_bulk

            Fint = Fint + detJ*wgt*matmul(B_mat,STRESS)

        dt = Le/self.material.Cl
        dt = dt*((1.+xi**2)**0.5-xi)

        self.model.update_nodal_state(jelem,Fint,dt)
        return