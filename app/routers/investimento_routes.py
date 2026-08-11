from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import pegar_sessao, get_current_user
from app.models import PosicaoInvestimento, Usuario
from app.schemas import InvestimentoResponseSchema, ResumoCarteiraSchema, MovimentarInvestimentoSchema
from app.services.finance_service import FinanceService
from typing import List

investimento_router = APIRouter(prefix="/investimentos", tags=["Investimentos"])
# Essa é a rota de comprar investimentos
@investimento_router.post("/comprar", response_model=InvestimentoResponseSchema, status_code=status.HTTP_201_CREATED,summary="Adicionar dinheiro a um investimento (Compra/Aporte)")
async def comprar_investimento(dados: MovimentarInvestimentoSchema, session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(get_current_user)):
    """
    Registra a compra de um ativo (ex: USD, EUR, PETR4, VALE3).
    A cotação é consultada em tempo real e a quantidade comprada é calculada automaticamente.
    """

    # Chama o serviço financeiro para consultar o valor da cotação em tempo real do ativo/moeda, e o await espera a resposta da api externa
    cotacao = await FinanceService.obter_cotacao(dados.ticker)

    # Se a cotação retornar None ou o usuario digitar um ativo nao catalogado, o ativo não existe
    if cotacao is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ativo '{dados.ticker}' não encontrado ou indisponível."
        )

    # Calcula a quantidade de ativos/moedas adquiridos
    quantidade_comprada = round(dados.valor_brl / cotacao, 4)

    novo_investimento = PosicaoInvestimento(
        usuario_id=usuario.id,
        ticker=dados.ticker.upper(),
        valor_investido_brl=dados.valor_brl, # Salva o valor positivo da compra
        cotacao_compra=cotacao,
        quantidade_ativos=quantidade_comprada
    )

    session.add(novo_investimento)
    session.commit()
    session.refresh(novo_investimento)
    return novo_investimento


# Essa é a rota de historico de investimentos comprados e vendidos pelo usuario
@investimento_router.get("/historico", response_model=List[InvestimentoResponseSchema], summary="Listar todo o histórico de compras e vendasdo usuário")
async def obter_historico_compras(session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(get_current_user)):
    """
    Retorna a lista de transações de compra e venda cadastradas no banco de dados.
    Esta rota é ultra rápida pois não consulta APIs de mercado externas, ela consulta apenas os dados do banco de dados.
    """
    transacoes = session.query(PosicaoInvestimento).filter(PosicaoInvestimento.usuario_id == usuario.id).all()

    return transacoes


# Essa é a rota que agrupa os investimentos e devolve o resumo deles
@investimento_router.get("/resumo", response_model=ResumoCarteiraSchema, summary="Obter patrimônio total atualizado (oculta ativos zerados)")
async def obter_resumo_carteira(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(get_current_user)):
    """
    Agrupa os ativos, calcula a soma das quantidades, busca a cotação 
    de HOJE no mercado e devolve o valor patrimonial total recalculado.
    """
    transacoes = session.query(PosicaoInvestimento).filter(PosicaoInvestimento.usuario_id == usuario.id).all()

    # Essa validação verifica se o usuario nao tem nenhum investimento registrado, caso ele não tenha o metodo get retorna tudo zerado
    if not transacoes:
        return ResumoCarteiraSchema(
            patrimonio_total_atual_brl=0.0,
            total_investido_historico_brl=0.0,
            ativos_agrupados=[]
        )

    agrupado = {}
    total_investido_geral = 0.0

    for item in transacoes:
        ticker = item.ticker.upper()
        if ticker not in agrupado:
            agrupado[ticker] = {"total_qtd": 0.0, "total_investido": 0.0}

        # Como as retiradas são salvas com valores negativos, a matemática se resolve sozinha:
        # Ex: 1000 + (-400) = 600
        agrupado[ticker]["total_qtd"] += item.quantidade_ativos
        agrupado[ticker]["total_investido"] += item.valor_investido_brl
        total_investido_geral += item.valor_investido_brl

    '''
    Essa é a logica de soma dos ativos ela começa criando um dicionario vazio. 
    Depois ela percorre cada compra pelo for, se o ativo nao estiver no dicionario ela adiciona com os valores zerados.
    Apos isso ela acumula as quantidades e valores em R$ para agrupar todas as compras daquele mesmo ativo.
    E por fim mantem o somatorio de total_investido_geral de todo o histórico do usuário
    '''

    ativos_consolidados = []
    patrimonio_total_atual = 0.0

    for ticker, dados in agrupado.items():
        # SOFT DELETE: Se a quantidade acumulada for zero (ou quase zero), ignora o ativo. Ele não aparece no Swagger/Painel, mas continua no DB
        if dados["total_qtd"] <= 0.01:
            continue

        cotacao_atual = await FinanceService.obter_cotacao(ticker)
        if cotacao_atual is None:
            cotacao_atual = dados["total_investido"] / dados["total_qtd"]

        valor_atual_brl = dados["total_qtd"] * cotacao_atual
        lucro_prejuizo = valor_atual_brl - dados["total_investido"]

        '''
        Aqui acontece os calculos com base na cotação atual 
        A primeira é do valor atual que seria a quantidade acumulada do ativo pelo preço atual de mercado
        A segunda calcula a rentabilidade, onde ela faz o valor atual ja calculado menos o total investido historicamente
        '''

        patrimonio_total_atual += valor_atual_brl

        ativos_consolidados.append({
            "ticker": ticker,
            "total_investido_brl": round(dados["total_investido"], 2),
            "total_quantidade": round(dados["total_qtd"], 2),
            "cotacao_atual": round(cotacao_atual, 2),
            "valor_atual_brl": round(valor_atual_brl, 2),
            "lucro_prejuizo_brl": round(lucro_prejuizo, 2)
        })

    return ResumoCarteiraSchema(
        patrimonio_total_atual_brl=round(patrimonio_total_atual, 2),
        total_investido_historico_brl=round(total_investido_geral, 2),
        ativos_agrupados=ativos_consolidados
    )


@investimento_router.post("/vender", response_model=InvestimentoResponseSchema, status_code=status.HTTP_201_CREATED, summary="Retirar dinheiro de um investimento (Venda/Resgate)")
async def vender_investimento(dados: MovimentarInvestimentoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(get_current_user)):
    ticker_upper = dados.ticker.upper()

    # Aqui ocorre a busca no histórico para calcular quanto o usuário tem atualmente desse ativo
    transacoes = session.query(PosicaoInvestimento).filter(PosicaoInvestimento.usuario_id == usuario.id, PosicaoInvestimento.ticker == ticker_upper).all()

    total_qtd_atual = sum(item.quantidade_ativos for item in transacoes)

    # Busca a cotação atual para saber quanto o dinheiro dele vale em ativos
    cotacao_atual = await FinanceService.obter_cotacao(ticker_upper)
    if cotacao_atual is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não foi possível obter a cotação atual de {ticker_upper} para realizar a venda."
        )

    # Quantidade de ativos equivalente ao valor em R$ que ele quer retirar
    quantidade_a_retirar = round(dados.valor_brl / cotacao_atual, 4)

    # Aqui ocorre a validação para verificar se ele tem ativos suficientes para realizar a retirada
    # Uso uma tolerância pequena (0.01) como uma "margem de tolerância" para que o sistema não barre o usuário por causa de um arredondamento de centavos invisíveis quando ele tentar sacar tudo
    if quantidade_a_retirar > (total_qtd_atual + 0.01):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Você possui o equivalente a {round(total_qtd_atual * cotacao_atual, 2)} BRL deste ativo."
        )

    # Se o usuario estiver tentando retirar praticamente tudo, zera a quantidade exata, abs = Absolute Value (Valor Absoluto)
    if abs(total_qtd_atual - quantidade_a_retirar) < 0.05:
        quantidade_a_retirar = total_qtd_atual

    '''
    Essa validação elimina pequenos restos de centavos causados por arredondamentos ao vender um ativo
    Se a retirada for quase igual ao saldo total, o sistema força o zeramento exato da posição no banco de dados
    Assim, o ativo atinge zero absoluto e some do Swagger automaticamente, mantendo o resumo limpo
    '''

    # Aqui o sistema grava a retirada no banco com valores NEGATIVOS (Indica saída no histórico)
    retirada = PosicaoInvestimento(
        usuario_id=usuario.id,
        ticker=ticker_upper,
        valor_investido_brl=-dados.valor_brl,        # Negativo: saiu dinheiro
        cotacao_compra=cotacao_atual,
        quantidade_ativos=-quantidade_a_retirar      # Negativo: saíram ativos
    )

    session.add(retirada)
    session.commit()
    session.refresh(retirada)
    return retirada


