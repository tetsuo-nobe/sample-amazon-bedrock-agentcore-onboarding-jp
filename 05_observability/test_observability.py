#!/usr/bin/env python3
"""
AgentCore 可観測性テストスクリプト

このスクリプトは以下によってAgentCoreの可観測性機能をデモンストレーションします：
1. .bedrock_agentcore.yamlからエージェントARNを読み込み
2. 意味のあるセッションID（user_id + 日時形式）を使用
3. 同一セッション内での複数の呼び出しをテスト
4. 意図的にエラーを発生させてエラー検出をテスト
5. 監視用にCloudWatchで観測可能なログを記録

使用方法:
    python test_observability.py
"""

import json
import logging
import boto3
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ObservabilityTester:
    """意味のあるセッション追跡でAgentCoreの可観測性をテスト"""
    
    def __init__(self, agent_arn: str, region: str = ""):
        self.agent_arn = agent_arn
        self.region = region
        if not self.region:
            # 指定されていない場合はboto3セッションからデフォルトリージョンを使用
            self.region = boto3.Session().region_name
        self.client = boto3.client('bedrock-agentcore', region_name=self.region)
    
    def generate_session_id(self, user_id: str) -> str:
        """最小長要件を満たす意味のあるセッションIDを生成"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # AgentCoreはセッションIDが最低16文字必要
        session_id = f"{user_id}_{timestamp}_observability_test"
        logger.info(f"Generated session ID: {session_id} (length: {len(session_id)})")
        return session_id
    
    def invoke_agent(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """エラーハンドリング付きの単一エージェント呼び出し"""
        try:
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(payload).encode('utf-8'),
                traceId=session_id[:128]  # トレースIDが制限内であることを確認
            )
            
            result = self._process_response(response)
            return {
                'status': 'success',
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Error in invocation: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def test_multiple_invocations_same_session(self, user_id: str) -> Dict[str, Any]:
        """同一セッション内での複数の呼び出しをテスト"""
        session_id = self.generate_session_id(user_id)
        
        # 複数のテストプロンプトを定義
        test_prompts = [
            "SSH用に小規模なEC2を用意したいのですが、費用はいくらくらいでしょうか?",
            "中規模の RDS MySQL データベースのコストはいくらですか?",
            "100GBのストレージを備えたシンプルなS3バケットのコストを見積もることができますか?"
        ]
        
        logger.info(f"Testing multiple invocations for user: {user_id}")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Number of invocations: {len(test_prompts)}")
        
        results = []
        
        for i, prompt in enumerate(test_prompts, 1):
            logger.info(f"\n--- Invocation {i}/{len(test_prompts)} ---")
            logger.info(f"Prompt: {prompt}")
            
            payload = {"prompt": prompt}
            result = self.invoke_agent(session_id, payload)
            
            result.update({
                'invocation_number': i,
                'prompt': prompt
            })
            results.append(result)
            
            if result['status'] == 'success':
                logger.info(f"✅ Invocation {i} completed successfully")
            else:
                logger.error(f"❌ Invocation {i} failed: {result['error']}")
        
        return {
            'session_id': session_id,
            'user_id': user_id,
            'total_invocations': len(test_prompts),
            'results': results
        }

    def _process_response(self, response: Dict[str, Any]) -> str:
        """AgentCoreランタイムレスポンスを処理"""
        content = []
        
        if "text/event-stream" in response.get("contentType", ""):
            # ストリーミングレスポンスを処理 - バイトバッファ使用
            byte_buffer = b''
            for line in response["response"].iter_lines(chunk_size=10):
                if line:
                    byte_buffer += line
                    # 完全なUTF-8文字のみをデコード
                    while byte_buffer:
                        try:
                            decoded = byte_buffer.decode('utf-8')
                            if decoded.startswith("data: "):
                                decoded = decoded[6:]
                            content.append(decoded)
                            byte_buffer = b''
                            break
                        except UnicodeDecodeError as e:
                            # 不完全なバイト列の場合、次のチャンクを待つ
                            if e.start == 0:
                                # 最初から無効な場合は1バイト削除
                                byte_buffer = byte_buffer[1:]
                            else:
                                # 有効な部分をデコードして残りを保持
                                valid_part = byte_buffer[:e.start]
                                if valid_part:
                                    decoded = valid_part.decode('utf-8')
                                    if decoded.startswith("data: "):
                                        decoded = decoded[6:]
                                    content.append(decoded)
                                byte_buffer = byte_buffer[e.start:]
                                break
        
        elif response.get("contentType") == "application/json":
            # JSONレスポンスを処理 - 全体を結合してからデコード
            all_chunks = b''.join(response.get("response", []))
            if all_chunks:
                content.append(all_chunks.decode('utf-8'))
        
        else:
            content = response.get("response", [])
        
        return ''.join(content)
    
    # def _process_response(self, response: Dict[str, Any]) -> str:
    #     """AgentCoreランタイムレスポンスを処理"""
    #     content = []
        
    #     if "text/event-stream" in response.get("contentType", ""):
    #         # ストリーミングレスポンスを処理
    #         for line in response["response"].iter_lines(chunk_size=10):
    #             if line:
    #                 line = line.decode("utf-8")
    #                 if line.startswith("data: "):
    #                     line = line[6:]
    #                     content.append(line)
        
    #     elif response.get("contentType") == "application/json":
    #         # JSONレスポンスを処理
    #         for chunk in response.get("response", []):
    #             content.append(chunk.decode('utf-8'))
        
    #     else:
    #         content = response.get("response", [])
        
    #     return ''.join(content)


def load_agent_arn() -> str:
    """.bedrock_agentcore.yamlからエージェントARNを読み込み"""
    yaml_path = Path("../02_runtime/.bedrock_agentcore.yaml")
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {yaml_path}")
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    default_agent = config.get('default_agent')
    if not default_agent:
        raise ValueError("No default_agent specified in configuration")
    
    agent_config = config.get('agents', {}).get(default_agent, {})
    agent_arn = agent_config.get('bedrock_agentcore', {}).get('agent_arn')
    
    if not agent_arn:
        raise ValueError(f"No agent_arn found for agent: {default_agent}")
    
    return agent_arn


def main():
    """可観測性テストを実行するメイン関数"""
    logger.info("🚀 Starting AgentCore Observability Tests")
    
    try:
        # 設定からエージェントARNを読み込み
        agent_arn = load_agent_arn()
        logger.info(f"Loaded Agent ARN: {agent_arn}")
        
        # ARNからリージョンを抽出
        region = agent_arn.split(':')[3]
        logger.info(f"Region: {region}")
        
        tester = ObservabilityTester(agent_arn, region)
        
        # テスト1: 同一セッション内での複数の成功した呼び出し
        logger.info("\n" + "="*60)
        logger.info("Invoke test invocations in Same Session")
        logger.info("="*60)
        tester.test_multiple_invocations_same_session("user0001")
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    main()
