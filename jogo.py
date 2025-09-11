import socket
'''
socket_conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
endereco = ('127.0.0.1', 50001)
socket_conexao.bind(endereco)

socket_conexao.listen(2)

socket_dados, info_cliente = socket_conexao.accept()
'''

class Jogador:
    def __init__ (self, cor):
        self.cor = cor 
        self.qtd_pecas = 12

class Damas:
    def __init__ (self, jogador1, jogador2):
        self.tabuleiro = self.criar_tabuleiro_inicial()
        self.jogador1 = jogador1
        self.jogador2 = jogador2 
        self.jogador_atual = jogador1
    
    def criar_tabuleiro_inicial(self):
        tabuleiro = []
        for i in range (8):
            linha_atual = []
            for j in range (8):
                if ((i+j)%2):
                    if i in [0, 1, 2]:
                        linha_atual.append('x')
                    elif i in [5, 6, 7]:
                        linha_atual.append('o')
                    else:
                        linha_atual.append('-')
                else:
                    linha_atual.append('#')
            tabuleiro.append(linha_atual)
        return tabuleiro

    def imprimir_tabuleiro(self):
        print("    0 1 2 3 4 5 6 7\n")
        for i in range (8):
            print(i, end=" ")
            print(" ", end=" ")
            for j in range (8):
                print(self.tabuleiro[i][j], end=" ")
            print()

    def mover(self, pos_inicial, pos_final):
        linha_inicial, coluna_inicial = pos_inicial
        linha_final, coluna_final = pos_final
        peca_selecionada = self.tabuleiro[linha_inicial][coluna_inicial]
        destino = self.tabuleiro[linha_final][coluna_final]

        if (linha_inicial not in range(8) or coluna_inicial not in range(8) or
            linha_final not in range(8) or coluna_final not in range(8)):
            print("Movimento invalido: Posicao fora do tabuleiro.")
            return

        if(peca_selecionada in ['x', 'o', 'X', 'O']):
            if(peca_selecionada != self.jogador_atual.cor):
                print("\nVoce nao pode mover a peca do adversario.")
                return
        else:
            print("\nVoce nao selecionou nenhuma peca")
            return

        if(destino not in ['-', '#']):
            print("\nMovimento invalido")
            return

        distancia_linhas = abs(linha_final - linha_inicial)
        distancia_colunas = abs(coluna_final - coluna_inicial)

        movimento_diagonal_simples = (distancia_linhas == 1 and distancia_colunas == 1)

        if not movimento_diagonal_simples:
            print("\nMovimento inválido: Só é possível se mover 1 posição na diagonal.")
        else:
            print("\nO movimento é um passo diagonal válido.") 


jogador1 = Jogador('o')
jogador2 = Jogador('x')
jogo = Damas(jogador1, jogador2)

jogo.imprimir_tabuleiro()
jogo.mover((5,0),(3,2))