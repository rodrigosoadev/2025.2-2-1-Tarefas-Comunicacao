#!/usr/bin/env python3
import argparse
import hashlib
import os
import socket
import sys
from pathlib import Path


def read_exact(f, size: int) -> bytes:
    chunks = []
    remaining = size
    while remaining > 0:
        chunk = f.read(remaining)
        if not chunk:
            raise EOFError('Conexão encerrada antes do término do arquivo')
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def main():
    parser = argparse.ArgumentParser(description='Cliente IPC para requisitar arquivos (Unix domain socket)')
    parser.add_argument('--socket', default='/tmp/ipc_files.sock', help='Caminho do Unix socket')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_get = sub.add_parser('get', help='Baixar um arquivo do servidor')
    p_get.add_argument('path', help='Caminho relativo do arquivo no servidor')
    p_get.add_argument('--out', help='Caminho de saída local (padrão: basename em cwd)')

    args = parser.parse_args()

    if args.cmd == 'get':
        rel_path = args.path
        out_path = Path(args.out) if args.out else Path(os.path.basename(rel_path))

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(args.socket)
        except FileNotFoundError:
            print(f"ERRO: socket não encontrado em {args.socket}. Inicie o servidor.", file=sys.stderr)
            sys.exit(1)

        f = sock.makefile('rwb')
        try:
            request = f"GET {rel_path}\n".encode('utf-8')
            f.write(request)
            f.flush()

            header = f.readline()
            if not header:
                print('ERRO: sem resposta do servidor', file=sys.stderr)
                sys.exit(1)
            try:
                header_txt = header.decode('utf-8').rstrip('\n')
            except UnicodeDecodeError:
                print('ERRO: resposta inválida do servidor', file=sys.stderr)
                sys.exit(1)

            if header_txt.startswith('ERR '):
                print(f"ERRO do servidor: {header_txt[4:]}", file=sys.stderr)
                sys.exit(1)

            parts = header_txt.split()
            if len(parts) != 3 or parts[0] != 'OK':
                print(f"ERRO: cabeçalho inesperado: {header_txt}", file=sys.stderr)
                sys.exit(1)
            try:
                size = int(parts[1])
            except ValueError:
                print('ERRO: tamanho inválido', file=sys.stderr)
                sys.exit(1)
            expected_sha = parts[2]

            data = read_exact(f, size)

            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open('wb') as wf:
                wf.write(data)

            got_sha = hashlib.sha256(data).hexdigest()
            if got_sha != expected_sha:
                print('AVISO: checksum divergente (arquivo salvo mesmo assim).', file=sys.stderr)
            else:
                print(f"OK: {rel_path} -> {out_path} ({size} bytes)")
        finally:
            try:
                f.close()
            except Exception:
                pass
            sock.close()


if __name__ == '__main__':
    main()
