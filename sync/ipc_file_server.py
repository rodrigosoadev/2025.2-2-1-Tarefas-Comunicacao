#!/usr/bin/env python3
import argparse
import hashlib
import os
import socket
import sys
import signal
import time
from pathlib import Path


def compute_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def secure_join(root: Path, rel_path: str) -> Path:
    # Evita absolutos e escapes com '..'
    candidate = (root / rel_path).resolve()
    root_resolved = root.resolve()
    if not str(candidate).startswith(str(root_resolved) + os.sep) and candidate != root_resolved:
        raise ValueError('Caminho fora do diretório raiz permitido')
    return candidate


def handle_client(conn: socket.socket, root: Path, chunk_size: int):
    f = conn.makefile('rwb')
    try:
        line = f.readline()
        if not line:
            return
        try:
            line_text = line.decode('utf-8', errors='strict').rstrip('\n')
        except UnicodeDecodeError:
            f.write(b"ERR Protocolo invalido\n")
            f.flush()
            return

        if not line_text.startswith('GET '):
            f.write(b"ERR Comando desconhecido\n")
            f.flush()
            return

        rel_path = line_text[4:].strip()
        print(f"Conexão estabelecida. Arquivo solicitado: {rel_path}")
        try:
            target = secure_join(root, rel_path)
        except ValueError as e:
            msg = str(e).replace('\n', ' ')
            f.write(f"ERR {msg}\n".encode('utf-8'))
            f.flush()
            return

        if not target.exists() or not target.is_file():
            f.write(b"ERR Arquivo inexistente\n")
            f.flush()
            return

        size = target.stat().st_size
        sha256 = compute_sha256(target)
        header = f"OK {size} {sha256}\n".encode('utf-8')
        f.write(header)
        f.flush()

        with target.open('rb') as rf:
            while True:
                buf = rf.read(chunk_size)
                time.sleep(0.05)
                if not buf:
                    break
                f.write(buf)
        f.flush()
        print(f"Conexão finalizada. Arquivo enviado: {rel_path}")

    finally:
        try:
            f.close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description='Servidor IPC para envio de arquivos (Unix domain socket)')
    parser.add_argument('--socket', default='/tmp/ipc_files.sock', help='Caminho do Unix socket')
    parser.add_argument('--root', default='shared', help='Diretório raiz de arquivos a serem servidos')
    parser.add_argument('--chunk-size', type=int, default=1024 * 64, help='Tamanho do bloco de envio em bytes')
    args = parser.parse_args()

    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)

    sock_path = Path(args.socket)

    # Remove socket antigo se existir
    if sock_path.exists():
        sock_path.unlink()

    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def cleanup_and_exit(signum=None, frame=None):
        try:
            srv.close()
        except Exception:
            pass
        try:
            if sock_path.exists():
                sock_path.unlink()
        except Exception:
            pass
        if signum is not None:
            sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    srv.bind(str(sock_path))
    # Permissões 660 para o socket
    try:
        os.chmod(str(sock_path), 0o660)
    except Exception:
        pass
    srv.listen(1)
    print(f"Servidor pronto. Raiz: {root.resolve()} | Socket: {sock_path}")
    try:
        while True:
            conn, _ = srv.accept()
            with conn:
                handle_client(conn, root, args.chunk_size)
    finally:
        cleanup_and_exit()


if __name__ == '__main__':
    main()
