import socket
import threading
from urllib.parse import parse_qs

HOST = '192.168.10.158'
PORT = 8080


def handle_client(client_socket, client_address):
    message = client_socket.recv(1024).decode('utf-8')
    print(f'Mensagem recebida pelo cliente: {client_address}')
    print(message)

    response = handle_request(message)
    client_socket.sendall(response.encode('utf-8'))

    client_socket.close()



def handle_request(request):
    """Trata da requisição"""
    cabecalho, *corpo = request.split('\r\n\r\n', 1)
    cabecalho = cabecalho.split(' ')
    metodo = cabecalho[0]
    caminho = cabecalho[1]

    print("CABECALHO:::")
    print(cabecalho)

    try:
        if metodo == 'POST':
            if caminho == '/':
                # Verificar se é uma requisição POST para a raiz ('/')
                dados_corpo = corpo[0]
                print("DADOS DO CORPO:::")
                print(dados_corpo)
                #nome=augusto&disciplina=R2
                #nota=4
                
                # Parse dos parâmetros da URL
                params = parse_qs(dados_corpo)

                # Obter o valor associado à chave 'disciplina' ou 'nota' 
                retorno_chave = params.get('disciplina', [params.get('nota', ['error'])[0]])[0]

                if retorno_chave == 'R1': 
                    filename = 'forms_R1.html'
                elif retorno_chave == 'R2':
                    filename = 'forms_R2.html'
                elif retorno_chave == 'BD':
                    filename = 'forms_BD.html'
                elif retorno_chave == 'E1':
                    filename = 'forms_E1.html'
                else:
                    filename = 'index.html'

                resposta = 'HTTP/1.1 200 OK\n\nDados recebidos com sucesso!'

            else:
                resposta = 'HTTP/1.1 404 NOT FOUND\n\nFile Not Found!!!'
        else:
            if metodo == 'GET':
                if caminho == '/':
                    filename = 'index.html'
                elif caminho == '/index.css':
                    filename = 'index.css'
                elif caminho == '/favicon.ico':
                    filename = 'favicon.ico'
    except IndexError:
        print('Posição inválida!')
    try:
        fin = open(filename)
        content = fin.read(-1)
        fin.close()

        resposta = 'HTTP/1.1 200 OK\n\n' + content
    except FileNotFoundError:
        resposta = 'HTTP/1.1 404 NOT FOUND\n\nFile Not Found!!!'

    return resposta

    
try:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((HOST, PORT))

    s.listen()


    print('Aguardando conexões...')

    while True:
        (communication_socket, address) = s.accept()

        print(f'Conectado em: {address}')

        client_thread = threading.Thread(
            target=handle_client, args=(communication_socket, address))
        client_thread.start()


except KeyboardInterrupt:
    print('Servidor fechado!')
    s.close()