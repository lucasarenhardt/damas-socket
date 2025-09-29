# cliente_damas.py

import socket
import json

def enviar_mensagem(sock, tipo, dados):
    """Codifica e envia uma mensagem no formato JSON."""
    msg = json.dumps({"tipo": tipo, "dados": dados})
    sock.sendall(msg.encode('utf-8'))

def receber_mensagem(sock):
    """Recebe, decodifica e retorna uma mensagem JSON."""
    try:
        data = sock.recv(4096)
        if not data:
            return None
        return json.loads(data.decode('utf-8'))
    except (ConnectionResetError, json.JSONDecodeError):
        return None

def main():
    HOST = '127.0.0.1'
    PORT = 50000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print(f"Conectado ao servidor de damas em {HOST}:{PORT}")
    except ConnectionRefusedError:
        print("Não foi possível se conectar ao servidor. Verifique se ele está em execução.")
        return

    msg_inicial = receber_mensagem(client_socket)
    if msg_inicial and msg_inicial["tipo"] == "info":
        print(msg_inicial["dados"])
        print("Aguardando o início do jogo...")
    
    game_over = False
    while not game_over:
        mensagem = receber_mensagem(client_socket)

        if not mensagem:
            print("\nConexão perdida com o servidor.")
            break
            
        tipo = mensagem.get("tipo")
        dados = mensagem.get("dados")

        if tipo == "estado_jogo":
            print("\n" + ("-"*30))
            print("--- Jogo de Damas em Rede ---")
            print(dados["tabuleiro"])
            print(dados["info"])
            
            if dados["sua_vez"]:
                jogada = input("Digite a jogada (formato: linha,coluna linha,coluna): ")
                enviar_mensagem(client_socket, "jogada", jogada)
        
        elif tipo == "erro_jogada":
            print(f"\nERRO: {dados}")

        elif tipo == "fim_de_jogo":
            print("\n" + ("="*30))
            print("--- Jogo de Damas em Rede ---")
            print(dados["tabuleiro"])
            print(f"\n{dados['mensagem']}")
            game_over = True
        
        else:
            print(dados)

    print("\nO jogo terminou. Desconectando.")
    client_socket.close()

if __name__ == "__main__":
    main()