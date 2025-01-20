import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from utils import load_yaml_config, create_methods


@CrewBase
class DynamicAgentCrew:
    """DynamicAgentCrew class to dynamically create agents and tasks from YAML configurations."""

    base_dir = os.path.dirname(__file__)  # Base directory of the script
    agents_config_file = os.path.join(base_dir, 'config', 'agents.yaml')
    tasks_config_file = os.path.join(base_dir, 'config', 'tasks.yaml')
    crew_config_file = os.path.join(base_dir, 'config', 'crew.yaml')

    def __init__(self):
        # Load YAML configurations
        self.agents_config = load_yaml_config(self.agents_config_file)
        self.tasks_config = load_yaml_config(self.tasks_config_file)
        self.crew_config = load_yaml_config(self.crew_config_file)

        # Mappings for dynamically created methods
        self.agent_methods = {}
        self.task_methods = {}

        # Initialize agents and tasks
        create_methods(self.agents_config, self._create_agent_method, self.agent_methods, agent, self.__class__)
        create_methods(self.tasks_config, self._create_task_method, self.task_methods, task, self.__class__)

    def _create_agent_method(self, agent_name, config):
        """Creates a method for an agent."""
        def agent_method(self) -> Agent:
            return Agent(config=config, verbose=True)
        return agent_method

    def _create_task_method(self, task_name, config):
        """Creates a method for a task."""
        def task_method(self) -> Task:
            agent_name = config.get("agent")
            agent = self.get_agent_by_name(agent_name)
            return Task(config=config, agent=agent, output_file=config.get("output_file"))
        return task_method

    def get_agent_by_name(self, agent_name):
        """
        Retrieves a dynamically created agent by its name.

        :param agent_name: Name of the agent.
        :return: Instance of the agent.
        :raises ValueError: If the agent does not exist.
        """
        if agent_name not in self.agent_methods:
            raise ValueError(f"Agent '{agent_name}' not found.")
        return self.agent_methods[agent_name](self)

    def get_task_by_name(self, task_name):
        """
        Retrieves a dynamically created task by its name.

        :param task_name: Name of the task.
        :return: Instance of the task.
        :raises ValueError: If the task does not exist.
        """
        if task_name not in self.task_methods:
            raise ValueError(f"Task '{task_name}' not found.")
        return self.task_methods[task_name](self)

    @crew
    def crew(self) -> Crew:
        """
        Creates the DynamicAgentCrew with configurations loaded dynamically.

        :return: Instance of the Crew object.
        """
        agents = [self.get_agent_by_name(name) for name in self.crew_config['agents']]
        tasks = [self.get_task_by_name(name) for name in self.crew_config['tasks']]
        process = Process[self.crew_config['process']]
        verbose = self.crew_config['verbose']

        return Crew(
            agents=agents,
            tasks=tasks,
            process=process,
            verbose=verbose,
        )