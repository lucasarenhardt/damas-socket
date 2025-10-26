class Jogador:
    """Representa um jogador do jogo de damas"""
    
    def __init__(self, cor, nome):
        """
        Inicializa um jogador
        cor: 'b' para brancas ou 'p' para pretas
        nome: identificação do jogador
        """
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
    """Representa uma peça do jogo (pedra ou dama)"""
    
    def __init__(self, tipo, cor):
        """
        tipo: 'p' para pedra ou 'd' para dama
        cor: 'b' para brancas ou 'p' para pretas
        """
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
            raise ValueError("tipo inválido: use 'p' (pedra) ou 'd' (dama)")
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
        """Retorna o símbolo visual da peça (o/O para brancas, x/X para pretas)"""
        if self._tipo == "p":
            return "o" if self._cor == "b" else "x"
        else:
            return "O" if self._cor == "b" else "X"

    def __str__(self):
        return self.simbolo


class Casa:
    """Representa uma casa do tabuleiro"""
    
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
        if (not isinstance(valor, tuple) or len(valor) != 2 or not all(isinstance(v, int) for v in valor)):
            raise ValueError("posicao deve ser uma tupla (linha, coluna) de inteiros")
        linha, coluna = valor
        if not (0 <= linha < 8 and 0 <= coluna < 8):
            raise ValueError("posicao fora do tabuleiro")
        self._posicao = (linha, coluna)
        # Define a cor da casa baseada na posição (padrão xadrez)
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
    """Gerencia o tabuleiro 8x8 e a disposição inicial das peças"""
    
    def __init__(self, jogador_branco, jogador_preto):
        self.jogador_branco = jogador_branco
        self.jogador_preto = jogador_preto
        self._casas = self._criar_tabuleiro_inicial()

    @property
    def casas(self):
        return self._casas

    def _criar_tabuleiro_inicial(self):
        """Cria o tabuleiro 8x8 e posiciona as peças iniciais"""
        tabuleiro = []
        for i in range(8):
            linha = []
            for j in range(8):
                casa = Casa((i, j))
                # Coloca peças pretas nas 3 primeiras linhas (casas pretas)
                if casa.cor == "p":
                    if i in (0, 1, 2):
                        peca = Peca("p", self.jogador_preto.cor)
                        self.jogador_preto.adicionar_peca(peca)
                        casa.conteudo = peca
                    # Coloca peças brancas nas 3 últimas linhas (casas pretas)
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
        """Retorna representação visual do tabuleiro como string"""
        board_str = "   0 1 2 3 4 5 6 7\n  -----------------\n"
        for i, linha in enumerate(self._casas):
            board_str += f"{i}| "
            for casa in linha:
                board_str += str(casa) + " "
            board_str += f"|{i}\n"
        board_str += "  -----------------\n   0 1 2 3 4 5 6 7\n"
        return board_str


class Damas:
    """Controla a lógica do jogo de damas"""
    
    def __init__(self, jogador1, jogador2):
        """Inicializa o jogo com dois jogadores (brancas começam)"""
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
        """Verifica se o jogador possui algum movimento válido disponível"""
        for peca in jogador.pecas:
            if not peca.casa:
                continue
            l_ini, c_ini = peca.casa.posicao
            
            # Todas as 4 direções diagonais possíveis
            direcoes = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            
            for dl, dc in direcoes:
                # Peões só se movem em uma direção
                if peca.tipo == 'p':
                    direcao_peca = -1 if peca.cor == 'b' else 1
                    if dl != direcao_peca:
                        continue
                
                # Verifica movimento simples
                l_dest, c_dest = l_ini + dl, c_ini + dc
                if 0 <= l_dest < 8 and 0 <= c_dest < 8:
                    casa_dest = self.tabuleiro.get_casa(l_dest, c_dest)
                    if casa_dest and not casa_dest.conteudo:
                        return True
                
                # Verifica captura para peões
                if peca.tipo == 'p':
                    l_dest2, c_dest2 = l_ini + 2*dl, c_ini + 2*dc
                    if 0 <= l_dest2 < 8 and 0 <= c_dest2 < 8:
                        casa_meio = self.tabuleiro.get_casa(l_ini + dl, c_ini + dc)
                        casa_dest2 = self.tabuleiro.get_casa(l_dest2, c_dest2)
                        if casa_meio and casa_dest2:
                            peca_meio = casa_meio.conteudo
                            if peca_meio and peca_meio.cor != peca.cor and not casa_dest2.conteudo:
                                return True
            
                # Verifica movimentos da dama em qualquer distância
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
                            if pecas_encontradas[0].cor != peca.cor:
                                continue
                            else:
                                break
                        else:
                            if len(pecas_encontradas) == 0:
                                return True
                            elif len(pecas_encontradas) == 1 and pecas_encontradas[0].cor != peca.cor:
                                return True
        return False

    def verificar_vitoria(self):
        """
        Verifica condições de vitória ou empate
        Retorna: jogador vencedor, "EMPATE" ou None (jogo continua)
        """
        # Vitória por captura de todas as peças
        if not self._get_adversario().pecas:
            return self.jogador_atual

        jogador_atual_pode_mover = self._tem_movimentos_validos(self.jogador_atual)
        adversario_pode_mover = self._tem_movimentos_validos(self._get_adversario())

        # Empate: nenhum jogador pode se mover
        if not jogador_atual_pode_mover and not adversario_pode_mover:
            return "EMPATE"

        # Vitória por bloqueio
        if not jogador_atual_pode_mover:
            return self._get_adversario()

        if not adversario_pode_mover:
            return self.jogador_atual

        return None

    def validar_e_mover(self, posicoes):
        """
        Valida e executa uma sequência de movimentos
        posicoes: lista de tuplas [(linha_inicial, coluna_inicial), (linha_final, coluna_final), ...]
        Retorna: mensagem de erro ou None se movimento foi válido
        """
        if not isinstance(posicoes, list) and isinstance(posicoes, tuple):
            return "Formato de posições inválido."

        if len(posicoes) < 2:
            return "É necessário informar pelo menos posição inicial e final."

        # Valida formato das posições
        try:
            for pos in posicoes:
                if not isinstance(pos, tuple) or len(pos) != 2:
                    return "Formato de posição inválido. Use (linha,coluna)."
                l, c = pos
                if not isinstance(l, int) or not isinstance(c, int):
                    return "Coordenadas devem ser números inteiros."
        except (ValueError, TypeError):
            return "Erro ao processar as posições. Verifique o formato."

        # Valida posição inicial e peça
        l_ini, c_ini = posicoes[0]
        casa_inicial = self.tabuleiro.get_casa(l_ini, c_ini)
        if not casa_inicial or not casa_inicial.conteudo:
            return "Posição inicial inválida ou vazia."
        peca = casa_inicial.conteudo
        if peca.cor != self.jogador_atual.cor:
            return "A peça selecionada não pertence ao jogador atual."

        adversario = self._get_adversario()

        # Valida cada movimento da sequência
        movimentos_validados = []
        atual_l, atual_c = l_ini, c_ini
        tipo_peca_atual = peca.tipo
        
        for idx in range(1, len(posicoes)):
            l_fin, c_fin = posicoes[idx]
            casa_final = self.tabuleiro.get_casa(l_fin, c_fin)
            if not casa_final:
                return "Posição final inválida."
            
            # Verifica se destino está ocupado
            ocupada_por_outra = False
            if casa_final.conteudo is not None:
                if casa_final.posicao != (l_ini, c_ini):
                    ocupada_por_outra = True
            
            if ocupada_por_outra:
                return "Posição final já está ocupada."

            # Valida movimento baseado no tipo da peça
            if tipo_peca_atual == 'p':
                valido, peca_capturada, msg = self._validar_movimento_pedra(peca, atual_l, atual_c, l_fin, c_fin)
            else:
                valido, peca_capturada, msg = self._validar_movimento_dama(peca, atual_l, atual_c, l_fin, c_fin)

            if not valido:
                return msg or "Movimento inválido."

            # Múltiplos movimentos só são permitidos em capturas encadeadas
            if len(posicoes) > 2 and peca_capturada is None:
                return "Movimento inválido: múltiplos movimentos sem captura não são permitidos."

            movimentos_validados.append((l_fin, c_fin, peca_capturada))
            atual_l, atual_c = l_fin, c_fin
            
            # Checa promoção a dama
            if tipo_peca_atual == 'p':
                if (peca.cor == 'b' and l_fin == 0) or (peca.cor == 'p' and l_fin == 7):
                    tipo_peca_atual = 'd'

        # Executa todos os movimentos validados
        atual_casa = casa_inicial
        
        for l_fin, c_fin, peca_capturada in movimentos_validados:
            casa_final = self.tabuleiro.get_casa(l_fin, c_fin)
            
            # Remove peça capturada
            if peca_capturada:
                casa_meio = peca_capturada.casa
                if casa_meio:
                    casa_meio.conteudo = None
                adversario.remover_peca(peca_capturada)

            # Move a peça
            if atual_casa.conteudo is peca:
                atual_casa.conteudo = None

            casa_final.conteudo = peca
            atual_casa = casa_final

        # Promove a dama se atingiu a última linha
        if peca.tipo == 'p':
            l_fin_final = atual_casa.posicao[0]
            if (peca.cor == 'b' and l_fin_final == 0) or (peca.cor == 'p' and l_fin_final == 7):
                peca.tipo = 'd'

        return None

    def _validar_movimento_pedra(self, peca, l_ini, c_ini, l_fin, c_fin):
        """
        Valida movimento de pedra
        Retorna: (válido: bool, peça_capturada: Peca|None, mensagem_erro: str|None)
        """
        d_l = l_fin - l_ini
        d_c = c_fin - c_ini
        dist_l, dist_c = abs(d_l), abs(d_c)
        direcao = -1 if peca.cor == 'b' else 1
        
        # Movimento simples (1 casa diagonal)
        if dist_l == 1 and dist_c == 1 and d_l == direcao:
            return True, None, None
        
        # Captura (2 casas diagonais)
        if dist_l == 2 and dist_c == 2 and d_l == direcao * 2:
            l_meio, c_meio = (l_ini + l_fin) // 2, (c_ini + c_fin) // 2
            casa_meio = self.tabuleiro.get_casa(l_meio, c_meio)
            peca_meio = casa_meio.conteudo if casa_meio else None
            if peca_meio and peca_meio.cor != peca.cor:
                return True, peca_meio, None
            else:
                return False, None, "Captura inválida. Não há peça adversária para capturar."
        return False, None, "Movimento inválido para pedra."

    def _validar_movimento_dama(self, peca, l_ini, c_ini, l_fin, c_fin):
        """
        Valida movimento de dama (qualquer distância diagonal)
        Retorna: (válido: bool, peça_capturada: Peca|None, mensagem_erro: str|None)
        """
        d_l = l_fin - l_ini
        d_c = c_fin - c_ini
        dist = abs(d_l)
        
        # Dama deve se mover na diagonal
        if dist == 0 or dist != abs(d_c):
            return False, None, "Dama deve mover-se na diagonal."
        
        # Calcula direção do movimento
        step_l = 1 if d_l > 0 else -1
        step_c = 1 if d_c > 0 else -1
        
        # Verifica todas as casas no caminho
        pecas_no_caminho = []
        for k in range(1, dist):
            casa = self.tabuleiro.get_casa(l_ini + k * step_l, c_ini + k * step_c)
            if casa and casa.conteudo:
                pecas_no_caminho.append(casa.conteudo)
        
        # Movimento livre (sem peças no caminho)
        if not pecas_no_caminho:
            return True, None, None
        
        # Captura (exatamente uma peça adversária no caminho)
        if len(pecas_no_caminho) == 1 and pecas_no_caminho[0].cor != peca.cor:
            return True, pecas_no_caminho[0], None
        
        return False, None, "Movimento de Dama bloqueado ou captura inválida."