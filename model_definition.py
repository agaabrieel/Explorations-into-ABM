from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import pyglet

class Food(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)
        self.amount = 30
        self.sprite = None

    def step(self):
        self.amount = min(50, self.amount + 1)

        if self.amount == 0:
            self.model.food_sources.remove(self)
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

class Prey(Agent):

    def __init__(self, id, model):
        super().__init__(id, model)
        self.energy = 500
        self.sprite = None

    def step(self):
        neighborhood = self.model.grid.get_neighborhood(
                                self.pos, 
                                moore = True, 
                                include_center = False)
        self.eat()
        self.move(neighborhood)
        self.eat()
        self.reproduce()

        if self.energy == 0:
            self.model.current_prey.remove(self)
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def move(self, neighborhood):
        new_pos = self.random.choice(neighborhood)
        self.energy -= 1
        self.model.grid.move_agent(self, new_pos)

    def eat(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            for mate in cellmates:
                if isinstance(mate, Food):
                    mate.amount -= 1
                    self.model.grid.remove_agent(mate)
                    self.model.schedule.remove(mate)
                    self.energy = min(1000, self.energy + 5)
        else: pass

    def reproduce(self):
        if self.energy/1000 >= 0.9:
            self.energy *= 0.5
            child = Prey(self.model.random.randint(10000000, 1000000000), self.model)
            self.model.schedule.add(child)
            self.model.current_prey.append(child)
            print("I'm a prey and I just reproduced!!")

            x, y = self.pos[0], self.pos[1]
            self.model.grid.place_agent(child, (x, y))
            child.sprite = pyglet.shapes.Circle(child.pos[0] + 200, child.pos[1] + 50, 1, color = (0, 0, 255))

class Predator(Agent):

    def __init__(self, id, model):
        super().__init__(id, model)
        self.energy = 250
        self.sprite = None

    def step(self):
        neighborhood = self.model.grid.get_neighborhood(
                                self.pos, 
                                moore = True, 
                                include_center = False)

        self.eat()
        self.move(neighborhood)
        self.eat()
        self.reproduce()

        if self.energy == 0:
            self.model.current_predator.remove(self)
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def move(self, neighborhood):
        new_pos = self.random.choice(neighborhood)
        self.model.grid.move_agent(self, new_pos)
        self.energy -= 1

    def eat(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            for mate in cellmates:
                if isinstance(mate, Prey):
                    self.model.current_prey.remove(mate)
                    self.model.grid.remove_agent(mate)
                    self.model.schedule.remove(mate)
                    self.energy = min(500, self.energy + 5)
        else: pass

    def reproduce(self):
        if self.energy/500 >= 0.95:
            self.energy *= 0.5
            child = Predator(self.model.random.randint(10000000, 1000000000), self.model)
            self.model.schedule.add(child)
            self.model.current_predator.append(child)
            print("I'm a predator and I just reproduced!!")

            x, y = self.pos[0], self.pos[1]
            self.model.grid.place_agent(child, (x, y))
            child.sprite = pyglet.shapes.Circle(child.pos[0] + 200, child.pos[1] + 50, 1, color = (255, 0, 0))            

class ABM(Model):

    def __init__(self, N_prey, N_predator, N_food, w, h):
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(w, h, True)
        self.current_prey = []
        self.current_predator = []
        self.food_sources = []

        # Gerando presas
        for i in range(N_prey):
            new_agent = Prey(i, self)
            self.current_prey.append(new_agent)
            self.schedule.add(new_agent)

            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(new_agent, (x, y))
            new_agent.sprite = pyglet.shapes.Circle(new_agent.pos[0] + 200, new_agent.pos[1] + 50, 1, color = (0, 0, 255))

        # Gerando predadores
        for i in range(N_predator):
            new_agent = Predator(N_prey + i, self)
            self.current_predator.append(new_agent)
            self.schedule.add(new_agent)

            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(new_agent, (x, y))
            new_agent.sprite = pyglet.shapes.Circle(new_agent.pos[0] + 200, new_agent.pos[1] + 50, 1, color = (255, 0, 0))

        # Gerando alimento para presas
        for i in range(N_food):
            new_agent = Food(N_prey + N_predator + i, self)
            self.schedule.add(new_agent)
            self.food_sources.append(new_agent)

            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(new_agent, (x, y))
            new_agent.sprite = pyglet.shapes.Rectangle(new_agent.pos[0] + 200, new_agent.pos[1] + 50, 1, 1, color = (0, 8*new_agent.amount, 0))


        self.datacollector = DataCollector(
            model_reporters = {"agent count": lambda m: m.schedule.get_agent_count(),
                                "prey count": lambda m: len(m.current_prey),
                                "predator count": lambda m: len(m.current_predator)}, 
            agent_reporters = {"predator energy": lambda a: a.energy if isinstance(a, Predator) else None})

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()