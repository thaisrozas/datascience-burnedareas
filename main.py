import basedosdados as bd
import pandas as pd

df = pd.read_csv("./dados_queimadas.csv")

class Table:
    def __init__(self, df):
        self.df = df

        self.ano = df['ano']
        self.sigla_uf = df['sigla_uf']
        self.id_municipio = df['id_municipio']
        self.bioma = df['bioma']
        self.id_bdq = df['id_bdq']
        self.id_foco = df['id_foco']
        self.data_hora = df['data_hora']
        self.centroide = df['centroide']


TABELA = Table(df)


