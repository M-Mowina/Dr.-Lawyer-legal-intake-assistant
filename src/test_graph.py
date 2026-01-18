from workflow import graph
from workflow.state import AgentState
from workflow.graph import DB_URL
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver 

print(f"Graph imported successfully: {type(graph)}")

init_state = AgentState("Some one assaulted me and i want to raise a case!")

config = {"configurable": {"thread_id": "1"}}


async def run_test():
    async with AsyncPostgresSaver.from_conn_string(DB_URL) as checkpointer:
        graph.checkpointer = checkpointer
        result = await graph.ainvoke(init_state, config=config)
        print(f"Result: {result}")

# run test
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_test())
