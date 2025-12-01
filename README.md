# 2025.2-2-1-Tarefas-Comunicacao

## Checklist inicial

- [ ] fork desse repositório
- [ ] criar um arquivo `/relatorio.md` para relatar o que se pede abaixo

```md
# Relato da atividade de comunicação entre processo usando sockets

## Informações gerais
- **disciplina**: Sistemas operacionais
- **semestre letivo**: 2025.2
- **aluno**: FIXME seu nome

## Parte 1 — 1 servidor e 1 cliente (bloqueante)
FIXME seu relato

## Parte 2 — 1 servidor e 2 clientes (bloqueante)
FIXME seu relato

## Parte 3 — Modificar o servidor para múltiplos clientes
FIXME seu relato

## Parte 4 — 1 servidor (concorrente) e 2 clientes
FIXME seu relato


```

## Atividade: Cliente/Servidor (bloqueante → concorrente)

Esta atividade usa os arquivos `src/servidor.py` e `src/cliente.py` para explorar comunicação direta (bloqueante) 1:1 e, em seguida, evoluir o servidor para aceitar múltiplos clientes.

Observação: os comandos abaixo usam `python3 src/servidor.py` e `python3 src/cliente.py` sem parâmetros, pois a interface exata pode variar. Caso seus programas exijam argumentos, adapte os comandos conforme a sua implementação (ex.: porta, caminho de socket, mensagem, etc.).

### Parte 1 — 1 servidor e 1 cliente (bloqueante)

Objetivo: executar e validar o funcionamento básico 1:1.

Comandos (dois terminais):

```bash
# Terminal A — servidor
python3 src/servidor.py

# Terminal B — cliente (ajuste argumentos se necessário)
python3 src/cliente.py
```

Checklist (marque ao validar):

- [ ] Servidor inicia sem erros e fica aguardando conexão.
- [ ] Cliente consegue conectar ao servidor.
- [ ] Há troca de mensagem/serviço concluída com sucesso (ex.: resposta do servidor exibida).
- [ ] Conexões são encerradas limpidamente (sem stack traces inesperados).
- [ ] Descreva brevemente a interação observada (o que o cliente pediu e o que o servidor retornou).

Critérios de aceitação:

- Servidor permanece estável após o término do cliente; nenhuma exceção não tratada.
- Cliente finaliza com código de saída 0 e saída coerente (mensagens esperadas).

### Parte 2 — 1 servidor e 2 clientes (bloqueante)

Objetivo: observar o comportamento do servidor atual quando dois clientes tentam usar o serviço (quase) ao mesmo tempo.

Comandos (três terminais):

```bash
# Terminal A — servidor
python3 src/servidor.py

# Terminal B — cliente 1
python3 src/cliente.py

# Terminal C — cliente 2 (dispare próximo do cliente 1)
python3 src/cliente.py
```

Checklist de observação:

- [ ] Apenas um cliente é atendido por vez (o outro aguarda/bloqueia) OU ocorre erro de conexão para o segundo.
- [ ] O servidor continua responsivo após atender o primeiro cliente.
- [ ] O segundo cliente eventualmente é atendido ou recebe erro consistente (ex.: timeout, recusa, protocolo).
- [ ] Registre timestamps (ou ordem) de início/fim de cada cliente para evidenciar serialização/bloqueio.
- [ ] Anote logs/prints relevantes do servidor (ex.: "aceitei conexão de ...").

Perguntas para relatório:

- O segundo cliente bloqueou? Por quanto tempo? Houve recusa imediata?
- O servidor atende estritamente em série? O que evidencia isso?

### Parte 3 — Modificar o servidor para múltiplos clientes

Objetivo: tornar o servidor concorrente, aceitando e atendendo múltiplos clientes em paralelo.

Requisito mínimo: manter o mesmo protocolo/contrato entre cliente-servidor; apenas a concorrência muda.

Estratégias sugeridas (escolha uma):

- Threads: para cada conexão aceita, criar uma `Thread` que executa `handle_client(conn, addr)` e o laço principal volta ao `accept()` imediatamente.
- Multiplexação (`select`/`selectors`): laço único que monitora múltiplos sockets não bloqueantes.
- Assíncrono (`asyncio`): transformar o servidor em corrotinas com `async/await`.

Pontos de atenção (checklist de implementação):

- [ ] O `accept()` não bloqueia o atendimento de novos clientes (ex.: thread por conexão ou não-bloqueante com `select`).
- [ ] Tratamento robusto de exceções em cada conexão para não derrubar o servidor.
- [ ] Fechamento correto de sockets em todos os caminhos (sucesso/erro).
- [ ] Se houver recursos compartilhados (ex.: arquivo/log), proteger com `Lock` ou usar filas.
- [ ] Logs claros: conexão iniciada, processando, finalizada (com identificação do cliente).
- [ ] Encerramento gracioso (opcional): sinal para fechar, parar de aceitar, aguardar workers.

Critérios de aceitação:

- Dois (ou mais) clientes podem ser atendidos sobrepostos no tempo (paralelismo observável por timestamps/sleeps).
- O servidor permanece estável sob conexões simultâneas e após desconexões abruptas.

Sugestão prática para evidenciar paralelismo:

- Introduza um `sleep` curto (ex.: 2–3s) dentro do tratamento de cada cliente. Se dois clientes terminarem quase ao mesmo tempo, seu servidor está concorrente; se terminarem estritamente em sequência, ainda está serial.

### Parte 4 — 1 servidor (concorrente) e 2 clientes

Objetivo: validar a nova versão concorrente do servidor.

Comandos (três terminais):

```bash
# Terminal A — servidor concorrente (após sua modificação)
python3 src/servidor.py

# Terminal B — cliente 1
python3 src/cliente.py

# Terminal C — cliente 2 (dispare quase junto do cliente 1)
python3 src/cliente.py
```

Checklist de validação:

- [ ] Ambos os clientes iniciam, conectam e recebem respostas sem bloquear um ao outro.
- [ ] Timestamps mostram processamento sobreposto (ex.: início próximo e término próximo se houver `sleep`).
- [ ] O servidor registra múltiplas conexões ativas simultaneamente.
- [ ] Não há exceções não tratadas; sockets são fechados corretamente.

Entrega sugerida (relatório curto):

- Capturas de tela/prints dos três cenários (Partes 1, 2 e 4) com timestamps.
- Breve descrição das mudanças feitas na Parte 3 (abordagem escolhida e por quê).
- Conclusões: diferenças entre modelo bloqueante 1:1 e versão concorrente; trade-offs da técnica adotada (threads vs. `select` vs. `asyncio`).
