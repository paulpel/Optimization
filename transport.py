import cplex
from cplex.exceptions import CplexError
import random
import timeit
import matplotlib.pyplot as plt


def generate_data(num_sources, num_destinations, supply_range, cost_range):
    """
    Generates random input data for the transportation problem.

    Args:
    num_sources (int): The number of supply sources.
    num_destinations (int): The number of demand destinations.
    supply_range (tuple): A tuple (min, max) representing the range of supply values.
    cost_range (tuple): A tuple (min, max) representing the range of transportation costs.

    Returns:
    tuple: A tuple containing the generated supply, demand, and costs lists.
    """
    # Generate random supply values for each source
    supply = [
        random.randint(supply_range[0], supply_range[1]) for _ in range(num_sources)
    ]

    # Calculate the total supply and distribute it among destinations
    total_supply = sum(supply)
    demand = [
        random.randint(1, total_supply // num_destinations)
        for _ in range(num_destinations - 1)
    ]
    demand.append(total_supply - sum(demand))

    # Generate random transportation costs for each source-destination pair
    costs = [
        random.randint(cost_range[0], cost_range[1])
        for _ in range(num_sources * num_destinations)
    ]

    return supply, demand, costs


def transportation_problem(supply, demand, costs, show=True):
    try:
        # Initialize CPLEX problem
        problem = cplex.Cplex()

        # Minimize the total transportation cost
        problem.objective.set_sense(problem.objective.sense.minimize)

        # Variables (x[i][j]): amount to be shipped from source i to destination j
        variables = [
            f"x{i}_{j}" for i in range(len(supply)) for j in range(len(demand))
        ]
        problem.variables.add(obj=costs, lb=[0] * len(variables), names=variables)

        # Constraints

        # Supply constraints: sum of shipments from each source i should not exceed its supply capacity
        for i in range(len(supply)):
            constraint = cplex.SparsePair(
                ind=[f"x{i}_{j}" for j in range(len(demand))], val=[1] * len(demand)
            )
            problem.linear_constraints.add(
                lin_expr=[constraint], senses=["L"], rhs=[supply[i]]
            )

        # Demand constraints: sum of shipments to each destination j should meet its demand requirement
        for j in range(len(demand)):
            constraint = cplex.SparsePair(
                ind=[f"x{i}_{j}" for i in range(len(supply))], val=[1] * len(supply)
            )
            problem.linear_constraints.add(
                lin_expr=[constraint], senses=["E"], rhs=[demand[j]]
            )

        # Solve the problem
        problem.solve()

        if show:
            # Print the solution
            print("Solution status:", problem.solution.get_status_string())
            print("Objective value:", problem.solution.get_objective_value())
            for i, x in enumerate(problem.solution.get_values()):
                if x > 0:
                    print(variables[i], "=", x)

    except CplexError as e:
        print("Exception raised:", e)


def measure_execution_time(
    num_sources, num_destinations, supply_range, cost_range, num_iterations, show
):
    def wrapper():
        supply, demand, costs = generate_data(
            num_sources, num_destinations, supply_range, cost_range
        )
        transportation_problem(supply, demand, costs, show)

    execution_time = timeit.timeit(wrapper, number=num_iterations)
    return execution_time / num_iterations


if __name__ == "__main__":
    # Parameters
    supply_range = (50, 100)
    cost_range = (1, 20)
    num_iterations = 1
    show = False

    time_s = []
    amount = []
    # Measure execution time for different numbers of sources and destinations
    for i in range(2, 200):
        execution_time = measure_execution_time(
            i, i, supply_range, cost_range, num_iterations, show
        )
        time_s.append(round(execution_time, 4))
        amount.append(i)
    plt.plot(amount, time_s)
    plt.title("Execution time and sum of suppliers and distributors")
    plt.ylabel("Time [s]")
    plt.xlabel("Sum of distributors and suplliers")
    plt.savefig("transport_time.png")
