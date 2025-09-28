#!/usr/bin/env python3
"""
ADK Agent client for managing sessions and interactions
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator, Optional

from google.adk.agents import Agent
from google.adk.runners import Event, Runner
from google.adk.sessions import Session, VertexAiSessionService
from google.genai import types

logger = logging.getLogger(__name__)


class AgentClientError(Exception):
    """Custom exception for AgentClient errors."""

    pass


_RESPONSE_ERROR = "Sorry, an internal error occurred while processing the response."


class AgentSession:
    """Manages an agent session with conversation state."""

    def __init__(self, session: Session, runner: Runner, user_id: str) -> None:
        self.session: Session = session
        self.runner: Runner = runner
        self.user_id: str = user_id

    @property
    def session_id(self) -> str:
        return self.session.id

    async def get_response(self, query: str) -> str:
        """Execute the agent and get response."""
        try:
            content = types.Content(role="user", parts=[types.Part(text=query)])
            events: AsyncGenerator[Event, None] = self.runner.run_async(
                user_id=self.user_id, session_id=self.session.id, new_message=content
            )

            async for event in events:
                if event.is_final_response():
                    try:
                        final_response: str = event.content.parts[0].text
                        return final_response
                    except Exception:
                        logger.exception(
                            "Failed to extract final response user_id=%s session_id=%s",
                            self.user_id,
                            self.session.id,
                        )
                        return _RESPONSE_ERROR

            return _RESPONSE_ERROR

        except Exception:
            logger.exception(
                "Agent execution failed user_id=%s session_id=%s",
                self.user_id,
                self.session.id,
            )
            return _RESPONSE_ERROR


class AgentClient:
    """Client for managing agent sessions and interactions."""

    def __init__(
        self,
        session_service: VertexAiSessionService,
        app_name: str,
        agent: Agent,
    ) -> None:
        self.session_service: VertexAiSessionService = session_service
        self.app_name: str = app_name
        self.agent: Agent = agent

    async def create_session(
        self, user_id: str, state: Optional[dict] = None
    ) -> AgentSession:
        """Create a new session and return AgentSession instance."""
        try:
            session = await self.session_service.create_session(
                app_name=self.app_name, user_id=user_id, state=state
            )
        except Exception as exc:
            logger.exception("Failed to create session for user_id=%s", user_id)
            raise AgentClientError("Failed to create session") from exc

        runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )

        return AgentSession(session, runner, user_id)

    async def _get_session(self, user_id: str, session_id: str) -> AgentSession:
        """Get existing session and return AgentSession instance."""
        try:
            session = await self.session_service.get_session(
                app_name=self.app_name, user_id=user_id, session_id=session_id
            )
        except Exception as exc:
            logger.exception(
                "Failed to load existing session user_id=%s session_id=%s",
                user_id,
                session_id,
            )
            raise AgentClientError("Failed to load existing session") from exc

        runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )

        return AgentSession(session, runner, user_id)

    async def get_or_create_session(
        self, user_id: str, session_id: Optional[str] = None
    ) -> AgentSession:
        """Get existing session or create new one if not found."""
        if session_id:
            try:
                return await self._get_session(user_id, session_id)
            except Exception as exc:
                logger.exception(
                    "Failed to get existing session, creating a new one user_id=%s session_id=%s",
                    user_id,
                    session_id,
                )
                raise AgentClientError("Failed to get existing session") from exc

        return await self.create_session(user_id)
