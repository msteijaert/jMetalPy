import logging
import os
from pathlib import Path
from typing import List, TypeVar

from tqdm import tqdm

from jmetal.core.observable import Observer
from jmetal.core.problem import DynamicProblem
from jmetal.core.quality_indicator import InvertedGenerationalDistance
from jmetal.util.solution_list import print_function_values_to_file
from jmetal.util.visualization import StreamingPlot, IStreamingPlot, Plot

S = TypeVar('S')

LOGGER = logging.getLogger('jmetal')

"""
.. module:: observer
   :platform: Unix, Windows
   :synopsis: Implementation of algorithm's observers.

.. moduleauthor:: Antonio J. Nebro <antonio@lcc.uma.es>
"""


class ProgressBarObserver(Observer):

    def __init__(self, max: int) -> None:
        """ Show a smart progress meter with the number of evaluations and computing time.

        :param max: Number of expected iterations.
        :param desc: Prefix for the progressbar.
        """
        self.progress_bar = None
        self.progress = 0
        self.maxx = max

    def update(self, *args, **kwargs):
        if not self.progress_bar:
            self.progress_bar = tqdm(total=self.maxx, ascii=True, desc='Progress')

        evaluations = kwargs['EVALUATIONS']

        self.progress_bar.update(evaluations - self.progress)
        self.progress = evaluations

        if self.progress >= self.maxx:
            self.progress_bar.close()


class BasicObserver(Observer):

    def __init__(self, frequency: float = 1.0) -> None:
        """ Show the number of evaluations, best fitness and computing time.

        :param frequency: Display frequency. """
        self.display_frequency = frequency

    def update(self, *args, **kwargs):
        computing_time = kwargs['COMPUTING_TIME']
        evaluations = kwargs['EVALUATIONS']
        solutions = kwargs['SOLUTIONS']

        if (evaluations % self.display_frequency) == 0 and solutions:
            if type(solutions) == list:
                fitness = solutions[0].objectives
            else:
                fitness = solutions.objectives

            LOGGER.info(
                'Evaluations: {} \n Best fitness: {} \n Computing time: {}'.format(
                    evaluations, fitness, computing_time
                )
            )


class WriteFrontToFileObserver(Observer):

    def __init__(self, output_directory: str) -> None:
        """ Write function values of the front into files.

        :param output_directory: Output directory. Each front will be saved on a file `FUN.x`. """
        self.counter = 0
        self.directory = output_directory

        if Path(self.directory).is_dir():
            LOGGER.warning('Directory {} exists. Removing contents.'.format(self.directory))
            for file in os.listdir(self.directory):
                os.remove('{0}/{1}'.format(self.directory, file))
        else:
            LOGGER.warning('Directory {} does not exist. Creating it.'.format(self.directory))
            Path(self.directory).mkdir(parents=True)

    def update(self, *args, **kwargs):
        solutions = kwargs['SOLUTIONS']

        if solutions:
            print_function_values_to_file(solutions, '{}/FUN.{}'.format(self.directory, self.counter))
            self.counter += 1


class PlotFrontToFileObserver(Observer):

    def __init__(self,
                 output_directory: str) -> None:
        self.directory = output_directory
        self.plot_front = Plot(plot_title='Front approximation')
        self.last_front = []
        self.fronts = []
        self.counter = 0

        if Path(self.directory).is_dir():
            LOGGER.warning('Directory {} exists. Removing contents.'.format(self.directory))
            for file in os.listdir(self.directory):
                os.remove('{0}/{1}'.format(self.directory, file))
        else:
            LOGGER.warning('Directory {} does not exist. Creating it.'.format(self.directory))
            Path(self.directory).mkdir(parents=True)

    def update(self, *args, **kwargs):
        problem = kwargs['PROBLEM']
        solutions = kwargs['SOLUTIONS']

        if solutions and isinstance(problem, DynamicProblem):
            termination_criterion_is_met = kwargs.get('termination_criterion_is_met', None)

            if termination_criterion_is_met:
                if self.counter > 0:
                    igd = InvertedGenerationalDistance(self.last_front)
                    igd_value = igd.compute(solutions)
                else:
                    igd_value = 1

                if igd_value > 0.005:
                    self.fronts += solutions
                    self.plot_front.plot([self.fronts],
                                         label=[problem.get_name()],
                                         filename='{}/jmetalpy-{}'.format(self.directory, self.counter))

                self.counter += 1
                self.last_front = solutions
        else:
            evaluations = kwargs['EVALUATIONS']
            self.plot_front.plot([solutions],
                                 filename='{}/jmetalpy-{}'.format(self.directory, evaluations))


class VisualizerObserver(Observer):

    def __init__(self,
                 reference_front: List[S] = None,
                 reference_point: List[float] = None,
                 display_frequency: float = 1.0) -> None:
        self.figure = None
        self.display_frequency = display_frequency

        self.reference_point = reference_point
        self.reference_front = reference_front

    def update(self, *args, **kwargs):
        evaluations = kwargs['EVALUATIONS']
        solutions = kwargs['SOLUTIONS']

        if solutions:
            if self.figure is None:
                self.figure = StreamingPlot(plot_title='Pareto front approximation',
                                            reference_point=self.reference_point,
                                            reference_front=self.reference_front)
                self.figure.plot(solutions)

            if (evaluations % self.display_frequency) == 0:
                self.figure.update(solutions)
                self.figure.ax.set_title('Eval: {}'.format(evaluations), fontsize=13)


class IVisualizerObserver(Observer):

    def __init__(self,
                 reference_front: List[S] = None,
                 reference_point: List[float] = None,
                 display_frequency: float = 1.0) -> None:
        self.figure = None
        self.display_frequency = display_frequency

        self.reference_point = reference_point
        self.reference_front = reference_front

    def update(self, *args, **kwargs):
        evaluations = kwargs['EVALUATIONS']
        solutions = kwargs['SOLUTIONS']

        if solutions:
            if self.figure is None:
                self.figure = IStreamingPlot(plot_title='Pareto front approximation',
                                             reference_point=self.reference_point,
                                             reference_front=self.reference_front)
                self.figure.plot(solutions)

            if (evaluations % self.display_frequency) == 0:
                self.figure.update(solutions)