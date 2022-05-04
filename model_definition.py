from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np

class Prey(Agent):

    def __init__(self, id, model):
        super().__init__(id, model)

    def step(self):
        print(f'My current position is: {self.pos}')
        neighborhood = self.model.grid.get_neighborhood(
                                self.pos, 
                                moore = True, 
                                include_center = False)
        self.move(neighborhood)

    def move(self, neighborhood):
        new_pos = self.random.choice(neighborhood)
        print(f'I am moving to {new_pos}')
        self.model.grid.move_agent(self, new_pos)

class Predator(Agent):

    def __init__(self, id, model):
        super().__init__(id, model)
        self.energy = 100

    def step(self):
        print(f'My current position is: {self.pos}')
        neighborhood = self.model.grid.get_neighborhood(
                                self.pos, 
                                moore = True, 
                                include_center = False)

        self.move(neighborhood)
        self.eat()

        if self.energy == 0:
            self.model.current_predator -= 1
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def move(self, neighborhood):
        new_pos = self.random.choice(neighborhood)
        print(f'I am a predator moving from {self.pos} to {new_pos}')
        self.model.grid.move_agent(self, new_pos)
        self.energy -= 1

    def eat(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            for mate in cellmates:
                if isinstance(mate, Prey):
                    print(f'The prey {mate.unique_id} is in the position {self.pos} with me! I am gonna eat it!')
                    self.model.grid.remove_agent(mate)
                    self.model.schedule.remove(mate)
                    self.model.current_prey -= 1
                    print(f'My energy is {self.energy}')
                    self.energy += 5
                    print(f'After eating, it now is {self.energy}')
                    self.energy = min(100, self.energy)
        else: pass

            

class ABM(Model):

    def __init__(self, N_prey, N_predator, w, h):
        self.num_predator = N_predator
        self.num_prey = N_prey
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(w, h, False)
        self.current_prey = self.num_prey
        self.current_predator = self.num_predator

        # Gerando presas
        for i in range(self.num_prey):
            new_agent = Prey(i, self)
            self.schedule.add(new_agent)

            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(new_agent, (x, y))

        # Gerando predatores
        for i in range(self.num_predator):
            new_agent = Predator(N_prey + i, self)
            self.schedule.add(new_agent)

            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(new_agent, (x, y))

        self.datacollector = DataCollector(
            model_reporters = {"agent count": lambda m: m.schedule.get_agent_count(),
                                "prey count": lambda m: m.current_prey,
                                "predator count": lambda m: m.current_predator}, 
            agent_reporters = {"predator energy": lambda a: a.energy if isinstance(a, Predator) else None})

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()