import matplotlib.pyplot as plt
import basedosdados as bd
import pandas as pd
import requests
import geopandas as gpd
from shapely import wkt


def get_cities_dict():
    res = requests.get(
        "https://servicodados.ibge.gov.br/api/v1/localidades/distritos"
    ).json()
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


def top_5_cities(table):
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


def temporal_analysis(table):
    # Convertendo a coluna 'data_hora' para o tipo datetime
    table.data_hora = pd.to_datetime(table.data_hora)

    # Extraindo o ano da coluna 'data_hora'
    table.ano = table.data_hora.dt.year

    # Agrupando o número de queimadas por ano
    queimadas_por_ano = df.groupby("ano").size()

    # Plotando a tendência temporal das queimadas por ano
    plt.figure(figsize=(10, 6))
    plt.plot(
        queimadas_por_ano.index,
        queimadas_por_ano.values,
        marker="o",
        linestyle="-",
        color="green",
    )
    plt.title("Tendência Temporal das Queimadas por Ano")
    plt.xlabel("Ano")
    plt.ylabel("Número de Queimadas")
    plt.grid(True)
    plt.xticks(queimadas_por_ano.index, rotation=45)
    plt.tight_layout()
    plt.show()


def heat_map(table):
    # Convertendo a coluna 'centroide' para o formato GeoDataFrame
    table["centroide"] = table["centroide"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(table, geometry="centroide")

    # Extraindo as coordenadas de latitude e longitude dos pontos
    gdf["latitude"] = gdf["centroide"].apply(lambda ponto: ponto.y)
    gdf["longitude"] = gdf["centroide"].apply(lambda ponto: ponto.x)

    # Plotando o mapa de calor
    plt.figure(figsize=(10, 8))
    plt.hexbin(gdf["longitude"], gdf["latitude"], gridsize=100, cmap="hot", bins="log")
    plt.colorbar(label="Log Scale")
    plt.title("Mapa de Calor dos Centroides das Queimadas")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.show()


def top_5_biomas(table):
    # Contagem dos focos de queimadas por bioma
    bioma_queimadas = table.df.groupby("bioma").size().sort_values(ascending=False)

    # Obter os top 5 biomas com mais focos de queimadas
    top_biomas = bioma_queimadas.head(5)

    # Criando um gráfico de pizza com cores verdes diferentes para cada parte
    plt.figure(figsize=(8, 8))
    colors = ["limegreen", "forestgreen", "green", "mediumseagreen", "darkgreen"]
    plt.pie(
        top_biomas,
        labels=top_biomas.index,
        autopct="%1.1f%%",
        startangle=190,
        colors=colors,
    )
    plt.title("Porcentagem de Queimadas por Bioma")
    plt.axis("equal")  # Assegura que o gráfico de pizza é desenhado como um círculo.
    plt.show()

    # Criando um gráfico de barras

    plt.figure(figsize=(10, 6))

    # Definindo cores diferentes para as barras
    colors = ["limegreen", "forestgreen", "green", "mediumseagreen", "darkgreen"]

    # Iterando sobre as barras e plotando-as individualmente com cores diferentes
    for i, (bioma, queimadas) in enumerate(top_biomas.items()):
        plt.bar(bioma, queimadas, color=colors[i])

    plt.title("Ranking dos Biomas Mais Afetados por Queimadas")
    plt.xlabel("Bioma")
    plt.ylabel("Número de Queimadas")
    plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo x para facilitar a leitura
    plt.grid(axis="y", linestyle="--", alpha=0.7)  # Adiciona linhas de grade no eixo y
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição de elementos
    plt.show()


def top_yearly_variance_states(table):
    # Calculando a variação anual de queimadas por estado
    var_anual_queimadas = (
        table.df.groupby(["sigla_uf", "ano"])
        .size()
        .unstack()
        .diff(axis=1)
        .dropna(axis=1)
    )

    # Calculando a variação total por estado
    var_total_por_estado = var_anual_queimadas.sum(axis=1)

    # Ordenando os estados pela maior variação total
    var_total_por_estado = var_total_por_estado.sort_values(ascending=False)

    # Selecionando os 5 estados com a maior variação total
    top_estados_variacao = var_total_por_estado.head(5)

    # Criando um gráfico de barras
    plt.figure(figsize=(10, 6))
    bars = top_estados_variacao.plot(kind="bar", color="skyblue")
    plt.title("Estados com Maior Variação Anual de Queimadas")
    plt.xlabel("Estado")
    plt.ylabel("Variação Anual de Queimadas")
    plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo x para facilitar a leitura
    plt.grid(axis="y", linestyle="--", alpha=0.7)  # Adiciona linhas de grade no eixo y

    # Adicionando números em cada barra
    for i, v in enumerate(top_estados_variacao):
        plt.text(i, v + 0.1, str(int(v)), ha="center", va="bottom")

    plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição de elementos
    plt.show()


def temporal_analysis_by_state(table, sigla):
    queimadas_amazonas = data_frame.df[data_frame.df["sigla_uf"] == sigla]

    # Criando um gráfico de linha para a análise temporal das queimadas no Amazonas
    plt.figure(figsize=(10, 6))
    queimadas_amazonas.groupby("ano").size().plot(marker="o", color="green")
    plt.title(f"Análise Temporal das Queimadas no {sigla}")
    plt.xlabel("Ano")
    plt.ylabel("Número de Queimadas")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def top_months(table):
    # Convertendo a coluna de data_hora para o tipo datetime
    table.df["data_hora"] = pd.to_datetime(table.df["data_hora"])

    # Extraindo o mês da coluna de data_hora
    table.df["mes"] = table.df["data_hora"].dt.month

    # Criando um ranking dos meses com maior índice de queimadas
    ranking_meses_queimadas = (
        table.df.groupby("mes").size().sort_values(ascending=False)
    )

    # Plotando o ranking dos meses com maior índice de queimadas
    plt.figure(figsize=(10, 6))
    ranking_meses_queimadas.plot(kind="bar", color="orange")
    plt.title("Ranking dos Meses com Maior Índice de Queimadas")
    plt.xlabel("Mês")
    plt.ylabel("Número de Queimadas")
    plt.xticks(rotation=0)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


def top_5_states(table):
    # Calculando a soma total de queimadas por estado
    soma_total_queimadas_por_estado = data_frame.df.groupby("sigla_uf").size()

    # Selecionando os 5 estados com maior soma total de queimadas
    top_estados_queimadas_total = soma_total_queimadas_por_estado.nlargest(5)

    # Criando um gráfico de barras
    plt.figure(figsize=(10, 6))
    top_estados_queimadas_total.plot(kind="bar", color="orange")
    plt.title("Estados com Maior Número de Queimadas")
    plt.xlabel("Estado")
    plt.ylabel("Número de Queimadas Total")
    plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo x para facilitar a leitura
    plt.grid(axis="y", linestyle="--", alpha=0.7)  # Adiciona linhas de grade no eixo y
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição de elementos
    plt.show()


def top_5_hours(table):
    # Extraindo a hora da coluna de data_hora
    table.df["data_hora"] = pd.to_datetime(table.df["data_hora"])
    table.df["hora"] = table.df["data_hora"].dt.hour

    # Criando um ranking das horas com maior índice de queimadas
    ranking_horas_queimadas = (
        table.df.groupby("hora").size().sort_values(ascending=False)
    )

    # Plotando o ranking das horas com maior índice de queimadas
    plt.figure(figsize=(10, 6))
    ranking_horas_queimadas.plot(kind="bar", color="orange")
    plt.title("Ranking das Horas com Maior Índice de Queimadas")
    plt.xlabel("Hora do Dia")
    plt.ylabel("Número de Queimadas")
    plt.xticks(rotation=0)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


def top_5_centroid(table):
    centroides_freq = table.df["centroide"].value_counts()

    # Selecionar os cinco centroides com as maiores frequências
    top_5_centroides = centroides_freq.nlargest(5)
    # Coordenadas dos cinco centroides com os maiores índices de queimadas
    top_5_centroides_coords = [
        (-54.802, -13.035),
        (-54.316, -11.985),
        (-56.719, -7.392),
        (-52.633, -6.27),
        (-64.019, -12.076),
    ]

    # Carregar o contorno do Brasil
    brasil = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    # Filtrar apenas o contorno do Brasil
    brasil = brasil[brasil.name == "Brazil"]

    # Plotar o contorno do Brasil
    fig, ax = plt.subplots(figsize=(10, 10))
    brasil.boundary.plot(ax=ax, color="black")

    # Plotar os pontos dos cinco centroides com os maiores índices de queimadas
    for lon, lat in top_5_centroides_coords:
        ax.plot(lon, lat, "ro", markersize=10, color="green")

    # Adicionar título
    plt.title("Top 5 Centroides das Queimadas no Brasil")

    # Exibir o mapa
    plt.show()


# Top 5 Municípios com Mais Queimadas
top_5_cities(data_frame)

# Análise temporal
temporal_analysis(data_frame)

# Mapa de calor no Brasil
heat_map(df)

# Ranking dos Biomas Mais Afetados
top_5_biomas(data_frame)

# Estados com Maior Variação Anual de Queimadas
top_yearly_variance_states(data_frame)

# Analise temporal das queimadas do Pará
temporal_analysis_by_state(data_frame, "PA")

# Top Meses com Mais Queimadas
top_months(data_frame)

# Top 5 Estados com Mais Queimadas
top_5_states(data_frame)

# Top 5 Horarios com mais queimadas
top_5_hours(data_frame)

# Top 5 Centroides das queimadas no Brasil
top_5_centroid(data_frame)
