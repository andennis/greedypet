from entities import IndicatorType, FilterConfig, TradeAlgorithm
from .base_filter import BaseFilter
from .rsi_filter import RSIFilter
from .bollinger_bends_filter import BollingerBendsFilter


filter_map = {
    IndicatorType.RSI: RSIFilter,
    IndicatorType.BOLLINGER_BENDS: BollingerBendsFilter,
}


def create_filter(filter_config: FilterConfig, trade_algorithm: TradeAlgorithm) -> BaseFilter:
    return filter_map[filter_config.indicator](filter_config, trade_algorithm)
