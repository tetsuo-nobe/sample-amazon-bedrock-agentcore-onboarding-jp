"""
cost_estimator_agent_with_identityを呼び出してAgentCore Identityをテスト

このスクリプトは以下の方法を実演します:
1. AgentCore IdentityからOAuthトークンを取得
2. 取得したトークンでRuntimeを呼び出し
"""

import json
import base64
import logging
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone
import requests
from strands import Agent
from strands import tool
from bedrock_agentcore.identity.auth import requires_access_token

# より詳細な出力でログを設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


CONFIG_FILE = Path("inbound_authorizer.json")
OAUTH_PROVIDER = ""
OAUTH_SCOPE = ""
RUNTIME_URL = ""
with CONFIG_FILE.open('r') as f:
    config = json.load(f)
    OAUTH_PROVIDER = config["provider"]["name"]
    OAUTH_SCOPE = config["cognito"]["scope"]
    RUNTIME_URL = config["runtime"]["url"]


@tool(name="cost_estimator_tool", description="アーキテクチャの説明からAWSのコストを見積もる")
@requires_access_token(
    provider_name= OAUTH_PROVIDER,
    scopes= [OAUTH_SCOPE],
    auth_flow= "M2M",
    force_authentication= False)
async def cost_estimator_tool(architecture_description, access_token: str) -> str:
    session_id = f"runtime-with-identity-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    if access_token:
        logger.info("✅ Successfully load the access token from AgentCore Identity!")
        for element in access_token.split("."):
            logger.info(f"\t{json.loads(base64.b64decode(element).decode())}")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
        "X-Amzn-Trace-Id": session_id,
    }

    response = requests.post(
        RUNTIME_URL,
        headers=headers,
        data=json.dumps({"prompt": architecture_description})
    )

    response.raise_for_status()
    return response.text


async def main():
    """メインテスト関数"""
    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description='さまざまな方法で AgentCore Gateway をテストする')
    parser.add_argument(
        '--architecture',
        type=str,
        default="Application Load Balancer、2 つの EC2 t3.medium インスタンス、および us-east-1 の RDS MySQL データベースを備えたシンプルな Web アプリケーション。",
        help='コスト見積もりのためのアーキテクチャの説明。デフォルト: ALB、2つのEC2インスタンス、RDS MySQLを使用したシンプルなウェブアプリケーション。'
    )
    args = parser.parse_args()

    agent = Agent(
        system_prompt=(
            "あなたはプロのソリューション アーキテクトです。"
            "顧客からアーキテクチャの説明や要件を受け取ります。 "
            "「cost_estimator_tool」を使用して見積もりを提供してください。"
        ),
        tools=[cost_estimator_tool]
    )

    logger.info("Invoke agent that calls Runtime with Identity...")
    await agent.invoke_async(args.architecture)
    logger.info("✅ Successfully called agent!")


if __name__ == "__main__":
    asyncio.run(main())
