"""
The Backward 7evin - Advanced Cryptocurrency Predictor
CS379 Machine Learning - Enhanced Version
Author: Joey Bolkovatz
Date: October 2025

Advanced Supervised Learning: Random Forest & XGBoost
Predicts next-day BTC movement direction (Up/Down) based on macro correlations
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class CryptoPredictor:
    """Advanced cryptocurrency movement predictor using Random Forest"""

    def __init__(self, lookback_days=90):
        self.lookback_days = lookback_days
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_names = []

    def fetch_data(self):
        """Fetch historical market data"""
        # Use current date for end date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days)

        symbols = {
            'BTC-USD': 'BTC',
            'ETH-USD': 'ETH',
            'GC=F': 'Gold',
            'DX-Y.NYB': 'USD',
            '^GSPC': 'SP500',
            'XRP-USD': 'XRP',
            'ADA-USD': 'ADA',
            'SOL-USD': 'SOL'
        }

        print(f"Fetching {self.lookback_days} days of market data...")
        data = {}
        for symbol, name in symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                if not df.empty:
                    data[name] = df['Close']
            except Exception as e:
                print(f"Warning: Could not fetch {symbol}")

        df = pd.DataFrame(data).dropna()
        print(f"Loaded {len(df)} days of complete data")
        return df

    def engineer_features(self, df):
        """Create features for machine learning"""
        features_df = pd.DataFrame(index=df.index)

        # Calculate returns for all assets
        for col in df.columns:
            features_df[f'{col}_return'] = df[col].pct_change()
            features_df[f'{col}_return_5d'] = df[col].pct_change(5)
            features_df[f'{col}_return_10d'] = df[col].pct_change(10)

        # Rolling correlations with BTC
        window = 20
        for col in df.columns:
            if col != 'BTC':
                features_df[f'corr_{col}_BTC'] = (
                    df[col].rolling(window).corr(df['BTC'])
                )

        # Volatility features
        for col in df.columns:
            features_df[f'{col}_volatility'] = (
                df[col].pct_change().rolling(10).std()
            )

        # Momentum indicators
        features_df['BTC_momentum_5'] = df['BTC'].diff(5)
        features_df['BTC_momentum_10'] = df['BTC'].diff(10)

        # Moving averages
        features_df['BTC_MA7'] = df['BTC'].rolling(7).mean()
        features_df['BTC_MA21'] = df['BTC'].rolling(21).mean()
        features_df['BTC_MA_diff'] = features_df['BTC_MA7'] - features_df['BTC_MA21']

        # RSI-like indicator
        delta = df['BTC'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features_df['BTC_RSI'] = 100 - (100 / (1 + rs))

        # Target: Next day BTC movement (1 = Up, 0 = Down)
        features_df['target'] = (df['BTC'].shift(-1) > df['BTC']).astype(int)

        # Clean data
        features_df = features_df.dropna()

        return features_df

    def train_model(self, X_train, y_train):
        """Train Random Forest classifier"""
        print("\nTraining Random Forest model...")

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

        return self.model

    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        X_test_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_test_scaled)

        print("\n" + "="*60)
        print("MODEL EVALUATION RESULTS")
        print("="*60)

        # Accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nTest Accuracy: {accuracy:.4f}")

        # Confusion Matrix
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print("\n[0,0]=True Down | [0,1]=False Up")
        print("[1,0]=False Down | [1,1]=True Up")

        # Classification Report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred,
                                   target_names=['Down', 'Up']))

        # Feature Importance
        print("\nTop 10 Most Important Features:")
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print(feature_importance.head(10).to_string(index=False))

        return accuracy, feature_importance

    def predict_current_signal(self, features_df):
        """Predict signal for most recent data"""
        latest_features = features_df.iloc[-1:, :-1]
        latest_scaled = self.scaler.transform(latest_features)
        prediction = self.model.predict(latest_scaled)[0]
        probability = self.model.predict_proba(latest_scaled)[0]

        signal = "BUY LONG" if prediction == 1 else "BUY SHORT"
        confidence = max(probability) * 100

        print("\n" + "="*60)
        print("CURRENT MARKET SIGNAL")
        print("="*60)
        print(f"Prediction: {signal}")
        print(f"Confidence: {confidence:.2f}%")
        print(f"Probability [Down, Up]: [{probability[0]:.3f}, {probability[1]:.3f}]")

        return signal, confidence

    def run_full_analysis(self):
        """Execute complete prediction workflow"""
        print("="*60)
        print("The Backward 7evin - Advanced Crypto Predictor")
        print("Supervised Learning: Random Forest Classification")
        print("="*60)

        # Step 1: Fetch data
        df = self.fetch_data()

        # Step 2: Engineer features
        print("\nEngineering features...")
        features_df = self.engineer_features(df)
        print(f"Created {len(features_df.columns)-1} features")

        # Step 3: Prepare train/test split
        X = features_df.iloc[:, :-1]
        y = features_df['target']
        self.feature_names = X.columns.tolist()

        # Use temporal split (last 20% for testing)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        print(f"\nTraining samples: {len(X_train)}")
        print(f"Testing samples: {len(X_test)}")

        # Step 4: Train model
        self.train_model(X_train, y_train)

        # Step 5: Evaluate
        accuracy, feature_importance = self.evaluate_model(X_test, y_test)

        # Step 6: Current prediction
        signal, confidence = self.predict_current_signal(features_df)

        # Save results
        results = {
            'accuracy': accuracy,
            'signal': signal,
            'confidence': confidence,
            'feature_importance': feature_importance
        }

        # Save feature importance to CSV
        feature_importance.to_csv('feature_importance.csv', index=False)
        print(f"\nFeature importance saved to: feature_importance.csv")

        return results

def main():
    """Main execution"""
    predictor = CryptoPredictor(lookback_days=90)
    results = predictor.run_full_analysis()

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)

if __name__ == "__main__":
    main()
