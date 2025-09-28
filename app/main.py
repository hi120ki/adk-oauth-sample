import asyncio

import httpx
from authlib.integrations.requests_client import OAuth2Session
from google.adk.agents import Agent
from google.adk.sessions import VertexAiSessionService
from google.adk.tools import FunctionTool, ToolContext
from oauth.oauth import OAuthApp
from util.agent.agent import AgentClient
from util.config.config import Config
from util.credential.credential import Credential
from util.envelope.envelope_aead import EnvelopeAEAD

config = Config()

# https://google.github.io/adk-docs/sessions/state/#organizing-state-with-prefixes-scope-matters
# Using 'user:' prefix for proper scoping and persistence:
# - Scope: Tied to the user_id, shared across all sessions for that user (within the same app_name)
# - Persistence: Persistent with VertexAI SessionService
# - Use Case: This OAuth flow stores individual user's refresh tokens that need to persist across sessions
USER_GOOGLE_STATE_KEY = "user:google"

credential: Credential = Credential(
    envelope_aead=EnvelopeAEAD(kek_uri=config.gcp_kms_key_uri),
    oauth_session=OAuth2Session(
        client_id=config.google_client_id,
        client_secret=config.google_client_secret,
        token_endpoint="https://oauth2.googleapis.com/token",
    ),
)


async def get_user_profile_tool(tool_context: ToolContext, requires_email: bool) -> str:
    access_token = credential.get_access_token_from_context(
        tool_context=tool_context, state_key=USER_GOOGLE_STATE_KEY
    )
    if not access_token:
        return "Failed to obtain access token"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        user_info = response.json()

    if requires_email:
        return f"User profile: Name={user_info.get('name')}, Email={user_info.get('email')}"

    return f"User profile: Name={user_info.get('name')}"


agent = Agent(
    name="agent",
    model="gemini-2.5-flash",
    description="Agent to answer questions.",
    instruction="I can answer your questions by my own knowledge and available tools. Just ask me anything!",
    tools=[
        FunctionTool(get_user_profile_tool),
    ],
)

# https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations
agent_client = AgentClient(
    session_service=VertexAiSessionService(
        project=config.google_cloud_project,
        location=config.google_cloud_location,
    ),
    app_name=config.app_name,
    agent=agent,
)

# Initialize OAuth app
oauth_app = OAuthApp(
    config=config,
    agent_client=agent_client,
    credential=credential,
    scope="openid email profile",
    state_key=USER_GOOGLE_STATE_KEY,
)


async def main():
    """Start web server"""
    await asyncio.gather(oauth_app.start())


if __name__ == "__main__":
    asyncio.run(main())
