import socket 
import threading
import time

def processamento (connection, address):
    while True:
        msg = connection.recv(1024)

        if not msg:
            print("IJGWUGRHJG ODEIO REDES GJEWGUJWRGJWRUG")
            break
        
        print(msg.decode('utf-8'))
        print(f"Recebi uma ligação do cliente {address}")


    connection.close()

def main():    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    endereco = ''
    porta = 3333
    s.bind((endereco, porta))
    s.listen()


    print(f"Estou à escuta no {endereco}:{porta}")

    while True:
        connection, address = s.accept()

        threading.Thread(target=processamento,args=(connection, address)).start()
        

    s.close()


if __name__ == "__main__":
    main()