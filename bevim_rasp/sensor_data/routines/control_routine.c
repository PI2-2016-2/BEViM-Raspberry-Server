#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <string.h>

// RESPONSE CODES
#define CONTROL_INTEGRATE_ERROR 500 
#define SUCCESS 200

void print_general_informations()
{
	printf("Universidade de Brasilia - UnB\n");
	printf("Faculdade UnB Gama - FGA\n");
	printf("Disciplina: Projeto Integrador 2 de Engenharia\n");
	printf("Rotina para envio de parâmetros ao Sistema de Controle\n\n");
}

int open_serial()
{
	int descriptor = open("/dev/ttyAMA0", O_RDWR | O_NOCTTY | O_NDELAY);
	if (descriptor == -1)
	{
		printf("Erro ao abrir a porta. Verifique se a porta nao esta ocupada.\n");
		printf("Response(%d) \n", CONTROL_INTEGRATE_ERROR);
		exit(1);
	}
	else {
		prepare_serial(descriptor);
		printf("Porta aberta com sucesso.\n\n");
		return descriptor;
	}
}

void close_serial(int descriptor)
{
	close(descriptor);
	printf("Porta fechada.\n");
}

int prepare_serial(int descriptor)
{
	struct termios options;
	tcgetattr(descriptor, &options);
	options.c_cflag = B9600 | CS8 | CLOCAL | CREAD;
	options.c_iflag = IGNPAR;
	options.c_oflag = 0;
	options.c_lflag = 0;
	tcflush(descriptor, TCIFLUSH);
	tcsetattr(descriptor, TCSANOW, &options);
}

int send_data(int descriptor, unsigned char *buffer, size_t bytes_number)
{
	int counter;
	counter = write(descriptor, buffer, bytes_number);
		if (counter < 0)
		{
			printf("Erro ao escrever dados na porta.\n");
			printf("Response(%d) \n", CONTROL_INTEGRATE_ERROR);
			exit(1);
		}
		else 
		{
			printf("Dados enviados (numero de bytes): %d.\n", counter);
		}
	return counter;
}

int main(int argc, char *argv[])
{
	int frequency_input;
	pid_t main_pid = getpid();

	print_general_informations();

	printf("PID deste processo: %d.\n\n", main_pid);

	if(argc <= 1)
	{
		printf("O valor da frequência de operação da bancada não foi passado.\n\n");
		exit(1);
	}
	else
	{
		frequency_input = atoi(argv[1]);
		printf("Frequência a ser enviada para o Sistema de Controle: %d.\n\n", frequency_input);
	}

	printf("Abrindo porta serial...\n");

	int descriptor_uart = open_serial();

	unsigned char transmission_buffer[256];

	memcpy(&transmission_buffer[0], &frequency_input, 4);

	send_data(descriptor_uart, transmission_buffer, 4);

	close_serial(descriptor_uart);

	printf("Frequencia enviada com sucesso para o Sistema de Controle.\n");
	printf("Response(%d) \n", SUCCESS);

	return 0;
}