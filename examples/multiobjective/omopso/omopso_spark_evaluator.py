<<<<<<< HEAD:examples/multiobjective/omopso/omopso_spark_evaluator.py
from examples.multiobjective.zdt1_modified import ZDT1Modified
=======
from jmetal.util.solutions import SparkEvaluator

from examples.multiobjective.parallel.zdt1_modified import ZDT1Modified
>>>>>>> 62f5065855a15103e25bf874f08cf7a1355c9576:examples/multiobjective/parallel/omopso_spark_evaluator.py
from jmetal.algorithm.multiobjective.omopso import OMOPSO
from jmetal.operator import UniformMutation
from jmetal.operator.mutation import NonUniformMutation
from jmetal.util.archive import CrowdingDistanceArchive
<<<<<<< HEAD:examples/multiobjective/omopso/omopso_spark_evaluator.py
from jmetal.util.evaluator import SparkEvaluator
from jmetal.util.solution import print_function_values_to_file, print_variables_to_file, read_solutions
=======
from jmetal.util.solutions_utils import print_function_values_to_file, print_variables_to_file
from jmetal.util.solutions_utils import read_solutions
>>>>>>> 62f5065855a15103e25bf874f08cf7a1355c9576:examples/multiobjective/parallel/omopso_spark_evaluator.py
from jmetal.util.termination_criterion import StoppingByEvaluations

if __name__ == '__main__':
    problem = ZDT1Modified()
    problem.reference_front = read_solutions(filename='resources/reference_front/ZDT1.pf')
    mutation_probability = 1.0 / problem.number_of_variables

    max_evaluations = 100
    swarm_size = 10
    algorithm = OMOPSO(
        problem=problem,
        swarm_size=swarm_size,
        epsilon=0.0075,
        uniform_mutation=UniformMutation(probability=mutation_probability, perturbation=0.5),
        non_uniform_mutation=NonUniformMutation(mutation_probability, perturbation=0.5, max_iterations = max_evaluations/swarm_size),
        leaders=CrowdingDistanceArchive(10),
        termination_criterion=StoppingByEvaluations(max=max_evaluations),
        swarm_evaluator=SparkEvaluator(),
    )

    algorithm.run()
    front = algorithm.get_result()

    # Save results to file
    print_function_values_to_file(front, 'FUN.' + algorithm.get_name() + "." + problem.get_name())
    print_variables_to_file(front, 'VAR.'+ algorithm.get_name() + "." + problem.get_name())

    print('Algorithm (continuous problem): ' + algorithm.get_name())
    print('Problem: ' + problem.get_name())
    print('Computing time: ' + str(algorithm.total_computing_time))