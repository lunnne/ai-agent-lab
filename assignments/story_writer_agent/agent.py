from google.adk.agents import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent


story_writer = LlmAgent(
    name="story_writer",
    model="gemini-2.0-flash",
    instruction="""
Create a 5 page children's story.

Return JSON only.

Format:
[
 { "page":1, "text":"...", "visual":"..." }
]

Must be Korean.
Must be exactly 5 pages.
""",
    output_key="storybook_pages",
)

illustrator = LlmAgent(
    name="illustrator",
    model="gemini-2.0-flash",
    instruction="""
Read storybook_pages from state.

For each page show:

Page X
Text:
Visual:
Image: generated
""",
)

root_agent = SequentialAgent(
    name="pipeline",
    sub_agents=[story_writer, illustrator],
)