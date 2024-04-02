import requests
from cryptography.fernet import Fernet

# Substitua isso pela sua chave de criptografia real
key = '-cFe-4twR3G_uml6mn8ZiAuZm9lIMCPig3n9YpqnU9o='
cipher_suite = Fernet(key)

def decrypt_file(encrypted_file_path, decrypted_file_path):
    # Ler o conteúdo criptografado do arquivo
    with open(encrypted_file_path, 'rb') as file:
        encrypted_data = file.read()

    # Descriptografar os dados
    decrypted_data = cipher_suite.decrypt(encrypted_data)

    # Salvar o arquivo descriptografado
    with open(decrypted_file_path, 'wb') as file:
        file.write(decrypted_data)
        
# Hash do arquivo que você quer baixar do IPFS
file_hash = 'QmZkrGwnu3yPA24ycHYW9jRJT4HLdiNuBkNP96v8r8LDqd'

# URL do gateway IPFS público
url = f'http://127.0.0.1:5001/api/v0/cat?arg={file_hash}'

# Fazendo a requisição para baixar o arquivo
response = requests.post(url)

# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    # Salvando o arquivo baixado, substitua 'nome_do_arquivo' pelo nome que deseja salvar
    with open('client.enc', 'wb') as f:
        f.write(response.content)
    print('Arquivo baixado com sucesso.')
else:
    print('Erro ao baixar o arquivo.')
    
# Caminho do arquivo criptografado
encrypted_file_path = './client.enc'

# Caminho onde o arquivo descriptografado será salvo
decrypted_file_path = './client_uncrypted.mat'

# Descriptografar o arquivo
decrypt_file(encrypted_file_path, decrypted_file_path)