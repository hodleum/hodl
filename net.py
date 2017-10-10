import block
from socket import socket


port = 6666
sock_send = socket()
sock_listen = socket()

def listen():    # слушает, если что-то пришло, возвращает tuple (IP откуда пришло, адрес в системе того устройства, сообщение)
	sock.listen(1)
	conn, addr = sock.accept()
	data = conn.recv(4096)
	mess = ''
	addr = ''
	ip = ''
	flag = false
	for i in data :
		if flag == True :
			mess += i
		else :
			addr += i
	summary_tuple = (ip, addr, mess)
	return summary_tuple


def send(ip, mess, myaddr=''):    # отправляет сообщение на адрес ip, ничего не возвращает
    sock_send.connect((ip, port))
    sock_send.send(myaddr + " " + mess)


def is_my_ip_white():    # возвращает True/False белый ли IP устройства, на котором выполняется программа
    pass


def is_ip_white(ip):    # возвращает True/False, белый ли ip
    pass
