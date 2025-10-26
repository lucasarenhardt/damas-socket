import socket
import json

def enviar_mensagem(sock, tipo, dados):
    """Envia mensagem JSON com prefixo de tamanho (2 bytes)"""
    try:
        msg = json.dumps({"tipo": tipo, "dados": dados})
        msg_bytes = msg.encode('utf-8')
        prefix = len(msg_bytes).to_bytes(2, byteorder='big')
        sock.sendall(prefix + msg_bytes)
    except (ConnectionResetError, BrokenPipeError):
        print("Erro: Conexão com o servidor foi perdida.")

def recv_all(sock, n):
    """Recebe exatamente n bytes do socket"""
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
    """Recebe mensagem JSON com prefixo de tamanho"""
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
    """Função principal do cliente - conecta ao servidor e processa jogo"""
    HOST = '127.0.0.1'
    PORT = 50000

    # Conecta ao servidor
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print(f"\nConectado ao servidor de damas em {HOST}:{PORT}\n")
    except ConnectionRefusedError:
        print("Não foi possível se conectar ao servidor.")
        return

    # Recebe mensagem inicial
    msg_inicial = receber_mensagem(client_socket)
    if msg_inicial and msg_inicial["tipo"] == "info":
        print(msg_inicial["dados"])
    
    # Loop principal do jogo
    game_over = False
    while not game_over:
        mensagem = receber_mensagem(client_socket)

        if not mensagem:
            print("\nConexão perdida com o servidor.")
            break
            
        tipo = mensagem.get("tipo")
        dados = mensagem.get("dados")

        # Processa estado do jogo
        if tipo == "estado_jogo":
            print("\n" + ("-"*21))
            print(dados["tabuleiro"])
            print(dados["info"])
            
            # Se é o turno do cliente, solicita jogada
            if dados["sua_vez"]:
                jogada = input("Digite sua jogada: ")
                enviar_mensagem(client_socket, "jogada", jogada)
        
        # Processa erro na jogada
        elif tipo == "erro_jogada":
            print(f"ERRO: {dados} Tente novamente.")
            jogada = input("\nDigite sua jogada: ")
            enviar_mensagem(client_socket, "jogada", jogada)

        # Processa fim de jogo
        elif tipo == "fim_de_jogo":
            print(dados["tabuleiro"])
            print(f"\n{dados['mensagem']}")
            game_over = True
        
        else:
            print(dados)

    print("\nO jogo terminou. Desconectando.")
    client_socket.close()

if __name__ == "__main__":
    main()