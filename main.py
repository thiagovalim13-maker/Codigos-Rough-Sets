from LoadFlow import LoadFlow
from casos_base import CasosBase
from arquivos_rs import Data_Base
from rough_sets import RoughSets
from filtro_rs import FiltroRs


import json
import numpy as np
import pandas as pd
import sys

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
np.set_printoptions(legacy="1.25")
sys.stdout.reconfigure(encoding='utf-8')

#"Barra 4 70.0%, Barra 5 80.0% e Barra 6 79.0%"
vetor_1 = [[1,1.05-0.05,0.0],[2,1.05,-1.2899755423364656],[3,1.0643693181510803,-1.2206160221239375],[4,1.0085282703960157,-2.1157674456642153],
[5,1.0018753353127863,-2.8106448239873476],[6,1.0153517437860342,-2.8206342828523963]]


#"Barra 4 77.0%, Barra 5 88.00000000000001% e Barra 6 76.0%": 
vetor_2 = [[1,1.05,0.0],[2,1.05,-1.6409870038054848],[3,1.0629961777225982,-1.5700306464937925],[4,1.003672796784895,-2.4630040039088428],
[5,0.9957089746429437,-3.211509590305573],[6,1.014926810796786,-3.136609117590474]]



#"Barra 4 88.00000000000001%, Barra 5 77.0% e Barra 6 76.0%": 
vetor_3 = [[1,1.05,0.0],[2,1.05,-1.6423320935185552],[3,1.0662068998237937,-1.4804299148924982],[4,0.9980701284126656,-2.5817019688839573],
[5,1.0033440953007267,-3.0194595406149833],[6,1.0182272805757147,-3.048435733533834]]


with open('six_bus.json', mode='r', encoding='utf-8') as f:
    busses = json.load(f)
with open('six_bus_lines.json', mode='r', encoding='utf-8') as f:
    lines = json.load(f)

while True:
    resp = input(f'Selecione a opção desejada:' 
                 '\n1- LoadFlow caso base six_bus'
                 '\n2- LoadFlow caso alteração de carga six_bus'
                 '\n3- Criar data_base Rough Sets'
                 '\n4- Criar Rough Sets'
                 '\n5- Testar filtro RS'
                 '\n6- Encerrar programa\n'
                 )
    try: 
        resp = int(resp)
    except:
        print('Resposta inválida.')
        input('Pressione qualquer tecla para continuar.')
        continue
    match resp:
        case 1:
            six_bus = LoadFlow(busses, lines)
            v_finais, theta_finais, sol, p_calc,q_calc = six_bus.solve()
            six_bus.print_resposta(p_calc,q_calc,sol)

        case 2:
            casos_base = CasosBase(busses,lines)
            input('Aviso: devido a grande quantidade casos, o programa pode demorar um pouco, não interrompa a execução do programa' \
            'Pressione qualquer tecla para continuar')
            casos_base.caso_mudança_de_carga()

        case 3:
            db = Data_Base()
            db.gerar_estrutura_rs()

        case 4:
            rs = RoughSets()
            rs.execucao_rs()

        case 5:
            filtro = FiltroRs()
            filtro.filtro_rs(vetor_1)

        case 6:
            print('Encerrando programa.')
            break

                

    









'''
#three_bus = LoadFlow('three_buses.json', 'three_lines.json')


#print(f'Tensões finais: \n{v_finais},\nÂngulos finais:\n{np.deg2rad(theta_finais)}')
print(sol)
'''
'''
inicio = time.time()
fim = time.time()
print(f'Tempo de execução: {fim-inicio} segundos.')

print(conjunto.keys())
len1 = len(conjunto['1 linha perdida'])
len2 = len(conjunto['2 linhas perdidas'])
len3 = len(conjunto['1 barra mudando sua carga ativa'])
len4 = len(conjunto['1 barra mudando sua carga ativa e reativa'])
len5 = len(conjunto['Caso perda de 1 linha e mudança de carga'])
len6 = len(conjunto['Caso perda de 2 linhas e mudança de carga'])
len_tot = len1+len2+len3+len4+len5+len6
print(len_tot)
'''
#print(conjunto['1 linha perdida'])
'''
conjunto = six_bus.casos_perda_de_linha()
print(conjunto['1 linha perdida'].keys())
print(conjunto['2 linhas perdidas'].keys())
print(conjunto['1 linha perdida'].keys())
print(len(casos))
print(casos['Caso [2, 4]'])
print(len(casos))
print(list(casos.values()).count('Matriz singular'))
'''