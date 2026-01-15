from workflow import graph
from workflow.state import AgentState

print(f"Graph imported successfully: {type(graph)}")

init_state = AgentState(
    initial_description="I want to apply for a divorce",
    iteration_count=0,
    answers_so_far={'questions': [], 'answers': []},
    is_ready=False,
    final_description=None,
    is_complete=False,
    error=None
)

test_final_state = AgentState(
    initial_description="I want to apply for a divorce, my spouse and I have been separated for 6 months.",
    answers_so_far={
        'questions': [
            "In which state, province, or country do you and your spouse currently reside?",
            "Do you have any children together, and if so, how old are they?",
            "When and where were you married?"
        ],
        'answers': [
            "We both reside in California.",
            "We have two children, ages 8 and 12.",
            "We were married in Las Vegas, Nevada, in 2010."
        ]
    },
    iteration_count=2,
    is_ready=False, # Set to True to allow the final description node to execute
    final_description=None,
    is_complete=False,
    error=None
)

config = {"configurable": {"thread_id": "1"}}


# run test
if __name__ == "__main__":
    result = graph.invoke(test_final_state, config=config)
    print(f"Result: {result}")
