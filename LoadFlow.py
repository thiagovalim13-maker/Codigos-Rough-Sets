import json
import numpy as np

class LoadFlow:
    def __init__(self, bus_file, line_file):
        self.busses = bus_file
        self.lines = line_file
        self.n_bus = len(self.busses)
        
        # [id, type, V, theta_deg, P_load, Q_load, P_gen, Q_max, Q_min]
        self.bus_types = [b[1] for b in self.busses]  
        self.bus_types_orig = list(self.bus_types)   
        
        self.v_mag = np.array([b[2] for b in self.busses], dtype=float)
        self.v_spec = np.array([b[2] for b in self.busses], dtype=float)
        self.theta = np.deg2rad([b[3] for b in self.busses], dtype=float)

        self.p_load = np.array([b[4] for b in self.busses], dtype=float)
        self.q_load = np.array([b[5] for b in self.busses], dtype=float)
        self.p_gen  = np.array([b[6] for b in self.busses], dtype=float)
        self.q_max  = np.array([b[7] for b in self.busses], dtype=float)
        self.q_min  = np.array([b[8] for b in self.busses], dtype=float)

        self.p_spec = self.p_gen - self.p_load
        self.q_spec = np.zeros(self.n_bus, dtype=float)

        self.tol = 0.001
        self.max_iter = 30

    def build_y_bus(self):
        Y = np.zeros((self.n_bus, self.n_bus), dtype=complex)
        for line in self.lines:
            f, t = int(line[0]) - 1, int(line[1]) - 1
            r, x, b_shunt = line[2], line[3], line[4]
            z = complex(r, x)
            y_ser = 1.0 / z
            
            # Elementos fora da diagonal 
            Y[f, t] -= y_ser
            Y[t, f] -= y_ser
            
            # Elementos da diagonal principal
            Y[f, f] += y_ser + 1j * b_shunt
            Y[t, t] += y_ser + 1j * b_shunt
        return Y

    def update_bus_indices(self):
        """Atualiza quais barras são P-ativas e Q-ativas"""
        self.pv_buses = [i for i, t in enumerate(self.bus_types) if t == 2]
        self.pq_buses = [i for i, t in enumerate(self.bus_types) if t == 3]

        self.p_buses = sorted(self.pv_buses + self.pq_buses)
        self.q_buses = self.pq_buses

    def check_q_limits(self, Q_calc, iteration):
        """
        Verifica os limites de Q nas barras PV e altera os tipos de barra (PV <-> PQ)
        """
        if iteration < 1:
            return

        for i in range(self.n_bus):
            # 1. Testar barra originalmente PV
            if self.bus_types_orig[i] == 2:
                Q_gen_i = Q_calc[i] + self.q_load[i]

                # Se a barra atualmente é PV e violou limite superior
                if self.bus_types[i] == 2 and Q_gen_i > self.q_max[i]:
                    print(f"  -> Barra {i+1} (PV) violou Qmax ({Q_gen_i:.3f} > {self.q_max[i]}). MUDANDO PARA PQ.")
                    self.bus_types[i] = 3
                    self.q_spec[i] = self.q_max[i] - self.q_load[i]

                # Se a barra atualmente é PV e violou limite inferior
                elif self.bus_types[i] == 2 and Q_gen_i < self.q_min[i]:
                    print(f"  -> Barra {i+1} (PV) violou Qmin ({Q_gen_i:.3f} < {self.q_min[i]}). MUDANDO PARA PQ.")
                    self.bus_types[i] = 3
                    self.q_spec[i] = self.q_min[i] - self.q_load[i]

                # 2. Testar se uma barra convertida em PQ deve RETORNAR para PV
                elif self.bus_types[i] == 3:
                    if self.q_spec[i] == (self.q_max[i] - self.q_load[i]) and self.v_mag[i] > self.v_spec[i]:
                        print(f"  -> Barra {i+1} recuperou controle de tensão. RETORNANDO PARA PV.")
                        self.bus_types[i] = 2
                        self.v_mag[i] = self.v_spec[i]

                    elif self.q_spec[i] == (self.q_min[i] - self.q_load[i]) and self.v_mag[i] < self.v_spec[i]:
                        print(f"  -> Barra {i+1} recuperou controle de tensão. RETORNANDO PARA PV.")
                        self.bus_types[i] = 2
                        self.v_mag[i] = self.v_spec[i]

    def solve(self):
        sol = []
        Y = self.build_y_bus() 
        G, B = Y.real, Y.imag

        for it in range(self.max_iter):
            # Atualiza quais barras são PQ e PV na iteração atual
            self.update_bus_indices()

            # Ajusta o q_spec para barras PQ nativas
            for i in self.pq_buses:
                if self.bus_types_orig[i] == 3:
                    self.q_spec[i] = -self.q_load[i]

            P_calc = np.zeros(self.n_bus)
            Q_calc = np.zeros(self.n_bus)
            for i in range(self.n_bus):
                for j in range(self.n_bus):
                    t_diff = self.theta[i] - self.theta[j]
                    P_calc[i] += self.v_mag[i] * self.v_mag[j] * (G[i, j] * np.cos(t_diff) + B[i, j] * np.sin(t_diff))
                    Q_calc[i] += self.v_mag[i] * self.v_mag[j] * (G[i, j] * np.sin(t_diff) - B[i, j] * np.cos(t_diff))

            # Limites de geração
            self.check_q_limits(Q_calc, it)
            self.update_bus_indices()

            # Missmatch
            dP = self.p_spec[self.p_buses] - P_calc[self.p_buses]
            dQ = self.q_spec[self.q_buses] - Q_calc[self.q_buses]
            mismatch = np.concatenate([dP, dQ])

            max_err = np.max(np.abs(mismatch))
            print(f"Iteração {it + 1}: Maior Mismatch = {max_err:.6f}")

            if max_err < self.tol:
                break
            nH, nL = len(self.p_buses), len(self.q_buses)
            H, N = np.zeros((nH, nH)), np.zeros((nH, nL))
            M, L = np.zeros((nL, nH)), np.zeros((nL, nL))

            for i_idx, i in enumerate(self.p_buses):
                for j_idx, j in enumerate(self.p_buses):
                    if i == j:
                        H[i_idx, j_idx] = -Q_calc[i] - B[i, i]*(self.v_mag[i]**2)
                    else:
                        t_diff = self.theta[i] - self.theta[j]
                        H[i_idx, j_idx] = self.v_mag[i] * self.v_mag[j] * (G[i, j]*np.sin(t_diff) - B[i, j]*np.cos(t_diff))

                for j_idx, j in enumerate(self.q_buses):
                    if i == j:
                        N[i_idx, j_idx] = P_calc[i] + G[i, i]*self.v_mag[i]
                    else:
                        t_diff = self.theta[i] - self.theta[j]
                        N[i_idx, j_idx] = self.v_mag[i] * (G[i, j]*np.cos(t_diff) + B[i, j]*np.sin(t_diff))

            for i_idx, i in enumerate(self.q_buses):
                for j_idx, j in enumerate(self.p_buses):
                    if i == j:
                        M[i_idx, j_idx] = P_calc[i] - G[i, i]*(self.v_mag[i]**2)
                    else:
                        t_diff = self.theta[i] - self.theta[j]
                        M[i_idx, j_idx] = -self.v_mag[i]*self.v_mag[j] * (G[i, j]*np.cos(t_diff) + B[i, j]*np.sin(t_diff))

                for j_idx, j in enumerate(self.q_buses):
                    if i == j:
                        L[i_idx, j_idx] = Q_calc[i]- B[i, i]*(self.v_mag[i]**2)
                    else:
                        t_diff = self.theta[i] - self.theta[j]
                        L[i_idx, j_idx] = self.v_mag[i] * (G[i, j] * np.sin(t_diff) - B[i, j] * np.cos(t_diff))

            J = np.block([[H, N], [M, L]])
            dx = np.linalg.solve(J, mismatch)

            dTheta = dx[:nH]
            dV = dx[nH:]

            for idx, i in enumerate(self.p_buses):
                self.theta[i] += dTheta[idx]

            for idx, i in enumerate(self.q_buses):
                self.v_mag[i] += dV[idx]

        for i in range(self.n_bus):
            sol.append([i+1, self.v_mag[i], np.rad2deg(self.theta[i])])

        
        return self.v_mag, np.rad2deg(self.theta), sol, P_calc,Q_calc

    def print_resposta(self, P_calc, Q_calc, sol):
        print('  Tensões    Ângulos     P_ativa     P_reativa')
        print('----------------------------------------------')
        for aux in range(len(self.v_mag)):
            print(f'{float(self.v_mag[aux]):8.3f}   {float(self.theta[aux]):8.3f}    {float(P_calc[aux]):8.3f}    {float(Q_calc[aux]):8.3f}')
        resp = input('Deseja salvar o arquivo da solução? S-N\n')
        while True:
            if resp.upper() == 'S':
                nome = input('Digite o nome do arquivo: (utilize a extensão .json)\n')
                with open(f"{nome}.json", "w") as f:
                    json.dump(sol, f, ensure_ascii=False, indent=4)
                
                input('Arquivo salvo.\nPressione qualquer tecla para continuar.')
                break

            elif resp.upper() == 'N':
                break

            else:
                input('Resposta inválida, pressione qualquer tecla para continuar.')
        
