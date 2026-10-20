import numpy as np
import json
import pandas as pd




#criação dos dados para rough set
class Data_Base():
    def gerar_valores_anomalos(self,id,tipo,barra,vmag,thetamag):
        #cria as magnitudes dos valores anomalos
        folga_tens = 0.05
        folga_ang = 5
        if id == 'tensao':
            if tipo == 'down':
                mag_anomalia = np.random.uniform(0.70, max(0.71, min(vmag[barra])-folga_tens))
            if tipo == 'up':
                mag_anomalia = np.random.uniform(max(vmag[barra])+folga_tens, 1.3)

        if id == 'angulo':
            if tipo == 'down':
                mag_anomalia = np.random.uniform(-15, min(thetamag[barra])-folga_ang)
            if tipo == 'up':
                mag_anomalia = np.random.uniform(max(thetamag[barra])+folga_ang, 15)

        return mag_anomalia

    def gerar_estrutura_rs(self):
        while True:
            conjunto_file_name = input('Digite o nome do arquivo de casos base:\n')
            anomalia_file_name = input('Digite o nome do arquivo de anomalia:\n')
            horario = input('Digite o horário:(Somente números ex: 07)\n')
            try:
                with open(conjunto_file_name, mode='r', encoding='utf-8') as f:
                    conjunto = json.load(f)
                with open(anomalia_file_name, mode='r', encoding='utf-8') as f:
                    anomalia = json.load(f)

                vmag1 = []
                vmag2 = []
                vmag3 = []
                vmag4 = []
                vmag5 = []
                vmag6 = []
                thetamag1 = []
                thetamag2 = []
                thetamag3 = []
                thetamag4 = []
                thetamag5 = []
                thetamag6 = []
                for aux in conjunto[f'{horario} horas'].values():
                    for aux1 in aux[0]:
                        for k, aux2 in enumerate(aux1):
                            match aux2:
                                case 1:
                                    vmag1.append(aux1[1])
                                    thetamag1.append(aux1[2])
                                case 2:
                                    vmag2.append(aux1[1])
                                    thetamag2.append(aux1[2])
                                case 3:
                                    vmag3.append(aux1[1])
                                    thetamag3.append(aux1[2])
                                case 4:
                                    vmag4.append(aux1[1])
                                    thetamag4.append(aux1[2])
                                case 5:
                                    vmag5.append(aux1[1])
                                    thetamag5.append(aux1[2])
                                case 6:
                                    vmag6.append(aux1[1])
                                    thetamag6.append(aux1[2])
            
            except FileNotFoundError:
                input('\n[Erro] Um dos arquivos não foi encontrado. Tente novamente.\n')
            except KeyError:
                input(f'\n[Erro] O horário "{horario} horas" não foi encontrado no arquivo. Tente novamente.\n')
            except json.JSONDecodeError:
                print('\n[Erro] Um dos arquivos não é um JSON válido. Tente novamente.\n')
            else:
                break

        # criando a tabela de valores normais
        identificador = ['Normal']*len(vmag1)  
        data_base = [vmag1, vmag2, vmag3, vmag4, vmag5, vmag6,
                        thetamag1, thetamag2, thetamag3, thetamag4, thetamag5, thetamag6, identificador]
        vmag = [vmag1,vmag2,vmag3,vmag4,vmag5,vmag6]
        thetamag = [thetamag1,thetamag2,thetamag3,thetamag4,thetamag5,thetamag6]
        data_base = np.array(data_base).T

        #Criando as anomalias nas tensões
        vet_anomalia = []
        vet_pos_anomalia_tens = anomalia['Tensao'][0]
        vet_barra_anomalia_tens = anomalia['Tensao'][1]

        for k,aux in enumerate(anomalia['Tensao'][0]):
            #Alternador para valor acima do range e valor abaixo do range
            if k % 2 == 0:
                tipo = 'up'
            else:
                tipo = 'down'

            vetor_tensao = [vmag1[vet_pos_anomalia_tens[k]], vmag2[vet_pos_anomalia_tens[k]], vmag3[vet_pos_anomalia_tens[k]],
                    vmag4[vet_pos_anomalia_tens[k]], vmag5[vet_pos_anomalia_tens[k]], vmag6[vet_pos_anomalia_tens[k]],
                        thetamag1[vet_pos_anomalia_tens[k]], thetamag2[vet_pos_anomalia_tens[k]], thetamag3[vet_pos_anomalia_tens[k]],
                    thetamag4[vet_pos_anomalia_tens[k]], thetamag5[vet_pos_anomalia_tens[k]], thetamag6[vet_pos_anomalia_tens[k]], 'Anormal']
            
            mag_tens_anomala = self.gerar_valores_anomalos(id='tensao',tipo=tipo,barra=vet_barra_anomalia_tens[k],vmag=vmag,thetamag=thetamag)
            vetor_tensao[vet_barra_anomalia_tens[k]] = mag_tens_anomala
            vet_anomalia.append(vetor_tensao)


        #Criando as anomalias nos ângulos
        vet_pos_anomalia_ang = anomalia['Angulo'][0]
        vet_barra_anomalia_ang = anomalia['Angulo'][1]

        for k,aux in enumerate(anomalia['Angulo'][0]):
            #Alternador para valor acima do range e valor abaixo do range
            if k % 2 == 0:
                tipo = 'up'
            else:
                tipo = 'down'

            vetor_angulo = [vmag1[vet_pos_anomalia_ang[k]], vmag2[vet_pos_anomalia_ang[k]], vmag3[vet_pos_anomalia_ang[k]], 
                    vmag4[vet_pos_anomalia_ang[k]], vmag5[vet_pos_anomalia_ang[k]], vmag6[vet_pos_anomalia_ang[k]],
                    thetamag1[vet_pos_anomalia_ang[k]], thetamag2[vet_pos_anomalia_ang[k]], thetamag3[vet_pos_anomalia_ang[k]], 
                    thetamag4[vet_pos_anomalia_ang[k]], thetamag5[vet_pos_anomalia_ang[k]], thetamag6[vet_pos_anomalia_ang[k]], 'Anormal']
            
            mag_ang_anomala = self.gerar_valores_anomalos(id='angulo',tipo=tipo,barra=vet_barra_anomalia_ang[k],vmag=vmag,thetamag=thetamag)
            vetor_angulo[vet_barra_anomalia_ang[k]+6] = mag_ang_anomala
            vet_anomalia.append(vetor_angulo)

        data_base = pd.DataFrame(data_base)
        vet_anomalia = pd.DataFrame(vet_anomalia)
        data_base_completo = pd.concat([data_base,vet_anomalia], ignore_index=True)

        resp = input('Deseja salvar o arquivo data_base? S-N:  ')
        while True:
            if resp.upper() == 'S':
                resp_s = input('Digite o nome do arquivo para salvar:(utilize a extensão .json)\n')
                dados_para_salvar = data_base_completo.to_numpy().tolist()
                with open(f'{resp_s}', "w") as f:
                    json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

                input('Arquivo salvo.\nPressione qualquer tecla para continuar.')

                break
            elif resp.upper() == 'N':
                break
            else:
                print('Valor inválido')

        return data_base_completo

