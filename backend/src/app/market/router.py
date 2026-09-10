from app.core.dependencies import get_market_service
from fastapi import APIRouter, Depends, HTTPException

from .schemas import (
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
        print(f"symbol = {request.symbol}")
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

    return MarketKlineResponse(
        symbol=request.symbol,

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