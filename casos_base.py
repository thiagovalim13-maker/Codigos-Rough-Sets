import json
import numpy as np
from LoadFlow import LoadFlow
import copy

class CasosBase():
    def __init__(self, bus_file, line_file):

        self.busses = bus_file
        self.lines = line_file
        self.bus_connect = []
        self.conjunto = {}
        self.teste = []
        self.n_conv = {}
        for i in self.lines:
            self.bus_connect.append([i[0],i[1]])

    '''
    def casos_perda_de_linha(self):
        caso_perda1 = {}
        caso_perda2 = {}
        n_conv_local1 = {}
        n_conv_local2 = {}
        # 1 linha perdida
        for ind, i in enumerate(self.bus_connect):
            try:
                alt_lines = [item for aux,item in enumerate(self.lines) if aux!=ind]
                six_bus = LoadFlow(self.busses, alt_lines)
                vmag, theta_mag,sol = six_bus.solve()
                if max(vmag) >= 2 or min(vmag) < 0:
                    n_conv_local1[f'Caso {i}'] = ['Matriz singular',sol]
                else:
                    caso_perda1[f'Caso {i}'] = sol
            except:
                n_conv_local1[f'Caso {i}'] = 'Matriz singular'

        # 2 linhas perdidas
        for ind, i in enumerate(self.bus_connect):
                for ind2, j in enumerate(self.bus_connect):
                    if ind2 <= ind:
                        continue 
                    try:
                        alt_lines = [item for k, item in enumerate(self.lines) if k not in {ind, ind2}]
                        six_bus = LoadFlow(self.busses, alt_lines)
                        vmag, _, sol = six_bus.solve()
                        if max(vmag) >= 2 or min(vmag) < 0:
                            n_conv_local2[f'Caso {i} e {j}'] = ['Matriz singular',sol]

                        else:
                            caso_perda2[f'Caso {i} e {j}'] = sol
                    except:
                        n_conv_local2[f'Caso {i} e {j}'] = ['Matriz singular',sol]

        self.conjunto['1 linha perdida'] = caso_perda1
        self.conjunto['2 linhas perdidas'] = caso_perda2
        self.n_conv['1 linha perdida'] = n_conv_local1
        self.n_conv['2 linhas perdidas'] = n_conv_local2

    '''
    def caso_mudança_de_carga(self):
        n_conv_local1 = {}
        n_conv_local2 = {}
        n_conv_local3 = {}
        caso1_altcarg = {}
        caso2_altcarg = {}
        caso3_altcarg = {}

        #vetor de variação de carga entre 70% a 130%
        vet_inc = np.arange(0.7,1.30,0.01)
        #vet_inc = vet_inc[vet_inc != 1]

        '''
        # 1 barra de carga mudando sua potência ativa
        for ind1, aux in enumerate(self.busses):
            #verificando se a barra em questão possui carga ativa
            if aux[4] == 0:
                continue
            else:
                for inc in vet_inc:
                    try:
                        alt_buses = copy.deepcopy(self.busses)
                        alt_buses[ind1][4] = alt_buses[ind1][4]*inc
                        six_bus = LoadFlow(alt_buses, self.lines)
                        vmag, _,sol = six_bus.solve()
                        if max(vmag) >= 2 or min(vmag) < 0:
                            n_conv_local1[f'Barra {ind1+1} {inc*100}%'] = 'Sem convergência'
                        else:
                            caso1_altcarg[f'Barra {ind1+1} {inc*100}%'] = sol

                    except:
                        n_conv_local1[f'Barra {ind1+1} {inc*100}%'] = 'Matriz singular'

        
        # 1 barra de carga mudando sua potência ativa e reativa
        for ind1, aux in enumerate(self.busses):
            #verificando se a barra em questão possui carga ativa ou reativa
            if aux[4] == 0 and aux[5] == 0:
                continue
            else:
                for inc in vet_inc:
                    try:
                        alt_buses = copy.deepcopy(self.busses)
                        alt_buses[ind1][4] = alt_buses[ind1][4]*inc
                        alt_buses[ind1][5] = alt_buses[ind1][5]*inc
                        six_bus = LoadFlow(alt_buses, self.lines)
                        vmag, _,sol = six_bus.solve()
                        if max(vmag) >= 2 or min(vmag) < 0:
                            n_conv_local2[f'Barra {ind1+1} {inc*100}%'] = 'Sem convergência'

                        else:
                            caso2_altcarg[f'Barra {ind1+1} {inc*100}%'] = sol

                    except:
                        n_conv_local2[f'Barra {ind1+1} {inc*100}%'] = 'Matriz singular'


        self.conjunto['1 barra mudando sua carga ativa'] = caso1_altcarg
        self.conjunto['1 barra mudando sua carga ativa e reativa'] = caso2_altcarg
        '''

        # 3 barras de carga mudando sua potência ativa e reativa simultaneamente
        #primeira barra
        for ind1, aux in enumerate(self.busses):
            #verificando se a barra em questão possui carga ativa ou reativa
            if aux[4] == 0 and aux[5] == 0:
                continue
            else:
                #segunda barra
                for ind2, aux2 in enumerate(self.busses):
                    if ind2 <= ind1 or (aux2[4] == 0 and aux2[5] == 0):
                        continue
                    elif aux2[4] == 0 and aux2[5] == 0:
                        continue
                    else:
                        #terceira barra
                        for ind3, aux3 in enumerate(self.busses):
                            if ind3 <= ind1 or ind3 <= ind2:
                                continue
                            elif aux3[4] == 0 and aux3[5] == 0:
                                continue
                            else:             
                                alt_buses = self.busses
                                #variação de carga da primeira barra
                                for inc1 in vet_inc:
                                    try:
                                        #faz uma copia verdadeira dos valores nominais das barras
                                        alt_buses = copy.deepcopy(self.busses)
                                        #alteração dos valores modificados da barra para os valores reais, no primeiro laço não faz diferença
                                        alt_buses[ind1][4] = self.busses[ind1][4]
                                        alt_buses[ind1][5] = self.busses[ind1][5]
                                        #modificação dos valores de carga da primeira barra ([4] potência ativa [5] potência reativa) conforme vetor inc
                                        alt_buses[ind1][4] = alt_buses[ind1][4]*inc1
                                        alt_buses[ind1][5] = alt_buses[ind1][5]*inc1
                                        #variação de carga da segunda barra
                                        for inc2 in vet_inc:
                                            #alteração dos valores modificados da barra para os valores reais, no primeiro laço não faz diferença
                                            alt_buses[ind2][4] = self.busses[ind2][4]
                                            alt_buses[ind2][5] = self.busses[ind2][5]
                                            #modificação dos valores de carga da segunda barra ([4] potência ativa [5] potência reativa) conforme vetor inc
                                            alt_buses[ind2][4] = alt_buses[ind2][4]*inc2
                                            alt_buses[ind2][5] = alt_buses[ind2][5]*inc2
                                            for inc3 in vet_inc:
                                                #alteração dos valores modificados da barra para os valores reais, no primeiro laço não faz diferença
                                                alt_buses[ind3][4] = self.busses[ind3][4]
                                                alt_buses[ind3][5] = self.busses[ind3][5]
                                                #modificação dos valores de carga da terceira barra ([4] potência ativa [5] potência reativa) conforme vetor inc
                                                alt_buses[ind3][4] = alt_buses[ind3][4]*inc3
                                                alt_buses[ind3][5] = alt_buses[ind3][5]*inc3
                                                #six_bus = LoadFlow(alt_buses, self.lines)
                                                #vmag, _,sol, P_calc,Q_calc = six_bus.solve()
                                                #filtro para valores de tensão divergentes ou com carga excessiva que façam a tensão despencar
                                                #if max(vmag) >= 1.1 or min(vmag) < 0.9:
                                                #    n_conv_local3[f'Barra {ind1+1} {inc1*100}%, Barra {ind2+1} {inc2*100}% e Barra {ind3+1} {inc3*100}%'] = 'Sem convergência'
                                                condicao1 = inc1<=0.9 and inc2<=0.9 and inc3<=0.9
                                                condicao2 = int((inc1 < 0.8)) + int((inc2 < 0.8)) + int((inc3 < 0.8)) >= 2
                                                condicao7h = condicao1 and condicao2
                                                if condicao7h:
                                                    six_bus = LoadFlow(alt_buses, self.lines)
                                                    vmag, _,sol, P_calc,Q_calc = six_bus.solve()
                                                    #filtro para valores de tensão divergentes ou com carga excessiva que façam a tensão despencar
                                                    if max(vmag) >= 1.1 or min(vmag) < 0.9:
                                                        n_conv_local3[f'Barra {ind1+1} {inc1*100}%, Barra {ind2+1} {inc2*100}% e Barra {ind3+1} {inc3*100}%'] = 'Sem convergência'
                                                        
                                                    else:
                                                        caso3_altcarg[f'Barra {ind1+1} {inc1*100}%, Barra {ind2+1} {inc2*100}% e Barra {ind3+1} {inc3*100}%'] = [sol,P_calc.tolist(),Q_calc.tolist()]

                                                

                                    except:
                                        n_conv_local3[f'Barra {ind1+1} {inc1*100}%, Barra {ind2+1} {inc2*100}% e Barra {ind3+1} {inc3*100}%'] = ['Matriz singular', sol]


        #self.conjunto['1 barra mudando sua carga ativa'] = caso1_altcarg
        #self.conjunto['1 barra mudando sua carga ativa e reativa'] = caso2_altcarg
        self.conjunto['07 horas'] = caso3_altcarg

        #self.n_conv['1 barra mudando sua carga ativa'] = n_conv_local1
        #self.n_conv['1 barra mudando sua carga ativa e reativa'] = n_conv_local2
        self.n_conv['07 horas'] = n_conv_local3

        resp = input('Deseja salvar o arquivo de casos? S-N:  ')
        while True:
            if resp.upper() == 'S':
                resp_s = input('Digite o nome do arquivo para salvar:(utilize a extensão .json)\n')
                resp_s_n_conv = resp_s.replace('.json', '_nconv.json')
                with open(f'{resp_s}', "w") as f:
                    json.dump(self.conjunto, f, ensure_ascii=False, indent=4)
                with open(f'{resp_s_n_conv}_nconv', "w") as f:
                    json.dump(self.n_conv, f, ensure_ascii=False, indent=4)
                
                input('Arquivo salvo.\nPressione qualquer tecla para continuar.')
                break
            elif resp.upper() == 'N':
                break
            else:
                print('Valor inválido')



    def casos_perda_de_linha_e_mudança_de_carga(self):
        caso1_altcarg = {}
        caso2_altcarg = {}

        vet_inc = np.arange(0.7,1.4,0.05)
        #vet_inc = vet_inc[vet_inc != 1]

        # 1 linha perdida
        for ind, i in enumerate(self.bus_connect):
            alt_lines = [item for aux,item in enumerate(self.lines) if aux!=ind]
            six_bus = LoadFlow(self.busses, alt_lines)
            for ind1, aux in enumerate(self.busses):
                if aux[4] == 0 and aux[5] == 0:
                    continue
                else:
                    alt_buses = self.busses
                    for inc in vet_inc:
                            try:
                                alt_buses[ind1][4] = alt_buses[ind1][4]*inc
                                six_bus = LoadFlow(alt_buses, alt_lines)
                                vmag, _,sol = six_bus.solve()
                                if max(vmag) >= 2 or min(vmag) < 0:
                                    self.n_conv[f'Caso {i} Barra {ind1+1} {inc*100}%'] = 'Matriz singular'
                                else:    
                                    caso1_altcarg[f'Caso {i} Barra {ind1+1} {inc*100}%'] = sol
                
                            except:
                                self.n_conv[f'Caso {i} Barra {ind1+1} {inc*100}%'] = 'Matriz singular'

        self.conjunto['Caso perda de 1 linha e mudança de carga'] = caso1_altcarg


        # 2 linhas perdidas
        for ind, i in enumerate(self.bus_connect):
                for ind2, j in enumerate(self.bus_connect):
                    if ind2 <= ind:
                        continue 
                    else:
                        alt_lines = [item for k, item in enumerate(self.lines) if k not in {ind, ind2}]
                        for ind3, aux in enumerate(self.busses):                                                        
                            if aux[4] == 0 and aux[5] == 0:
                                continue
                            else:
                                alt_buses = self.busses
                                for inc in vet_inc:
                                        try:
                                            alt_buses[ind3][4] = alt_buses[ind][4]*inc
                                            six_bus = LoadFlow(alt_buses, alt_lines)
                                            vmag, _,sol = six_bus.solve()
                                            if max(vmag) >= 2 or min(vmag) < 0:
                                                self.n_conv[f'Caso {i} Barra {ind1+1} {inc*100}%'] = 'Matriz singular'
                                            else:
                                                caso2_altcarg[f'Caso {i} e {j}, Barra {ind1+1} {inc*100}%'] = sol
                            
                                        except:
                                            self.n_conv[f'Caso {i} Barra {ind1+1} {inc*100}%'] = 'Matriz singular'


        self.conjunto['Caso perda de 2 linhas e mudança de carga'] = caso2_altcarg

        


