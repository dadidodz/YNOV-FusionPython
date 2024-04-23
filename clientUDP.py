import socket

def send_message(pseudo):
    SERVER_HOST = '10.34.0.248'
    SERVER_PORT = 12345   
    message = f"Pseudo: {pseudo}"
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print("Réponse du serveur:", response.decode())
    client_socket.close()

