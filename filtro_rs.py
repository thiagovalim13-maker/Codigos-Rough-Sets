import pandas as pd
import numpy as np
import json
import copy 



class FiltroRs():
    def filtro_rs(self, vetor_teste):
        rs_filename = input('Digite o nome do arquivo de rough sets:  ')
        with open(rs_filename, mode='r', encoding='utf-8') as f:
            rs = json.load(f)

        regra = {}
        for i,k in enumerate(rs):
            for aux in list(k.values()):
                barra = []
                estado = []
                [aux1,_]= aux.replace(' ', '').split('ENTAO')
                aux1 = aux1.replace('==','=').replace("'","")
                aux1 = aux1[2:]
                aux1 = aux1.replace('E','=')
                aux1 = aux1.split("=")
                for j,aux2 in enumerate(aux1):
                    if j % 2 == 0:
                        barra.append(aux2)
                    else:
                        estado.append(aux2)
            regra[f'{i}'] = [barra,estado]


        amostra = {}


        for linha in vetor_teste:
            barra = linha[0]
            tensao = linha[1]
            angulo = linha[2]

            amostra[f'V{barra}'] = tensao
            amostra[f'A{barra}'] = angulo


        df_amostra = pd.DataFrame([amostra])
        df_discreto = pd.DataFrame()

        rotulos = ['el', 'l', 'nl', 'nh', 'h','eh']
        bins_v = [-np.inf, 0.90, 0.95, 1.00, 1.05, 1.10, np.inf]
        bins_a = [-np.inf, -5.0, -2.5, 0, 2.5, 5.0, np.inf]
        # 3. Discretiza cada coluna de acordo com o tipo (Tensão ou Ângulo)
        for col in df_amostra.columns:
            bins = bins_v if col.startswith('V') else bins_a
            df_discreto[col] = pd.cut(
                df_amostra[col],
                bins=bins,
                labels=rotulos,
                include_lowest=True
            ).astype(str)

        dicionario_discreto = df_discreto.iloc[0].to_dict()


        vetor_estado = []
        normal = True
        for aux in regra.values():
            if len(aux[0])>1:
                cont = 0
                cond = len(aux[0])
                for k,aux1 in enumerate(aux[0]):
                    a1 = dicionario_discreto[aux1]
                    a2 = aux[1][k]
                    if a1 == a2:
                        cont+= 1
                    elif cont == cond:
                        normal = False
                    else:
                        break

            else:
                if dicionario_discreto[aux[0][0]] == aux[1][0]:
                    normal = False
                    break
                else:
                    continue

        vetor_estado.append('Normal' if normal else 'Anormal')
        print('Valor normal' if normal else 'Valor anormal')
        input('Pressione qualquer tecla para continuar')

        return vetor_estado
