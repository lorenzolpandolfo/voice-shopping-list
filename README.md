# Voice Shopping List

Um **bot do Telegram** que recebe áudios para anotar compras e salva como tabela no **Google Planilhas**.

---

# Setup

Abaixo segue um guia de como configurar o projeto.

## Configurando Google Cloud

### Criando um projeto do Google Cloud
1. Será necessário criar um projeto gratuíto no [Google Cloud](https://console.cloud.google.com/)

### Permitir criação de chave da Conta de Serviço
1. Acesse [IAM](https://console.cloud.google.com/iam-admin/iam)
2. Selecione no topo da página, ao lado direito de Google Cloud, a sua organização pessoal
   - A organização deve ter sido criada com o free-trial do Google Cloud. O nome é parecido com `seuemail-org`
   - Se não encontrar, tente clicar nos 3 pontinhos no canto direito da janela de selecionar projetos e escolha **IAM/Permissões**. Deve carregar a página de permissões da organização
3. Defina a permissão **Administrador da política da organização** no seu usuário
4. Em [Políticas da Organização](https://console.cloud.google.com/iam-admin/orgpolicies/list) encontre a flag `iam.managed.disableServiceAccountApiKeyCreation` e desative-a

### Criando a Conta de Serviço
1. Acesse [IAM > Contas de Serviço](https://console.cloud.google.com/iam-admin/serviceaccounts) e selecione o projeto
2. Clique em Criar conta de serviço, defina o nome e pule as etapas de **Permissão** e **Principais com acesso**
3. **Guarde o email da conta de serviço**, ele será utilizado depois, para dar acesso ao bot na sua Google Planilha
4. Em `Ações > Gerenciar chaves > Adicionar chave > Criar nova chave`, crie uma chave de acesso JSON. Não a compartilhe com ninguém!

