#!/usr/bin/env python3
"""
OAuth and web application management
"""

import html
from typing import Optional, TypedDict

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from util.agent.agent import AgentClient
from util.config.config import Config
from util.credential.credential import Credential


class GoogleUserInfo(TypedDict):
    iss: str
    azp: str
    aud: str
    sub: str
    hd: str
    email: str
    email_verified: bool
    at_hash: str
    nonce: str
    name: str
    picture: str
    given_name: str
    family_name: str
    iat: int
    exp: int


class GoogleOAuthToken(TypedDict):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str
    id_token: str
    expires_at: int
    userinfo: GoogleUserInfo


class UserSession(TypedDict):
    email: str
    name: str


class OAuthApp:
    """
    OAuth web application manager
    """

    def __init__(
        self,
        config: Config,
        agent_client: AgentClient,
        credential: Credential,
        scope: str,
        state_key: str,
    ):
        """
        Initialize OAuth application with required dependencies

        Args:
            config: Configuration instance
            agent_client: Agent client instance
            credential: Credential management instance
            state_key: State key for Google user data
        """
        self.config = config
        self.agent_client = agent_client
        self.credential = credential
        self.state_key = state_key

        # Initialize Starlette app
        self.app: Starlette = Starlette()
        self.app.add_middleware(SessionMiddleware, secret_key=config.session_secret_key)

        # Initialize OAuth
        self.oauth: OAuth = OAuth()
        self.oauth.register(
            name="google",
            client_id=config.google_client_id,
            client_secret=config.google_client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={
                "scope": scope,
                "prompt": "select_account",
            },
        )

        # Register routes
        self._register_routes()

    def _register_routes(self) -> None:
        """Register all application routes"""
        self.app.add_route("/", self.index)
        self.app.add_route("/login", self.login)
        self.app.add_route("/callback", self.callback)
        self.app.add_route("/logout", self.logout)
        self.app.add_route("/llm", self.llm)

    async def index(self, request: Request) -> Response:
        """Home page route"""
        user: Optional[UserSession] = request.session.get("user")
        if user:
            content: str = f"""
            <h2>Hello, {html.escape(user['name'])}!</h2>
            <p>You are logged in as: <strong>{html.escape(user['email'])}</strong></p>
            <p>Use the <a href="/llm">/llm</a> endpoint to test the interaction with the AI Agent.</p>
            <a href="/logout">Logout</a>
            """
            return HTMLResponse(content)
        return RedirectResponse(url="/login")

    async def login(self, request: Request) -> RedirectResponse:
        """Login route"""
        google_client: StarletteOAuth2App = self.oauth.google
        redirect_uri: str = self.config.redirect_uri
        return await google_client.authorize_redirect(
            request,
            redirect_uri,
            code_challenge_method="S256",
            prompt="consent",
            access_type="offline",
            include_granted_scopes="true",
        )

    async def callback(self, request: Request) -> Response:
        """OAuth callback route"""
        try:
            google_client: StarletteOAuth2App = self.oauth.google
            token: GoogleOAuthToken = await google_client.authorize_access_token(
                request
            )

            if not token or not token.get("userinfo") or not token.get("refresh_token"):
                return HTMLResponse(
                    """
                    <h2>Authentication Error</h2>
                    <p>Authentication failed. Please try logging in again.</p>
                    <a href="/login">Login</a>
                    """
                )

            userinfo: GoogleUserInfo = token["userinfo"]
            user_session: UserSession = {
                "email": userinfo["email"],
                "name": userinfo["name"],
            }

            await self.agent_client.create_session(
                user_id=userinfo["email"],
                state={
                    self.state_key: self.credential.encrypt_token(
                        token["refresh_token"], userinfo["email"]
                    )
                },
            )
            request.session["user"] = user_session
            return RedirectResponse(url="/")

        except Exception as e:
            return HTMLResponse(
                f"""
                <h2>Authentication Error</h2>
                <p>Error during authentication: {html.escape(str(e))}</p>
                <a href="/login">Login</a>
                """
            )

    async def logout(self, request: Request) -> RedirectResponse:
        """Logout route"""
        request.session.pop("user", None)
        return RedirectResponse(url="/")

    async def llm(self, request: Request) -> Response:
        """LLM interaction route"""
        user_id_header = request.headers.get("x-goog-authenticated-user-email")
        if not user_id_header:
            return HTMLResponse(
                "<h2>Error:</h2><p>x-goog-authenticated-user-email header is required. Please enable IAP for this workload.</p>",
                status_code=400,
            )
        user_id = user_id_header.removeprefix("accounts.google.com:")
        if not user_id:
            return HTMLResponse(
                "<h2>Error:</h2><p>Invalid user email format</p>", status_code=400
            )

        agent_session = await self.agent_client.get_or_create_session(user_id)
        response: str = await agent_session.get_response(
            "Please use get_user_profile_tool to fetch user profile information with email address."
        )
        return HTMLResponse(f"<h2>LLM Response:</h2><p>{html.escape(response)}</p>")

    async def start(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """
        Start web server

        Args:
            host: Host address to bind to
            port: Port number to bind to (defaults to config.port if not specified)
        """
        import uvicorn

        if port is None:
            port = self.config.port

        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()
