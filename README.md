# Platform Scraper

Uma aplicação web moderna para rastreamento automático de vídeos do YouTube, TikTok, Facebook e Instagram contendo palavras-chave relacionadas a investimentos.

## Sobre o Projeto

O Platform Scraper usa técnicas de web scraping para coletar dados reais de vídeos postados no último mês, encontrando nomes de plataformas, links de sites e conteúdo de aplicativos de mensagens como WhatsApp e Telegram. A aplicação possui um design inspirado em terminal/hacker com texto verde neon em fundo escuro.

## Funcionalidades

- Rastreamento de vídeos com palavras-chave específicas
- Extração de nomes de plataformas, links e grupos de mensagens
- Análise de conteúdo de websites
- Visualização de estatísticas e tendências
- Design moderno inspirado em estilo terminal/hacker

## Instruções de Deploy

### Deploy no Streamlit Cloud

1. Crie uma conta em [Streamlit Cloud](https://streamlit.io/cloud)
2. Conecte ao seu repositório GitHub (primeiro faça o upload deste projeto para um repositório)
3. Selecione o arquivo `app.py` como ponto de entrada
4. Configure os recursos necessários (mínimo recomendado: 1GB de RAM)
5. Defina a porta como 5000 no arquivo `.streamlit/config.toml` (já configurado)

### Deploy no Replit

1. Use o botão "Deploy" no Replit para tornar o aplicativo acessível publicamente
2. A aplicação já está configurada para usar a porta 5000 e endereço "0.0.0.0"

### Requisitos

O projeto utiliza as seguintes bibliotecas Python:
- streamlit
- pandas
- beautifulsoup4
- requests
- plotly
- trafilatura
- apscheduler
- pillow
- selenium

Todas as dependências estão listadas no arquivo `pyproject.toml`.

## Uso Local

Para executar o projeto localmente:

```bash
streamlit run app.py --server.port 5000
```