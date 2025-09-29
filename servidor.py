import socket
import json
from jogo import Damas, Jogador

def enviar_mensagem(sock, tipo, dados):
    try:
        msg = json.dumps({"tipo": tipo, "dados": dados})
        sock.sendall(msg.encode('utf-8'))
    except (ConnectionResetError, BrokenPipeError):
        print("Erro: Conexão com o cliente foi perdida.")

def receber_mensagem(sock):
    try:
        data = sock.recv(4096)
        if not data: return None
        return json.loads(data.decode('utf-8'))
    except (ConnectionResetError, json.JSONDecodeError):
        return None

def main():
    endereco = ('127.0.0.1', 50000)
    
    socket_conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_conexao.bind(endereco)
    socket_conexao.listen(1)
    print(f"Servidor de Damas iniciado em {endereco[0]}:{endereco[1]}.")
    print("Aguardando um jogador remoto se conectar...")

    sock_dados, info_cliente = socket_conexao.accept()
    print(f"Jogador Remoto ({info_cliente}) conectou-se.")

    jogador_servidor = Jogador('p', "Jogador Servidor (Pretas)")
    jogador_cliente = Jogador('b', "Jogador Cliente (Brancas)")
    jogo = Damas(jogador_cliente, jogador_servidor)

    enviar_mensagem(sock_dados, "info", "Você é o Jogador Cliente (Brancas 'o'). Você começa.")
    
    vencedor = None
    while not vencedor:
        jogador_da_vez = jogo.jogador_atual

        if jogador_da_vez.nome == "Jogador Servidor (Pretas)":
            print("\n" + ("-"*30))
            print(jogo.tabuleiro.to_string())
            print(f"--- TURNO DO JOGADOR LOCAL (Servidor - Peças 'x') ---")
            
            enviar_mensagem(sock_dados, "estado_jogo", {
                "tabuleiro": jogo.tabuleiro.to_string(),
                "sua_vez": False,
                "info": "Aguardando a jogada do Jogador Servidor."
            })

            jogada_valida = False
            while not jogada_valida:
                try:
                    jogada = input("Digite sua jogada (formato: linha,coluna linha,coluna): ")
                    pos_ini_str, pos_fin_str = jogada.split()
                    pos_inicial = tuple(map(int, pos_ini_str.split(',')))
                    pos_final = tuple(map(int, pos_fin_str.split(',')))
                    
                    erro = jogo.validar_e_mover(pos_inicial, pos_final)
                    if erro:
                        print(f"ERRO: {erro}")
                    else:
                        jogada_valida = True
                except (ValueError, IndexError):
                    print("ERRO: Formato de entrada inválido.")

        else:
            print("\nTurno do Jogador Cliente. Aguardando jogada remota...")
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
                    pos_ini_str, pos_fin_str = msg_jogada["dados"].split()
                    pos_inicial = tuple(map(int, pos_ini_str.split(',')))
                    pos_final = tuple(map(int, pos_fin_str.split(',')))
                    erro = jogo.validar_e_mover(pos_inicial, pos_final)
                    
                    if erro:
                        enviar_mensagem(sock_dados, "erro_jogada", erro)
                        enviar_mensagem(sock_dados, "estado_jogo", {
                            "tabuleiro": jogo.tabuleiro.to_string(),
                            "sua_vez": True,
                            "info": "Jogada inválida. Tente novamente."
                        })
                    else:
                        jogada_valida = True
                except (ValueError, IndexError):
                    enviar_mensagem(sock_dados, "erro_jogada", "Formato de jogada inválido enviado pelo cliente.")

            if not jogada_valida: break

        vencedor = jogo.verificar_vitoria()
        if not vencedor:
            jogo.trocar_turno()

    board_final = jogo.tabuleiro.to_string()
    msg_final = f"FIM DE JOGO! O vencedor é {vencedor.nome}!"
    print(board_final)
    print(msg_final)
    enviar_mensagem(sock_dados, "fim_de_jogo", {"tabuleiro": board_final, "mensagem": msg_final})

    sock_dados.close()
    socket_conexao.close()
    print("Servidor encerrado.")

if __name__ == "__main__":
    main()