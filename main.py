from model_definition import ABM
import matplotlib.pyplot as plt
import pyglet

window = pyglet.window.Window(1024, 768)

@window.event 
def on_draw():
    
    window.clear()
    
    for prey in Model.current_prey:
        prey.sprite.draw()
    
    for predator in Model.current_predator:
        predator.sprite.draw()

def model_update(dt):
    Model.step()

def main():
    pyglet.app.run()

    model_data = Model.datacollector.get_model_vars_dataframe()
    agent_data = Model.datacollector.get_agent_vars_dataframe()

    plt.plot(model_data)
    plt.show()
    print(agent_data.describe(), agent_data.head())

if __name__ == '__main__':
    Model = ABM(1000, 500, 1024, 768)
    pyglet.clock.schedule_interval(model_update, 1/5)
    main()