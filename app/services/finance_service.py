import logging
import httpx
import yfinance as yf

# Oculta mensagens de erro do Yahoo Finance no terminal para tickers inexistentes, e evita que mensagens vermelhas de aviso poluam o terminal caso o usuário digite um ticker que não existe
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

class FinanceService:

    @staticmethod
    async def obter_cotacao(ticker: str) -> float | None:
        ticker_clean = ticker.strip().upper()

        # MOEDAS E CRIPTOS (AwesomeAPI - Cotação Comercial Exata e Gratuita)
        # Verifica se o ticker solicitado é uma moeda estrangeira ou criptomoeda suportada pela awesomeAPI.
        if ticker_clean in ["USD", "EUR", "GBP", "CAD", "JPY", "ARS", "BTC", "ETH"]:
            url_awesome = f"https://economia.awesomeapi.com.br/last/{ticker_clean}-BRL"
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(url_awesome, timeout=5.0)
                    # Faz a requisição get para a awesomeAPI esperando no máximo 5 segundos.
                    if response.status_code == 200:
                        dados = response.json()
                        # Converte a resposta recebida em json para um dicionário python.
                        chave = f"{ticker_clean}BRL"
                    if chave in dados:
                        ask = float(dados[chave]["ask"])
                        # Retornar 'ask' costuma bater muito mais próximo do Google no momento do mercado aberto:
                        return round(ask, 4)
                except Exception:
                    pass

        
        # AÇÕES E FIIS DA B3 (Yahoo Finance)
        try:
            # O yfinance exige o sufixo .SA para ações da bolsa, aqui o programa adiciona o .SA caso o usuário não tenha escrito
            symbol_sa = f"{ticker_clean}.SA" if not ticker_clean.endswith(".SA") else ticker_clean
            
            ticker_data = yf.Ticker(symbol_sa)
            historico = ticker_data.history(period="1d")
            '''
            Cria a conexão com o ticker no yahoo finance
            E com o .iloc busca o histórico de preços do último dia de negociação (1d).
            '''

            if not historico.empty:
                # Pega o último preço registrado na coluna de fechamento ("Close")
                preco_fechamento = float(historico["Close"].iloc[-1])
                return round(preco_fechamento, 2)
        except Exception:
            pass

        return None