# Presente!

O **Presente!** é um sistema open source para gerenciamento de frequência em atividades extra-classe no IFRN.
Professores e gestores podem cadastrar atividades ou eventos, e os participantes registram sua presença por meio de QR Codes ou códigos em texto.

O sistema utiliza o **SUAP** para autenticação e identificação automática das turmas, permitindo a geração de relatórios de frequência de forma integrada.

---

## Funcionalidades

* Registro de atividades extra-classe autorizadas pelo professor.
* Registro de presença pelos próprios participantes, por meio de QR-Code.
* Validação automática ou manual da presença pelo administrador.
* Mecanismos para prevenção de fraudes:
    * QR-Code/código de verificação dinâmico com tempo de atualização configurável;
    * Registro de IP e *timestamp* no momento do registro;
    * Possibilidade de restringir o acesso à rede local do campus.
* Autenticação via SUAP, com identificação automática dos participantes.
* Geração de relatórios de frequência e participação com filtros por curso, turma, turno, etc.
* Interface simples e objetiva.

---

## Integração com o SUAP

O sistema utiliza a **API do SUAP** para:

* Autenticação institucional.
* Importação de dados de turmas, diários e alunos.

> Para utilizar a integração, é necessário configurar credenciais de acesso à API do SUAP fornecidas pela instituição.

---

## Instalação e uso

1. Clone o repositório:

   ```bash
   git clone https://github.com/IFRN-SPP/presente.git
   cd presente
   ```

2. Configure o ambiente (Python/Django):

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Defina as variáveis de ambiente no arquivo `.env`, usando o arquivo `.env.example` como modelo:

   ```
   SUAP_API_URL=https://suap.ifrn.edu.br/api/
   SUAP_CLIENT_ID=xxxx
   SUAP_CLIENT_SECRET=yyyy
   etc...
   ```

4. Execute as migrações e inicie o servidor:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Acesse o sistema em: [http://localhost:8000](http://localhost:8000)

---

## Contribuição

O projeto é aberto a contribuições.

* Faça um fork do repositório.
* Crie uma branch para sua modificação.
* Envie um pull request com a descrição das alterações.

---

## Licença

Distribuído sob a licença **MIT**. Veja `LICENSE` para mais informações.
