# Diagrama de Comunicação - Jogo de Damas Socket

## Arquitetura Geral

```
┌─────────────────┐                    ┌─────────────────┐
│    SERVIDOR     │                    │     CLIENTE     │
│  (Pretas 'x')   │◄──────────────────►│  (Brancas 'o')  │
│  127.0.0.1      │    TCP/IP Socket   │                 │
│  Porta: 50002   │                    │                 │
└─────────────────┘                    └─────────────────┘
```

## Protocolo de Mensagens

Todas as mensagens são enviadas no formato JSON com prefixo de tamanho:

```
┌──────────────┬────────────────────────────────┐
│  2 bytes     │  N bytes                       │
│  (tamanho)   │  JSON payload                  │
├──────────────┼────────────────────────────────┤
│  Big-endian  │  {"tipo": "...", "dados": ...} │
└──────────────┴────────────────────────────────┘
```

## Tipos de Mensagens

### 1. **info** (Servidor → Cliente)
Mensagem informativa inicial
```json
{
  "tipo": "info",
  "dados": "Você é o Jogador Cliente (Brancas 'o'). Você começa."
}
```

### 2. **estado_jogo** (Servidor → Cliente)
Estado atual do tabuleiro e turno
```json
{
  "tipo": "estado_jogo",
  "dados": {
    "tabuleiro": "...",
    "sua_vez": true/false,
    "info": "Sua vez de jogar." ou "Turno do Jogador Servidor. Aguardando jogada..."
  }
}
```

### 3. **jogada** (Cliente → Servidor)
Jogada do cliente
```json
{
  "tipo": "jogada",
  "dados": "2,3 3,4"
}
```

### 4. **erro_jogada** (Servidor → Cliente)
Notificação de erro na jogada
```json
{
  "tipo": "erro_jogada",
  "dados": "A peça selecionada não pertence ao jogador atual."
}
```

### 5. **fim_de_jogo** (Servidor → Cliente)
Finalização do jogo
```json
{
  "tipo": "fim_de_jogo",
  "dados": {
    "tabuleiro": "...",
    "mensagem": "FIM DE JOGO! O vencedor é ..."
  }
}
```

## Fluxo de Comunicação Completo

```
SERVIDOR                                          CLIENTE
   │                                                 │
   │ 1. Inicia servidor (127.0.0.1:50002)          │
   │    aguarda conexão                             │
   │                                                 │
   │◄────────────── 2. Conecta ─────────────────────│
   │                                                 │
   │──────── 3. info: "Você é Brancas" ────────────►│
   │                                                 │
   │──── 4. estado_jogo (sua_vez=true) ────────────►│
   │                                                 │  Exibe tabuleiro
   │                                                 │  Solicita jogada
   │                                                 │
   │◄───────── 5. jogada: "2,3 3,4" ────────────────│
   │                                                 │
   │  Valida movimento                               │
   │  Atualiza tabuleiro                             │
   │                                                 │
   ├─ Se erro: ───────────────────────────────────► │
   │  erro_jogada: "mensagem de erro"                │
   │◄───────── jogada: "nova tentativa" ────────────│
   │                                                 │
   │  Troca turno                                    │
   │                                                 │
   │─── 6. estado_jogo (sua_vez=false) ────────────►│
   │                                                 │  Aguarda jogada servidor
   │                                                 │
   │  Exibe tabuleiro                                │
   │  Solicita jogada local                          │
   │  Executa movimento                              │
   │  Atualiza tabuleiro                             │
   │  Exibe tabuleiro atualizado                     │
   │  Troca turno                                    │
   │                                                 │
   │──── 7. estado_jogo (sua_vez=true) ────────────►│
   │                                                 │
   │◄───────── 8. jogada: "4,5 5,6" ────────────────│
   │                                                 │
   │  ... Repete ciclo até fim de jogo ...          │
   │                                                 │
   │  Detecta condição de vitória                    │
   │                                                 │
   │────── 9. fim_de_jogo + resultado ─────────────►│
   │                                                 │  Exibe resultado
   │                                                 │  Encerra
   │  Fecha conexão                                  │
   │◄────────────── Desconecta ─────────────────────│
   │                                                 │
   ✕ Encerra                                        ✕
```

## Ciclo de Turnos Detalhado

### Turno do Cliente (Brancas 'o')

```
SERVIDOR                                          CLIENTE
   │                                                 │
   │─── estado_jogo (sua_vez=true) ────────────────►│
   │    - tabuleiro atual                            │
   │    - info: "Sua vez de jogar."                  │
   │                                                 │
   │                                                 ├─► Exibe tabuleiro
   │                                                 ├─► Solicita input
   │                                                 │
   │◄────────── jogada: "origem destino" ───────────│
   │                                                 │
   ├─► Valida jogada                                 │
   │   - Verifica se peça pertence ao jogador        │
   │   - Verifica se movimento é válido              │
   │   - Executa movimento                           │
   │   - Verifica capturas                           │
   │                                                 │
   │   Se INVÁLIDA:                                  │
   │─────── erro_jogada: "mensagem" ────────────────►│
   │                                                 ├─► Exibe erro
   │                                                 ├─► Solicita nova jogada
   │◄──────── jogada: "nova tentativa" ─────────────│
   │                                                 │
   │   Se VÁLIDA:                                    │
   ├─► Atualiza tabuleiro                            │
   ├─► Verifica vitória                              │
   ├─► Troca turno                                   │
   │                                                 │
```

### Turno do Servidor (Pretas 'x')

```
SERVIDOR                                          CLIENTE
   │                                                 │
   ├─► Exibe tabuleiro                               │
   ├─► Solicita input local                          │
   │                                                 │
   │─── estado_jogo (sua_vez=false) ───────────────►│
   │    - info: "Turno do Jogador Servidor..."       │
   │                                                 │
   │                                                 ├─► Exibe mensagem
   │                                                 ├─► Aguarda
   │                                                 │
   ├─► Input: "origem destino"                       │
   ├─► Valida jogada                                 │
   ├─► Executa movimento                             │
   ├─► Exibe tabuleiro atualizado                    │
   ├─► Verifica vitória                              │
   ├─► Troca turno                                   │
   │                                                 │
```

## Tratamento de Erros

### Desconexão do Cliente
```
SERVIDOR                                          CLIENTE
   │                                                 │
   │  Aguarda mensagem do cliente                    │
   │◄─────────────── ✕ Desconecta ──────────────────│
   │                                                 
   ├─► receber_mensagem() retorna None              
   ├─► "Cliente desconectado. Fim de jogo."         
   ├─► Servidor vence por W.O.                       
   │                                                 
   ✕ Encerra                                        
```

### Erro de Validação de Jogada
```
SERVIDOR                                          CLIENTE
   │                                                 │
   │◄────────── jogada: "3,2 4,3" ──────────────────│
   │                                                 │
   ├─► validar_e_mover() retorna erro               │
   │   "A peça selecionada não pertence              │
   │    ao jogador atual."                           │
   │                                                 │
   │────── erro_jogada: "mensagem" ─────────────────►│
   │                                                 │
   │                                                 ├─► Exibe erro
   │                                                 ├─► Solicita nova jogada
   │                                                 │
   │◄────────── jogada: "2,3 3,4" ──────────────────│
   │                                                 │
   ├─► Valida novamente                              │
   │   ... movimento válido ...                      │
   │                                                 │
```

### Formato de Entrada Inválido
```
SERVIDOR/CLIENTE
   │
   ├─► Input: "abc def"
   ├─► ValueError/IndexError na conversão
   ├─► "ERRO: Formato de entrada inválido."
   ├─► Solicita nova entrada
   │
```

## Condições de Término

1. **Vitória por Captura**: Um jogador captura todas as peças adversárias
2. **Vitória por Bloqueio**: Um jogador não tem movimentos válidos
3. **Empate**: Ambos os jogadores sem movimentos válidos
4. **Desconexão**: Cliente desconecta (servidor vence por W.O.)

## Notas Técnicas

### Protocolo de Tamanho Prefixado
- Evita problemas de fragmentação TCP
- Garante leitura completa da mensagem
- 2 bytes permitem mensagens até 65KB

### Codificação
- JSON para estruturação de dados
- UTF-8 para encoding de strings
- Big-endian para prefixo de tamanho

### Tratamento de Erros
- ConnectionResetError: Detecta desconexões abruptas
- BrokenPipeError: Detecta tentativas de escrita em socket fechado
- JSONDecodeError: Detecta mensagens corrompidas

### Estado do Jogo
- Mantido apenas no servidor
- Cliente recebe atualizações via mensagens
- Validação de jogadas ocorre no servidor
