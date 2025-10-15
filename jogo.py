import os

class Jogador:
    def __init__(self, cor, nome):
        if cor not in ("b", "p"):
            raise ValueError("cor inválida: use 'b' (brancas) ou 'p' (pretas)")
        self._cor = cor
        self._nome = nome
        self._pecas = []

    @property
    def nome(self):
        return self._nome

    @property
    def cor(self):
        return self._cor

    @property
    def pecas(self):
        return self._pecas

    def adicionar_peca(self, peca):
        if not isinstance(peca, Peca):
            raise ValueError("Só é permitido adicionar objetos Peca")
        if peca not in self._pecas:
            self._pecas.append(peca)

    def remover_peca(self, peca):
        if peca in self._pecas:
            self._pecas.remove(peca)


class Peca:
    def __init__(self, tipo, cor):
        self._tipo = None
        self._cor = None
        self._casa = None
        self.tipo = tipo
        self.cor = cor

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if valor not in ("p", "d"):
            raise ValueError("tipo inválido: use 'p' (peão) ou 'd' (dama)")
        self._tipo = valor

    @property
    def cor(self):
        return self._cor

    @cor.setter
    def cor(self, valor):
        if valor not in ("b", "p"):
            raise ValueError("cor inválida: use 'b' (brancas) ou 'p' (pretas)")
        self._cor = valor

    @property
    def casa(self):
        return self._casa

    @casa.setter
    def casa(self, casa):
        if casa is not None and not isinstance(casa, Casa):
            raise ValueError("casa deve ser um objeto Casa ou None")
        self._casa = casa

    @property
    def simbolo(self):
        if self._tipo == "p":
            return "o" if self._cor == "b" else "x"
        else:
            return "O" if self._cor == "b" else "X"

    def __str__(self):
        return self.simbolo


class Casa:
    def __init__(self, posicao):
        self._posicao = None
        self._cor = None
        self._conteudo = None
        self.posicao = posicao

    @property
    def posicao(self):
        return self._posicao

    @posicao.setter
    def posicao(self, valor):
        if (
            not isinstance(valor, tuple)
            or len(valor) != 2
            or not all(isinstance(v, int) for v in valor)
        ):
            raise ValueError("posicao deve ser uma tupla (linha, coluna) de inteiros")
        linha, coluna = valor
        if not (0 <= linha < 8 and 0 <= coluna < 8):
            raise ValueError("posicao fora do tabuleiro")
        self._posicao = (linha, coluna)
        self._cor = "p" if (linha + coluna) % 2 else "b"

    @property
    def cor(self):
        return self._cor

    @property
    def conteudo(self):
        return self._conteudo

    @conteudo.setter
    def conteudo(self, valor):
        if valor is not None and not isinstance(valor, Peca):
            raise ValueError("conteudo deve ser uma Peca ou None")
        if self._conteudo is not None:
            self._conteudo._casa = None
        self._conteudo = valor
        if valor is not None:
            valor._casa = self

    def __str__(self):
        if self._conteudo:
            return str(self._conteudo)
        return "#" if self._cor == "b" else "-"


class Tabuleiro:
    def __init__(self, jogador_branco, jogador_preto):
        self.jogador_branco = jogador_branco
        self.jogador_preto = jogador_preto
        self._casas = self._criar_tabuleiro_inicial()

    @property
    def casas(self):
        return self._casas

    def _criar_tabuleiro_inicial(self):
        tabuleiro = []
        for i in range(8):
            linha = []
            for j in range(8):
                casa = Casa((i, j))
                if casa.cor == "p":
                    if i in (0, 1, 2):
                        peca = Peca("p", self.jogador_preto.cor)
                        self.jogador_preto.adicionar_peca(peca)
                        casa.conteudo = peca
                    elif i in (5, 6, 7):
                        peca = Peca("p", self.jogador_branco.cor)
                        self.jogador_branco.adicionar_peca(peca)
                        casa.conteudo = peca
                linha.append(casa)
            tabuleiro.append(linha)
        return tabuleiro

    def get_casa(self, linha, coluna):
        if not (0 <= linha < 8 and 0 <= coluna < 8):
            return None
        return self._casas[linha][coluna]

    def to_string(self):
        board_str = "   0 1 2 3 4 5 6 7\n  -----------------\n"
        for i, linha in enumerate(self._casas):
            board_str += f"{i}| "
            for casa in linha:
                board_str += str(casa) + " "
            board_str += f"|{i}\n"
        board_str += "  -----------------\n   0 1 2 3 4 5 6 7\n"
        return board_str


class Damas:
    def __init__(self, jogador1, jogador2):
        if jogador1.cor == 'b':
            self._jogador_branco = jogador1
            self._jogador_preto = jogador2
        else:
            self._jogador_branco = jogador2
            self._jogador_preto = jogador1
        self._jogador_atual = self._jogador_branco
        self._tabuleiro = Tabuleiro(self._jogador_branco, self._jogador_preto)

    @property
    def jogador_atual(self):
        return self._jogador_atual

    @property
    def tabuleiro(self):
        return self._tabuleiro

    def trocar_turno(self):
        if self._jogador_atual == self._jogador_preto:
            self._jogador_atual = self._jogador_branco
        else:
            self._jogador_atual = self._jogador_preto

    def _get_adversario(self):
        if self._jogador_atual == self._jogador_branco:
            return self._jogador_preto
        else:
            return self._jogador_branco

    def _tem_movimentos_validos(self, jogador):
        """
        Verifica se o jogador tem pelo menos um movimento válido.
        Retorna True se houver algum movimento possível, False caso contrário.
        """
        for peca in jogador.pecas:
            if not peca.casa:
                continue
            l_ini, c_ini = peca.casa.posicao
            
            # Testar todos os movimentos possíveis (diagonais)
            direcoes = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            
            for dl, dc in direcoes:
                # Para peões, verificar apenas direção permitida
                if peca.tipo == 'p':
                    direcao_peca = -1 if peca.cor == 'b' else 1
                    if dl != direcao_peca:
                        continue
                
                # Testar movimento simples (1 casa)
                l_dest, c_dest = l_ini + dl, c_ini + dc
                if 0 <= l_dest < 8 and 0 <= c_dest < 8:
                    casa_dest = self.tabuleiro.get_casa(l_dest, c_dest)
                    if casa_dest and not casa_dest.conteudo:
                        return True
                
                # Testar captura (2 casas) para peões
                if peca.tipo == 'p':
                    l_dest2, c_dest2 = l_ini + 2*dl, c_ini + 2*dc
                    if 0 <= l_dest2 < 8 and 0 <= c_dest2 < 8:
                        casa_meio = self.tabuleiro.get_casa(l_ini + dl, c_ini + dc)
                        casa_dest2 = self.tabuleiro.get_casa(l_dest2, c_dest2)
                        if casa_meio and casa_dest2:
                            peca_meio = casa_meio.conteudo
                            if peca_meio and peca_meio.cor != peca.cor and not casa_dest2.conteudo:
                                return True
                
                # Para damas, testar movimentos em todas as distâncias
                if peca.tipo == 'd':
                    pecas_encontradas = []
                    for dist in range(1, 8):
                        l_test, c_test = l_ini + dist*dl, c_ini + dist*dc
                        if not (0 <= l_test < 8 and 0 <= c_test < 8):
                            break
                        casa_test = self.tabuleiro.get_casa(l_test, c_test)
                        if casa_test.conteudo:
                            pecas_encontradas.append(casa_test.conteudo)
                            if len(pecas_encontradas) > 1:
                                break
                            # Se encontrou peça adversária, ainda pode ter movimento de captura além dela
                            if pecas_encontradas[0].cor != peca.cor:
                                continue
                            else:
                                break
                        else:
                            # Casa vazia encontrada
                            if len(pecas_encontradas) == 0:
                                return True  # movimento simples
                            elif len(pecas_encontradas) == 1 and pecas_encontradas[0].cor != peca.cor:
                                return True  # captura válida
        
        return False

    def verificar_vitoria(self):
        """
        Verifica condições de vitória ou empate.
        Retorna:
        - jogador vencedor se houver vitória
        - "EMPATE" se for empate
        - None se o jogo continua
        """
        # Verifica se adversário perdeu todas as peças
        if not self._get_adversario().pecas:
            return self.jogador_atual
        
        # Verifica se jogadores têm movimentos válidos
        jogador_atual_pode_mover = self._tem_movimentos_validos(self.jogador_atual)
        adversario_pode_mover = self._tem_movimentos_validos(self._get_adversario())
        
        # Se nenhum dos dois pode mover: EMPATE
        if not jogador_atual_pode_mover and not adversario_pode_mover:
            return "EMPATE"
        
        # Se apenas o jogador atual não pode mover: adversário vence
        if not jogador_atual_pode_mover:
            return self._get_adversario()
        
        # Se apenas o adversário não pode mover: jogador atual vence
        if not adversario_pode_mover:
            return self.jogador_atual
        
        # Jogo continua
        return None

    def validar_e_mover(self, posicoes):
        """
        Recebe uma lista de posições [(l0,c0),(l1,c1),...].
        Valida e executa cada segmento em sequência, permitindo múltiplas capturas.
        Retorna None se OK ou string com erro.
        """
        # aceitar também as chamadas com dois argumentos passadas acidentalmente
        if not isinstance(posicoes, list) and isinstance(posicoes, tuple):
            return "Formato de posições inválido."

        if len(posicoes) < 2:
            return "É necessário informar pelo menos posição inicial e final."

        # Validar formato de todas as posições ANTES de fazer qualquer mudança
        try:
            for pos in posicoes:
                if not isinstance(pos, tuple) or len(pos) != 2:
                    return "Formato de posição inválido. Use (linha,coluna)."
                l, c = pos
                if not isinstance(l, int) or not isinstance(c, int):
                    return "Coordenadas devem ser números inteiros."
        except (ValueError, TypeError):
            return "Erro ao processar as posições. Verifique o formato."

        l_ini, c_ini = posicoes[0]
        casa_inicial = self.tabuleiro.get_casa(l_ini, c_ini)
        if not casa_inicial or not casa_inicial.conteudo:
            return "Posição inicial inválida ou vazia."
        peca = casa_inicial.conteudo
        if peca.cor != self.jogador_atual.cor:
            return "A peça selecionada não pertence ao jogador atual."

        adversario = self._get_adversario()
        
        # FASE 1: VALIDAR TODOS OS MOVIMENTOS sem modificar o tabuleiro
        movimentos_validados = []
        atual_l, atual_c = l_ini, c_ini
        tipo_peca_atual = peca.tipo
        
        for idx in range(1, len(posicoes)):
            l_fin, c_fin = posicoes[idx]
            casa_final = self.tabuleiro.get_casa(l_fin, c_fin)
            if not casa_final:
                return "Posição final inválida."
            
            # verificar se a casa final está ocupada (ignorando casas já processadas nesta sequência)
            ocupada_por_outra = False
            if casa_final.conteudo is not None:
                # verificar se é a própria peça que está se movendo
                if casa_final.posicao != (l_ini, c_ini):
                    ocupada_por_outra = True
            
            if ocupada_por_outra:
                return "Posição final já está ocupada."

            # validar segmento conforme tipo atual da peça
            if tipo_peca_atual == 'p':
                valido, peca_capturada, msg = self._validar_movimento_peao(peca, atual_l, atual_c, l_fin, c_fin)
            else:
                valido, peca_capturada, msg = self._validar_movimento_dama(peca, atual_l, atual_c, l_fin, c_fin)

            if not valido:
                return msg or "Movimento inválido."

            # se houver mais de um segmento (sequência), exigimos que cada segmento seja captura
            if len(posicoes) > 2 and peca_capturada is None:
                return "Movimento inválido: múltiplos movimentos sem captura não são permitidos."

            movimentos_validados.append((l_fin, c_fin, peca_capturada))
            atual_l, atual_c = l_fin, c_fin
            
            # atualizar tipo se houver promoção no meio da sequência
            if tipo_peca_atual == 'p':
                if (peca.cor == 'b' and l_fin == 0) or (peca.cor == 'p' and l_fin == 7):
                    tipo_peca_atual = 'd'

        # FASE 2: APLICAR TODOS OS MOVIMENTOS (já validados)
        atual_casa = casa_inicial
        
        for l_fin, c_fin, peca_capturada in movimentos_validados:
            casa_final = self.tabuleiro.get_casa(l_fin, c_fin)
            
            # aplicar captura (se houver)
            if peca_capturada:
                casa_meio = peca_capturada.casa
                if casa_meio:
                    casa_meio.conteudo = None
                adversario.remover_peca(peca_capturada)

            # limpar a casa atual antes de mover para evitar que a mesma peça fique referenciada em duas casas
            if atual_casa.conteudo is peca:
                atual_casa.conteudo = None

            # mover peça para casa_final
            casa_final.conteudo = peca
            atual_casa = casa_final

        # promoção de peão ao final da sequência
        if peca.tipo == 'p':
            l_fin_final = atual_casa.posicao[0]
            if (peca.cor == 'b' and l_fin_final == 0) or (peca.cor == 'p' and l_fin_final == 7):
                peca.tipo = 'd'

        return None

    def _validar_movimento_peao(self, peca, l_ini, c_ini, l_fin, c_fin):
        d_l = l_fin - l_ini
        d_c = c_fin - c_ini
        dist_l, dist_c = abs(d_l), abs(d_c)
        direcao = -1 if peca.cor == 'b' else 1
        # movimento simples (apenas um passo diagonal na direção)
        if dist_l == 1 and dist_c == 1 and d_l == direcao:
            return True, None, None
        # captura: pulo de duas casas com peça adversária no meio
        if dist_l == 2 and dist_c == 2 and d_l == direcao * 2:
            l_meio, c_meio = (l_ini + l_fin) // 2, (c_ini + c_fin) // 2
            casa_meio = self.tabuleiro.get_casa(l_meio, c_meio)
            peca_meio = casa_meio.conteudo if casa_meio else None
            if peca_meio and peca_meio.cor != peca.cor:
                return True, peca_meio, None
            else:
                return False, None, "Captura inválida. Não há peça adversária para capturar."
        return False, None, "Movimento inválido para peão."

    def _validar_movimento_dama(self, peca, l_ini, c_ini, l_fin, c_fin):
        d_l = l_fin - l_ini
        d_c = c_fin - c_ini
        dist = abs(d_l)
        if dist == 0 or dist != abs(d_c):
            return False, None, "Dama deve mover-se na diagonal."
        step_l = 1 if d_l > 0 else -1
        step_c = 1 if d_c > 0 else -1
        pecas_no_caminho = []
        for k in range(1, dist):
            casa = self.tabuleiro.get_casa(l_ini + k * step_l, c_ini + k * step_c)
            if casa and casa.conteudo:
                pecas_no_caminho.append(casa.conteudo)
        # movimento simples: caminho livre
        if not pecas_no_caminho:
            return True, None, None
        # captura: exatamente uma peça adversária no caminho
        if len(pecas_no_caminho) == 1 and pecas_no_caminho[0].cor != peca.cor:
            return True, pecas_no_caminho[0], None
        return False, None, "Movimento de Dama bloqueado ou captura inválida."