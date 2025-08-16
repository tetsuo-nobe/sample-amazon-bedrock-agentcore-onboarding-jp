# Amazon Bedrock AgentCore オンボーディング

* **このリポジトリは、[sample-amazon-bedrock-agentcore-onboarding](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-onboarding) を日本語化したものです。**

すべての開発者がAmazon Bedrock AgentCoreを効果的に学習できる **実用的でシンプル、実行可能な例** です。このプロジェクトは、AgentCoreのコア機能のハンズオン実装を通じて段階的な学習パスを提供します。

## 概要

Amazon Bedrock AgentCoreは、AIエージェントを大規模に構築、デプロイ、管理するための包括的なプラットフォームです。このオンボーディングプロジェクトは、実行、修正、学習が可能な **実際に動作する実装** を通じて、各AgentCore機能をデモンストレーションします。

### 学習内容

- **Code Interpreter**: 動的計算とデータ処理のためのセキュアなサンドボックス実行
- **Runtime**: AWSクラウドインフラでのスケーラブルなエージェントデプロイと管理
- **Gateway**: 認証とMCPプロトコルサポート付きAPIゲートウェイ統合
- **Identity**: エージェント操作のためのOAuth 2.0認証とセキュアなトークン管理
- **Observability**: CloudWatch統合での包括的な監視、トレーシング、デバッグ
- **Memory**: コンテキスト認識エージェントインタラクションのための短期および長期メモリ機能

### 学習哲学

私たちの **Amazon Bedrock AgentCore 実装原則** に従い、このプロジェクトのすべての例は以下の通りです：

- ✅ **実行可能コードファースト** - ライブAWSサービスでテストされた完全な実行可能な例
- ✅ **実用的な実装** - 包括的なログとエラーハンドリングを持つ実世界の使用例
- ✅ **シンプルで洗練** - 機能を維持しながら学習コストを最小化する明確で説明的なコード
- ✅ **段階的学習** - 基本から高度な概念まで段階的に複雑さを構築する番号付きシーケンス

## ディレクトリ構成

```
sample-amazon-bedrock-agentcore-onboarding/
├── 01_code_interpreter/          # セキュアなサンドボックス実行
│   ├── README.md                 # 📖 Code Interpreter ハンズオンガイド
│   ├── cost_estimator_agent/     # AWSコスト見積もりエージェント実装
│   └── test_code_interpreter.py  # 完全なテストスイートと例
│
├── 02_runtime/                   # エージェントデプロイと管理
│   ├── README.md                 # 📖 Runtimeデプロイハンズオンガイド
│   ├── prepare_agent.py          # エージェント準備自動化ツール
│   └── deployment/               # デプロイ用パッケージエージェント
│
├── 03_identity/                  # OAuth 2.0認証
│   ├── README.md                 # 📖 Identity統合ハンズオンガイド
│   ├── setup_inbound_authorizer.py  # OAuth2プロバイダーセットアップ
│   └── test_identity_agent.py    # Identity保護エージェント
│
├── 04_gateway/                   # 認証付きAPIゲートウェイ
│   ├── README.md                 # 📖 Gateway統合ハンズオンガイド
│   ├── setup_outbound_gateway.py # Gatewayデプロイ自動化
│   ├── src/app.py                # Lambda関数実装
│   ├── deploy.sh                 # Lambdaデプロイスクリプト
│   └── test_gateway.py           # Gatewayテストエージェント
│
├── 05_observability/             # 監視とデバッグ
│   ├── README.md                 # 📖 Observabilityセットアップハンズオンガイド
│   └── test_observability.py     # 可観測性のためのランタイム複数回呼び出し
│
├── 06_memory/                    # コンテキスト認識インタラクション
│   ├── README.md                 # 📖 Memory統合ハンズオンガイド
│   └── test_memory.py            # メモリ強化エージェント実装
│
├── pyproject.toml                # プロジェクト依存関係と設定
├── uv.lock                       # 依存関係ロックファイル
└── README.md                     # この概要ドキュメント
```

## ハンズオン学習パス

### 🚀 クイックスタート（推奨順序）

1. **[Code Interpreter](01_code_interpreter/README.md)** - 基礎的なエージェント開発のためにここから始める
   - セキュアなPython実行でAWSコスト見積もりを構築
   - 即座に実用的な結果でAgentCoreの基本を学習
   - **時間**: 約10分 | **難易度**: 初級

2. **[Runtime](02_runtime/README.md)** - AWSクラウドインフラにエージェントをデプロイ
   - コスト見積もりをAgentCore Runtimeにパッケージしてデプロイ
   - スケーラブルなエージェントデプロイパターンを理解
   - **時間**: 約15分 | **難易度**: 中級

3. **[Identity](03_identity/README.md)** - セキュアな操作のためのOAuth 2.0認証を追加
   - Cognito OAuthプロバイダーとセキュアランタイムをセットアップ
   - `@requires_access_token`で透明な認証を実装
   - **時間**: 約15分 | **難易度**: 中級

4. **[Gateway](04_gateway/README.md)** - MCP互換APIでエージェントを公開
   - Lambda統合でアウトバウンドゲートウェイを作成
   - ローカルツールとリモートゲートウェイ機能を結合
   - **時間**: 約15分 | **難易度**: 中級

5. **[Observability](05_observability/README.md)** - 本番エージェントの監視とデバッグ
   - 包括的な監視のためのCloudWatch統合を有効化
   - トレーシング、メトリクス、デバッグ機能を確認
   - **時間**: 約15分 | **難易度**: 初級

6. **[Memory](06_memory/README.md)** - コンテキスト認識、学習エージェントを構築
   - 短期および長期メモリ機能を実装
   - パーソナライズされた適応型エージェントエクスペリエンスを作成
   - **時間**: 約15分 | **難易度**: 上級

### 🎯 集中学習（使用例別）

**初めてのエージェント構築**
→ [01_code_interpreter](01_code_interpreter/README.md)から始める

**本番デプロイ**
→ [02_runtime](02_runtime/README.md) → [03_identity](03_identity/README.md) → [04_gateway](04_gateway/README.md) → [05_observability](05_observability/README.md) の順で学習

**エンタープライズセキュリティ**
→ [03_identity](03_identity/README.md) → [04_gateway](04_gateway/README.md) に集中

**高度なAI機能**
[01_code_interpreter](01_code_interpreter/README.md) → [06_memory](06_memory/README.md) を探索

## 前提条件

### システム要件
- **Python 3.11+** と `uv` パッケージマネージャー
    - uv を pip でインストールする場合: `pip install uv`
- **AWS CLI** 適切な権限で設定済み
- **AWSアカウント** Bedrock AgentCore（プレビュー）へのアクセス付き
- **Amazon Bedrock** 必要なモデルへのアクセス付き


### クイックセットアップ
```bash
# リポジトリをクローン
git clone <repository-url>
cd sample-amazon-bedrock-agentcore-onboarding-jp

# 依存関係をインストール
uv sync

# AWS設定を確認
aws sts get-caller-identity
```

## 主要機能

### 🔧 **実装重視**
- ダミーデータや関数なし
- すべての例が実際の使用例に接続
- 本格的な複雑さとエラーハンドリングパターン

### 📚 **段階的学習設計**
- 各ディレクトリが前の概念を基盤に構築
- 明確な前提条件と依存関係
- ステップバイステップの実行手順

### 🔍 **デバッグフレンドリー**
- 動作監視のための幅広いログ出力
- 明確なエラーメッセージとトラブルシューティングガイダンス
- 部分的障害復旧のための漸進的状態管理

## リソースクリーンアップ

### 🧹 **重要: AWSリソースのクリーンアップ**

継続的な料金を避けるため、ハンズオン演習完了後にリソースをクリーンアップしてください。**依存関係のため逆順（06→01）でクリーンアップ**:

```bash
# 1. まずMemoryリソースをクリーンアップ
cd 06_memory
uv run python clean_resources.py

# 2. Gatewayリソースをクリーンアップ (SAM CLIを使用)
cd 04_gateway
sam delete  # Lambda関数と関連リソースを削除
uv run python clean_resources.py  # 必要に応じて追加クリーンアップ

# 3. Identityリソースをクリーンアップ
cd 03_identity
uv run python clean_resources.py

# 4. Runtimeリソースをクリーンアップ
cd 02_runtime
uv run python clean_resources.py
```

## ヘルプの取得

### よくある問題
- **AWS権限**: 認証情報が上記の必要権限を持っていることを確認
- **サービス可用性**: AgentCoreはプレビュー中 - リージョン可用性を確認
- **依存関係**: `uv sync` を使用して一貫した依存関係バージョンを確保
- **リソースクリーンアップ**: 予期しない料金を避けるため、常に逆順でクリーンアップスクリプトを実行

### サポートリソース

- [Amazon Bedrock AgentCore開発者ガイド](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AWSサポート](https://aws.amazon.com/support/) アカウント固有の問題用
- [GitHub Issues](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-onboarding/issues) プロジェクト固有の質問用

## コントリビューション

私たちの **実装原則** に沿ったコントリビューションを歓迎します：

1. **実行可能コードファースト** - すべての例は現在のAWS SDKバージョンで動作する必要があります
2. **実用的な実装** - 包括的なコメントと実世界の使用例を含める
3. **シンプルで洗練** - 機能を保持しながら明確さを維持
4. **意味のある構造** - 説明的な名前と論理的な組織を使用

