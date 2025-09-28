import os

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines

load_dotenv()

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

agent_list = list(agent_engines.list())
if len(agent_list) == 0:
    agent_engines.create()
