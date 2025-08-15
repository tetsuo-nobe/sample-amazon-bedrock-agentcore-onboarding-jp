# AgentCore Identity統合

[English](README.md) / [日本語](README_ja.md)

この実装では、セキュアなランタイム呼び出しのためのOAuth 2.0認証を使用した**AgentCore Identity**を実演します。`@requires_access_token`デコレータは、認証されたエージェント操作のための透明なトークン管理を提供します。

## プロセス概要

```mermaid
sequenceDiagram
    participant Agent as Strands Agent
    participant Identity as AgentCore Identity
    participant Cognito as Cognito OAuth
    participant Runtime as Secure Runtime
    participant Tool as Cost Estimator Tool

    Agent->>Identity: @requires_access_token
    Identity->>Cognito: OAuth M2M Flow
    Cognito-->>Identity: Access Token
    Identity-->>Agent: Inject Token
    Agent->>Runtime: Authenticated Runtime Request
    Runtime->>Tool: Execute Cost Estimation
    Tool-->>Runtime: Results
    Runtime-->>Agent: Response
```

## 前提条件

1. **ランタイムデプロイ済み** - まず`02_runtime`セットアップを完了
2. **AWS認証情報** - `bedrock-agentcore-control`権限付き
3. **依存関係** - `uv`経由でインストール（pyproject.toml参照）

## 使用方法

### ファイル構成

```
03_identity/
├── README.md                      # このドキュメント
├── setup_inbound_authorizer.py    # OAuth2プロバイダーとセキュアランタイムセットアップ
└── test_identity_agent.py         # Identity認証付きテストエージェント
```

### ステップ1: OAuth2認証情報プロバイダーとセキュアランタイムを作成

```bash
cd 03_identity
uv run python setup_inbound_authorizer.py
```

このスクリプトは以下を実行します：
- M2Mクライアント認証情報を使用したCognito OAuthオーソライザーの作成
- AgentCore Identity OAuth2認証情報プロバイダーのセットアップ
- JWT認証付きセキュアランタイムのデプロイ
- `inbound_authorizer.json`での設定生成

### ステップ2: Identity保護エージェントをテスト

```bash
cd 03_identity
uv run python test_identity_agent.py
```

これにより、トークン取得とセキュアランタイム呼び出しを含む完全な認証フローがテストされます。

## 主要な実装パターン

### Strandsツールでの@requires_access_token使用

```python
from strands import tool
from bedrock_agentcore.identity.auth import requires_access_token

@tool(name="cost_estimator_tool", description="アーキテクチャ記述からAWSのコストを見積もり")
@requires_access_token(
    provider_name=OAUTH_PROVIDER,
    scopes=[OAUTH_SCOPE],
    auth_flow="M2M",
    force_authentication=False
)
async def cost_estimator_tool(architecture_description, access_token: str) -> str:
    """アクセストークンはデコレータによって自動的に注入されます"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(RUNTIME_URL, headers=headers, data=json.dumps({
        "prompt": architecture_description
    }))
    
    return response.text
```

### エージェント統合パターン

```python
from strands import Agent

agent = Agent(
    system_prompt="あなたはプロフェッショナルなソリューションアーキテクトです...",
    tools=[cost_estimator_tool]
)

# エージェントは自動的にトークンの取得と注入を処理します
await agent.invoke_async("アーキテクチャの説明をここに...")
```

## 使用例

```python
import asyncio
from strands import Agent
from test_identity_agent import cost_estimator_tool

agent = Agent(
    system_prompt=(
        "あなたはプロフェッショナルなソリューションアーキテクトです。"
        "お客様からアーキテクチャの説明や要件を受け取ります。"
        "'cost_estimator_tool'を使用して見積もりを提供してください"
    ),
    tools=[cost_estimator_tool]
)

# アーキテクチャ記述でのテスト
architecture = """
シンプルなWebアプリケーション：
- Application Load Balancer
- 2x EC2 t3.mediumインスタンス
- us-east-1のRDS MySQLデータベース
"""

result = await agent.invoke_async(architecture)
print(result)
```

## セキュリティの利点

- **トークンの露出ゼロ** - トークンがログやコードに表示されることはありません
- **自動ライフサイクル管理** - AgentCoreが有効期限を処理します
- **ランタイムレベルのセキュリティ** - ランタイムレベルでのJWT認証
- **M2M認証** - 自動化システムに適しています

## 参考資料

- [AgentCore Identity開発者ガイド](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)
- [OAuth 2.0 Client Credentials Flow](https://tools.ietf.org/html/rfc6749#section-4.4)
- [Cognito OAuth統合](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-app-integration.html)
- [Strands Agentsドキュメント](https://github.com/aws-samples/strands-agents)

---

**次のステップ**: ここで実演されたパターンを使用して、Identity保護エージェントをアプリケーションに統合するか、[04_gateway](../04_gateway/README.md)に進んでMCP互換APIを通じてエージェントを公開しましょう。
