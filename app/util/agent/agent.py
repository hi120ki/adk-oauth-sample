#!/usr/bin/env python3
"""
ADK Agent client for managing sessions and interactions
"""

from __future__ import annotations

from typing import AsyncGenerator, Optional

from google.adk.agents import Agent
from google.adk.runners import Event, Runner
from google.adk.sessions import Session, VertexAiSessionService
from google.genai import types


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
        """Execute the agent and get response"""
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
                    except Exception as e:
                        print(f"Error extracting final response: {e}")
                        return "Sorry, an error occurred while processing the response."

            return "Sorry, an error occurred. No final response received."

        except Exception as e:
            print(f"Error in get_response: {e}")
            return f"An error occurred in getting response: {str(e)}"


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
        """Create a new session and return AgentSession instance"""
        try:
            session = await self.session_service.create_session(
                app_name=self.app_name, user_id=user_id, state=state
            )
            print(f"Created new session with ID: {session.id}")

            runner = Runner(
                agent=self.agent,
                app_name=self.app_name,
                session_service=self.session_service,
            )

            return AgentSession(session, runner, user_id)
        except Exception as e:
            print(f"Error creating session: {e}")
            raise e

    async def _get_session(self, user_id: str, session_id: str) -> AgentSession:
        """Get existing session and return AgentSession instance"""
        try:
            session = await self.session_service.get_session(
                app_name=self.app_name, user_id=user_id, session_id=session_id
            )

            runner = Runner(
                agent=self.agent,
                app_name=self.app_name,
                session_service=self.session_service,
            )

            return AgentSession(session, runner, user_id)
        except Exception as e:
            print(f"Session not found: {e}")
            raise e

    async def get_or_create_session(
        self, user_id: str, session_id: Optional[str] = None
    ) -> AgentSession:
        """Get existing session or create new one if not found"""
        if session_id:
            try:
                return await self._get_session(user_id, session_id)
            except Exception:
                print(f"Session ID {session_id} not found. Creating a new session.")

        return await self.create_session(user_id)
