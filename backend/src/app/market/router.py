from app.core.dependencies import get_market_service
from fastapi import APIRouter, Depends, HTTPException

from .schemas import (
    MarketKlineData,
    MarketKlineRequest,
    MarketKlineResponse,
    CandleResponse,
    IndicatorResponse,
    IndicatorSeries,
    MarketKlineMeta,
)
from .service import IndicatorService, MarketService

router = APIRouter(
    prefix="/api/v1/market",
    tags=["Market"],
)

@router.post(
    "/kline",
    response_model=MarketKlineResponse,
)
async def get_kline(
    request: MarketKlineRequest,
    service: MarketService = Depends(get_market_service),
):
    try:
        candles, indicators = await service.get_kline(
            symbol=request.symbol,
            period=request.period,
            adjust=request.adjust,
            start=request.start,
            end=request.end,
            indicators=request.indicators,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    stock_name = service.get_stock_name(request.symbol)
    market_kline_data = MarketKlineData(
        symbol=request.symbol,

        name=stock_name,

        period=request.period,

        adjust=request.adjust,

        start=request.start,

        end=request.end,

        candles=[
            CandleResponse(
                time=candle.time,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                amount=candle.amount,
                turnover=candle.turnover,
                amplitude=candle.amplitude,
                change_pct=candle.change_pct,
                change_amount=candle.change_amount
            )
            for candle in candles
        ],

        indicators=[
            IndicatorResponse(
                name=result.name,
                type=result.type,
                params=result.params,
                series=[
                    IndicatorSeries(
                        name=series.name,
                        values=series.values,
                    )
                    for series in result.series
                ],
            )
            for result in indicators
        ],

        meta=MarketKlineMeta(),
    )
    
    return MarketKlineResponse(
            code=0,
            message="success",
            data=market_kline_data,
        )