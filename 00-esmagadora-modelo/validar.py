import pandas as pd

d = "dados_limpos/"
p = pd.read_csv(d + "fato_producao.csv", parse_dates=["data"])
pa = pd.read_csv(d + "fato_paradas.csv", parse_dates=["data"]).merge(pd.read_csv(d + "dim_motivo_parada.csv"), on="id_motivo")
r = pd.read_csv(d + "fato_recebimento.csv", parse_dates=["data"])
e = pd.read_csv(d + "fato_expedicao.csv", parse_dates=["data"])
l = pd.read_csv(d + "fato_lab_farelo.csv", parse_dates=["data"])

p["ano"] = p.data.dt.year
g = p.groupby("ano").agg(esm=("soja_esmagada_t", "sum"), far=("farelo_produzido_t", "sum"),
                         ol=("oleo_degomado_t", "sum"), h=("horas_trabalhadas", "sum"),
                         hex=("hexano_l", "sum"), vap=("vapor_kg", "sum"), en=("energia_kwh", "sum"))
g["rend_ol"] = g.ol / g.esm * 100
g["rend_far"] = g.far / g.esm * 100
g["t_h"] = g.esm / g.h
g["hex_t"] = g.hex / g.esm
g["vap_t"] = g.vap / g.esm
g["kwh_t"] = g.en / g.esm
print(g.round(2).to_string())
print("\nRecebimento:", r.groupby(r.data.dt.year).peso_liquido_t.sum().round(0).to_dict())
print("Desconto:", r.groupby(r.data.dt.year).desconto_t.sum().round(0).to_dict())
est = [c for c in p if "estoque" in c]
print("\nEstoques:\n", p[est].describe().loc[["min", "max"]].round(0).to_string())
pa["ano"] = pa.data.dt.year
print("\nHoras paradas:\n", (pa.pivot_table(index="motivo", columns="ano", values="duracao_min", aggfunc="sum") / 60).round(0).to_string())
hp = pa.groupby("data").duracao_min.sum() / 60
chk = p.set_index("data").horas_trabalhadas.add(hp, fill_value=0)
print("\nHoras trab + paradas (deve ser ~24):", chk.describe()[["min", "mean", "max"]].round(2).to_dict())
bal = (p.farelo_produzido_t + p.oleo_degomado_t) / p.soja_esmagada_t
print("Farelo + óleo / soja (balanço):", bal.describe()[["min", "mean", "max"]].round(3).to_dict())
print("\nResidual por ano:", l.groupby(l.data.dt.year).residual_farelo_branco_pct.mean().round(3).to_dict())
print("Residual por turno:", l.groupby("turno").residual_farelo_branco_pct.mean().round(3).to_dict())
print("\nExpedição:\n", e.pivot_table(index=e.data.dt.year, columns="produto", values="quantidade_t", aggfunc="sum").round(0).to_string())
