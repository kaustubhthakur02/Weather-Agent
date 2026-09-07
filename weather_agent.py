from agent import run_agent

if __name__ == "__main__":
    input_query = input("Enter your weather query: ")
    final_output = run_agent(input_query, on_step=print)
    print(final_output)
