"""
Test the AgentCore Identity by invoking cost_estimator_agent_with_identity

This script demonstrates how to:
1. Obtain an OAuth token from AgentCore Identity
2. Call the Runtime with obtained token
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

# Configure logging with more verbose output
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


@tool(name="cost_estimator_tool", description="Estimate cost of AWS from architecture description")
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
    """Main test function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test AgentCore Gateway with different methods')
    parser.add_argument(
        '--architecture',
        type=str,
        default="A simple web application with an Application Load Balancer, 2 EC2 t3.medium instances, and an RDS MySQL database in us-east-1.",
        help='Architecture description for cost estimation. Default: A simple web application with ALB, 2 EC2 instances, and RDS MySQL'
    )
    args = parser.parse_args()

    agent = Agent(
        system_prompt=(
            "Your are a professional solution architect. "
            "You will receive architecture descriptions or requirements from customers. "
            "Please provide estimate by using 'cost_estimator_tool'"
        ),
        tools=[cost_estimator_tool]
    )

    logger.info("Invoke agent that calls Runtime with Identity...")
    await agent.invoke_async(args.architecture)
    logger.info("✅ Successfully called agent!")


if __name__ == "__main__":
    asyncio.run(main())
