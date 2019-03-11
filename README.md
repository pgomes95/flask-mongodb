# API REST Flask + MongoDB

## Objetivo

Criar uma simples API REST capaz de inserir, buscar e deletar países.  
Para cada país temos os campos: `name, terrain e climate`.  
Ao acessar o endpoint que retorna a lista de países, para cada país listado
é acrescentado a quantidade de aparições em filmes do Star Wars, e caso não seja
encontrado na [API do Star Wars](https://swapi.co/) é notificado no campo `obs` que o país não foi encontrado.

## Requisitos
* [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
* [pip3](https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/)
* [MongoDB](https://docs.mongodb.com/manual/administration/install-community/)

## Executando o projeto

Após instalar os requisitos é necessário startar o MongoDB.  
O próximo passo é executar o comando: `./startup.sh`,
ele vai setar as variáveis de ambiente, instalar as libs utilizadas no desenvolvimento do projeto e
por fim startar o servidor.  
O projeto roda na porta 5000, `http://127.0.0.1:5000/`.

## Endpoints

* __GET__
    * /get-planets
    * /get-planets?name=<planet_name>
    * /get-planets?id=<planet_id>
* __POST__
    * /add-planet
        ``` 
        {
            "name" : "Alderaan",
            "terrain" : "grasslands, mountains",
            "climate": "temperate"
        } 
        ```
* __DELETE__
    * /delete-planet/<planet_id>
