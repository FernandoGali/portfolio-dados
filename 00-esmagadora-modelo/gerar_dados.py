"""
Gerador de dados fictícios da Esmagadora Modelo (esmagamento de soja).

Simula, dia a dia, de 01/01/2022 a 30/09/2026:
  recebimento de soja -> estoque em silo -> esmagamento -> farelo + óleo degomado
  -> expedição, com paradas, consumo de utilidades e análises de laboratório.

Todos os nomes, números e eventos são inventados. A estrutura foi inspirada
em um boletim diário de produção típico do setor.

Saída: pasta dados_limpos/ (CSV UTF-8, separador vírgula, decimal ponto)
       e esmagadora_modelo.xlsx (mesmas tabelas, uma por aba).
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

INICIO, FIM = "2022-01-01", "2026-09-30"
SAIDA = Path(__file__).parent / "dados_limpos"

# ---------------------------------------------------------------- parâmetros
CAP_SILO_SOJA = 140_000   # t
CAP_FARELO = 28_000       # t
CAP_OLEO = 6_000          # t
TAXA_NOMINAL = 61.0       # t/h esmagadas

# Parâmetros de cada ano
CENARIO = {
    # recebimento anual alvo (t), multiplicador de expedição de farelo,
    # índice de hexano base (L/t), residual de óleo no farelo base (%)
    2022: dict(receb=470_000, exp_farelo=1.00, hexano=1.32, residual=0.66),
    2023: dict(receb=455_000, exp_farelo=1.00, hexano=1.40, residual=0.63),
    2024: dict(receb=490_000, exp_farelo=1.02, hexano=0.95, residual=0.61),
    2025: dict(receb=430_000, exp_farelo=0.74, hexano=0.92, residual=0.82),
    2026: dict(receb=300_000, exp_farelo=1.05, hexano=0.90, residual=0.52),
}

# Sazonalidade do recebimento (safra fev-jun)
SAZ_RECEB = {1: .55, 2: 1.35, 3: 2.0, 4: 2.05, 5: 1.7, 6: 1.25, 7: .95,
             8: .75, 9: .55, 10: .45, 11: .4, 12: .35}
media_saz = np.mean(list(SAZ_RECEB.values()))
SAZ_RECEB = {m: v / media_saz for m, v in SAZ_RECEB.items()}

# Sazonalidade da exportação de farelo (porto mais ativo mar-ago)
SAZ_EXP = {1: .85, 2: .9, 3: 1.1, 4: 1.15, 5: 1.15, 6: 1.1, 7: 1.05,
           8: 1.0, 9: .95, 10: .9, 11: .9, 12: .95}

TURNOS = {"I": (7, 15), "II": (15, 23), "III": (23, 7)}

# ---------------------------------------------------------------- dimensões
MOTIVOS = pd.DataFrame([
    (1, "Processo", "Não planejada", "Processo"),
    (2, "Falha mecânica", "Não planejada", "Manutenção"),
    (3, "Falha elétrica", "Não planejada", "Manutenção"),
    (4, "Falha de automação / instrumentação", "Não planejada", "Manutenção"),
    (5, "Falta de energia (interna)", "Não planejada", "Utilidades"),
    (6, "Falta de energia (externa)", "Não planejada", "Utilidades"),
    (7, "Outras paradas", "Não planejada", "Outros"),
    (8, "Entressafra", "Planejada", "Programação"),
    (9, "Falta de matéria-prima", "Planejada", "Supply Chain"),
    (10, "Falta de espaço para armazenar", "Planejada", "Supply Chain"),
    (11, "Manutenção preventiva", "Planejada", "Manutenção"),
], columns=["id_motivo", "motivo", "tipo", "area_responsavel"])

EQUIPAMENTOS = pd.DataFrame([
    (1, "MOE-01", "Moega de recebimento", "Recebimento"),
    (2, "SEC-01", "Secador de grãos", "Preparação"),
    (3, "QBR-01", "Quebrador", "Preparação"),
    (4, "DSC-01", "Descascador", "Preparação"),
    (5, "CND-01", "Condicionador", "Preparação"),
    (6, "LAM-01", "Laminador 1", "Preparação"),
    (7, "LAM-02", "Laminador 2", "Preparação"),
    (8, "EXP-01", "Expander", "Preparação"),
    (9, "EXT-01", "Extrator", "Extração"),
    (10, "DT-01", "Dessolventizador-tostador 1", "Extração"),
    (11, "DT-02", "Dessolventizador-tostador 2", "Extração"),
    (12, "DST-01", "Destilaria de óleo", "Extração"),
    (13, "DEG-01", "Degomagem", "Óleo"),
    (14, "PEL-01", "Peletizadora de casca", "Farelo"),
    (15, "RSC-01", "Rosca transportadora de farelo", "Farelo"),
    (16, "CLD-01", "Caldeira", "Utilidades"),
    (17, "SUB-01", "Subestação", "Utilidades"),
], columns=["id_equipamento", "tag", "equipamento", "setor"])

# frases de parada por motivo: (texto, tags de equipamento possíveis)
FRASES = {
    "Processo": [("Embuchamento válvula rotativa {eq}", ["DT-01", "DT-02", "EXT-01"]),
                 ("Ajuste de temperatura {eq}", ["CND-01", "DT-01", "DT-02"]),
                 ("Entupimento de rosca {eq}", ["RSC-01", "EXT-01"]),
                 ("Excesso de umidade na massa {eq}", ["CND-01", "EXP-01"])],
    "Falha mecânica": [("Quebra de corrente {eq}", ["EXT-01", "RSC-01"]),
                       ("Troca de rolamento {eq}", ["LAM-01", "LAM-02", "QBR-01"]),
                       ("Vazamento de vapor {eq}", ["DT-01", "DT-02", "CND-01"]),
                       ("Desalinhamento de rolos {eq}", ["LAM-01", "LAM-02"]),
                       ("Quebra de eixo {eq}", ["EXP-01", "RSC-01", "DSC-01"])],
    "Falha elétrica": [("Queima de motor {eq}", ["LAM-01", "LAM-02", "RSC-01", "EXP-01"]),
                       ("Desarme de disjuntor {eq}", ["EXT-01", "DT-01", "SUB-01"]),
                       ("Falha no inversor {eq}", ["EXT-01", "RSC-01"])],
    "Falha de automação / instrumentação": [("Desarme sensor de nível {eq}", ["DT-01", "DT-02", "EXT-01"]),
                                            ("Falha de comunicação CLP {eq}", ["EXT-01", "DST-01"]),
                                            ("Leitura incorreta de temperatura {eq}", ["DT-01", "DT-02", "CND-01"])],
    "Falta de energia (interna)": [("Queda de energia interna {eq}", ["SUB-01"])],
    "Falta de energia (externa)": [("Queda de energia da concessionária", ["SUB-01"])],
    "Outras paradas": [("Limpeza emergencial {eq}", ["EXT-01", "DST-01"]),
                       ("Parada por inspeção de segurança", ["EXT-01"])],
    "Manutenção preventiva": [("Manutenção preventiva programada", [None])],
    "Entressafra": [("Parada programada de entressafra", [None])],
    "Falta de matéria-prima": [("Falta de MP", [None])],
    "Falta de espaço para armazenar": [("Armazém de farelo cheio", ["RSC-01"])],
}

# taxa de ocorrência por dia e duração mediana (h) das paradas não planejadas
NAO_PLANEJADAS = {
    "Processo": (0.10, 0.45),
    "Falha mecânica": (0.16, 1.4),
    "Falha elétrica": (0.05, 0.9),
    "Falha de automação / instrumentação": (0.04, 0.5),
    "Falta de energia (interna)": (0.004, 0.6),
    "Falta de energia (externa)": (0.012, 1.0),
    "Outras paradas": (0.015, 1.5),
}


def gerar_fornecedores(n=160):
    prefixos = ["Fazenda", "Sítio", "Agropecuária", "Cooperativa Agrícola", "Grupo"]
    nomes = ["Santa Clara", "Boa Vista", "São João", "Três Irmãos", "Bela Aurora",
             "Vale Verde", "Santa Rita", "Recanto", "Primavera", "Esperança",
             "Bom Jardim", "Santo Antônio", "Água Limpa", "Ouro Verde", "Palmeiras",
             "Serra Azul", "Rio Claro", "São Pedro", "Monte Alegre", "Paraíso",
             "Campo Belo", "Estrela", "Pinheiros", "Lagoa Seca", "Nova Era",
             "Santa Helena", "Cachoeira", "Bandeirantes", "Jatobá", "Ipê Amarelo",
             "Aroeira", "Cerrado Vivo", "Sol Nascente", "Duas Pontes", "Mata Velha",
             "Santa Luzia", "Horizonte", "Capim Dourado", "Pedra Branca", "Coqueiros"]
    regioes = ["Alta Mogiana", "Noroeste Paulista", "Triângulo Mineiro",
               "Sul de Goiás", "Centro-Oeste Paulista", "Sudoeste de Goiás"]
    peso_reg = [.28, .22, .2, .12, .1, .08]
    linhas, usados = [], set()
    while len(linhas) < n:
        nome = f"{rng.choice(prefixos)} {rng.choice(nomes)}"
        if nome in usados:
            nome = f"{nome} {rng.choice(['I', 'II', 'Norte', 'Sul', 'Velha', 'Nova'])}"
        if nome in usados:
            continue
        usados.add(nome)
        tipo = "Cooperativa" if "Cooperativa" in nome else ("Grupo" if "Grupo" in nome else "Produtor")
        linhas.append((len(linhas) + 1, f"F{len(linhas) + 1:04d}", nome, tipo,
                       rng.choice(regioes, p=peso_reg)))
    df = pd.DataFrame(linhas, columns=["id_fornecedor", "cod_fornecedor", "fornecedor", "tipo", "regiao"])
    # volume concentrado (Pareto): poucos fornecedores entregam muito
    pesos = rng.pareto(1.3, n) + 0.05
    pesos[df["tipo"].ne("Produtor").to_numpy()] *= 4
    df["_peso"] = pesos / pesos.sum()
    return df


def gerar_clientes():
    dados = [
        ("Nutri Ração Ltda", "Fábrica de ração", "Farelo"),
        ("Rações Campo Forte", "Fábrica de ração", "Farelo"),
        ("Avícola Planalto", "Integradora avícola", "Farelo"),
        ("Granja Sete Lagoas", "Integradora suína", "Farelo"),
        ("Coop. Leiteira Vale do Rio", "Cooperativa", "Farelo"),
        ("Trading Atlântico Grãos", "Trading (exportação)", "Farelo"),
        ("Exporta Sul Commodities", "Trading (exportação)", "Farelo"),
        ("Pecuária Três Marias", "Confinamento", "Farelo"),
        ("Rações Bom Trato", "Fábrica de ração", "Farelo"),
        ("Avícola Serra Dourada", "Integradora avícola", "Farelo"),
        ("Refinadora Ouro Fino", "Refinaria de óleo", "Óleo"),
        ("BioEnergia Cerrado", "Usina de biodiesel", "Óleo"),
        ("Óleos Vegetais Paulista", "Refinaria de óleo", "Óleo"),
        ("Trading Atlântico Grãos", "Trading (exportação)", "Óleo"),
        ("Biodiesel Rio Grande", "Usina de biodiesel", "Óleo"),
    ]
    df = pd.DataFrame(dados, columns=["cliente", "segmento", "produto"])
    df.insert(0, "id_cliente", range(1, len(df) + 1))
    df["_peso"] = rng.dirichlet(np.ones(len(df)) * 1.2)
    return df


def calendario():
    datas = pd.date_range(INICIO, FIM, freq="D")
    cal = pd.DataFrame({"data": datas})
    cal["ano"] = cal.data.dt.year
    cal["mes"] = cal.data.dt.month
    cal["nome_mes"] = cal.mes.map({1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
                                   7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"})
    cal["trimestre"] = cal.data.dt.quarter
    cal["semana_iso"] = cal.data.dt.isocalendar().week.astype(int)
    cal["dia_semana"] = cal.data.dt.dayofweek.map({0: "seg", 1: "ter", 2: "qua", 3: "qui",
                                                   4: "sex", 5: "sáb", 6: "dom"})
    cal["periodo"] = np.where(cal.mes.between(2, 7), "Safra", "Entressafra")
    return cal


def hora_para_turno(h):
    if 7 <= h < 15:
        return "I"
    if 15 <= h < 23:
        return "II"
    return "III"


# ---------------------------------------------------------------- simulação
def simular():
    cal = calendario()
    forn = gerar_fornecedores()
    cli = gerar_clientes()
    cli_farelo = cli[cli.produto == "Farelo"]
    cli_oleo = cli[cli.produto == "Óleo"]

    # entressafra: uma parada longa por ano, entre dezembro e janeiro
    bloqueios = set()
    for ano in range(2022, 2026):
        ini = pd.Timestamp(f"{ano}-12-01") + pd.Timedelta(days=int(rng.integers(5, 25)))
        for d in pd.date_range(ini, periods=int(rng.integers(24, 34))):
            bloqueios.add(d)
    # preventiva: um dia por mês (fora da entressafra)
    preventivas = {}
    for (ano, mes), g in cal.groupby(["ano", "mes"]):
        candidatos = [d for d in g.data if d not in bloqueios and d.dayofweek < 5]
        if candidatos:
            preventivas[candidatos[int(rng.integers(0, len(candidatos)))]] = float(rng.uniform(8, 16))

    est_soja, est_farelo, est_oleo = 45_000.0, 9_000.0, 1_800.0
    # Operação em campanha: sem matéria-prima ou sem espaço, a fábrica PARA e só
    # volta a rodar cheia quando há estoque/espaço para alguns dias (não roda a meia carga).
    rng_op = np.random.default_rng(SEED + 1)
    aguardando_mp = aguardando_espaco = False
    ontem_parado = False
    motivo_ontem = "Falta de matéria-prima"
    DIAS_PARA_RETOMAR_MP = 5.0
    DIAS_PARA_RETOMAR_ESPACO = 2.0
    prod, paradas, lab, lab_soja, receb, exped = [], [], [], [], [], []
    n_ticket, n_parada, n_lab, n_nf = 0, 0, 0, 0

    for d in cal.data:
        ano, mes = d.year, d.month
        cen = CENARIO[ano]

        # ---- recebimento do dia (chega em caminhões)
        fator_semana = {5: 0.65, 6: 0.25}.get(d.dayofweek, 1.08)
        alvo = cen["receb"] / 365 * SAZ_RECEB[mes] * fator_semana
        receb_dia = float(rng.gamma(4, alvo / 4)) if alvo > 0 else 0.0
        receb_dia = min(receb_dia, max(CAP_SILO_SOJA - est_soja, 0))
        cargas_dia = []
        total = 0.0
        while total < receb_dia - 10:
            peso = float(np.clip(rng.normal(37.5, 4.5), 15, 49))
            cargas_dia.append(peso)
            total += peso
        receb_dia = sum(cargas_dia)

        # qualidade da soja na safra/entressafra
        umid_base = 11.2 + (1.6 if mes in (2, 3) else 0) - (1.2 if mes in (8, 9, 10) else 0)
        for peso in cargas_dia:
            n_ticket += 1
            f = forn.sample(1, weights="_peso", random_state=int(rng.integers(1e9))).iloc[0]
            umid = float(np.clip(rng.normal(umid_base, 1.6), 7.5, 19))
            imp = float(np.clip(rng.gamma(4, 0.25), 0.1, 4.5))
            avar = float(np.clip(rng.gamma(3, 2.4 + (1.5 if ano == 2026 else 0)), 0.5, 30))
            verde = float(np.clip(rng.gamma(2, 1.3 + (2 if ano in (2022, 2023) else 0)), 0, 20))
            prot = float(np.clip(rng.normal(34.8 - (1.2 if ano == 2026 else 0), 0.9), 31, 38))
            oleo = float(np.clip(rng.normal(21.3, 0.7), 18.5, 23.5))
            # desconto por classificação (regra simplificada de mercado)
            desc_pct = (max(umid - 14, 0) * 1.5 + max(imp - 1, 0) + max(avar - 8, 0) * 0.5) / 100
            hora = int(np.clip(rng.normal(13, 3.5), 6, 22))
            receb.append(dict(
                id_ticket=f"RC{n_ticket:06d}", data=d.date(),
                hora_entrada=f"{hora:02d}:{int(rng.integers(0, 60)):02d}",
                id_fornecedor=int(f.id_fornecedor), peso_bruto_t=round(peso + 18.2 + rng.normal(0, 0.6), 2),
                peso_liquido_t=round(peso, 2), umidade_pct=round(umid, 2), impureza_pct=round(imp, 2),
                avariados_pct=round(avar, 2), esverdeados_pct=round(verde, 2),
                proteina_pct=round(prot, 2), oleo_pct=round(oleo, 2),
                desconto_t=round(peso * desc_pct, 3)))
        receb_liq = receb_dia - sum(r["desconto_t"] for r in receb[len(receb) - len(cargas_dia):])

        # ---- expedição (antes da produção, libera espaço)
        exp_far = rng.gamma(5, 980 / 5) * SAZ_EXP[mes] * cen["exp_farelo"]
        if est_farelo > 0.8 * CAP_FARELO:
            exp_far *= 1.05 if ano == 2025 else 1.3
        exp_far = max(min(exp_far, est_farelo), 0)
        exp_ol = rng.gamma(3, 250 / 3)
        if est_oleo > 0.8 * CAP_OLEO:
            exp_ol *= 1.4
        exp_ol = max(min(exp_ol, est_oleo), 0)
        for produto, qtd, cap_carga, clientes in (("Farelo", exp_far, 37.0, cli_farelo),
                                                   ("Óleo", exp_ol, 31.0, cli_oleo)):
            total = 0.0
            limite = est_farelo if produto == "Farelo" else est_oleo
            while total < qtd - cap_carga * 0.6:
                carga = float(np.clip(rng.normal(cap_carga, 2.5), 14, cap_carga + 6))
                carga = min(carga, limite - total)
                if carga < 14:
                    break
                n_nf += 1
                c = clientes.sample(1, weights="_peso", random_state=int(rng.integers(1e9))).iloc[0]
                exped.append(dict(id_expedicao=f"EX{n_nf:06d}", data=d.date(), produto=produto,
                                  id_cliente=int(c.id_cliente), quantidade_t=round(carga, 2)))
                total += carga
            if produto == "Farelo":
                est_farelo -= total
            else:
                est_oleo -= total

        # ---- horas e paradas
        eventos = []  # (motivo, horas)
        if d in bloqueios:
            eventos.append(("Entressafra", 24.0))
        else:
            if d in preventivas:
                eventos.append(("Manutenção preventiva", preventivas[d]))
            for motivo, (taxa, mediana) in NAO_PLANEJADAS.items():
                taxa_ef = taxa * (1.8 if motivo == "Falta de energia (externa)" and mes in (11, 12, 1, 2, 3) else 1)
                for _ in range(rng.poisson(taxa_ef)):
                    eventos.append((motivo, float(min(rng.lognormal(np.log(mediana), 0.8), 14))))
            # evento raro: quebra longa
            if rng.random() < 0.004:
                eventos.append(("Falha mecânica", float(rng.uniform(14, 22))))
        soma = sum(h for _, h in eventos)
        if soma > 24.0:  # eventos sobrepostos no mesmo dia: o dia tem no máximo 24 h
            eventos = [(m, h * 24.0 / soma) for m, h in eventos]
        horas_paradas = min(sum(h for _, h in eventos), 24.0)
        horas_disp = 24.0 - horas_paradas

        taxa = float(np.clip(rng.normal(TAXA_NOMINAL + (1 if ano >= 2024 else 0), 2.4), 48, 67))
        cheio_dia = 24.0 * taxa
        desejado = horas_disp * taxa

        # ---- partida: no dia em que volta a rodar depois de um dia parado, roda só parte do dia
        # (as horas antes da partida contam no motivo que deixou a fábrica parada)
        if d not in bloqueios and ontem_parado and not aguardando_mp and not aguardando_espaco and desejado > 0:
            horas_partida = float(rng_op.uniform(8, 18))
            if horas_partida < horas_disp:
                eventos.append((motivo_ontem, horas_disp - horas_partida))
                desejado = horas_partida * taxa

        # ---- limite por matéria-prima (campanha)
        disponivel_soja = est_soja + 0.55 * receb_liq - 300  # 300 t de lastro no silo
        if d in bloqueios:
            esmagado = 0.0
        elif aguardando_mp:
            if disponivel_soja >= DIAS_PARA_RETOMAR_MP * cheio_dia:
                aguardando_mp = False
                horas_partida = float(rng_op.uniform(8, 18))
                desejado = min(desejado, horas_partida * taxa)
                eventos.append(("Falta de matéria-prima", max(horas_disp - horas_partida, 0)))
                esmagado = desejado
            else:
                eventos.append(("Falta de matéria-prima", horas_disp))
                esmagado = 0.0
        else:
            esmagado = min(desejado, max(disponivel_soja, 0))
            if desejado - esmagado > 0.5 * taxa:
                eventos.append(("Falta de matéria-prima", (desejado - esmagado) / taxa))
                aguardando_mp = True

        # ---- rendimentos
        umid_ind = float(np.clip(rng.normal(10.1, 0.5), 8.5, 12))
        oleo_ind = float(np.clip(rng.normal(21.4, 0.35), 20.2, 22.6))
        residual_dia = float(np.clip(rng.normal(cen["residual"], 0.05) + 0.004 * (taxa - 61), 0.3, 1.4))
        rend_oleo = (oleo_ind - 1.25 - 0.8 * (residual_dia - 0.5) + rng.normal(0, 0.12)) / 100
        rend_farelo = (72.5 + 0.35 * (umid_ind - 10.1) + rng.normal(0, 0.35)) / 100

        # ---- limite por espaço no armazém de farelo
        espaco = CAP_FARELO - est_farelo
        if aguardando_espaco and esmagado > 0:
            if espaco >= DIAS_PARA_RETOMAR_ESPACO * cheio_dia * rend_farelo:
                aguardando_espaco = False
            else:
                eventos.append(("Falta de espaço para armazenar", esmagado / taxa))
                esmagado = 0.0
        if esmagado * rend_farelo > espaco:
            novo = max(espaco, 0) / rend_farelo
            eventos.append(("Falta de espaço para armazenar", (esmagado - novo) / taxa))
            esmagado = novo
            aguardando_espaco = True
        espaco_ol = CAP_OLEO - est_oleo
        if esmagado * rend_oleo > espaco_ol:
            novo = max(espaco_ol, 0) / rend_oleo
            eventos.append(("Falta de espaço para armazenar", (esmagado - novo) / taxa))
            esmagado = novo

        horas_trab = round(esmagado / taxa, 2) if esmagado > 0 else 0.0
        ontem_parado = esmagado <= 0
        if ontem_parado and eventos:
            motivo_ontem = max(eventos, key=lambda e: e[1])[0]
        farelo = esmagado * rend_farelo
        oleo = esmagado * rend_oleo
        est_soja = est_soja + receb_liq - esmagado
        est_farelo += farelo
        est_oleo += oleo

        # ---- utilidades (parte fixa por hora: consumo específico sobe quando a taxa cai)
        if esmagado > 0:
            partida = horas_trab < 20
            hex_lt = cen["hexano"] * (1.25 if partida else 1) * float(rng.lognormal(0, 0.12))
            if rng.random() < 0.01:
                hex_lt *= rng.uniform(1.6, 2.6)  # vazamento / perda pontual
            hexano = esmagado * hex_lt
            vapor = 195 * esmagado + 4300 * horas_trab + (9000 if partida else 0)
            vapor *= float(rng.lognormal(0, 0.05))
            energia = (37 * esmagado + 520 * horas_trab) * float(rng.lognormal(0, 0.04))
        else:
            hexano = vapor = energia = 0.0

        prod.append(dict(data=d.date(), soja_esmagada_t=round(esmagado, 2), horas_trabalhadas=horas_trab,
                         farelo_produzido_t=round(farelo, 2), oleo_degomado_t=round(oleo, 2),
                         hexano_l=round(hexano), vapor_kg=round(vapor), energia_kwh=round(energia),
                         estoque_soja_t_fechamento=round(est_soja, 2),
                         estoque_farelo_t_fechamento=round(est_farelo, 2),
                         estoque_oleo_t_fechamento=round(est_oleo, 2)))

        # ---- grava paradas como eventos com horário de início
        cursor = float(rng.uniform(0, 3))
        for motivo, horas in eventos:
            if horas < 0.05:
                continue
            frase, tags = FRASES[motivo][int(rng.integers(0, len(FRASES[motivo])))]
            tag = tags[int(rng.integers(0, len(tags)))]
            if motivo == "Entressafra":
                inicio = 0.0
            else:
                inicio = float(rng.uniform(0, max(24 - horas, 0.1)))
            n_parada += 1
            eq_id = None if tag is None else int(EQUIPAMENTOS.loc[EQUIPAMENTOS.tag == tag, "id_equipamento"].iloc[0])
            paradas.append(dict(
                id_parada=f"PA{n_parada:06d}", data=d.date(),
                hora_inicio=f"{int(inicio):02d}:{int((inicio % 1) * 60):02d}",
                turno=hora_para_turno(int(inicio)),
                id_motivo=int(MOTIVOS.loc[MOTIVOS.motivo == motivo, "id_motivo"].iloc[0]),
                id_equipamento=eq_id, duracao_min=int(round(min(horas, 24) * 60)),
                descricao=frase.format(eq=tag or "").strip()))

        # ---- laboratório do farelo por turno (só turnos que rodaram)
        if horas_trab > 0:
            n_turnos = int(np.ceil(horas_trab / 8))
            turnos_rodaram = ["I", "II", "III"][:n_turnos] if n_turnos < 3 else ["III", "I", "II"]
            for t in turnos_rodaram:
                efeito = {"I": -0.02, "II": 0.0, "III": 0.035}[t]
                res = float(np.clip(residual_dia + efeito + rng.normal(0, 0.04), 0.25, 1.6))
                umid_f = float(np.clip(rng.normal(11.35, 0.3), 10.2, 12.8))
                fibra = float(np.clip(rng.normal(6.2, 0.35), 5.0, 7.8))
                prot_f = float(np.clip(46.0 - 0.45 * (umid_f - 11.35) - 0.5 * (fibra - 6.2)
                                       - (0.4 if ano == 2026 else 0) + rng.normal(0, 0.18), 44, 48))
                n_lab += 1
                lab.append(dict(
                    id_analise=f"LB{n_lab:06d}", data=d.date(), turno=t,
                    residual_farelo_branco_pct=round(res, 2),
                    residual_pellets_pct=round(float(np.clip(rng.normal(1.18, 0.12), 0.7, 2.2)), 2),
                    umidade_pct=round(umid_f, 2), proteina_pct=round(prot_f, 2), fibra_pct=round(fibra, 2),
                    silica_pct=round(float(np.clip(rng.normal(0.82, 0.09), 0.5, 1.3)), 2),
                    oleo_casca_pct=round(float(np.clip(rng.lognormal(np.log(1.0), 0.35), 0.4, 4.5)), 2)
                    if t != "III" else None,
                    atividade_ureatica=round(float(np.clip(rng.normal(0.065, 0.01), 0.02, 0.2)), 3),
                    proteina_soluvel_pct=round(float(np.clip(rng.normal(81.5, 0.7), 78, 84)), 2)
                    if t == "II" else None))
            n_lab_soja = len(lab_soja) + 1
            lab_soja.append(dict(
                data=d.date(), proteina_pct=round(float(np.clip(rng.normal(34.7 - (1.1 if ano == 2026 else 0), 0.5), 32, 37)), 2),
                oleo_pct=round(oleo_ind, 2), umidade_pct=round(umid_ind, 2),
                impureza_pct=round(float(np.clip(rng.normal(1.05, 0.2), 0.4, 2.2)), 2),
                avariados_pct=round(float(np.clip(rng.normal(7.4 + (1 if ano == 2026 else 0), 1.2), 3, 14)), 2),
                esverdeados_pct=round(float(np.clip(rng.normal(2.6 + (4 if ano in (2022, 2023) else 0), 0.8), 0.3, 12)), 2)))

    tabelas = {
        "dim_calendario": cal,
        "dim_motivo_parada": MOTIVOS,
        "dim_equipamento": EQUIPAMENTOS,
        "dim_fornecedor": forn.drop(columns="_peso"),
        "dim_cliente": cli.drop(columns="_peso"),
        "fato_producao": pd.DataFrame(prod),
        "fato_paradas": pd.DataFrame(paradas),
        "fato_lab_farelo": pd.DataFrame(lab),
        "fato_lab_soja_industrializada": pd.DataFrame(lab_soja),
        "fato_recebimento": pd.DataFrame(receb),
        "fato_expedicao": pd.DataFrame(exped),
    }
    tabelas["fato_paradas"]["id_equipamento"] = tabelas["fato_paradas"]["id_equipamento"].astype("Int64")
    tabelas["dim_calendario"]["data"] = tabelas["dim_calendario"]["data"].dt.date
    return tabelas


def salvar(tabelas):
    SAIDA.mkdir(exist_ok=True)
    for nome, df in tabelas.items():
        df.to_csv(SAIDA / f"{nome}.csv", index=False, encoding="utf-8")
    with pd.ExcelWriter(SAIDA.parent / "esmagadora_modelo.xlsx") as xw:
        for nome, df in tabelas.items():
            df.to_excel(xw, sheet_name=nome[:31], index=False)


if __name__ == "__main__":
    t = simular()
    salvar(t)
    for nome, df in t.items():
        print(f"{nome:35s} {len(df):>7,d} linhas")
