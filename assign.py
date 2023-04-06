import cplex
import numpy as np

def assign_problem(circles, flows, n):
    # Problem definition
    problem = cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.minimize)

    # Variables
    x = [f"x{i}" for i in range(n)]
    y = [f"y{i}" for i in range(n)]
    d = [f"d{i}{j}" for i in range(n) for j in range(n) if i != j]

    problem.variables.add(names=x + y, lb=[0] * (2 * n), ub=[float("inf")] * (2 * n))
    problem.variables.add(names=d, lb=[0] * len(d), ub=[float("inf")] * len(d))

    # Constraints
    for i, circle in enumerate(circles):
        a, b, r = circle
        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[i], y[i]], val=[1, 1])],
            senses=["L"],
            rhs=[a + r],
            names=[f"circle_x_ub_{i}"],
        )
        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[i], y[i]], val=[-1, -1])],
            senses=["L"],
            rhs=[r - a],
            names=[f"circle_x_lb_{i}"],
        )
        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[i], y[i]], val=[1, -1])],
            senses=["L"],
            rhs=[b + r],
            names=[f"circle_y_ub_{i}"],
        )
        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[i], y[i]], val=[-1, 1])],
            senses=["L"],
            rhs=[r - b],
            names=[f"circle_y_lb_{i}"],
        )

    # Objective function
    objective_terms = [(d[idx], flows[i][j]) for idx, (i, j) in enumerate([(i, j) for i in range(n) for j in range(n) if i != j])]
    problem.objective.set_linear(objective_terms)

    # Constraints for auxiliary variables d
    for idx, (i, j) in enumerate([(i, j) for i in range(n) for j in range(n) if i != j]):
        problem.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=[x[i], x[j], y[i], y[j], d[idx]],
                    val=[2, -2, 2, -2, -1]
                )
            ],
            senses=["L"],
            rhs=[0],
            names=[f"aux_distance_{i}{j}_lb"],
        )
        problem.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=[x[i], x[j], y[i], y[j], d[idx]],
                    val=[-2, 2, -2, 2, -1]
                )
            ],
            senses=["L"],
            rhs=[0],
            names=[f"aux_distance_{i}{j}_ub"],
        )

    # Solve the problem
    problem.solve()



    # Output solution
    print(f"Solution status: {problem.solution.get_status_string()}")
    print(f"Objective value: {problem.solution.get_objective_value()}")

    for i in range(n):
        xi = problem.solution.get_values(x[i])
        yi = problem.solution.get_values(y[i])
        print(f"({xi}, {yi})")

def generate_connected_data(n, min_coord=0, max_coord=10, min_radius=1, max_radius=5, max_flow=10):
    """
    Generates random input data for the problem, ensuring that the circles are connected.
    
    Args:
        n: The number of facilities.
        min_coord: The minimum absolute value of x and y coordinates for circles.
        max_coord: The maximum absolute value of x and y coordinates for circles.
        min_radius: The minimum radius for circles.
        max_radius: The maximum radius for circles.
        max_flow: The maximum flow value between facilities.
        
    Returns:
        circles: A list of n tuples (a_i, b_i, r_i) representing the circles.
        flows: A nested list of size n x n representing the flows between facilities.
    """
    circles = []
    for _ in range(n):
        while True:
            circle = (np.random.uniform(min_coord, max_coord),
                      np.random.uniform(min_coord, max_coord),
                      np.random.uniform(min_radius, max_radius))
            if len(circles) == 0 or any(np.sqrt((circle[0] - c[0])**2 + (circle[1] - c[1])**2) <= circle[2] + c[2] for c in circles):
                circles.append(circle)
                break

    flows = np.random.randint(0, max_flow, size=(n, n))
    np.fill_diagonal(flows, 0)

    return circles, flows.tolist()

if __name__ == "__main__":
    n = 5
    circles, flows = generate_connected_data(n)
    print("Circles:", circles)
    print("Flows:", flows)

    assign_problem(circles, flows, n)
