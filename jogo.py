# ============================================================
# ENCRUZILHADA SOMBRIA - Ludo gotico para 2 jogadores
# Fundo e musica carregados a partir da pasta deste arquivo.
# Requer: pip install pygame
# ============================================================

import os
import sys
import math
import random
import json
import pygame

pygame.init()
pygame.mixer.init()

TEMPO_JOGADA = 30

som_dado = pygame.mixer.Sound("som_dado.mp3")

PASTA_JOGO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_FUNDO = os.path.join(PASTA_JOGO, "fundo_gotico.png")
CAMINHO_MUSICA = os.path.join(PASTA_JOGO, "musica_terror.mp3")
ARQUIVO_SAVE = os.path.join(PASTA_JOGO, "salvamento_encruzilhada.json")
ARQUIVO_RANKING = os.path.join(PASTA_JOGO, "ludo_ranking.json")

LARGURA, ALTURA = 1320, 800
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Encruzilhada Sombria")
RELOGIO = pygame.time.Clock()

# Paleta gótica
PRETO = (5, 5, 12)
PAINEL = (10, 8, 18)
PEDRA = (34, 31, 42)
PEDRA_CLARA = (54, 46, 54)
OURO = (218, 164, 73)
OURO_CLARO = (255, 207, 119)
BRANCO = (244, 231, 220)
VERMELHO = (221, 28, 48)
ROXO = (174, 48, 215)
AZUL = (40, 112, 235)
AMARELO = (236, 166, 28)
VERDE = (28, 105, 70)

try:
    TITULO = pygame.font.SysFont("georgia", 27, bold=True)
    SUBTITULO = pygame.font.SysFont("georgia", 19, bold=True)
    FONTE = pygame.font.SysFont("georgia", 17)
    PEQUENA = pygame.font.SysFont("arial", 14)
    MINI = pygame.font.SysFont("arial", 12)
    DADO_FONTE = pygame.font.SysFont("georgia", 42, bold=True)
except pygame.error:
    TITULO = pygame.font.Font(None, 28)
    SUBTITULO = pygame.font.Font(None, 20)
    FONTE = pygame.font.Font(None, 18)
    PEQUENA = pygame.font.Font(None, 14)
    MINI = pygame.font.Font(None, 12)
    DADO_FONTE = pygame.font.Font(None, 42)

# Carrega o fundo usando o caminho absoluto deste arquivo.
fundo = None
if os.path.isfile(CAMINHO_FUNDO):
    try:
        imagem = pygame.image.load(CAMINHO_FUNDO).convert()
        fundo = pygame.transform.smoothscale(imagem, (LARGURA, ALTURA))
        print(f"Fundo carregado: {CAMINHO_FUNDO}")
    except (pygame.error, OSError) as erro:
        print(f"Nao foi possivel carregar o fundo: {erro}")
else:
    print(f"Fundo nao encontrado: {CAMINHO_FUNDO}")

musica_ok = False
if pygame.mixer.get_init() and os.path.isfile(CAMINHO_MUSICA):
    try:
        pygame.mixer.music.load(CAMINHO_MUSICA)
        pygame.mixer.music.set_volume(0.22)
        pygame.mixer.music.play(-1)
        musica_ok = True
        print(f"Musica iniciada: {CAMINHO_MUSICA}")
    except (pygame.error, OSError) as erro:
        print(f"Nao foi possivel tocar a musica: {erro}")
else:
    print("Musica nao encontrada ou mixer indisponivel:", CAMINHO_MUSICA)

# Tabuleiro: coordenadas (coluna, linha), casas 0 a 51.
TAMANHO = 36
ORIGEM_X = 25
ORIGEM_Y = 100
TRILHA = [
    (6,13),(6,12),(6,11),(6,10),(6,9),
    (5,8),(4,8),(3,8),(2,8),(1,8),(0,8),
    (0,7),(0,6),(1,6),(2,6),(3,6),(4,6),
    (5,6),(6,5),(6,4),(6,3),(6,2),(6,1),
    (6,0),(7,0),(8,0),(8,1),(8,2),(8,3),
    (8,4),(8,5),(9,6),(10,6),(11,6),(12,6),
    (13,6),(14,6),(14,7),(14,8),(13,8),
    (12,8),(11,8),(10,8),(9,8),(8,9),(8,10),
    (8,11),(8,12),(8,13),(8,14),(7,14),(6,14)
]
CORREDORES = [
    [(7,12),(7,11),(7,10),(7,9),(7,8)],
    [(7,2),(7,3),(7,4),(7,5),(7,6)]
]
SEGUROS = {0, 8, 13, 21, 26, 34, 39, 47}
CASAS_CARTA = {5, 11, 18, 24, 31, 37, 44, 50}

jogadores = [
    {"nome": "Obsidiana", "cor": VERMELHO, "inicio": 0,
     "pos": [0, 0, 0, 0], "escudos": 0, "vitorias": 0, "perde_turno": False},
    {"nome": "Sangue Seco", "cor": ROXO, "inicio": 26,
     "pos": [0, 0, 0, 0], "escudos": 0, "vitorias": 0, "perde_turno": False},
]
turno = 0
dado = 0
escolhendo = False
vencedor = None
mensagem = "Lance o dado para comecar a partida."
tela_inicio = True
nomes_digitados = ["", ""]
campo_nome_ativo = 0
BOTAO_ENTRAR = pygame.Rect(0, 0, 260, 48)
CAMPO_NOME1 = pygame.Rect(0, 0, 360, 48)
CAMPO_NOME2 = pygame.Rect(0, 0, 360, 48)
mostrar_manual = False

# Areas de interface
PAINEL_X = 690
BOTAO_DADO = pygame.Rect(PAINEL_X + 24, 205, 260, 48)
BOTOES_PECA = [pygame.Rect(PAINEL_X + 20 + i * 133, 355, 119, 42) for i in range(4)]
BOTAO_SALVAR = pygame.Rect(PAINEL_X + 18, 700, 145, 38)
BOTAO_CARREGAR = pygame.Rect(PAINEL_X + 174, 700, 145, 38)
BOTAO_REINICIAR = pygame.Rect(PAINEL_X + 330, 700, 155, 38)
BOTAO_MUSICA = pygame.Rect(PAINEL_X + 493, 700, 130, 38)
BOTAO_MANUAL = pygame.Rect(PAINEL_X + 440, 748, 150, 30)


def texto(conteudo, fonte, cor, x, y, centro=False):
    img = fonte.render(str(conteudo), True, cor)
    rect = img.get_rect()
    if centro:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    TELA.blit(img, rect)


def centro_casa(coluna, linha):
    return (ORIGEM_X + coluna * TAMANHO + TAMANHO // 2,
            ORIGEM_Y + linha * TAMANHO + TAMANHO // 2)


def borda_gotica(rect, cor=OURO, largura=2):
    pygame.draw.rect(TELA, (9, 7, 14), rect, border_radius=5)
    pygame.draw.rect(TELA, cor, rect, largura, border_radius=5)
    # Pequenos ornamentos nos cantos
    for x, y, sx, sy in [(rect.left+5, rect.top+5, 1, 1),
                         (rect.right-5, rect.top+5, -1, 1),
                         (rect.left+5, rect.bottom-5, 1, -1),
                         (rect.right-5, rect.bottom-5, -1, -1)]:
        pygame.draw.line(TELA, cor, (x, y), (x + 7*sx, y), 1)
        pygame.draw.line(TELA, cor, (x, y), (x, y + 7*sy), 1)


def desenhar_casa(coluna, linha, cor, alpha=220):
    x = ORIGEM_X + coluna * TAMANHO
    y = ORIGEM_Y + linha * TAMANHO
    camada = pygame.Surface((TAMANHO, TAMANHO), pygame.SRCALPHA)
    camada.fill((*cor, alpha))
    TELA.blit(camada, (x, y))
    pygame.draw.rect(TELA, OURO, (x, y, TAMANHO, TAMANHO), 1)
    pygame.draw.line(TELA, (115, 83, 53), (x+3, y+3), (x+TAMANHO-4, y+3), 1)


def desenhar_base(coluna, linha, indice_jogador):
    jogador = jogadores[indice_jogador]
    x = ORIGEM_X + coluna * TAMANHO
    y = ORIGEM_Y + linha * TAMANHO
    rect = pygame.Rect(x, y, TAMANHO*6, TAMANHO*6)
    camada = pygame.Surface(rect.size, pygame.SRCALPHA)
    camada.fill((*jogador["cor"], 105))
    TELA.blit(camada, rect.topleft)
    pygame.draw.rect(TELA, OURO, rect, 3)
    pygame.draw.rect(TELA, jogador["cor"], rect.inflate(-10, -10), 1)
    texto(jogador["nome"].upper(), MINI, BRANCO, rect.centerx, y+15, True)
    pontos = [(coluna+2, linha+2), (coluna+4, linha+2),
              (coluna+2, linha+4), (coluna+4, linha+4)]
    for c, l in pontos:
        px, py = centro_casa(c, l)
        pygame.draw.circle(TELA, (7, 6, 12), (px+2, py+3), 15)
        pygame.draw.circle(TELA, OURO, (px, py), 14, 2)


def desenhar_tabuleiro():
    # Tabuleiro translúcido para deixar o cenário gótico aparecer.
    desenhar_base(0, 0, 0)
    desenhar_base(9, 9, 1)

    # Quadrantes vazios com transparência
    for col, lin in [(9,0), (0,9)]:
        rect = pygame.Rect(ORIGEM_X + col*TAMANHO, ORIGEM_Y + lin*TAMANHO,
                           TAMANHO*6, TAMANHO*6)
        camada = pygame.Surface(rect.size, pygame.SRCALPHA)
        camada.fill((20, 14, 26, 145))
        TELA.blit(camada, rect.topleft)
        pygame.draw.rect(TELA, OURO, rect, 2)

    # Braços da cruz
    for linha in range(6):
        for coluna in range(6, 9):
            desenhar_casa(coluna, linha, PEDRA, 205)
    for linha in range(9, 15):
        for coluna in range(6, 9):
            desenhar_casa(coluna, linha, PEDRA, 205)
    for linha in range(6, 9):
        for coluna in list(range(6)) + list(range(9, 15)):
            desenhar_casa(coluna, linha, PEDRA, 205)

    # Trilha
    for i, (coluna, linha) in enumerate(TRILHA):
        cor = PEDRA_CLARA
        if i in SEGUROS:
            cor = VERDE
        elif i in CASAS_CARTA:
            cor = (83, 31, 83)
        desenhar_casa(coluna, linha, cor, 225)
        x, y = centro_casa(coluna, linha)
        if i in SEGUROS:
            texto("✦", FONTE, OURO_CLARO, x, y, True)
        elif i in CASAS_CARTA:
            pygame.draw.circle(TELA, OURO, (x, y), 10, 2)
            texto("?", PEQUENA, BRANCO, x, y-1, True)

    # Corredores finais coloridos
    for coluna, linha in CORREDORES[0]:
        desenhar_casa(coluna, linha, (130, 17, 35), 230)
    for coluna, linha in CORREDORES[1]:
        desenhar_casa(coluna, linha, (87, 24, 112), 230)

    # Centro da encruzilhada
    x = ORIGEM_X + 6*TAMANHO
    y = ORIGEM_Y + 6*TAMANHO
    rect = pygame.Rect(x, y, TAMANHO*3, TAMANHO*3)
    camada = pygame.Surface(rect.size, pygame.SRCALPHA)
    camada.fill((8, 7, 15, 235))
    TELA.blit(camada, rect.topleft)
    pygame.draw.rect(TELA, OURO, rect, 3)
    # Losango e caveira estilizada
    cx, cy = rect.center
    pygame.draw.polygon(TELA, (23, 16, 24), [(cx, y+12), (x+TAMANHO*3-12, cy),
                                             (cx, y+TAMANHO*3-12), (x+12, cy)])
    pygame.draw.polygon(TELA, OURO, [(cx, y+12), (x+TAMANHO*3-12, cy),
                                     (cx, y+TAMANHO*3-12), (x+12, cy)], 2)
    texto("☠", DADO_FONTE, OURO_CLARO, cx, cy, True)


def posicao_pixel(jogador_idx, peca_idx):
    jogador = jogadores[jogador_idx]
    pos = jogador["pos"][peca_idx]
    if pos == 0:
        col_base = 0 if jogador_idx == 0 else 9
        lin_base = 0 if jogador_idx == 0 else 9
        pontos = [(col_base+2, lin_base+2), (col_base+4, lin_base+2),
                  (col_base+2, lin_base+4), (col_base+4, lin_base+4)]
        return centro_casa(*pontos[peca_idx])
    if pos == 58:
        finais = [(6,6), (8,6), (6,8), (8,8)]
        return centro_casa(*finais[peca_idx])
    if pos >= 53:
        return centro_casa(*CORREDORES[jogador_idx][pos-53])
    indice = (jogador["inicio"] + pos - 1) % 52
    return centro_casa(*TRILHA[indice])


def pecas_moveis():
    disponiveis = []
    if dado == 0:
        return disponiveis
    for i, pos in enumerate(jogadores[turno]["pos"]):
        if pos == 0 and dado == 6:
            disponiveis.append(i)
        elif 1 <= pos < 58 and pos + dado <= 58:
            disponiveis.append(i)
    return disponiveis


def desenhar_pecas():
    for j, jogador in enumerate(jogadores):
        for p, pos in enumerate(jogador["pos"]):
            x, y = posicao_pixel(j, p)
            destaque = escolhendo and j == turno and p in pecas_moveis()
            raio = 14 if destaque else 11
            pygame.draw.circle(TELA, (0, 0, 0), (x+2, y+3), raio+3)
            pygame.draw.circle(TELA, jogador["cor"], (x, y), raio)
            pygame.draw.circle(TELA, OURO_CLARO if destaque else BRANCO, (x, y), raio, 2)
            pygame.draw.circle(TELA, (255, 255, 255), (x-3, y-4), 3)
            texto(str(p+1), MINI, BRANCO, x, y, True)


def desenhar_dado(rect, valor):
    pygame.draw.rect(TELA, (232, 220, 207), rect, border_radius=8)
    pygame.draw.rect(TELA, OURO, rect, 2, border_radius=8)
    pontos = {
        1: [(0,0)], 2: [(-1,-1),(1,1)], 3: [(-1,-1),(0,0),(1,1)],
        4: [(-1,-1),(1,-1),(-1,1),(1,1)],
        5: [(-1,-1),(1,-1),(0,0),(-1,1),(1,1)],
        6: [(-1,-1),(1,-1),(-1,0),(1,0),(-1,1),(1,1)]
    }
    if valor not in pontos:
        texto("—", DADO_FONTE, BRANCO, rect.centerx, rect.centery, True)
        return
    for dx, dy in pontos[valor]:
        pygame.draw.circle(TELA, (30, 20, 20),
                           (rect.centerx + dx*rect.width//4,
                            rect.centery + dy*rect.height//4), 5)


def botao(rect, nome, ativo=True, cor=None):
    base = cor or ((94, 19, 35) if ativo else (35, 31, 41))
    pygame.draw.rect(TELA, base, rect, border_radius=5)
    pygame.draw.rect(TELA, OURO if ativo else (105, 83, 54), rect, 2, border_radius=5)
    texto(nome, PEQUENA, BRANCO if ativo else (145, 135, 130), rect.centerx, rect.centery, True)


def desenhar_painel():
    # Painel escuro translúcido, sem esconder totalmente a arte.
    camada = pygame.Surface((LARGURA-PAINEL_X, ALTURA), pygame.SRCALPHA)
    camada.fill((8, 6, 15, 225))
    TELA.blit(camada, (PAINEL_X, 0))
    pygame.draw.line(TELA, OURO, (PAINEL_X, 0), (PAINEL_X, ALTURA), 3)

    texto("ENCRUZILHADA SOMBRIA", TITULO, OURO_CLARO, PAINEL_X+24, 22)
    texto("RANKING DAS ALMAS", SUBTITULO, OURO, PAINEL_X+25, 66)
    pygame.draw.line(TELA, (115, 76, 45), (PAINEL_X+24, 96), (LARGURA-24, 96), 1)

    for i, j in enumerate(jogadores):
        y = 108 + i*31
        pygame.draw.circle(TELA, j["cor"], (PAINEL_X+39, y+9), 8)
        pygame.draw.circle(TELA, OURO, (PAINEL_X+39, y+9), 9, 1)
        texto(f"{i+1}. {j['nome']}", FONTE, j["cor"], PAINEL_X+57, y)
        texto(f"Vitorias: {j['vitorias']}", PEQUENA, BRANCO, PAINEL_X+300, y+2)

    texto("DADO MISTICO", SUBTITULO, OURO, PAINEL_X+25, 181)
    desenhar_dado(pygame.Rect(PAINEL_X+480, 111, 68, 68), dado)
    botao(BOTAO_DADO, "LANCAR DADO  [ESPACO]", not escolhendo)

    jogador_atual = jogadores[turno]
    texto("TURNO", SUBTITULO, OURO, PAINEL_X+25, 270)
    texto(jogador_atual["nome"], FONTE, jogador_atual["cor"], PAINEL_X+25, 298)
    texto("Escolha uma peça para mover:", PEQUENA, BRANCO, PAINEL_X+25, 328)
    for i, rect in enumerate(BOTOES_PECA):
        botao(rect, f"PEÇA {i+1}", escolhendo and i in pecas_moveis())

    # Estado das peças
    y = 420
    for j in jogadores:
        texto(j["nome"], FONTE, j["cor"], PAINEL_X+25, y)
        estados = "   ".join(f"P{i+1}:{'Base' if p == 0 else 'Chegada' if p == 58 else p}"
                              for i, p in enumerate(j["pos"]))
        texto(estados, MINI, BRANCO, PAINEL_X+25, y+24)
        texto(f"Escudos: {j['escudos']}", MINI, OURO, PAINEL_X+25, y+43)
        y += 78

    # Mensagem do jogo
    msg_rect = pygame.Rect(PAINEL_X+24, 590, 600, 78)
    pygame.draw.rect(TELA, (5, 4, 10), msg_rect)
    borda_gotica(msg_rect, OURO, 1)
    palavras = mensagem.split()
    linhas, linha = [], ""
    for palavra in palavras:
        teste = (linha + " " + palavra).strip()
        if PEQUENA.size(teste)[0] > msg_rect.width-20:
            linhas.append(linha)
            linha = palavra
        else:
            linha = teste
    if linha:
        linhas.append(linha)
    for i, item in enumerate(linhas[:3]):
        texto(item, PEQUENA, BRANCO, msg_rect.x+10, msg_rect.y+10+i*19)

    botao(BOTAO_SALVAR, "SALVAR [S]")
    botao(BOTAO_CARREGAR, "CARREGAR [L]")
    botao(BOTAO_REINICIAR, "REINICIAR [R]")
    botao(BOTAO_MUSICA, "MUSICA: ON" if pygame.mixer.get_init() and pygame.mixer.music.get_busy() else "MUSICA: OFF")
    texto("✦ Casa segura     ? Carta amaldiçoada", MINI, OURO, PAINEL_X+25, 758)
    texto("MANUAL [H]", MINI, OURO_CLARO, BOTAO_MANUAL.x, BOTAO_MANUAL.y)


def desenhar_manual():
    """Mostra as instrucoes do jogo por cima da partida."""
    sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 205))
    TELA.blit(sombra, (0, 0))

    painel = pygame.Rect(170, 75, 980, 650)
    pygame.draw.rect(TELA, (10, 7, 17), painel, border_radius=10)
    pygame.draw.rect(TELA, OURO, painel, 3, border_radius=10)
    texto("MANUAL DE INSTRUCOES", TITULO, OURO_CLARO, painel.centerx, 105, True)
    texto("ENCRUZILHADA SOMBRIA - jogo de tabuleiro para 2 jogadores", PEQUENA, BRANCO, painel.centerx, 140, True)

    secoes = [
        ("1. OBJETIVO", [
            "Leve as 4 pecas do seu time da base ate a chegada no centro.",
            "Vence quem conseguir colocar todas as pecas na chegada primeiro."
        ]),
        ("2. COMO JOGAR", [
            "Clique em LANCAR DADO ou pressione ESPACO.",
            "Depois do resultado, escolha uma peca destacada ou use as teclas 1, 2, 3 ou 4.",
            "Para tirar uma peca da base, e necessario tirar 6.",
            "A peca precisa tirar o numero exato para chegar ao final.",
            "Ao tirar 6, o jogador joga novamente; nos outros resultados, passa a vez."
        ]),
        ("3. CASAS ESPECIAIS", [
            "Casa segura (✦): protege a peca contra capturas.",
            "Casa com ?: puxa uma carta amaldiçoada: pode avancar, voltar, ganhar escudo ou perder a vez.",
            "Captura: ao cair numa casa ocupada pelo adversario fora de uma casa segura, a peca dele volta a base.",
            "Escudo: protege contra uma captura e e consumido quando usado."
        ]),
        ("4. BOTOES E TECLAS", [
            "SALVAR [S]: salva a partida em arquivo JSON.",
            "CARREGAR [L]: abre a ultima partida salva.",
            "REINICIAR [R]: comeca uma nova partida com as pecas na base.",
            "MUSICA [M]: liga ou pausa a musica de terror.",
            "N: volta para a tela de nomes. ESC: fecha o jogo.",
            "H: abre ou fecha este manual."
        ]),
        ("5. NOMES DOS JOGADORES", [
            "Na tela inicial, digite os nomes. Use TAB para alternar os campos e ENTER para iniciar.",
            "O ranking de vitorias fica registrado em ludo_ranking.json."
        ])
    ]
    y = 158
    for titulo_secao, linhas in secoes:
        texto(titulo_secao, SUBTITULO, OURO, painel.x+28, y)
        y += 22
        for linha in linhas:
            texto("• " + linha, MINI, BRANCO, painel.x+38, y)
            y += 18
        y += 4

    texto("Pressione H ou ESC para voltar a partida", PEQUENA, OURO_CLARO, painel.centerx, 690, True)


def puxar_carta(jogador_idx):
    global mensagem
    jogador = jogadores[jogador_idx]
    carta = random.choice(["avanca", "volta", "perde_turno", "escudo"])
    if carta == "avanca":
        for i, pos in enumerate(jogador["pos"]):
            if 1 <= pos < 58:
                jogador["pos"][i] = min(58, pos+3)
        mensagem = "Carta amaldiçoada: avance 3 casas!"
    elif carta == "volta":
        for i, pos in enumerate(jogador["pos"]):
            if 1 <= pos < 58:
                jogador["pos"][i] = max(1, pos-3)
        mensagem = "Carta amaldiçoada: volte 3 casas!"
    elif carta == "escudo":
        jogador["escudos"] += 1
        mensagem = f"{jogador['nome']} recebeu um escudo!"
    else:
        jogador["perde_turno"] = True
        mensagem = "Maldicao: voce perde a proxima rodada!"


def verificar_captura(jogador_idx, peca_idx):
    global mensagem
    jogador = jogadores[jogador_idx]
    pos = jogador["pos"][peca_idx]
    if not 1 <= pos <= 52:
        return
    indice = (jogador["inicio"] + pos - 1) % 52
    if indice in SEGUROS:
        return
    adversario = jogadores[1-jogador_idx]
    for i, pos_adv in enumerate(adversario["pos"]):
        if not 1 <= pos_adv <= 52:
            continue
        indice_adv = (adversario["inicio"] + pos_adv - 1) % 52
        if indice == indice_adv:
            if adversario["escudos"] > 0:
                adversario["escudos"] -= 1
                mensagem = f"{adversario['nome']} usou um escudo!"
            else:
                adversario["pos"][i] = 0
                mensagem = f"Captura! Peca {i+1} voltou a base."
            return


def mover_peca(indice_peca):
    global turno, dado, escolhendo, vencedor, mensagem
    if not escolhendo or indice_peca not in pecas_moveis():
        mensagem = "Essa peca nao pode se mover com este dado."
        return
    jogador = jogadores[turno]
    pos = jogador["pos"][indice_peca]
    if pos == 0:
        jogador["pos"][indice_peca] = 1
    else:
        nova = pos + dado
        if nova > 58:
            mensagem = "Precisa tirar o numero exato para chegar."
            return
        jogador["pos"][indice_peca] = nova
        if nova < 53:
            indice = (jogador["inicio"] + nova - 1) % 52
            if indice in CASAS_CARTA:
                puxar_carta(turno)
        verificar_captura(turno, indice_peca)
    if all(p == 58 for p in jogador["pos"]):
        vencedor = jogador["nome"]
        jogador["vitorias"] += 1
        registrar_vitoria(jogador["nome"])
        mensagem = f"{vencedor} venceu a Encruzilhada Sombria!"
        escolhendo = False
        dado = 0
        return
    resultado = dado
    dado = 0
    escolhendo = False
    if resultado != 6:
        turno = 1-turno
    else:
        mensagem += " Tirou 6: jogue novamente."


def lancar_dado():
    global dado, escolhendo, turno, mensagem
    global tempo_inicio

    if vencedor or escolhendo:
        return

    jogador = jogadores[turno]

    if jogador.get("perde_turno", False):
        jogador["perde_turno"] = False
        mensagem = f"{jogador['nome']} perdeu a vez pela maldicao!"
        turno = 1 - turno
        return

    dado = random.randint(1, 6)

    if not pecas_moveis():
        mensagem = f"Saiu {dado}, mas nao ha movimento possivel."
        dado = 0
        turno = 1 - turno

    else:
        escolhendo = True

        # Começa a contar os 30 segundos
        tempo_inicio = pygame.time.get_ticks()

        mensagem = f"Saiu {dado}. Escolha uma peça."


def salvar():
    global mensagem
    try:
        estado = {"jogadores": jogadores, "turno": turno, "dado": dado, "escolhendo": escolhendo, "vencedor": vencedor, "mensagem": mensagem}
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
        mensagem = "Partida salva com sucesso!"
    except (OSError, TypeError) as erro:
        mensagem = f"Nao foi possivel salvar: {erro}"


def carregar():
    global turno, dado, escolhendo, vencedor, mensagem
    try:
        with open(ARQUIVO_SAVE, "r", encoding="utf-8") as f:
            estado = json.load(f)
        for i in range(2):
            salvo = estado["jogadores"][i]
            jogadores[i]["nome"] = str(salvo.get("nome", jogadores[i]["nome"]))[:24]
            jogadores[i]["pos"] = salvo.get("pos", [0,0,0,0])
            jogadores[i]["escudos"] = salvo.get("escudos", 0)
            jogadores[i]["vitorias"] = salvo.get("vitorias", 0)
            jogadores[i]["perde_turno"] = salvo.get("perde_turno", False)
        turno = int(estado.get("turno", 0)) % 2
        dado = int(estado.get("dado", 0))
        escolhendo = bool(estado.get("escolhendo", False))
        vencedor = estado.get("vencedor")
        mensagem = estado.get("mensagem", "Partida carregada!")
        global tela_inicio
        tela_inicio = False
    except (OSError, ValueError, KeyError, TypeError, IndexError) as erro:
        mensagem = f"Nao foi possivel carregar: {erro}"


def reiniciar():
    global turno, dado, escolhendo, vencedor, mensagem
    for jogador in jogadores:
        jogador["pos"] = [0,0,0,0]
        jogador["escudos"] = 0
        jogador["perde_turno"] = False
    turno, dado, escolhendo, vencedor = 0, 0, False, None
    mensagem = "Nova partida. Lance o dado!"


def alternar_musica():
    global mensagem
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            mensagem = "Audio indisponivel neste computador."
            return
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        mensagem = "Musica pausada."
    else:
        try:
            if pygame.mixer.music.get_pos() < 0:
                pygame.mixer.music.load(CAMINHO_MUSICA)
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(CAMINHO_MUSICA)
                pygame.mixer.music.set_volume(0.22)
                pygame.mixer.music.play(-1)
            mensagem = "Musica de terror ativada."
        except (pygame.error, OSError) as erro:
            mensagem = f"Erro na musica: {erro}"


def desenhar_fundo():
    if fundo is not None:
        TELA.blit(fundo, (0, 0))
        escurecer = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escurecer.fill((3, 2, 10, 95))
        TELA.blit(escurecer, (0, 0))
    else:
        TELA.fill(PRETO)
        # Cenario alternativo se a imagem estiver ausente.
        for i in range(28):
            x = (i*97) % LARGURA
            y = (i*53) % ALTURA
            pygame.draw.circle(TELA, (28, 18, 35), (x, y), 2)
        texto("FUNDO NAO ENCONTRADO: fundo_gotico.png", PEQUENA, VERMELHO, 20, 15)


def registrar_vitoria(nome):
    """Mantem um ranking persistente por nome em ludo_ranking.json."""
    try:
        try:
            with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if not isinstance(dados, dict):
                dados = {}
        except (OSError, ValueError):
            dados = {}
        dados[nome] = int(dados.get(nome, 0)) + 1
        with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except (OSError, TypeError, ValueError) as erro:
        print("Nao foi possivel atualizar o ranking:", erro)


def desenhar_tela_inicio():
    desenhar_fundo()
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    camada.fill((4, 2, 10, 190))
    TELA.blit(camada, (0, 0))
    centro = LARGURA // 2
    texto("ENCRUZILHADA SOMBRIA", TITULO, OURO_CLARO, centro, 150, True)
    texto("Digite o nome dos dois jogadores", SUBTITULO, BRANCO, centro, 205, True)
    CAMPO_NOME1.topleft = (centro-180, 260)
    CAMPO_NOME2.topleft = (centro-180, 340)
    BOTAO_ENTRAR.topleft = (centro-130, 430)
    texto("JOGADOR 1", PEQUENA, VERMELHO, CAMPO_NOME1.x, CAMPO_NOME1.y-23)
    texto("JOGADOR 2", PEQUENA, ROXO, CAMPO_NOME2.x, CAMPO_NOME2.y-23)
    for i, rect in enumerate((CAMPO_NOME1, CAMPO_NOME2)):
        pygame.draw.rect(TELA, (18, 12, 25), rect, border_radius=5)
        pygame.draw.rect(TELA, OURO_CLARO if campo_nome_ativo == i else OURO, rect, 2, border_radius=5)
        texto(nomes_digitados[i] or ("Obsidiana" if i == 0 else "Sangue Seco"), FONTE,
              BRANCO if nomes_digitados[i] else (130, 120, 120), rect.x+12, rect.y+13)
    botao(BOTAO_ENTRAR, "ENTRAR NA PARTIDA")
    texto("ENTER para confirmar  |  ESC para sair", PEQUENA, OURO, centro, 510, True)


rodando = True
while rodando:
    if tela_inicio:
        desenhar_tela_inicio()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_TAB:
                    campo_nome_ativo = 1 - campo_nome_ativo
                elif evento.key == pygame.K_RETURN:
                    for i, padrao in enumerate(("Obsidiana", "Sangue Seco")):
                        jogadores[i]["nome"] = (nomes_digitados[i].strip() or padrao)[:24]
                    if jogadores[0]["nome"].casefold() == jogadores[1]["nome"].casefold():
                        mensagem = "Escolha nomes diferentes para os jogadores."
                    else:
                        tela_inicio = False
                        mensagem = f"Bem-vindos, {jogadores[0]['nome']} e {jogadores[1]['nome']}! Lancem o dado."
                elif evento.key == pygame.K_BACKSPACE:
                    nomes_digitados[campo_nome_ativo] = nomes_digitados[campo_nome_ativo][:-1]
                elif evento.unicode and evento.unicode.isprintable() and len(nomes_digitados[campo_nome_ativo]) < 24:
                    nomes_digitados[campo_nome_ativo] += evento.unicode
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if CAMPO_NOME1.collidepoint(evento.pos):
                    campo_nome_ativo = 0
                elif CAMPO_NOME2.collidepoint(evento.pos):
                    campo_nome_ativo = 1
                elif BOTAO_ENTRAR.collidepoint(evento.pos):
                    for i, padrao in enumerate(("Obsidiana", "Sangue Seco")):
                        jogadores[i]["nome"] = (nomes_digitados[i].strip() or padrao)[:24]
                    if jogadores[0]["nome"].casefold() != jogadores[1]["nome"].casefold():
                        tela_inicio = False
                        mensagem = f"Bem-vindos, {jogadores[0]['nome']} e {jogadores[1]['nome']}! Lancem o dado."
        pygame.display.flip()
        RELOGIO.tick(60)
        continue

    desenhar_fundo()
    desenhar_tabuleiro()
    desenhar_pecas()
    desenhar_painel()


    if vencedor:
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 210))
        TELA.blit(camada, (0, 0))

        # Titulo da tela
        texto(
            "VITORIA SUPREMA",
            TITULO,
            OURO_CLARO,
            LARGURA // 2,
            245,
            True
        )

        texto(
            "A Encruzilhada escolheu seu vencedor!",
            FONTE,
            BRANCO,
            LARGURA // 2,
            290,
            True
        )

        # Mostra os dois jogadores e suas vitorias
        for i, jogador in enumerate(jogadores):
            y = 355 + i * 65

            if jogador["nome"] == vencedor:
                cor_nome = OURO_CLARO
                situacao = "VENCEDOR!"
            else:
                cor_nome = BRANCO
                situacao = "PARTICIPANTE"

            texto(
                jogador["nome"],
                SUBTITULO,
                cor_nome,
                LARGURA // 2,
                y,
                True
            )

            texto(
                f"Vitorias nesta partida: {jogador['vitorias']}",
                FONTE,
                BRANCO,
                LARGURA // 2,
                y + 25,
                True
            )

            texto(
                situacao,
                FONTE,
                cor_nome,
                LARGURA // 2,
                y + 45,
                True
            )

        texto(
            "Pressione R para jogar novamente",
            FONTE,
            BRANCO,
            LARGURA // 2,
            535,
            True
        )

        texto(
            "Pressione ESC para sair",
            FONTE,
            BRANCO,
            LARGURA // 2,
            570,
            True
        )


    if mostrar_manual:
        desenhar_manual()

# Verifica o tempo da jogada
    if escolhendo:
        tempo_passado = (
            pygame.time.get_ticks() - tempo_inicio
        ) // 1000

        if tempo_passado >= TEMPO_JOGADA:
                escolhendo = False
                dado = 0
                turno = 1 - turno
                mensagem = "Tempo esgotado! A vez passou para o outro jogador."

# Processa teclado e mouse
    for evento in pygame.event.get():

            # Fechar o jogo
            if evento.type == pygame.QUIT:
                rodando = False

            # Teclado
            elif evento.type == pygame.KEYDOWN:

                # Fechar o manual
                if mostrar_manual and evento.key in (
                    pygame.K_h,
                    pygame.K_ESCAPE
                ):
                    mostrar_manual = False

                # Abrir o manual
                elif evento.key == pygame.K_h:
                    mostrar_manual = True

                # Sair do jogo
                elif evento.key == pygame.K_ESCAPE:
                    rodando = False

                # Lançar o dado
                elif evento.key == pygame.K_SPACE:
                    som_dado.play()
                    lancar_dado()

                # Escolher uma peça usando os números 1, 2, 3 ou 4
                elif evento.key in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4
                ):
                    if escolhendo:
                        mover_peca(evento.key - pygame.K_1)

                # Salvar o jogo
                elif evento.key == pygame.K_s:
                    salvar()

                # Carregar o jogo
                elif evento.key == pygame.K_l:
                    carregar()

                # Reiniciar o jogo
                elif evento.key == pygame.K_r:
                    reiniciar()

                # Voltar para a tela de nomes
                elif evento.key == pygame.K_n:
                    nomes_digitados[:] = [
                        jogadores[0]["nome"],
                        jogadores[1]["nome"]
                    ]
                    tela_inicio = True

                # Ligar ou desligar a música
                elif evento.key == pygame.K_m:
                    alternar_musica()

            # Cliques do mouse
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos

                # Fechar o manual com um clique
                if mostrar_manual:
                    mostrar_manual = False

                # Abrir o manual
                elif BOTAO_MANUAL.collidepoint(mx, my):
                    mostrar_manual = True

                # Reiniciar
                elif BOTAO_REINICIAR.collidepoint(mx, my):
                    reiniciar()

                # Salvar
                elif BOTAO_SALVAR.collidepoint(mx, my):
                    salvar()

                # Carregar
                elif BOTAO_CARREGAR.collidepoint(mx, my):
                    carregar()

                # Música
                elif BOTAO_MUSICA.collidepoint(mx, my):
                    alternar_musica()

                # Lançar o dado pelo botão
                elif BOTAO_DADO.collidepoint(mx, my):
                    som_dado.play()
                    lancar_dado()

                # Escolher uma peça pelo mouse
                elif escolhendo:
                    clicou = False

                    # Verifica os botões das peças
                    for i, rect in enumerate(BOTOES_PECA):
                        if rect.collidepoint(mx, my):
                            mover_peca(i)
                            clicou = True
                            break

                    # Se não clicou no botão, verifica a posição da peça
                    if not clicou:
                        for i in pecas_moveis():
                            px, py = posicao_pixel(turno, i)

                            if math.hypot(mx - px, my - py) <= 21:
                                mover_peca(i)
                                break

    # Atualiza a tela
    pygame.display.flip()

    # Controla a velocidade do jogo
    RELOGIO.tick(60)

# Encerra o Pygame
pygame.quit()
sys.exit()