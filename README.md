# Júnior, o Parceiro | Gestor de Jornada de Leads v3.1 (N8N-Ready)

Esta versão do assistente foi aprimorada para se integrar perfeitamente a um orquestrador de fluxos como o N8N, além de incorporar uma "memória conjunta" para dar mais contexto às interações.

## 🚀 Arquitetura com Orquestração

O sistema agora opera com uma arquitetura onde o N8N atua como o maestro do tempo, e o nosso sistema é o executor inteligente.

-   **N8N (Orquestrador Externo):**
    -   Controla o tempo do funil de 18 dias.
    -   A cada etapa (Dia 1, Dia 2, Dia 4...), o N8N pode fazer uma de duas coisas:
        1.  Chamar o nosso script `vigia_funil.py` para que ele verifique os status e envie follow-ups em massa.
        2.  Fazer uma chamada direta à nossa API (`/api/whatsapp/webhook`) para enviar uma mensagem específica a um lead.

-   **Nosso Sistema (Executor Inteligente):**
    -   `disparador_funil.py`: Inicia a campanha.
    -   `vigia_funil.py`: Motor de lógica de follow-up, que pode ser acionado pelo N8N.
    -   `API (main.py + endpoints.py)`: Recebe as respostas dos leads e executa a IA, além de poder receber comandos do N8N.

## 📋 Nova Funcionalidade: Memória Conjunta

Para dar mais contexto entre as interações, a IA agora pode resumir uma conversa e guardá-la no nosso sistema de rastreamento. Isto é crucial para quando o funil escalar para outros canais, como ligações.

## 🚀 Instalação e Execução

Os passos permanecem os mesmos, mas o fluxo de trabalho em produção será orquestrado pelo N8N, que chamará os nossos scripts e endpoints.