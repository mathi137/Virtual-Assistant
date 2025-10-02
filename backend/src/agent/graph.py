from langgraph.graph import StateGraph, END, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.mysql.aio import AIOMySQLSaver

from src.agent.state import AgentState
from src.agent.nodes import (
    entry_node,
    answer_node,
    save_message_node,
    AgentNodes,
)


class AgentGraph:
    def __init__(self) -> None:
        self._workflow = StateGraph(AgentState)

    async def build_graph(self, checkpointer: AIOMySQLSaver) -> CompiledStateGraph:
        self._workflow.add_node(AgentNodes.ENTRY, entry_node)
        self._workflow.add_node(AgentNodes.ANSWER, answer_node)
        self._workflow.add_node(AgentNodes.SAVE_MESSAGE, save_message_node)

        self._workflow.add_edge(START, AgentNodes.ENTRY)
        self._workflow.add_edge(AgentNodes.ENTRY, AgentNodes.ANSWER)
        self._workflow.add_edge(AgentNodes.ANSWER, AgentNodes.SAVE_MESSAGE)
        self._workflow.add_edge(AgentNodes.SAVE_MESSAGE, END)

        # Use the global checkpointer instance
        return self._workflow.compile(checkpointer=checkpointer)
