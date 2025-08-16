"""
MarkdownをHTMLに変換してSES経由で送信するAgentCore Gateway用のシンプルなLambda関数

このLambda関数はMarkdownテキストとメールアドレスを受け取り、Markdownを
HTMLに変換して、Amazon SESを使用してHTMLメールとして送信します。
"""

import json
import logging
import os
import boto3
import markdown
from botocore.exceptions import ClientError

# ログ設定
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


def lambda_handler(event, context):
    """
    Gatewayからのmarkdown_to_emailツール呼び出しを処理
    
    Args:
        event: Markdownテキストとメールアドレスを含む
        context: Gatewayメタデータを含むLambdaコンテキスト。その`client_context`には以下が含まれる
        ClientContext(custom={
            'bedrockAgentCoreGatewayId': 'Y02ERAYBHB'
            'bedrockAgentCoreTargetId': 'RQHDN3J002'
            'bedrockAgentCoreMessageVersion': '1.0'
            'bedrockAgentCoreToolName': 'markdown_to_email'
            'bedrockAgentCoreSessionId': ''
        },env=None,client=None]

    Returns:
        メール送信操作の成功またはエラーメッセージ
    """
    try:
        # 受信リクエストをログ出力
        logger.info(f"Received event: {json.dumps(event)}")
        
        # コンテキストからツール名を抽出
        if context and context.client_context:
            logger.info(f"Context: {context.client_context}")
            tool_name = context.client_context.custom.get('bedrockAgentCoreToolName', '')
            
            # Gatewayによって追加されたプレフィックスを削除（形式: targetName___toolName）
            if "___" in tool_name:
                tool_name = tool_name.split("___")[-1]
        else:
            tool_name = event.get('tool_name', '')

        logger.info(f"Processing tool: {tool_name}")
        
        # これがmarkdown_to_emailツールであることを確認
        if tool_name != 'markdown_to_email':
            return {
                'statusCode': 400,
                'body': f"Unknown tool: {tool_name}"
            }
        
        # イベントから必要なパラメータを取得
        markdown_text = event.get('markdown_text', '')
        email_address = event.get('email_address', '')
        subject = event.get('subject', 'AWS Cost Estimation Result')
        
        if not markdown_text:
            return {
                'statusCode': 400,
                'body': "Missing required parameter: markdown_text"
            }
        
        if not email_address:
            return {
                'statusCode': 400,
                'body': "Missing required parameter: email_address"
            }

        # MarkdownをHTMLに変換してメールを送信
        result = convert_and_send_email(markdown_text, email_address, subject)

        return {
            'statusCode': 200,
            'body': result
        }
        
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }


def convert_and_send_email(markdown_text, email_address, subject):
    """
    MarkdownをHTMLに変換してAmazon SES経由で送信
    
    Args:
        markdown_text: 変換するMarkdownコンテンツ
        email_address: 受信者のメールアドレス
        subject: メールの件名
        
    Returns:
        メッセージIDを含む成功メッセージ
    """
    try:
        # テーブルサポート付きでMarkdownをHTMLに変換
        logger.info("Converting markdown to HTML")
        html_content = markdown.markdown(
            markdown_text,
            extensions=['tables', 'nl2br']
        )
        
        # 環境変数から送信者メールアドレスを取得
        sender_email = os.environ.get('SES_SENDER_EMAIL')
        if not sender_email:
            raise ValueError("SES_SENDER_EMAIL environment variable not set")
        
        # SESクライアントを初期化
        ses_client = boto3.client('ses')
        
        # SES経由でメールを送信
        logger.info(f"Sending email to: {email_address}")
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [email_address]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': html_content,
                        'Charset': 'UTF-8'
                    },
                    'Text': {
                        'Data': markdown_text,  # プレーンテキスト版を含める
                        'Charset': 'UTF-8'
                    }
                }
            }
        )

        message_id = response['MessageId']
        logger.info(f"Email sent successfully. Message ID: {message_id}")

        return f"Email sent successfully to {email_address}. Message ID: {message_id}"
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'MessageRejected':
            logger.error(f"SES rejected the message: {error_message}")
            raise Exception(f"Email rejected by SES: {error_message}")
        elif error_code == 'MailFromDomainNotVerified':
            logger.error(f"Sender domain not verified: {error_message}")
            raise Exception(f"Sender email domain not verified in SES: {error_message}")
        else:
            logger.error(f"SES error ({error_code}): {error_message}")
            raise Exception(f"SES error: {error_message}")
            
    except Exception as e:
        logger.exception(f"Unexpected error sending email: {e}")
        raise Exception(f"Failed to send email: {str(e)}")
