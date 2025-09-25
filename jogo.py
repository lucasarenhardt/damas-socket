import os


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


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
        if (not isinstance(valor, tuple) or len(valor) != 2 or not all(isinstance(v, int) for v in valor)):
            raise ValueError("posicao deve ser uma tupla (linha, coluna) de inteiros")
        linha, coluna = valor
        if not (0 <= linha < 8 and 0 <= coluna < 8):
            raise ValueError("posicao fora do tabuleiro")
        self._posicao = (linha, coluna)
        # casas jogáveis (pretas) recebem 'p', outras 'b'
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
        # desanexar peça atual (se houver)
        if self._conteudo is not None:
            # não usar o setter público para evitar efeitos colaterais durante movimentos
            self._conteudo._casa = None
        self._conteudo = valor
        if valor is not None:
            # anexar peça a esta casa
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
                # posiciona peças apenas nas casas escuras ('p')
                if casa.cor == "p":
                    if i in (0, 1, 2):
                        peca = Peca("p", self.jogador_branco.cor)
                        self.jogador_branco.adicionar_peca(peca)
                        casa.conteudo = peca
                    elif i in (5, 6, 7):
                        peca = Peca("p", self.jogador_preto.cor)
                        self.jogador_preto.adicionar_peca(peca)
                        casa.conteudo = peca
                linha.append(casa)
            tabuleiro.append(linha)
        return tabuleiro

    def get_casa(self, linha, coluna):
        if not (0 <= linha < 8 and 0 <= coluna < 8):
            return None
        return self._casas[linha][coluna]

    def imprimir(self):
        print("   0 1 2 3 4 5 6 7")
        print("  -----------------")
        for i, linha in enumerate(self._casas):
            print(f"{i}| ", end="")
            for casa in linha:
                print(casa, end=" ")
            print(f"|{i}")
        print("  -----------------")
        print("   0 1 2 3 4 5 6 7")


class Damas:
    def __init__(self, jogador1, jogador2):
        # define jogadores claro/escuro
        if jogador1.cor == 'p':
            self._jogador_preto = jogador1
            self._jogador_branco = jogador2
        else:
            self._jogador_preto = jogador2
            self._jogador_branco = jogador1

        self._jogador_atual = self._jogador_branco
        self._tabuleiro = Tabuleiro(self._jogador_branco, self._jogador_preto)

    @property
    def jogador_atual(self):
        return self._jogador_atual

    @property
    def tabuleiro(self):
        return self._tabuleiro

    def _trocar_turno(self):
        self._jogador_atual = self._jogador_branco if self._jogador_atual == self._jogador_preto else self._jogador_preto

    def _get_adversario(self):
        return self._jogador_preto if self._jogador_atual == self._jogador_branco else self._jogador_branco

    def _verificar_vitoria(self):
        if not self._jogador_preto.pecas:
            return self._jogador_branco
        if not self._jogador_branco.pecas:
            return self._jogador_preto
        return None

    def _validar_e_mover(self, pos_inicial, pos_final):
        l_ini, c_ini = pos_inicial
        l_fin, c_fin = pos_final

        casa_inicial = self.tabuleiro.get_casa(l_ini, c_ini)
        casa_final = self.tabuleiro.get_casa(l_fin, c_fin)

        if not casa_inicial or not casa_inicial.conteudo:
            return "Posição inicial inválida ou vazia."
        peca = casa_inicial.conteudo

        if peca.cor != self.jogador_atual.cor:
            return "A peça selecionada não pertence ao jogador atual."
        if not casa_final:
            return "Posição final inválida."
        if casa_final.conteudo is not None:
            return "Posição final já está ocupada."

        # delegar validação ao tipo da peça
        if peca.tipo == 'p':
            valido, peca_capturada, msg = self._validar_movimento_peao(peca, l_ini, c_ini, l_fin, c_fin)
        else:
            valido, peca_capturada, msg = self._validar_movimento_dama(peca, l_ini, c_ini, l_fin, c_fin)

        if not valido:
            return msg or "Movimento inválido."

        # executar movimento: primeiro limpar origem para manter consistência dos atributos
        casa_inicial.conteudo = None

        # se houve captura, remover a peça capturada
        if peca_capturada:
            casa_meio = peca_capturada.casa
            if casa_meio:
                # retira do tabuleiro e da lista do adversário
                casa_meio.conteudo = None
            adversario = self._get_adversario()
            adversario.remover_peca(peca_capturada)

        # posicionar peça no destino
        casa_final.conteudo = peca

        # promoção de peão
        if peca.tipo == 'p':
            if (peca.cor == 'b' and l_fin == 7) or (peca.cor == 'p' and l_fin == 0):
                peca.tipo = 'd'
                print("PEÇA PROMOVIDA A DAMA!")

        return None

    def _validar_movimento_peao(self, peca, l_ini, c_ini, l_fin, c_fin):
        d_l = l_fin - l_ini
        d_c = c_fin - c_ini
        dist_l, dist_c = abs(d_l), abs(d_c)

        # movimento simples diagonal 1
        if dist_l == 1 and dist_c == 1:
            direcao = 1 if peca.cor == 'b' else -1
            if d_l != direcao:
                return False, None, "Peão só pode se mover para frente."
            return True, None, None

        # captura de peça adversária (salto)
        if dist_l == 2 and dist_c == 2:
            l_meio, c_meio = (l_ini + l_fin) // 2, (c_ini + c_fin) // 2
            casa_meio = self.tabuleiro.get_casa(l_meio, c_meio)
            peca_meio = casa_meio.conteudo if casa_meio else None
            if not peca_meio or peca_meio.cor == peca.cor:
                return False, None, "Captura inválida. Não há peça adversária para capturar."
            direcao = 1 if peca.cor == 'b' else -1
            if d_l != direcao * 2:
                return False, None, "Peão só pode capturar para frente."
            return True, peca_meio, None

        return False, None, "Movimento inválido para peão."

    def _validar_movimento_dama(self, peca, l_ini, c_ini, l_fin, c_fin):
        d_l = l_fin - l_ini
        d_c = c_fin - c_ini
        dist = abs(d_l)
        if dist == 0 or dist != abs(d_c):
            return False, None, "Dama deve mover-se na diagonal."

        step_l = 1 if d_l > 0 else -1
        step_c = 1 if d_c > 0 else -1

        # percorre caminho entre origem e destino e coleta peças encontradas
        encontrados = []
        for k in range(1, dist):
            casa = self.tabuleiro.get_casa(l_ini + k * step_l, c_ini + k * step_c)
            if casa and casa.conteudo:
                encontrados.append(casa.conteudo)

        if not encontrados:
            # caminho livre -> movimento simples
            return True, None, None

        # se encontrou exatamente uma peça adversária no caminho e destino vazio -> captura
        if len(encontrados) == 1 and encontrados[0].cor != peca.cor:
            return True, encontrados[0], None

        return False, None, "Movimento inválido para dama (bloqueado ou captura inválida)."

    def jogar(self):
        vencedor = None
        while not vencedor:
            limpar_tela()
            self.tabuleiro.imprimir()
            simbolo = 'o' if self.jogador_atual.cor == 'b' else 'x'
            print(f"\nTurno do jogador: {self.jogador_atual.nome} (peças '{simbolo}')")

            try:
                entrada = input("Digite a jogada (formato: linha,coluna linha,coluna): ")
                pos_ini_str, pos_fin_str = entrada.split()
                pos_inicial = tuple(map(int, pos_ini_str.split(',')))
                pos_final = tuple(map(int, pos_fin_str.split(',')))

                erro = self._validar_e_mover(pos_inicial, pos_final)

                if erro:
                    print(f"\nERRO: {erro}")
                    input("Pressione Enter para tentar novamente...")
                else:
                    vencedor = self._verificar_vitoria()
                    self._trocar_turno()

            except (ValueError, IndexError):
                print("\nERRO: Formato de entrada inválido. Use 'linha,coluna linha,coluna'.")
                input("Pressione Enter para tentar novamente...")

        limpar_tela()
        self.tabuleiro.imprimir()
        print(f"\nFIM DE JOGO! O jogador {vencedor.nome} venceu!")


if __name__ == "__main__":
    j1 = Jogador("p", "Jogador 1 (Pretas)")
    j2 = Jogador("b", "Jogador 2 (Brancas)")

    jogo = Damas(j1, j2)
    jogo.jogar()
