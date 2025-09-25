import os

def limpar_tela():
    """Limpa o terminal para uma melhor visualização."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Jogador:
    def __init__(self, cor, nome):
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
        self.tipo = tipo
        self.cor = cor
        self._casa = None

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if valor not in ("p", "d"):
            raise ValueError("tipo inválido: use 'p' ou 'd'")
        self._tipo = valor

    @property
    def cor(self):
        return self._cor

    @cor.setter
    def cor(self, valor):
        if valor not in ("b", "p"):
            raise ValueError("cor inválida: use 'b' ou 'p'")
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
        self.posicao = posicao
        self._conteudo = None

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
        if valor is not None:
            valor.casa = self
        self._conteudo = valor

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
        self._jogador_preto = jogador1 if jogador1.cor == 'p' else jogador2
        self._jogador_branco = jogador2 if jogador2.cor == 'b' else jogador1
        self._jogador_atual = self._jogador_preto
        self._tabuleiro = Tabuleiro(self._jogador_branco, self._jogador_preto)

    @property
    def jogador_atual(self):
        """Fornece acesso de leitura a quem é o jogador do turno atual."""
        return self._jogador_atual

    @property
    def tabuleiro(self):
        """Fornece acesso de leitura ao objeto do tabuleiro."""
        return self._tabuleiro

    def _trocar_turno(self):
        self._jogador_atual = self._jogador_branco if self._jogador_atual == self._jogador_preto else self._jogador_preto

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
        peca = casa_inicial.conteudo if casa_inicial else None

        if not peca or peca.cor != self.jogador_atual.cor:
            return "Posição inicial inválida ou a peça não é sua."
        if not casa_final or casa_final.conteudo is not None:
            return "Posição final inválida ou já ocupada."

        dist_l, dist_c = abs(l_fin - l_ini), abs(c_fin - c_ini)
        
        peca_capturada = None
        if dist_l == 1 and dist_c == 1:
            if peca.tipo == 'p':
                direcao = 1 if peca.cor == 'b' else -1
                if (l_fin - l_ini) != direcao:
                    return "Peão só pode se mover para frente."
        elif dist_l == 2 and dist_c == 2:
            l_meio, c_meio = (l_ini + l_fin) // 2, (c_ini + c_fin) // 2
            peca_meio = self.tabuleiro.get_casa(l_meio, c_meio).conteudo

            if not peca_meio or peca_meio.cor == self.jogador_atual.cor:
                return "Captura inválida. Não há peça adversária para capturar."
            
            if peca.tipo == 'p':
                direcao = 1 if peca.cor == 'b' else -1
                if (l_fin - l_ini) != direcao * 2:
                    return "Peão só pode capturar para frente."
            
            peca_capturada = peca_meio
        else:
            return "Movimento inválido. Mova apenas na diagonal."

        casa_final.conteudo = peca
        casa_inicial.conteudo = None
        
        if peca_capturada:
            adversario = self._jogador_branco if self._jogador_atual == self._jogador_preto else self._jogador_preto
            adversario.remover_peca(peca_capturada)
            peca_capturada.casa.conteudo = None
            
        if peca.tipo == 'p':
            if (peca.cor == 'b' and l_fin == 7) or (peca.cor == 'p' and l_fin == 0):
                peca.tipo = 'd'
                print(f"PEÇA PROMOVIDA A DAMA!")
        
        return None

    def jogar(self):
        vencedor = None
        while not vencedor:
            limpar_tela()
            self.tabuleiro.imprimir()
            print(f"\nTurno do jogador: {self.jogador_atual.nome} (peças '{'o' if self.jogador_atual.cor == 'b' else 'x'}')")
            
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