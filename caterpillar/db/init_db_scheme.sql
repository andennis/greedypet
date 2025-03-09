-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create role if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'greedypet') THEN
        CREATE ROLE greedypet WITH LOGIN PASSWORD '123';
    END IF;
END
$$;

-- Create enum for trade side
CREATE TYPE tradeside AS ENUM ('BUY', 'SELL');

-- Create table for currency pairs
CREATE TABLE currency_pairs (
    pair_id SERIAL PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (base_currency, quote_currency)
);

-- Set ownership and permissions
ALTER TABLE currency_pairs OWNER TO greedypet;

-- Create table for trades
CREATE TABLE trades (
    pair_id INTEGER NOT NULL REFERENCES currency_pairs(pair_id),
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    side tradeside NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (pair_id, timestamp)
);

-- Set ownership
ALTER TABLE trades OWNER TO greedypet;

-- Convert trades table to hypertable
SELECT create_hypertable('trades', 'timestamp');

-- Create indexes for better query performance
-- CREATE INDEX idx_trades_pair_timestamp ON trades (pair_id, timestamp DESC);
-- CREATE INDEX idx_trades_timestamp ON trades (timestamp DESC);

-- Optional: Create a continuous aggregate for OHLCV data
CREATE MATERIALIZED VIEW trades_1min_ohlcv
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', timestamp) AS bucket,
    pair_id,
    first(price, timestamp) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, timestamp) AS close,
    sum(volume) AS volume,
    count(*) AS number_of_trades
FROM trades
GROUP BY bucket, pair_id;

-- Set ownership for materialized view
ALTER MATERIALIZED VIEW trades_1min_ohlcv OWNER TO greedypet;

-- Refresh policy for the continuous aggregate
SELECT add_continuous_aggregate_policy('trades_1min_ohlcv',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute');

-- Create indexes on the continuous aggregate
CREATE INDEX idx_trades_1min_ohlcv_pair_time 
ON trades_1min_ohlcv (pair_id, bucket);

-- Insert popular currency pairs
INSERT INTO currency_pairs (base_currency, quote_currency) VALUES
    ('BTC', 'USDT'),
    ('ETH', 'USDT'),
    ('SOL', 'USDT'),
    ('BNB', 'USDT'),
    ('XRP', 'USDT'),
    ('ADA', 'USDT'),
    ('DOGE', 'USDT'),
    ('DOT', 'USDT'),
    ('POL', 'USDT'),
    ('LINK', 'USDT'),
    ('AVAX', 'USDT'),
    ('UNI', 'USDT'),
    ('ATOM', 'USDT'),
    ('TRX', 'USDT'),
    ('ETC', 'USDT'),
    ('FIL', 'USDT'),
    ('NEAR', 'USDT'),
    ('ALGO', 'USDT'),
    ('APE', 'USDT'),
    ('AAVE', 'USDT'),
    ('S', 'USDT'),
    ('FTM', 'USDT'),
    ('APEX', 'USDT'),
    ('OP', 'USDT'),
    ('ARB', 'USDT');

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO greedypet;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO greedypet; 