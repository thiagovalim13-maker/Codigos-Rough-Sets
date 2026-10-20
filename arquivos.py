import json
import numpy as np

# módulo de tensão e angulo e seus erros
volt_error = [[1, 0.0001], [1, 0.0001]]

# numero da barra, desvio padrão de potência ativa, desvio padrão de potência reativa
six_bus_inj = [[1, 0.01, 0.01],
           [2, 0.01, 0.01],
           [3, 0.01, 0.01],
           [4, 0.01, 0.01],
           [5, 0.01, 0.01],
           [6, 0.01, 0.01]]

#barra de origem e barra de destino, desvio padrão de potência ativa, desvio padrão de potência reativa
six_branch_flow = [[1,2,0.01,0.01],
               [1,4,0.01,0.01],
               [1,5,0.01,0.01],
               [2,1,0.01,0.01],
               [2,3,0.01,0.01],
               [2,4,0.01,0.01],
               [2,5,0.01,0.01],
               [2,6,0.01,0.01],
               [3,2,0.01,0.01],
               [3,5,0.01,0.01],
               [3,6,0.01,0.01],
               [4,1,0.01,0.01],
               [4,2,0.01,0.01],
               [4,5,0.01,0.01],
               [5,1,0.01,0.01],
               [5,2,0.01,0.01],
               [5,3,0.01,0.01],
               [5,4,0.01,0.01],
               [5,6,0.01,0.01],
               [6,2,0.01,0.01],
               [6,3,0.01,0.01],
               [6,5,0.01,0.01]]

#barra de origem, barra de destino, impedância(R), impedância(X), impedância(B), razão dos trafos
six_lines = [[1,2,0.10,0.20,0.02,1.0],
         [1,4,0.05,0.20,0.02,1.0],
         [1,5,0.08,0.30,0.03,1.0],
         [2,3,0.05,0.25,0.03,1.0],
         [2,4,0.05,0.10,0.01,1.0],
         [2,5,0.10,0.30,0.02,1.0],
         [2,6,0.07,0.20,0.025,1.0],
         [3,5,0.12,0.26,0.025,1.0],
         [3,6,0.02,0.10,0.01,1.0],
         [4,5,0.20,0.40,0.04,1.0],
         [5,6,0.10,0.30,0.03,1.0]]

#0 n° da barra,1 tipo da barra (1:referência,2: geração, 3: carga),2 tensão,3 angulo,4 carga ativa,5 carga reativa,6 potência gerada,
#7 limite de geração superior,7 limite de geração inferior
six_buses = [[1,1,1.05,0,0,0,0,1,-1],
         [2,2,1.05,0,0,0,0.5,1,-1],
         [3,2,1.07,0,0,0,0.6,0.6,-1],
         [4,3,1,0,0.7,0.7,0,0,0],
         [5,3,1,0,0.7,0.7,0,0,0],
         [6,3,1,0,0.7,0.7,0,0,0]]


three_lines = [[1,2, 0.03, 0.3, 0.02, 1],
               [2,3, 0.05, 0.8, 0.01, 1]]


three_buses = [[1, 3, 1,0,0.15,-0.10,0,1,-1],
               [2,1,1,0,0,0,0,-1,1],
               [3,2,1,0,0,0,0.2,-1,-1]]


vet_pos_anomalia = np.random.choice(4000,size = 4000, replace=False)
vet_pos_anomalia_tens = vet_pos_anomalia[:2000]
vet_pos_anomalia_ang = vet_pos_anomalia[2000:]
vet_barra_anomalia_tens = np.random.randint(0,6,size=2000)
vet_barra_anomalia_ang = np.random.randint(0,6,size=2000)

vet_anomalia = []
anomalia = {}
anomalia['Tensao'] = [vet_pos_anomalia_tens.tolist(),vet_barra_anomalia_tens.tolist()]
anomalia['Angulo'] = [vet_pos_anomalia_ang.tolist(),vet_barra_anomalia_ang.tolist()]



with open("anomalia.json", "w") as arquivo:
    json.dump(anomalia, arquivo, ensure_ascii=False, indent=4)

with open("bus_inj.json", "w") as arquivo:
    json.dump(six_bus_inj, arquivo, ensure_ascii=False, indent=4)


with open("branch_flow.json", "w") as arquivo:
    json.dump(six_branch_flow, arquivo, ensure_ascii=False, indent=4)


with open("lines.json", "w") as arquivo1:
    json.dump(six_lines, arquivo1, ensure_ascii=False, indent=4)


with open("buses.json", "w") as arquivo2:
    json.dump(six_buses, arquivo2, ensure_ascii=False, indent=4)


with open("three_buses.json", "w") as arquivo2:
    json.dump(three_buses, arquivo2, ensure_ascii=False, indent=4)


with open("three_lines.json", "w") as arquivo3:
    json.dump(three_lines, arquivo3, ensure_ascii=False, indent=4)







