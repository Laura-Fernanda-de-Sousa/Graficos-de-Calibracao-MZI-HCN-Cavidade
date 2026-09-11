#Código único para reproduzir as figuras do relatório de Laura.
#Os dados da cavidade foram cedidos por Gustavo Nunes.
#O CSV de Laura é usado somente para ilustrar o MZI antes da calibração.


#Para outra medição, revise recorte, canais, detecção e linhas HCN.
#Encontrar 54 mínimos não comprova sozinho a identificação das linhas.
#É importante que os bancos de dados estejam salvos na mesma pasta que o código


#Instalar bibliotecas: python, -m pip install ,numpy ,pandas ,matplotlib ,scipy  e pyarrow
#Rodar: python graficos_calibracao_final.py



#Configuração e bibliotecas

MOSTRAR_JANELAS = True
FAZER_EXPERIMENTO = True
FAZER_MODELOS = True
FAZER_RLC = True  #Desative se não tiver os arquivos do circuito

import matplotlib

# O backend deve ser escolhido antes de importar pyplot.
# Com janelas ativadas, utiliza o backend padrão do computador.
if not MOSTRAR_JANELAS:
    matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from matplotlib.widgets import Button, SpanSelector


BASE = Path(__file__).resolve().parent



    
#Procurar primeiro ao lado do código e depois na pasta Downloads.

ARQUIVO = BASE / "DADOS GUSTA .parquet"
if not ARQUIVO.is_file():
    ARQUIVO = Path.home() / "Downloads" / "DADOS GUSTA .parquet"
ARQUIVO_LAURA = BASE / "dados_mzi.csv"
SAIDA = BASE / "figuras_codigo_atualizado"

LARGURA_FIGURA = 6.53  # polegadas
ALTURA_FIGURA = 3.8

AZUL = "#2177b3"
LARANJA = "#f48130"
VERDE = "#2ea948"

# Preencha com "V" somente se confirmar a unidade dos canais.
UNIDADE = ""

# Recorte ajustado para DADOS GUSTA .parquet.
# Não é um recorte universal para qualquer aquisição.
INICIO = 605000
FIM = 1832000

# Recorte do MZI de Laura, antes da calibração.
INICIO_LAURA = 254175
FIM_LAURA = 254810

#Fonte: Gilbert, Swann e Wang, NIST SP 260-137 (2005), Tabela 3.
#https://www.nist.gov/system/files/documents/srm/SP260-137.pdf
#Referências HCN: R26 até R0, seguidas de P1 até P27.
LAMBDA_NM = np.array([
    1527.63342, 1528.05474, 1528.48574, 1528.92643,
    1529.37681, 1529.83688, 1530.30666, 1530.78615,
    1531.27537, 1531.77430, 1532.28298, 1532.80139,
    1533.32954, 1533.86745, 1534.41514, 1534.97258,
    1535.53981, 1536.11683, 1536.70364, 1537.30029,
    1537.90675, 1538.52305, 1539.14921, 1539.78523,
    1540.43120, 1541.08703, 1541.75280,
    1543.11423, 1543.80967, 1544.51503, 1545.23033,
    1545.95549, 1546.69055, 1547.43558, 1548.19057,
    1548.95555, 1549.73051, 1550.51546, 1551.31045,
    1552.11546, 1552.93051, 1553.75562, 1554.59079,
    1555.43605, 1556.29141, 1557.15686, 1558.03240,
    1558.91808, 1559.81389, 1560.71983, 1561.63593,
    1562.56218, 1563.49859, 1564.44519
])

REGIMES = [
    (1, 0.2, "Subacoplado"),
    (1, 1, "Crítico"),
    (1, 5, "Superacoplado")
]

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 12,
    "axes.titlesize": 12,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": None,
    "pdf.fonttype": 42
})

# Mantém os botões ativos enquanto as janelas estiverem abertas.
BOTOES = []






#Formatação e exportação em pdf


def preparar(ax, titulo, xlabel, ylabel):
    ax.set(
        title=titulo,
        xlabel=xlabel,
        ylabel=ylabel
    )
    ax.grid(
        axis="y",
        color="#e6e6e6",
        linewidth=0.6
    )
    ax.margins(x=0.01)


def finalizar(fig, nome):
    """Salva o PDF e adiciona um botão para exportar o zoom."""

    SAIDA.mkdir(parents=True, exist_ok=True)

    # Garante a largura física do arquivo exportado.
    fig.set_size_inches(
        LARGURA_FIGURA,
        fig.get_figheight(),
        forward=True
    )

    # Menos divisões nos painéis estreitos.
    for ax in fig.axes:
        grade = ax.get_subplotspec().get_gridspec()
        if grade.ncols == 3:
            ax.locator_params(axis="x", nbins=3)
            ax.locator_params(axis="y", nbins=4)

    
    # Uma legenda comum, abaixo dos eixos, com a mesma posição em cada PDF.
    itens = {}
    for ax in fig.axes:
        handles, labels = ax.get_legend_handles_labels()
        for handle, label in zip(handles, labels):
            itens.setdefault(label, handle)
        legenda = ax.get_legend()
        if legenda is not None:
            legenda.remove()
    if itens:
        fig.legend(list(itens.values()), list(itens.keys()),
                   loc="lower center", bbox_to_anchor=(0.5, 0.085),
                   ncol=min(4, len(itens)), fontsize=10,
                   frameon=False, columnspacing=1.0, handlelength=1.5)

    fig.tight_layout(
        rect=(0, 0.24 if itens else 0.12, 1, 1),
        pad=0.8,
        w_pad=1.0
    )

    # Não usar bbox_inches="tight":
    # essa opção pode alterar a largura física do PDF.
    fig.savefig(
        SAIDA / f"{nome}.pdf",
        format="pdf",
        bbox_inches=None
    )

    if not MOSTRAR_JANELAS:
        plt.close(fig)
        return

    tamanho_pdf = tuple(fig.get_size_inches())

    controles = []
    if nome == "01_cavidade":
        ax_cavidade = fig.axes[0]
        limites_originais = (ax_cavidade.get_xlim(), ax_cavidade.get_ylim())
        x_total = np.asarray(ax_cavidade.lines[0].get_xdata())
        y_total = np.asarray(ax_cavidade.lines[0].get_ydata())

        def selecionar_ressonancia(x1, x2):
            esquerda, direita = sorted((x1, x2))
            if direita <= esquerda:
                return
            dentro = (x_total >= esquerda) & (x_total <= direita)
            if np.count_nonzero(dentro) < 2:
                return
            y = y_total[dentro]
            margem = max(float(np.ptp(y)) * 0.10, 1e-6)
            ax_cavidade.set_xlim(esquerda, direita)
            ax_cavidade.set_ylim(float(y.min()) - margem, float(y.max()) + margem)
            fig.canvas.draw_idle()
            print(f"Zoom aplicado: {esquerda:.9f} a {direita:.9f} THz")

        seletor = SpanSelector(
            ax_cavidade, selecionar_ressonancia, "horizontal",
            useblit=False, button=1, interactive=False,
            props={"facecolor": AZUL, "alpha": 0.2}
        )
        area_restaurar = fig.add_axes([0.04, 0.02, 0.30, 0.055])
        restaurar = Button(area_restaurar, "Visão geral")
        restaurar.label.set_fontsize(10)
        def restaurar_visao(event):
            ax_cavidade.set_xlim(limites_originais[0])
            ax_cavidade.set_ylim(limites_originais[1])
            fig.canvas.draw_idle()
        restaurar.on_clicked(restaurar_visao)
        controles.append(area_restaurar)
        BOTOES.extend([seletor, restaurar])
        print("Cavidade: arraste da esquerda para a direita sobre a ressonância, sem ativar a lupa.")

    area_botao = fig.add_axes([0.50, 0.02, 0.45, 0.055])
    controles.append(area_botao)
    botao = Button(
        area_botao,
        "Salvar zoom em PDF",
        color="#edf1f7"
    )
    botao.label.set_fontsize(10)

    def salvar_zoom(event):
        horario = datetime.now().strftime("%H%M%S_%f")
        tamanho_janela = tuple(fig.get_size_inches())

        for controle in controles:
            controle.set_visible(False)

        try:
            # Mesmo que a janela seja ampliada, o PDF mantém
            # a largura original e os limites escolhidos no zoom.
            fig.set_size_inches(*tamanho_pdf, forward=False)

            destino = SAIDA / f"{nome}_zoom_{horario}.pdf"

            fig.savefig(
                destino,
                format="pdf",
                bbox_inches=None
            )

            print(f"Enquadramento salvo: {destino}")

        finally:
            fig.set_size_inches(*tamanho_janela, forward=False)
            for controle in controles:
                controle.set_visible(True)
            fig.canvas.draw_idle()

    botao.on_clicked(salvar_zoom)
    BOTOES.append(botao)




# Mzi de laura antes da calibração

def ler_mzi_laura():
    dados = pd.read_csv(ARQUIVO_LAURA)

    if "MZI" not in dados.columns:
        raise ValueError("O CSV precisa conter a coluna MZI.")

    if len(dados) < FIM_LAURA:
        raise ValueError("O CSV não contém o recorte solicitado.")

    sinal = dados["MZI"].to_numpy()[INICIO_LAURA:FIM_LAURA]

    if not np.isfinite(sinal).all():
        raise ValueError("Há valores inválidos no MZI de Laura.")

    amostras = np.arange(INICIO_LAURA, FIM_LAURA)
    maximos, _ = find_peaks(sinal, prominence=0.05)
    minimos, _ = find_peaks(-sinal, prominence=0.05)

    return amostras, sinal, maximos, minimos


def desenhar_mzi_laura(ax, dados_laura, tamanho=12):
    amostras, sinal, maximos, minimos = dados_laura

    ax.plot(
        amostras, sinal,
        color=AZUL,
        linewidth=0.9,
        label="MZI original"
    )
    ax.scatter(
        amostras[maximos], sinal[maximos],
        color=VERDE,
        s=tamanho,
        zorder=3,
        label="Máximos"
    )
    ax.scatter(
        amostras[minimos], sinal[minimos],
        color=LARANJA,
        s=tamanho,
        zorder=3,
        label="Mínimos"
    )
    ax.ticklabel_format(
        axis="x",
        style="plain",
        useOffset=False
    )


def mzi_laura(dados_laura):
    fig, ax = plt.subplots(
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA)
    )

    desenhar_mzi_laura(ax, dados_laura, tamanho=20)

    preparar(
        ax,
        "MZI antes da calibração — Laura",
        "Índice da amostra",
        "Sinal adquirido"
    )
    ax.set_xlim(INICIO_LAURA, FIM_LAURA)
    ax.legend(loc="upper right")

    finalizar(fig, "00a_mzi_laura")





#Modelo: energia e transmitância sobrepostas


def acoplamento_sobreposto():
    delta = np.linspace(-8, 8, 3001)

    fig, axes = plt.subplots(
        1, 3,
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA),
        sharex=True,
        sharey=True
    )

    for ax, (ki, ke, nome) in zip(axes, REGIMES):
        denominador = ((ki + ke) / 2)**2 + delta**2

        transmitancia = (
            ((ki - ke) / 2)**2 + delta**2
        ) / denominador

        energia = ke / denominador
        energia_normalizada = energia / energia.max()

        ax.plot(
            delta / (2 * np.pi), transmitancia,
            color=AZUL,
            linewidth=1.8,
            label="Transmitância"
        )
        ax.plot(
            delta / (2 * np.pi), energia_normalizada,
            color=LARANJA,
            linewidth=1.8,
            label=r"$|a|^2/|a|_{\max}^2$"
        )

        preparar(
            ax,
            nome,
            r"$\Delta/(2\pi\kappa_0)$",
            ""
        )
        ax.set_ylim(-0.03, 1.08)

    axes[0].set_ylabel("Valor adimensional")
    axes[0].legend()

    finalizar(fig, "00b_energia_transmitancia_sobrepostas")





#Calibração e gráficos experimentais

def experimento(dados_laura):
    dados = pd.read_parquet(ARQUIVO)

    if not {"trans", "mzi", "hcn"}.issubset(dados.columns):
        raise ValueError(
            "O Parquet precisa das colunas trans, mzi e hcn."
        )

    if not (0 <= INICIO < FIM <= len(dados)):
        raise ValueError(
            "INICIO e FIM precisam delimitar um recorte válido. "
            "O padrão foi escolhido para a aquisição de Gustavo."
        )

    recorte = dados.iloc[INICIO:FIM]

    trans = recorte["trans"].to_numpy()
    mzi = recorte["mzi"].to_numpy()
    hcn = recorte["hcn"].to_numpy()

    if not all(
        np.isfinite(sinal).all()
        for sinal in (trans, mzi, hcn)
    ):
        raise ValueError(
            "Há valores ausentes ou infinitos no recorte."
        )

    
    # Detectar linhas de absorção do HCN.
    hcn_filtrado = gaussian_filter1d(hcn, sigma=10)

    indices_hcn, _ = find_peaks(
        -hcn_filtrado,
        prominence=0.12,
        distance=3000
    )

    if len(indices_hcn) != len(LAMBDA_NM):
        raise ValueError(
            f"Foram encontrados {len(indices_hcn)} vales; "
            "são esperadas 54 linhas. "
            "Revise o recorte e a identificação do HCN."
        )
        

    # Detectar extremos do MZI da mesma aquisição.
    mzi_filtrado = gaussian_filter1d(mzi, sigma=2)

    picos, _ = find_peaks(
        mzi_filtrado,
        prominence=0.15
    )
    vales, _ = find_peaks(
        -mzi_filtrado,
        prominence=0.15
    )

    extremos = np.concatenate((picos, vales))
    tipos = np.concatenate((
        np.ones(len(picos)),
        -np.ones(len(vales))
    ))

    ordem = np.argsort(extremos)
    extremos = extremos[ordem]
    tipos = tipos[ordem]

    if len(extremos) < 3 or np.any(np.diff(tipos) == 0):
        raise ValueError(
            "Os extremos detectados do MZI não alternam. "
            "Revise a detecção."
        )

    if (
        indices_hcn[0] < extremos[0]
        or indices_hcn[-1] > extremos[-1]
    ):
        raise ValueError(
            "As referências HCN precisam estar dentro "
            "dos extremos detectados do MZI."
        )

    
    # Um máximo seguido de um mínimo representa meio ciclo.
    ciclos = np.arange(len(extremos)) / 2

    ciclos_hcn = np.interp(
        indices_hcn,
        extremos,
        ciclos
    )

    frequencias_referencia = (
        299792458 / (LAMBDA_NM * 1e-9)
    )

    fsrs = np.abs(
        np.diff(frequencias_referencia)
        / np.diff(ciclos_hcn)
    )

    if np.ptp(fsrs) / np.median(fsrs) > 0.01:
        raise ValueError(
            "Espaçamentos inconsistentes: "
            "revise a identificação das linhas HCN."
        )

    
    # Calibrar apenas entre a primeira e a última referência.
    indices = np.arange(
        indices_hcn[0],
        indices_hcn[-1] + 1
    )

    coordenada_mzi = np.interp(
        indices,
        extremos,
        ciclos
    )

    frequencia = np.interp(
        coordenada_mzi,
        ciclos_hcn,
        frequencias_referencia
    )

    
    # Validação interna: excluir uma referência por vez.
    erros = np.array([
        np.interp(
            ciclos_hcn[k],
            ciclos_hcn[[k - 1, k + 1]],
            frequencias_referencia[[k - 1, k + 1]]
        ) - frequencias_referencia[k]
        for k in range(1, len(indices_hcn) - 1)
    ])

    print(
        f"FSR mediano do MZI: "
        f"{np.median(fsrs) / 1e6:.6f} MHz"
    )
    print(
        f"Validação interna RMS: "
        f"{np.sqrt(np.mean(erros**2)) / 1e6:.6f} MHz"
    )
    print(
        "O erro de validação não representa "
        "a incerteza total da medição."
    )

    ylabel = (
        f"Sinal ({UNIDADE})"
        if UNIDADE else "Sinal adquirido"
    )


    #Gráficos:

    
    # 1 — Transmissão da cavidade.
    fig, ax = plt.subplots(
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA)
    )
    ax.plot(
        frequencia / 1e12,
        trans[indices],
        label="Transmissão da cavidade",
        color=VERDE,
        linewidth=0.8
    )
    preparar(
        ax,
        "Transmissão da cavidade — Gustavo",
        "Frequência óptica (THz)",
        ylabel
    )
    finalizar(fig, "01_cavidade")


    
    # 2 — MZI de Laura e HCN de Gustavo lado a lado.
    # São aquisições diferentes, identificadas nos títulos.
    fig, (ax_mzi, ax_hcn) = plt.subplots(
        1, 2,
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA)
    )

    desenhar_mzi_laura(ax_mzi, dados_laura, tamanho=4)

    preparar(
        ax_mzi,
        "(a) MZI antes da calibração\nLaura",
        "Índice da amostra",
        "Sinal adquirido"
    )
    ax_mzi.set_xlim(254200, 254650)
    ax_mzi.locator_params(axis="x", nbins=3)
    ax_mzi.set_title(
        "(a) MZI antes da calibração\nLaura",
        pad=6
    )
    ax_mzi.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=2
    )

    ax_hcn.plot(
        frequencia / 1e12,
        hcn[indices],
        color=LARANJA,
        linewidth=0.8,
        label="Espectro HCN"
    )
    preparar(
        ax_hcn,
        "(b) HCN calibrado\nGustavo",
        "Frequência óptica (THz)",
        ""
    )
    ax_hcn.ticklabel_format(
        axis="x",
        style="plain",
        useOffset=False
    )
    ax_hcn.legend(loc="lower left")

    finalizar(fig, "02_mzi_e_hcn_lado_a_lado")



    
    # 3 — HCN e MZI da mesma aquisição, perto da linha P1.
    frequencia_central = frequencias_referencia[27]
    deslocamento = (frequencia - frequencia_central) / 1e9

    fig, axes = plt.subplots(
        2, 1,
        figsize=(LARGURA_FIGURA, 5.8),
        sharex=True
    )

    axes[0].plot(
        deslocamento,
        hcn[indices],
        label="HCN",
        color=LARANJA,
        linewidth=1
    )
    axes[1].plot(
        deslocamento,
        mzi[indices],
        label="MZI",
        color=AZUL,
        linewidth=1
    )

    preparar(
        axes[0],
        "HCN — linha P1",
        "",
        ylabel
    )
    preparar(
        axes[1],
        "Interferômetro Mach–Zehnder",
        "Deslocamento de frequência (GHz)\n"
        f"referência {frequencia_central / 1e12:.6f} THz",
        ylabel
    )

    axes[1].set_xlim(-0.7, 0.7)
    perto = np.abs(deslocamento) <= 0.7

    for ax, sinal in zip(
        axes,
        (hcn[indices], mzi[indices])
    ):
        y = sinal[perto]
        margem = max(np.ptp(y) * 0.12, 1e-6)
        ax.set_ylim(y.min() - margem, y.max() + margem)

    finalizar(fig, "03_hcn_mzi_zoom")



    
    # 4 — Erro da validação interna.
    fig, ax = plt.subplots(
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA)
    )
    ax.axhline(0, color="gray", linewidth=0.7)
    ax.plot(
        frequencias_referencia[1:-1] / 1e12,
        erros / 1e6,
        ".-",
        color=AZUL
    )
    preparar(
        ax,
        "Validação: uma linha HCN excluída por vez",
        "Frequência de referência (THz)",
        "Erro (MHz)"
    )
    finalizar(fig, "04_validacao")





    
    #Mostrar a curva de calibração sem confundir índice com tempo.
    fig, ax = plt.subplots(figsize=(LARGURA_FIGURA, ALTURA_FIGURA))
    ax.plot(indices + INICIO, frequencia / 1e12, color=AZUL,
            linewidth=1, label="Calibração HCN/MZI")
    ax.scatter(indices_hcn + INICIO, frequencias_referencia / 1e12,
               color=LARANJA, s=10, label="Referências HCN", zorder=3)
    preparar(ax, "Curva de calibração", "Índice da amostra",
             "Frequência óptica (THz)")
    finalizar(fig, "10_curva_calibracao")




    
    #Salvar os resultados para conferir a identificação das referências.
    nomes_linhas = [f"R{k}" for k in range(26, -1, -1)]
    nomes_linhas += [f"P{k}" for k in range(1, 28)]
    pd.DataFrame({
        "linha_associada": nomes_linhas,
        "indice_amostra": indices_hcn + INICIO,
        "comprimento_onda_vacuo_nm": LAMBDA_NM,
        "frequencia_THz": frequencias_referencia / 1e12,
        "ciclos_MZI": ciclos_hcn,
    }).to_csv(SAIDA / "referencias_hcn.csv", index=False)
    (SAIDA / "resultados.txt").write_text(
        f"Dados da cavidade: {ARQUIVO.name}\n"
        f"Recorte: {INICIO}:{FIM}\n"
        f"FSR mediano: {np.median(fsrs)/1e6:.6f} MHz\n"
        f"RMS interno: {np.sqrt(np.mean(erros**2))/1e6:.6f} MHz\n"
        "O RMS interno não é a incerteza total da calibração.\n"
        "A associação R26...R0, P1...P27 é específica desta aquisição.\n",
        encoding="utf-8"
    )







#Figuras teóricas

def modelos():
    #5 - omega_0 é apenas a referência temporal desta ilustração.
   
    #Não representa uma frequência óptica medida; kappa/omega_0 = 0 ou 1.
    #A amplitude inicial está normalizada: |a(0)|² = 1.
    
    tempo = np.linspace(0, 6, 600)

    fig, axes = plt.subplots(
        1, 2,
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA)
    )

    for ax, taxa, titulo in zip(
        axes,
        (0, 1),
        ("Sem perdas", "Com perdas")
    ):
        ax.plot(
            tempo,
            np.exp(-taxa * tempo),
            color=AZUL,
            linewidth=1.8
        )
        preparar(
            ax,
            titulo,
            r"$\omega_0 t$",
            r"$|a|^2$"
        )
        ax.set_ylim(0, 1.1)

    finalizar(fig, "05_decaimento")



    

    # 6 — Perfis Lorentziano e Gaussiano, com área unitária.
    x = np.linspace(-5, 5, 2000)
    lorentziana = 1 / (np.pi * (1 + x**2))
    gaussiana = np.exp(-x**2) / np.sqrt(np.pi)

    fig, ax = plt.subplots(
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA)
    )
    ax.plot(
        x, lorentziana,
        color=AZUL,
        linewidth=1.8,
        label="Lorentziana"
    )
    ax.plot(
        x, gaussiana,
        color=LARANJA,
        linewidth=1.8,
        label="Gaussiana"
    )
    preparar(
        ax,
        "Comparação de perfis",
        "Coordenada adimensional",
        "Densidade adimensional"
    )
    ax.legend()
    finalizar(fig, "06_lorentziana_gaussiana")



    
    # 7 — Energia e transmitância em figuras separadas.
    delta = np.linspace(-8, 8, 3000)

    fig_energia, eixos_energia = plt.subplots(
        1, 3,
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA),
        sharex=True,
        sharey=True
    )
    fig_trans, eixos_trans = plt.subplots(
        1, 3,
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA),
        sharex=True,
        sharey=True
    )

    for j, (ki, ke, nome) in enumerate(REGIMES):
        denominador = ((ki + ke) / 2)**2 + delta**2

        
        # Energia escalada por Pin/kappa_0.
        energia = ke / denominador

        
        # Transmitância do modelo de porta passante.
        transmitancia = (
            ((ki - ke) / 2)**2 + delta**2
        ) / denominador

        eixos_energia[j].plot(
            delta / (2 * np.pi), energia,
            color=AZUL,
            linewidth=1.6
        )
        eixos_trans[j].plot(
            delta / (2 * np.pi), transmitancia,
            color=LARANJA,
            linewidth=1.6
        )

        titulo = (
            nome
            + f"\nκi/κ0 = {ki:g}"
            + f"\nκe/κ0 = {ke:g}"
        )

        for ax in (eixos_energia[j], eixos_trans[j]):
            preparar(
                ax,
                titulo,
                r"$\Delta/(2\pi\kappa_0)$",
                ""
            )
            ax.set_ylim(0, 1.05)

    eixos_energia[0].set_ylabel(
        r"$|a|^2/(P_{\mathrm{in}}/\kappa_0)$"
    )
    eixos_trans[0].set_ylabel(
        r"Transmitância $|\alpha_{out}/\alpha_{in}|^2$"
    )

    finalizar(fig_energia, "07a_energia_acoplamento")
    finalizar(fig_trans, "07b_transmitancia_acoplamento")





    
    # 8 — MZI ideal em três diferenças de fase.
    z = np.linspace(-2, 2, 1200)

    fig, axes = plt.subplots(
        1, 3,
        figsize=(LARGURA_FIGURA, ALTURA_FIGURA),
        sharex=True,
        sharey=True
    )

    for ax, fase, nome in zip(
        axes,
        (0, np.pi / 2, np.pi),
        ("0", "π/2", "π")
    ):
        saida1 = (1 + np.cos(2 * np.pi * z + fase)) / 2
        saida2 = 1 - saida1

        ax.plot(
            z, saida1,
            color=AZUL,
            linewidth=1.5,
            label="Saída 1"
        )
        ax.plot(
            z, saida2,
            color=LARANJA,
            linewidth=1.2,
            linestyle="--",
            label="Saída 2"
        )

        preparar(
            ax,
            f"Fase adicional: {nome}",
            "Deslocamento de\nfrequência / FSR",
            ""
        )
        ax.set_ylim(-0.05, 1.05)

    axes[0].set_ylabel("Potência normalizada")
    axes[0].legend()

    finalizar(fig, "08_mzi_tres_quadros")






#Execução

def grafico_rlc():
    """Reproduz a tensão máxima da coluna POUT usada no notebook original."""
    import re
    pasta = BASE.parent / "dados indutor pequeno"
    pontos = []
    for arquivo in pasta.glob("*.csv"):
        nome = re.fullmatch(r"(\d+(?:\.\d+)?)(khz|mhz)", arquivo.stem.lower())
        if nome is None:
            continue
        frequencia_mhz = float(nome.group(1))
        if nome.group(2) == "khz":
            frequencia_mhz /= 1000
        tabela = pd.read_csv(arquivo, skiprows=[1])
        tensao = pd.to_numeric(tabela["POUT"], errors="raise").to_numpy()
        if len(tensao) == 0 or not np.isfinite(tensao).all():
            raise ValueError(f"Valores inválidos em {arquivo.name}")
        pontos.append((frequencia_mhz, float(tensao.max())))
    if not pontos:
        print(f"RLC não gerado: não há arquivos em {pasta}")
        return
    pontos = np.array(sorted(pontos))
    fig, ax = plt.subplots(figsize=(LARGURA_FIGURA, ALTURA_FIGURA))
    ax.plot(pontos[:, 0], pontos[:, 1], "o-", color=AZUL,
            linewidth=1.0, markersize=4, label="Dados experimentais")
    preparar(ax, "Circuito RLC", "Frequência (MHz)", "Tensão máxima (V)")
    ax.set_xlim(0, 10.2)
    ax.set_ylim(3.25, 4.10)
    ax.set_xticks(np.arange(0, 11, 2))
    finalizar(fig, "09_rlc_tensao_frequencia")


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)




    
    # Conferir os arquivos antes de iniciar a análise.
    if FAZER_EXPERIMENTO:
        for caminho in (ARQUIVO_LAURA, ARQUIVO):
            if not caminho.is_file():
                raise FileNotFoundError(
                    f"Arquivo não encontrado: {caminho}"
                )

    if FAZER_MODELOS:
        acoplamento_sobreposto()
        modelos()

    if FAZER_EXPERIMENTO:
        if FAZER_RLC:
            grafico_rlc()
        dados_laura = ler_mzi_laura()
        mzi_laura(dados_laura)
        experimento(dados_laura)

    print(f"\nPDFs salvos em: {SAIDA}")

    if MOSTRAR_JANELAS:
        print(
            "Use a lupa para ampliar e "
            "'Salvar zoom em PDF' para exportar o recorte."
        )
        plt.show()
    else:
        plt.close("all")


if __name__ == "__main__":
    main()
