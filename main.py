from model_definition import ABM
import matplotlib.pyplot as plt
import pyglet

window = pyglet.window.Window(1000, 700)

@window.event 
def on_draw():

    window.clear()
    
    for prey in Model.current_prey:
        prey.sprite.draw()
    
    for predator in Model.current_predator:
        predator.sprite.draw()

    for food in Model.food_sources:
        food.sprite.draw()

def model_update(dt):
    Model.step()

def main():
    pyglet.app.run()

    model_data = Model.datacollector.get_model_vars_dataframe()
    agent_data = Model.datacollector.get_agent_vars_dataframe()

    plt.plot(model_data['prey count'])
    plt.plot(model_data['predator count'])
    plt.show()

if __name__ == '__main__':
    Model = ABM(3000, 1500, 50000, 600, 600)
    pyglet.clock.schedule_interval(model_update, 1/120)
    main()