# Relato da atividade de comunicação entre processos usando sockets

## Informações gerais

- **Disciplina**: Sistemas operacionais

- **Semestre letivo**: 2025.2
- **Aluno**: Rodrigo soares da camara

## Sumário

- [**Parte 1 - 1 servidor e 1 cliente (bloqueante)**](#parte-1--1-servidor-e-1-cliente-bloqueante)

- [**Parte 2 — 1 servidor e 2 clientes (bloqueante)**](#parte-2--1-servidor-e-2-clientes-bloqueante)
- [**Parte 3 — Modificar o servidor para múltiplos clientes**](#parte-3--modificar-o-servidor-para-múltiplos-clientes)
- [**Parte 4 — 1 servidor (concorrente) e 2 clientes**](#parte-4--1-servidor-concorrente-e-2-clientes)

## Parte 1 — 1 servidor e 1 cliente (bloqueante)

### Servidor iniciando e aguardando conexão

```bash
(virtual) PS C:\Users\20242014040005\Documents\ws-so\2025.2-2-1-Tarefas-Comunicacao> python src/servidor.py 
Servidor Echo escutando em localhost:5000

Aguardando conexão...
```

### Cliente se conectando com o Servidor

- **Cliente**

```bash
(virtual) PS C:\Users\20242014040005\Documents\ws-so\2025.2-2-1-Tarefas-Comunicacao> python src/cliente.py  
Conectado ao servidor Echo
Digite "sair" para encerrar a conexão

Digite uma mensagem:   
```

- **Servidor**

```bash
Conectado com ('127.0.0.1', 60257)
```

### Troca de mensagens

- **Cliente**

```bash
Digite "sair" para encerrar a conexão

Digite uma mensagem: oi
Resposta: Echo: oi
```

- **Servidor**

```bash
Recebido: oi
```

### Conexão encerrada limpidamente

- **Cliente**

```bash
Digite uma mensagem: sair
Conexão encerrada
(virtual) PS C:\Users\20242014040005\Documents\ws-so\2025.2-2-1-Tarefas-Comunicacao> 
```

- **Servidor**

```bash
Cliente desconectou

Aguardando conexão...
```

### Observação

O cliente envia uma mensagem e espera recebâ-la de volta através de uma resposta echo e o servidor espera receber uma mensagem do cliente e retorná-la para confirmar o êxito da tarefa.

## Parte 2 — 1 servidor e 2 clientes (bloqueante)

### Apenas um cliente é atendido por vez

- **Cliente 1**

```bash
(virtual) PS C:\Userspython src/cliente.py                      
Conectado ao servidor Echo
Digite "sair" para encerrar a conexão

Digite uma mensagem:
```

- **Cliente 2**

```bash
(virtual) PS C:\Users\20242014040005\Documents\ws-so\2025.2-2-1-Tarefas-Comunicacao> python src/cliente.py                      
Conectado ao servidor Echo
Digite "sair" para encerrar a conexão

Digite uma mensagem: 
```

- **Servidor**

```bash
(virtual) PS C:\Userspython src/servidor.py                     
Servidor Echo escutando em localhost:5000

Aguardando conexão...
Conectado com ('127.0.0.1', 65300)
```

### O Servidor continua responsivo após atender o primeiro cliente

- **Cliente 1**

```bash
Digite uma mensagem: eai
Resposta: Echo: eai

Digite uma mensagem: sair
Conexão encerrada
```

- **Cliente 2**

```bash
Digite uma mensagem: me atende mano
Resposta: Echo: me atende mano

Digite uma mensagem: 
```

- **Servidor**

```bash
Recebido: eai
Cliente desconectou

Aguardando conexão...
Conectado com ('127.0.0.1', 65302)
Recebido: me atende mano
```

### Registrando timestamps das conexões estabelecidas

```bash
(virtual) PS C:\Users\20242014040005\Documents\ws-so\2025.2-2-1-Tarefas-Comunicacao> python src/servidor.py                     
Servidor Echo escutando em localhost:5000

Aguardando conexão...
Conectado com ('127.0.0.1', 64337) em 2025-12-01 13:48:04.416018
Recebido: opa
Recebido: eai
Recebido: tudo bem
Recebido: vou sair
Cliente desconectou em 2025-12-01 13:48:22.589291

Aguardando conexão...
Conectado com ('127.0.0.1', 58529) em 2025-12-01 13:48:45.403075
Recebido: minha vez
Recebido: registrando nossa conversa...
Recebido: .
Recebido: vou sair
Cliente desconectou em 2025-12-01 13:49:16.720797
```

### Servidor respondendo o outro cliente após o primeiro se desconectar

- **Cliente 1**

```bash
(virtual) PS C:\Users\20242014040005\Documents\ws-so\2025.2-2-1-Tarefas-Comunicacao> python src/cliente.py
Conectado ao servidor Echo
Digite "sair" para encerrar a conexão

Digite uma mensagem: eai
Resposta: Echo: eai

Digite uma mensagem: responda meu amigo
Resposta: Echo: responda meu amigo

Digite uma mensagem: sair
Conexão encerrada
```

- **Cliente 2 (considere que esse cliente mandou a mensagem quase que ao mesmo tempo que o primeiro cliente e compare o tempo em que foi enviado com o recebido)**

```bash
(virtual) PS C:\Users\20242014040005\Documents\ws-so\2025.2-2-1-Tarefas-Comunicacao> python src/cliente.py                      
Conectado ao servidor Echo
Digite "sair" para encerrar a conexão

Digite uma mensagem: oi
Resposta: Echo: oi

Digite uma mensagem: sair
Conexão encerrada
```

- **Servidor**

```bash
Conectado com ('127.0.0.1', 60282) em 2025-12-01 13:51:40.732500
Recebido: eai
Recebido: responda meu amigo
Cliente desconectou em 2025-12-01 13:52:08.624542

Aguardando conexão...
Conectado com ('127.0.0.1', 60284) em 2025-12-01 13:52:08.626783
Recebido: oi
Cliente desconectou em 2025-12-01 13:52:15.031739
```

### Observações

- Pequena modificação no código do servidor para registrar os timestamps

```bash
import socket
# Import de marcação de data e tempo
from datetime import datetime

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind(('localhost', 5000))
servidor.listen(1)
print('Servidor Echo escutando em localhost:5000')

while True:
    print('\nAguardando conexão...')
    conexao, endereco = servidor.accept()
    # Adição do registro do momento que o servidor se conecta com o cliente
    print(f'Conectado com {endereco} em {datetime.today()}')
    
    try:
        while True:
            # Receber dados
            dados = conexao.recv(1024)
            
            if not dados:
                # Registro do momento que o cliente se desconecta com o servidor
                print(f'Cliente desconectou em {datetime.today()}')
                break
                
            mensagem = dados.decode('utf-8')
            print(f'Recebido: {mensagem}')
            
            # Enviar dados de volta (echo)
            resposta = f'Echo: {mensagem}'
            conexao.send(resposta.encode('utf-8'))
            
    finally:
        conexao.close()
```

- O servidor responde normalmente ao primeiro cliente conectado mas não dá nenhum devolutiva ao outro que tenta mandar mensagem, simplesmente após o primeiro se desconectar que a mensagem chega e o servidor retorna o echo

## Parte 3 — Modificar o servidor para múltiplos clientes

FIXME seu relato

## Parte 4 — 1 servidor (concorrente) e 2 clientes

FIXME seu relato