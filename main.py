import matplotlib.pyplot as plt
import basedosdados as bd
import pandas as pd
import requests


def get_cities_dict():
    res = requests.get(
        "https://servicodados.ibge.gov.br/api/v1/localidades/distritos"
    ).json()
    print(res[0])
    cities_dict = {}
    for city in res:
        cities_dict[city["municipio"]["id"]] = city["nome"]
    return cities_dict


def get_city_name(city_id, cities_dict):
    return cities_dict.get(city_id)


cities_dict = get_cities_dict()


class TabelaAcesso:
    def __init__(self, df, cities_dict):
        self.df = df

        self.ano = df["ano"]
        self.sigla_uf = df["sigla_uf"]
        self.id_municipio = df["id_municipio"]
        self.bioma = df["bioma"]
        self.id_bdq = df["id_bdq"]
        self.id_foco = df["id_foco"]
        self.data_hora = df["data_hora"]
        self.centroide = df["centroide"]

        self.df["nome"] = self.id_municipio.apply(
            lambda x: get_city_name(x, cities_dict)
        )


file_path = "./dados_queimadas.csv"
df = pd.read_csv(file_path)
data_frame = TabelaAcesso(df, cities_dict)


def get_top_5_cities(table):
    top_cities = (
        table.df.groupby("id_municipio").size().sort_values(ascending=False).head(5)
    )
    top_cities = top_cities.rename(index=lambda x: cities_dict.get(x))
    ax = top_cities.plot(kind="bar", title="Top 5 Municípios com Mais Queimadas")
    plt.xlabel("Município")
    plt.ylabel("Número de Queimadas")
    for i, v in enumerate(top_cities):
        ax.text(i, v + 0.1, str(v), ha="center", va="bottom")
    plt.show()


# Top 5 Municípios com Mais Queimadas
get_top_5_cities(data_frame)

# Top 3 Estados com Mais Queimadas

# Ranking dos Biomas Mais Afetados

# Municípios com Maior Média Anual de Queimadas

# Estados com Maior Variação Anual de Queimadas

# Top 3 Meses com Mais Incêndios

# Ranking de Focos de Incêndio Mais Comuns
