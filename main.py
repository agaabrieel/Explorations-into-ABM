from model_definition import ABM
import matplotlib.pyplot as plt
import pyglet

'''window = pyglet.window.Window(1024, 768)

@window.event 
def on_draw():
    window.clear()'''

def main():
    # pyglet.app.run()
    Model = ABM(200, 20, 30, 30)
    for i in range(200):
        Model.step()

    model_data = Model.datacollector.get_model_vars_dataframe()
    agent_data = Model.datacollector.get_agent_vars_dataframe()

    plt.plot(model_data)
    plt.show()
    print(agent_data.describe(), agent_data.head())

if __name__ == '__main__':
    main()