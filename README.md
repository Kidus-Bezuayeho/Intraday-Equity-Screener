# Intraday-Equity-Screener
This project is an AI-driven system designed to predict intraday stock price movements on an hourly basis. The API server provides machine learning and deep learning powered predictions of both direction (up or down) and magnitude (expected percentage return). By leveraging technical indicators (RSI, MACD, VWAP, ATR, Bollinger Bands), lagged returns, and OHLCV time-series data, the backend generates actionable trading signals that can be integrated into trading strategies or frontend dashboards.

The system begins with baseline models such as Multiple Linear Regression and XGBoost for interpretable results, then expands into advanced architectures including LSTM, GRU, and Transformers to capture sequential market patterns. Beyond prediction, the API includes endpoints for backtesting, performance evaluation, and analytics using metrics like Sharpe ratio, max drawdown, profit factor, and win rate.

Ultimately, this backend lays the foundation for a full-stack AI-powered trading platform, where the frontend will visualize predictions, performance, and live signals to support data-driven day trading decisions.
