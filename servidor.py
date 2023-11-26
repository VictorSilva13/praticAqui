import socket
import threading
import json
from urllib.parse import parse_qs

HOST = '192.168.10.158'
PORT = 8080

informacoes_por_ip = {}


def gerar_html():
    #Converte o dicionário para JSON
    json_data = json.dumps(informacoes_por_ip, indent=2)

    #Aqui segue o conteúdo da página de pontuações (pontuacoes.html) gerado dinamicamente que irá conter as informações armazenadas em json_data
    html_content = f'''
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultados</title>
        <script>
            var informacoesPorIP = {json_data};   
        </script>
        <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f4f4f4;
            font-family: 'Arial', sans-serif; /* Substitua pela fonte desejada */
        }}

        .main-container {{
            width: 80%;
            margin: auto;
            text-align: center;
        }}

        .main-box {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-top: 20px;
        }}

        .input-subject {{
            margin-bottom: 20px;
        }}

        .btn, th, td {{
            width: 100%;
            height: 40px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
            transition: background-color 0.3s;
            font-weight: bold;
        }}

        .btn:hover {{
            background-color: #45a049;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background-color: #4CAF50;
            color: white;
        }}

        td {{
            background-color: white;
            color: black;
        }}
    </style>
    </head>
    <body>
        <div class="main-container">
        <h2>Dados por IP</h2>
        <table>
            <thead>
                <tr>
                    <th>IP</th>
                    <th>Apelido</th>
                    <th>Disciplinas</th>
                </tr>
            </thead>
            <tbody id="dadosPorIP">
                <!-- Os dados serão preenchidos dinamicamente aqui -->
            </tbody>
        </table>
        <div class="main-box">
            <h4 class="input-subject">Escolha a disciplina para praticar:</h4>
            <button class="btn" type="button" onclick="enviarOpcao('R1main')">Redes de Computadores 1</button>
            <button class="btn" type="button" onclick="enviarOpcao('R2main')">Redes de Computadores 2</button>
            <button class="btn" type="button" onclick="enviarOpcao('BDmain')">Banco de Dados</button>
            <button class="btn" type="button" onclick="enviarOpcao('E1main')">Eletromagnetismo 1</button>
        </div>
    </div>

        <script>
            // Adicione a lógica para preencher a tabela com os dados de informacoesPorIP
            var tabela = document.getElementById('dadosPorIP');
            for (var ip in informacoesPorIP) {{
                var tr = document.createElement('tr');

                var tdIp = document.createElement('td');
                tdIp.textContent = ip;
                tr.appendChild(tdIp);

                var tdApelido = document.createElement('td');
                tdApelido.textContent = informacoesPorIP[ip].apelido;
                tr.appendChild(tdApelido);

                var tdDisciplinas = document.createElement('td');
                var disciplinas = informacoesPorIP[ip].disciplinas;
                var disciplinasString = '';
                for (var disciplina in disciplinas) {{
                    disciplinasString += `${{disciplina}} - Nota: <strong>${{disciplinas[disciplina]}}</strong>/5, `;
                }}
                // Remova a última vírgula e espaço em branco
                disciplinasString = disciplinasString.slice(0, -2);
                tdDisciplinas.innerHTML = disciplinasString;
                tr.appendChild(tdDisciplinas);

                tabela.appendChild(tr);
            }}
        </script>
        <script>
            function enviarOpcao(disciplina){{
                var form = document.createElement('form');
            form.method = 'post';
            //form.action = '192.168.1.2:8080'; // Substitua pelo seu endereço de servidor

            var campoDisciplina = document.createElement('input');
            campoDisciplina.type = 'hidden';
            campoDisciplina.name = 'disciplina';
            campoDisciplina.value = disciplina;
            form.appendChild(campoDisciplina);

            // Adicionar formulário ao corpo do documento
            document.body.appendChild(form);

            // Enviar formulário
            form.submit();
            }}     
        </script>

    </body>
    </html>
    '''

    #Escreve o conteúdo acima no arquivo HTML
    with open('pontuacoes.html', 'w') as f:
        f.write(html_content)


def handle_client(client_socket, client_address):
    #Recebe a mensagem do cliente (até 1024 bytes) e a decodifica de bytes para string usando UTF-8
    message = client_socket.recv(1024).decode('utf-8')
    print(f'Mensagem recebida pelo cliente: {client_address[0]}')
    print(message)
    
    #Chama a função handle_request para processar a mensagem e obter uma resposta
    response = handle_request(message, client_address[0])

    #Envia a resposta de volta ao cliente, convertendo a string para bytes usando UTF-8
    client_socket.sendall(response.encode('utf-8'))
    
    #Fecha o socket de comunicação com o cliente
    client_socket.close()


def adicionar_informacoes(ip, apelido):
    #Verifica se o endereço IP já existe no dicionário
    if ip not in informacoes_por_ip:
        # Se o endereço IP não existir, cria um novo dicionário para o endereço IP
        informacoes_por_ip[ip] = {'apelido': apelido, 'disciplinas': {}}


def adicionar_nota(ip, disciplina, pontuacao):
    #Verifica se o endereço IP existe no dicionário
    if ip in informacoes_por_ip:
        #Se a disciplina já existir, atualiza a pontuação apenas se for maior do que a pontuação existente
        if disciplina in informacoes_por_ip[ip]['disciplinas']:
            if pontuacao > informacoes_por_ip[ip]['disciplinas'][disciplina]:
                informacoes_por_ip[ip]['disciplinas'][disciplina] = pontuacao
        else:
            #Se a disciplina não existir, adiciona com a pontuação
            informacoes_por_ip[ip]['disciplinas'][disciplina] = pontuacao

    #Atualiza a página de pontuações para exibir o resultado    
    gerar_html()


def handle_request(request, client_address):
     #Divide a requisição em cabeçalho e corpo usando a sequência '\r\n\r\n' como delimitador
    cabecalho, *corpo = request.split('\r\n\r\n', 1)
    
    #Divide o cabeçalho em partes usando espaços em branco como delimitador
    cabecalho = cabecalho.split(' ')
    #CABEÇALHO: ['GET', '/', 'HTTP/1.1\r\nHost:', '192.168.10.158:8080\r\nConnection:', ...]
    #CORPO: nome=augusto&disciplina=R1main ou  nota=4&disciplina=Redes+1

    metodo = cabecalho[0]
    caminho = cabecalho[1]

    try:
        if metodo == 'POST':
            if caminho == '/':
                #Se for uma requisição POST na raiz ('/'), obtém os dados do corpo da mensagem
                dados_corpo = corpo[0]

                #Parse dos parâmetros da URL no corpo da mensagem
                params = parse_qs(dados_corpo)
                #{'nome': ['Augusto'], 'disciplina': ['R1main']}
                

                #Obtém o apelido, disciplina e nota dos parâmetros
                apelido = params.get('nome', [None])[0]
                disciplina = params.get('disciplina', [None])[0]
                nota = params.get('nota', [None])[0]

                #Chama as funções adequadas com base nos parâmetros recebidos
                if apelido is not None:
                    adicionar_informacoes(client_address, apelido)
                else:
                    if nota is not None:
                        adicionar_nota(client_address, disciplina, nota)

                #Define o nome do arquivo que será aberto com base na disciplina e na etapa do sistema 
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
            #Se o método não for o POST, verifica se o endereço IP já está no dicionário e retorna a página inicial do sistema 
            if client_address not in informacoes_por_ip:
                if metodo == 'GET':
                    if caminho == '/':
                        filename = 'index.html'
                    elif caminho == '/index.css':
                        filename = 'index.css'
                    elif caminho == '/favicon.ico':
                        filename = 'favicon.ico'
            else:
                #Caso o endereço IP já possua um usuário cadastrado, ele não poderá mudar sua identificação novamente e só poderá acessar a página de pontuações e aos formulários
                filename = 'pontuacoes.html'

    except IndexError:
        print('Posição inválida!')


    try:
        #Tenta abrir o arquivo pelo nome
        fin = open(filename)

        #Lê todo o conteúdo do arquivo
        content = fin.read(-1)

        #Fecha o arquivo
        fin.close()

        resposta = 'HTTP/1.1 200 OK\n\n' + content

    except FileNotFoundError:
        #Se o arquivo não for encontrado, cria uma resposta com o código 404 Not Found
        resposta = 'HTTP/1.1 404 NOT FOUND\n\nFile Not Found!!!'

    return resposta


try:
    # Aqui será chamada uma função que inicialmente “zera” o dicionário atribuido como informacoes_por_ip que veremos no futuro.
    gerar_html()

    #Os parâmetros para o método abaixo são: (Família de protocolo, Tipo de protocolo)
    #AF_INET => IP ; SOCK_STREAM => TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Para associar o socket no endereço e porta declarados => .bind((endereço, porta))
    s.bind((HOST, PORT))
    
    #Deixa o socket em modo de escuta, à procura de conexões 
    s.listen()

    print('Aguardando conexões...')

    while True:
         #Quando um cliente se conectar, ele deve retornar seu endereço e um socket para comunicação
        (communication_socket, address) = s.accept()

        print(f'Conectado em: {address}')

        #Cria uma nova thread para lidar com o cliente usando a função handle_client, passando o socket de comunicação (communication_socket) e o endereço do cliente (address) como argumentos.
        client_thread = threading.Thread(
            target=handle_client, args=(communication_socket, address))
        
        #Inicia a execução da thread criada para lidar com o cliente.
        client_thread.start()


except KeyboardInterrupt:
    print('Servidor fechado!')
    s.close()
