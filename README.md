<img src="static/img/presente-icon.svg" alt="Presente!" width="80">

# Presente!

Sistema open source para gerenciamento de presença em atividades extra-classe do IFRN. Professores e gestores cadastram atividades, e os participantes registram presença através de QR Codes dinâmicos.

Utiliza o **SUAP** para autenticação institucional e identificação dos participantes, com geração de relatórios integrada.

---

## Funcionalidades

### Atividades
* CRUD completo com suporte a múltiplos responsáveis
* Controle automático de status (não iniciada, ativa, encerrada)
* Página pública com QR Code para registro de presença
* Sincronização de tempo com o servidor
* Recarregamento automático da interface ao término

### Presença
* Registro via QR Code dinâmico ou link direto
* QR Codes com renovação configurável (padrão: 30 segundos)
* Tokens com validação de expiração
* Histórico completo por atividade e por usuário
* Contadores em tempo real

### Segurança
* Restrição por endereço IP ou faixa de rede (CIDR)
* Gerenciamento de redes permitidas (superusuários)
* Registro de IP e timestamp em cada marcação
* Sincronização de relógio cliente-servidor para prevenir manipulação

### Relatórios
* Filtros por nome, tipo de usuário, curso e período
* Seleção de colunas para impressão
* Ordenação customizável
* Formato otimizado para impressão física

### Interface
* Design responsivo (Bootstrap/AdminLTE)
* Atualizações via HTMX (sem reload completo)
* Contadores regressivos em tempo real
* Feedback visual de erros e sucessos

### Administração
* Painel para superusuários
* Gerenciamento de usuários e redes
* Visualização de todas as atividades do sistema

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
