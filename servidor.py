import socket
import threading
from urllib.parse import parse_qs

HOST = '192.168.10.158'
PORT = 8080

informacoes_por_ip = {}

def handle_client(client_socket, client_address):
    message = client_socket.recv(1024).decode('utf-8')
    print(f'Mensagem recebida pelo cliente: {client_address[0]}')
    print(message)

    response = handle_request(message, client_address[0])
    client_socket.sendall(response.encode('utf-8'))

    client_socket.close()

def adicionar_informacoes(ip, apelido):
    # Verifique se o endereço IP já existe no dicionário
    if ip not in informacoes_por_ip:
        # Se o endereço IP não existir, crie um novo dicionário para o endereço IP
        informacoes_por_ip[ip] = {'apelido': apelido, 'disciplinas': {}}

def adicionar_nota(ip, disciplina, pontuacao):
    # Verifique se o endereço IP existe no dicionário
    if ip in informacoes_por_ip:
        # Se a disciplina já existir, atualize a pontuação apenas se for maior do que a pontuação existente
        if disciplina in informacoes_por_ip[ip]['disciplinas']:
            if pontuacao > informacoes_por_ip[ip]['disciplinas'][disciplina]:
                informacoes_por_ip[ip]['disciplinas'][disciplina] = pontuacao
        else:
            # Se a disciplina não existir, adicione-a com a pontuação
            informacoes_por_ip[ip]['disciplinas'][disciplina] = pontuacao

def handle_request(request, client_address):
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

                apelido = params.get('nome',[None])[0]
                disciplina = params.get('disciplina', [None])[0]
                nota = params.get('nota', [None])[0] 

                if apelido is not None:
                    adicionar_informacoes(client_address, apelido)
                else:
                    adicionar_nota(client_address, disciplina, nota)


                if disciplina == 'R1main': 
                    filename = 'forms_R1.html'
                elif disciplina == 'R2main':
                    filename = 'forms_R2.html'
                elif disciplina == 'BDmain':
                    filename = 'forms_BD.html'
                elif disciplina == 'E1main':
                    filename = 'forms_E1.html'
                elif disciplina == 'Redes 1':
                    filename = 'pontuacoes.html'
                elif disciplina == 'Redes 2':
                    filename = 'pontuacoes.html'
                elif disciplina == 'Eletromagnetismo 1':
                    filename = 'pontuacoes.html'
                elif disciplina == 'Banco de dados':
                    filename = 'pontuacoes.html'

                resposta = 'HTTP/1.1 200 OK\n\nDados recebidos com sucesso!'

            else:
                resposta = 'HTTP/1.1 404 NOT FOUND\n\nFile Not Found!!!'
        else:

            if client_address not in informacoes_por_ip:
                if metodo == 'GET':
                    if caminho == '/':
                        filename = 'index.html'
                    elif caminho == '/index.css':
                        filename = 'index.css'
                    elif caminho == '/favicon.ico':
                        filename = 'favicon.ico'
            else:
                print('--------------- ENDERECO IP JA CADASTRADO ----------------')
                filename = 'pontuacoes.html'

    except IndexError:
        print('Posição inválida!')
    try:
        fin = open(filename)
        content = fin.read(-1)
        fin.close()

        print('INFORMACOOOOOOOES POR IP:::')
        print(informacoes_por_ip)

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