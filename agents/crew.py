"""EVSync multi-agent crew. Check the CrewAI docs for API changes between versions."""
import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import SerperDevTool
from tools.evsync_tools import (country_snapshot, worldbank_indicator, tco_calculator,
                                ev_share_forecast, oil_displacement, mineral_concentration)


def _llm(env, default):
    return LLM(model=os.getenv(env, default), temperature=0.2)


@CrewBase
class EVSyncCrew:
    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    def __init__(self, on_step=None, on_task=None):
        self.on_step, self.on_task = on_step, on_task
        self.cheap = _llm("EVSYNC_MODEL", "gpt-4o-mini")
        self.strong = _llm("EVSYNC_STRATEGIST_MODEL", "gpt-4o")
        self.search = SerperDevTool()

    # ---- agents ----
    @agent
    def data_researcher(self) -> Agent:
        return Agent(config=self.agents_config["data_researcher"], llm=self.cheap, max_iter=5,
                     tools=[self.search, worldbank_indicator, country_snapshot])

    @agent
    def policy_analyst(self) -> Agent:
        return Agent(config=self.agents_config["policy_analyst"], llm=self.cheap, max_iter=5,
                     tools=[self.search, country_snapshot])

    @agent
    def supply_chain_analyst(self) -> Agent:
        return Agent(config=self.agents_config["supply_chain_analyst"], llm=self.cheap, max_iter=5,
                     tools=[self.search, mineral_concentration])

    @agent
    def economist(self) -> Agent:
        return Agent(config=self.agents_config["economist"], llm=self.cheap, max_iter=6,
                     tools=[country_snapshot, tco_calculator, oil_displacement])

    @agent
    def forecaster(self) -> Agent:
        return Agent(config=self.agents_config["forecaster"], llm=self.cheap, max_iter=4,
                     tools=[ev_share_forecast])

    @agent
    def strategist(self) -> Agent:
        return Agent(config=self.agents_config["strategist"], llm=self.strong, max_iter=3)

    @agent
    def fact_checker(self) -> Agent:
        return Agent(config=self.agents_config["fact_checker"], llm=self.strong, max_iter=3)

    # ---- tasks ----
    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"], async_execution=True)

    @task
    def policy_task(self) -> Task:
        return Task(config=self.tasks_config["policy_task"], async_execution=True)

    @task
    def supply_chain_task(self) -> Task:
        return Task(config=self.tasks_config["supply_chain_task"], async_execution=True)

    @task
    def economics_task(self) -> Task:
        return Task(config=self.tasks_config["economics_task"])

    @task
    def forecast_task(self) -> Task:
        return Task(config=self.tasks_config["forecast_task"])

    @task
    def strategy_task(self) -> Task:
        return Task(config=self.tasks_config["strategy_task"],
                    context=[self.research_task(), self.policy_task(), self.supply_chain_task(),
                             self.economics_task(), self.forecast_task()])

    @task
    def factcheck_task(self) -> Task:
        return Task(config=self.tasks_config["factcheck_task"], context=[self.strategy_task()])

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential,
                    verbose=True, step_callback=self.on_step, task_callback=self.on_task)
