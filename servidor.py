import socket
import json
from jogo import Damas, Jogador

def enviar_mensagem(sock, tipo, dados):
    try:
        msg = json.dumps({"tipo": tipo, "dados": dados})
        msg_bytes = msg.encode('utf-8')
        prefix = len(msg_bytes).to_bytes(2, byteorder='big')
        sock.sendall(prefix + msg_bytes)
    except (ConnectionResetError, BrokenPipeError):
        print("Erro: Conexão com o cliente foi perdida.")

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
        except ConnectionResetError:
            return None
        if not packet:
            return None
        data += packet
    return data

def receber_mensagem(sock):
    try:
        prefix = recv_all(sock, 2)
        if not prefix:
            return None
        length = int.from_bytes(prefix, byteorder='big')
        payload = recv_all(sock, length)
        if not payload:
            return None
        return json.loads(payload.decode('utf-8'))
    except (ConnectionResetError, json.JSONDecodeError):
        return None

def main():
    endereco = ('127.0.0.1', 50002)
    
    socket_conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_conexao.bind(endereco)
    socket_conexao.listen(1)
    print(f"\nServidor de Damas iniciado em {endereco[0]}:{endereco[1]}.")
    print("Aguardando um jogador remoto se conectar...\n")

    sock_dados, info_cliente = socket_conexao.accept()
    print(f"Jogador Remoto ({info_cliente}) conectou-se.\n")

    print("Você é o Jogador Servidor (Pretas 'x').")

    jogador_servidor = Jogador('p', "Jogador Servidor (Pretas)")
    jogador_cliente = Jogador('b', "Jogador Cliente (Brancas)")
    jogo = Damas(jogador_cliente, jogador_servidor)

    enviar_mensagem(sock_dados, "info", "Você é o Jogador Cliente (Brancas 'o'). Você começa.")
    
    print("\n" + ("-"*21))
    print(jogo.tabuleiro.to_string())

    vencedor = None
    while not vencedor:
        jogador_da_vez = jogo.jogador_atual

        if jogador_da_vez.nome == "Jogador Servidor (Pretas)":
            print("\n" + ("-"*21))
            print(jogo.tabuleiro.to_string())
            print("Sua vez de jogar.")
            
            enviar_mensagem(sock_dados, "estado_jogo", {
                "tabuleiro": jogo.tabuleiro.to_string(),
                "sua_vez": False,
                "info": "Turno do Jogador Servidor. Aguardando jogada..."
            })

            jogada_valida = False
            while not jogada_valida:
                try:
                    jogada = input("Digite sua jogada: ")
                    partes = jogada.split()
                    posicoes = [tuple(map(int, p.split(','))) for p in partes]
                    erro = jogo.validar_e_mover(posicoes)
                    if erro:
                        print(f"ERRO: {erro} Tente novamente.\n")
                    else:
                        jogada_valida = True
                except (ValueError, IndexError):
                    print("ERRO: Formato de entrada inválido. Tente novamente.\n")
            
            print("\n" + ("-"*21))
            print(jogo.tabuleiro.to_string())

        else:
            print("Turno do Jogador Cliente. Aguardando jogada...")
            enviar_mensagem(sock_dados, "estado_jogo", {
                "tabuleiro": jogo.tabuleiro.to_string(),
                "sua_vez": True,
                "info": "Sua vez de jogar."
            })

            jogada_valida = False
            while not jogada_valida:
                msg_jogada = receber_mensagem(sock_dados)
                if not msg_jogada or msg_jogada.get("tipo") != "jogada":
                    print("Cliente desconectado. Fim de jogo.")
                    vencedor = jogador_servidor
                    break
                
                try:
                    partes = msg_jogada["dados"].split()
                    posicoes = [tuple(map(int, p.split(','))) for p in partes]
                    erro = jogo.validar_e_mover(posicoes)
                    if erro:
                        enviar_mensagem(sock_dados, "erro_jogada", erro)
                    else:
                        jogada_valida = True
                except (ValueError, IndexError):
                    enviar_mensagem(sock_dados, "erro_jogada", "Formato de entrada inválido.")

            if not jogada_valida: break

        vencedor = jogo.verificar_vitoria()
        if not vencedor:
            jogo.trocar_turno()

    board_final = jogo.tabuleiro.to_string()
    if vencedor == "EMPATE":
        msg_final = "FIM DE JOGO! O jogo terminou em EMPATE! Nenhum jogador tem movimentos válidos."
    else:
        msg_final = f"FIM DE JOGO! O vencedor é {vencedor.nome}!"
    print(board_final)
    print(msg_final)
    enviar_mensagem(sock_dados, "fim_de_jogo", {"tabuleiro": board_final, "mensagem": msg_final})

    sock_dados.close()
    socket_conexao.close()
    print("Servidor encerrado.")

if __name__ == "__main__":
    main()