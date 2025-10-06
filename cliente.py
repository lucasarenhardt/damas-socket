# cliente_damas.py

import socket
import json

def enviar_mensagem(sock, tipo, dados):
    """Codifica e envia uma mensagem JSON com prefixo de 2 bytes (big-endian)."""
    try:
        msg = json.dumps({"tipo": tipo, "dados": dados})
        msg_bytes = msg.encode('utf-8')
        prefix = len(msg_bytes).to_bytes(2, byteorder='big')  # 2 bytes big-endian
        sock.sendall(prefix + msg_bytes)
    except (ConnectionResetError, BrokenPipeError):
        print("Erro: Conexão com o servidor foi perdida.")

def recv_all(sock, n):
    """Lê exatamente n bytes do socket ou retorna None se a conexão fechar."""
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
    """Recebe, decodifica e retorna uma mensagem JSON lendo primeiro 2 bytes de tamanho."""
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
    HOST = '127.0.0.1'
    PORT = 5000  # ajustado para corresponder ao servidor

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