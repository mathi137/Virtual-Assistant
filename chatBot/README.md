SERVIÇO CHATBOT (INTEGRAÇÃO TELEGRAM)

Este serviço é o ponto de conexão entre o Telegram e o restante da nossa arquitetura. Ele utiliza FastAPI para gerenciar o Webhook e httpx para realizar a comunicação assíncrona com a API do Telegram.

Opera na porta 8001 e é essencialmente um serviço de comunicação (Gateway), dependendo do backend para toda a lógica de processamento e IA.

ESTRUTURA E TECNOLOGIA

FastAPI: Recebe as mensagens via requisições POST do Telegram.

Porta: 8001 (Porta interna e externa do container).

Endpoint Webhook: /webhook (Ponto que o Telegram deve acessar).

httpx: Cliente HTTP assíncrono para enviar respostas ao Telegram.

CONFIGURAÇÃO: TOKEN E VARIÁVEIS

O container precisa do token de autenticação do bot.

Variável OBRIGATÓRIA: TELEGRAM_BOT_TOKEN

Onde obter: Através do @BotFather no Telegram, usando o comando /newbot.

Localização: Deve ser configurado no arquivo .env na RAIZ do projeto.

Exemplo no arquivo .env:
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI_DO_BOTFATHER

COMO INICIAR E TESTAR LOCALMENTE

Para testes, utilizamos o ngrok para criar um túnel HTTPS seguro para o Telegram.

Passo 1: Iniciar o Container

Na pasta raiz do projeto:
docker compose up -d --build chat_bot

Passo 2: Expor o Serviço com ngrok

Inicie o túnel, apontando para a porta 8001:
ngrok http 8001

Anote a URL HTTPS de Forwarding (Ex: https://www.google.com/search?q=https://abcd1234.ngrok-free.dev).

Passo 3: Configurar o Webhook

Use o navegador para enviar o comando setWebhook (substitua o TOKEN e a URL com /webhook):
https://api.telegram.org/bot<SEU_TOKEN_AQUI>/setWebhook?url=<URL_HTTPS_DO_NGROK>/webhook

Passo 4: Teste Funcional

Vá para o seu bot no Telegram.

Envie qualquer mensagem (Ex: /start).

O bot deve responder com: "Olá! Recebi sua mensagem."

DEBUG E SOLUÇÃO DE PROBLEMAS

Logs do Container: docker compose logs chat_bot -f

Teste de Saúde do FastAPI: Acesse http://localhost:8001/

Status do Webhook: Verifique em https://api.telegram.org/bot<TOKEN>/getWebhookInfo

Atenção ao Erro 405: Se o log do ngrok mostrar "405 Method Not Allowed", o Webhook não foi configurado corretamente e você deve refazer o Passo 3, garantindo que a URL termine em /webhook.