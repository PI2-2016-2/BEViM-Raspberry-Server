# BEViM-Raspberry-Parser e Comunicaçao

Repositório para as rotinas de Comunicação, Parser e Processamento dos dados Brutos provindos do Sistema de Controle da Bancada.

##Changelog
* Paulo E. S. Borba - 20/09 - Criação do Repositório
* Paulo E. S. Borba - 04/10 - Atualização do Parser e Adição da Rotina de Comunicação
* Paulo E. S. Borba - 07/10 - Protótipo Funcional do Parser em Funcionamento e a Rotina de comunicação das chegada dos dados completada

## Rotina de Parser - Protótipo Funcional

O arquivo parser.py é responsavel por fazer leitura dos dados provindos do módulo de comunicação, realizar a
criação das tabelas em SQLite, tratar os dados e importa-los no banco de dados. A proposta que está sendo
desenvolvida conta com o parser tendo acesso ao modo leitura na porta serial e lendo diretamente todos os dados
provindos da porta serial.

## Rotina de Comunicação - Completo

A rotina conta com o auxílio da biblioteca pyserial, que é responsável por abstrair funções de baixo para um alto
nível de manipulação de dados e controle. Esta rotina permite realizar a abertura da porta serial, receber, ler e
escrever dados provindos da outra parte a qual o hardware se comunica.

## Rotina de Processamento - A ser realizado

Os dados recebidos pela rotina de parser precisam se processados para se obter os dados derivados, que irão preencher
o banco de dados o qual será acessado pela aplicação Web. Esta rotina irá obter dados e irá retorna-los ao parser para que
esse possa realizar a escrita destes dados no banco de dados.