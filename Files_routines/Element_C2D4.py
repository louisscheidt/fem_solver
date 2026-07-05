from numpy import zeros,array
from numpy.linalg import inv,det

class Element:
    def __init__(self,model):
        self.model = model

        self.nnode_elem = 4
        self.dim = 2
        self.n_GP = 4
        self.pos = 1/(3**0.5)

    def Calc_Le(self,B_mat,detJ,wgt_GP,mes_elem):
        B_mat_int = B_mat*detJ*wgt_GP

        coef = 0
        for i in range(self.model.ndef):
            for j in range(self.model.ndofel_tot):
                coef = coef + B_mat_int(i,k)**2

        Le = mes_elem/(coef**0.5)
        return Le

    def get_wgt_GP(self,i_GP,centroid=False):
        if not centroid:
            wgt = 1.
        else:
            wgt = 4.
        return wgt

    def get_coord_GP(self,i_GP):
        coord_GP = array([self.pos,self.pos])

        signs = np.array([[-1,-1],
        [+1,-1],
        [+1,+1],
        [-1,+1]])

        if not centroid:
            coord_GP = coord_GP**signs[i_GP,:]
        else:
            coord_GP = coord_GP*0.

        return coord_GP

    def Calc_Bmatrix(self,jelem,i_GP,centroid=False):
        Ni = zeros(self.nnode_elem)
        dN_dIso = zeros([self.dim,self.nnode_elem])
        dN_dSpatial = zeros([self.nnode_elem,self.dim])
        B_mat = np.zeros([self.model.ndef,self.model.ndofel_tot])

        coord_GP = self.get_coord_GP(i_GP,centroid=False)
        wgt_GP = self.get_wgt_GP(i_GP,centroid=False)

        coord_nodes = self.model.retrieve_nodal_state_elem(jelem)[0]

        facteur = 1/self.nnode_elem

        Ni[0] = facteur*((1-coord_GP[0])*(1-coord_GP[1]))
        Ni[1] = facteur*((1+coord_GP[0])*(1-coord_GP[1]))
        Ni[2] = facteur*((1+coord_GP[0])*(1+coord_GP[1]))
        Ni[3] = facteur*((1-coord_GP[0])*(1+coord_GP[1]))

        dN_dIso[0,0] = -facteur*(one-coord_GP[1])
        dN_dIso[0,1] = +facteur*(one-coord_GP[1])
        dN_dIso[0,2] = +facteur*(one+coord_GP[1])
        dN_dIso[0,3] = -facteur*(one+coord_GP[1])

        dN_dIso[1,0] = -facteur*(one-coord_GP[0])
        dN_dIso[1,1] = -facteur*(one+coord_GP[0])
        dN_dIso[1,2] = +facteur*(one+coord_GP[0])
        dN_dIso[1,3] = +facteur*(one-coord_GP[0])

        Jac = (dN_dIso.transpose()).dot(coord_nodes)
        invJac = inv(Jac)
        detJ = det(Jac)

        for i in range(self.nnode_elem):
            dN_dSpatial[i,:] = invJac.dot(dN_dIso[i,:])

        for i in range(self.nnode_elem):
            indice1 = i*self.model.mcrd
            indice2 = i*self.model.mcrd+self.model.mcrd
            Bi = np.zeros([self.model.ndef,self.model.mcrd])
            dNi_dSpatial = dN_dSpatial[i,:]
            Bi[0,0] = dNi_dSpatial[0]
            Bi[1,1] = dNi_dSpatial[1]
            Bi[2,:] = np.array([dNi_dSpatial[1],dNi_dSpatial[0]])
            B_mat[:,indice1:indice2] = Bi

        return B_mat,detJ

        def Calc_B_bar(self,B_mat,B_mat_cent):
            for i in range(self.model.mcrd):
                value = (1/self.dim)*(B_mat_cent[i,i]-B_mat[i,i])
                B_mat[i,i] = B_mat[i,i] + value

            return B_mat