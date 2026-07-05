from numpy import zeros,array

class Material:
    def __init__(self,model):
        self.model = model
        self.props = self.model.props

        self.DDSDDE,self.Cl = self.Calc_DDSDDE()

    def Calc_stress(self,DSTRAN,STRESS):
        dSTRESS = matmul(self.DDSDDE,DSTRAN)
        STRESS = STRESS + dSTRESS

        return STRESS

    def Calc_DDSDDE(self):
        rho = self.props[0]
        young = self.props[1]
        poisson = self.props[2]

        lame = poisson*young/((1-2*poisson)*(1+poisson))
        mu = young/(2*(1+poisson))

        DDSDDE = zeros((self.model.ntens,self.model.ntens))

        for i in range(self.model.ndi):
            for j in range(self.model.ndi):
                DDSDDE[j,i] = lame
            DDSDDE[i,i] = 2*mu + lame

        for i in range(self.model.ndi,self.model.ntens):
            DDSDDE[i,i] = mu

        Cl = ((lame+2*mu)/rho)**0.5
        return DDSDDE,Cl

    def material_integration(self,i_GP,DSTRAN,jelem):
        """
        elasticite lineaire en petites defs
        """
        jelem = jelem - 1
        indice1 = i_GP*self.model.nsvars
        indice2 = (i_GP+1)*self.model.nsvars

        SVARS = self.model.SVARS[jelem,:]
        STATEV = SVARS[indice1:indice2]
        STRESS = STATEV[0:self.model.ntens]

        STRESS = Calc_stress(DSTRAN,STRESS)

        STATEV = MAJ_STATEV(STATEV,STRESS,DSTRAN)

        update_material_state(indice1,indice2,jelem,STATEV)
        return

    def update_material_state(self,indice1,indice2,jelem,STATEV):
        self.model.svars[jelem,indice1:indice2] = STATEV
        return

    def MAJ_STATEV(self,STATEV,STRESS,DSTRAN):
        STATEV[0:self.model.ntens] = STRESS
        STATEV[self.model.ntens:2*self.model.ntens] += DSTRAN
        return