import numpy as np
import json
import pandas as pd

class RoughSets():
    def __init__(self):

        data_base_file = input('Digite o nome do arquivo data base para a criação das rough sets:  ')
        while True:
            try:
                with open(data_base_file, mode='r', encoding='utf-8') as f:
                    self.data_base = json.load(f)

                

            except FileNotFoundError:
                    input('\n[Erro] Um dos arquivos não foi encontrado. Tente novamente.\n')
            except json.JSONDecodeError:
                print('\n[Erro] Um dos arquivos não é um JSON válido. Tente novamente.\n')
            else:
                break
        self.df = pd.DataFrame()

    def criar_tabela_decisao(self):
        """
        Transforma a estrutura de dados bruta em um DataFrame estruturado.
        data_base_completo deve ser uma lista/array onde as linhas são amostras 
        e as colunas 0..5 são tensões, 6..11 são ângulos e a última é a condição.
        """
        data = np.array(self.data_base)
    
        colunas_v = [f'V{i+1}' for i in range(6)]
        colunas_a = [f'A{i+1}' for i in range(6)]
        colunas = colunas_v + colunas_a + ['Condicao']
    
        self.df = pd.DataFrame(data, columns=colunas)
    
        # Converte todas as colunas numéricas para float
        for col in colunas_v + colunas_a:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
        return self.df

    def discretizar_dados(self):
        """
        Discretiza atributos contínuos em faixas categóricas.
        Para tensões/ângulos elétricos, pode-se usar quantis ou limites operacionais.
        """
        df_disc = self.df.copy()
        
        colunas_v = [f'V{i+1}' for i in range(6)]
        colunas_a = [f'A{i+1}' for i in range(6)]
        
        # Discretização de Tensão em p.u. 
        for col in colunas_v:
            val = pd.to_numeric(df_disc[col], errors='coerce')
            df_disc[col] = pd.cut(
                val, 
                bins = [-np.inf, 0.90, 0.95, 1.00, 1.05, 1.10, np.inf],
                labels = ['el', 'l', 'nl', 'nh', 'h','eh']
            )
            
        # Discretização de Ângulo em graus
        for col in colunas_a:
            val = pd.to_numeric(df_disc[col], errors='coerce')
            df_disc[col] = pd.cut(
                val, 
                bins=[-np.inf, -5.0, -2.5, 0, 2.5, 5.0, np.inf], 
                labels=['el', 'l', 'nl', 'nh', 'h', 'eh']
            )
            
        return df_disc

    def induzir_regras_rough_sets(self,df_discreto):
        """
        Induz regras onde qualquer classe de indiscernibilidade com proporção de 
        Anomalias >= limiar_anomalia (padrão 5%) é classificada como 'Anormal'.
        """
        limiar_anomalia = 0.05
        atributos_condicionais = [col for col in df_discreto.columns if col != 'Condicao']
        agrupado = df_discreto.groupby(atributos_condicionais, observed=True)
        
        regras = []
        
        for condicao_valores, grupo in agrupado:
            suporte = len(grupo)
            if suporte == 0:
                continue
                
            # 1. Calcula a frequência de anomalias no grupo
            qtd_anormal = (grupo['Condicao'] == 'Anormal').sum()
            confianca_anormal = qtd_anormal / suporte
            
            # 2. Monta a premissa (SE V1=='...' E V2=='...' ...)
            premissas = [f"{attr} == '{val}'" for attr, val in zip(atributos_condicionais, condicao_valores)]
            texto_se = " E ".join(premissas)
            
            # 3. APLICAÇÃO DA REGRA B:
            # Se a probabilidade de anomalia for >= 5%, o filtro dispara 'Anormal'
            if confianca_anormal >= limiar_anomalia:
                decisao_filtro = 'Anormal'
                tipo_regra = 'Alerta Conservador' if confianca_anormal < 1.0 else 'Determinística Anormal'
            else:
                decisao_filtro = 'Normal'
                tipo_regra = 'Determinística Normal' if confianca_anormal == 0 else 'Normal Segura'
                
            regras.append({
                'Tipo': tipo_regra,
                'Regra': f"SE {texto_se} ENTAO Condicao = '{decisao_filtro}'",
                'Decisao_Filtro': decisao_filtro,
                'Suporte': suporte,
                'Confianca_Anormal': round(confianca_anormal, 4),
                'Confianca_Normal': round(1.0 - confianca_anormal, 4)
            })
            
        return pd.DataFrame(regras)

    def extrair_regras_simplificadas(self,df_regras_completas):
        """
        Consolida regras redundantes agrupando por atributos dominantes.
        """
        # Exemplo de consulta para verificar a cobertura acumulada de regras determinísticas
        regras_certas = df_regras_completas[df_regras_completas['Confianca_Anormal'] == 1.0]
        total_coberto = regras_certas['Suporte'].sum()
        
        print(f"Total de Anomalias Retidas em Regras Certas: {total_coberto} de 4000")
        return total_coberto

    def extrair_regras_reduto_local(self, df_discreto, coluna_decisao='Condicao'):
        """
        Gera regras mínimas (Redutos Locais) eliminando condições 
        desnecessárias de cada regra determinística.
        """
        atributos = [col for col in df_discreto.columns if col != coluna_decisao]
        df_anomalias = df_discreto[df_discreto[coluna_decisao] == 'Anormal'].drop_duplicates(subset=atributos)
        df_normais = df_discreto[df_discreto[coluna_decisao] == 'Normal']
        
        regras_minimas = []
        
        for _, linha in df_anomalias.iterrows():
            # Começa com todas as premissas da linha
            premissas_atuais = {attr: linha[attr] for attr in atributos}
            
            # Tenta remover uma a uma mantendo a regra 100% livre de conflito com a classe Normal
            for attr in atributos:
                premissas_teste = premissas_atuais.copy()
                del premissas_teste[attr]
                
                # Monta a condição para a consulta
                query_cond = " & ".join([f"`{k}` == '{v}'" for k, v in premissas_teste.items()])
                
                # CORREÇÃO DO ERRO:
                # Se a query ficou vazia, significa que removemos todas as premissas.
                # Uma regra vazia gera conflito com todas as amostras normais.
                if not query_cond:
                    conflitos = len(df_normais)
                else:
                    conflitos = len(df_normais.query(query_cond))
                
                # Se não colide com dados 'Normal', o atributo pode ser descartado da regra
                if conflitos == 0:
                    premissas_atuais = premissas_teste
                    
            # Monta o texto da regra enxuta
            texto_se = " E ".join([f"{k} == '{v}'" for k, v in premissas_atuais.items()])
            regras_minimas.append(f"SE {texto_se} ENTAO Condicao = 'Anormal'")
            
        # Retorna apenas as regras únicas resultantes
        regras_unicas = pd.DataFrame({'Regra_Minima': list(set(regras_minimas))})
        return regras_unicas

    
    def execucao_rs(self):
        self.criar_tabela_decisao()
        df_discreto = self.discretizar_dados()
        tabela_regras = self.induzir_regras_rough_sets(df_discreto)
        print(tabela_regras)
        reduto_atributos = self.extrair_regras_reduto_local(df_discreto)
        print(reduto_atributos)
        resp = input('Deseja salvar o arquivo data_base? S-N:  ')
        while True:
            if resp.upper() == 'S':
                resp_s = input('Digite o nome do arquivo para salvar:(utilize a extensão .json)\n')
                dados_para_salvar = reduto_atributos.to_dict(orient='records')
                with open(resp_s, "w") as f:
                    json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

                input('Arquivo salvo.\nPressione qualquer tecla para continuar.')
                break
            elif resp.upper() == 'N':
                break
            else:
                print('Valor inválido')
        return reduto_atributos


