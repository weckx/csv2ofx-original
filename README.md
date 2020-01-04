# csv2ofx-original

Script simples para converter arquivos CSV de extrato do Banco Original para o formato OFX.

## Dependências

O script utilizar a biblioteca [ofxtools](https://pypi.org/project/ofxtools/) para gerar o arquivo. Instalar seguindo
as instruções do site ou com o [pip](https://pypi.org/project/pip/) usando o comando:

   pip install ofxtools

## Uso

Para utilizar, simplesmente faça o clone ou download do repositório e execute o comando com:

```
python csv2ofx-original.py [arquivo csv]
```

O conteúdo do OFX será direcionado para a saída padrão. Para salvar num arquivo:

```
python csv2ofx-original.py [arquivo csv] > extrato.ofx
```


