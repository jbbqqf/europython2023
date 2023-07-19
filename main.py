from math import sin
import taipy as tp


def modulate(amplitude, frequency):
    return [amplitude * sin(frequency * x / 10) for x in range(1000)]


def generate_signals():
    signals = {"x": range(1000)}
    for scenario in tp.get_scenarios():
        if scenario.signal.read():
            signals[scenario.name] = scenario.signal.read()
    return signals


def create_chart(signals):
    columns = []
    for i, column in enumerate(signals.keys()):
        if column != "x":
            columns.append(f"y[{i}]={column}")
    return "<|{signals}|chart|x=x|" + "|".join(columns) + "|>"


def submit_signal(state):
    state.selected_scenario.submit()
    state.signals = generate_signals()


def on_amplitude_change(state):
    state.selected_scenario.amplitude.write(state.amplitude)
    submit_signal(state)


def on_frequency_change(state):
    state.selected_scenario.frequency.write(state.frequency)
    submit_signal(state)


def on_scenario_change(state, variable_name, value):
    if variable_name == "selected_scenario" and value:
        state.amplitude = state.selected_scenario.amplitude.read()
        state.frequency = state.selected_scenario.frequency.read()

        if not state.selected_scenario.signal.is_ready_for_reading:
            submit_signal(state)
        else:
            state.signals = generate_signals()
        state.chart_partial.update_content(state, create_chart(state.signals))

tp.config.Config.load("signal.toml")
tp.Core().run()

amplitude = 1
frequency = 1
selected_scenario = None
signals = generate_signals()

page = tp.gui.Markdown(
"""
# Taipy Application

<|1 1 1|layout|

<|{selected_scenario}|scenario_selector|on_change=on_scenario_change|>

<|
## Amplitude (<|{amplitude}|text|>)
<|{amplitude}|slider|on_change=on_amplitude_change|>
|>

<|
## Frequency (<|{frequency}|text|>)
<|{frequency}|slider|on_change=on_frequency_change|>
|>

|>

<|part|partial={chart_partial}|>
"""
)


if __name__ == "__main__":
    gui = tp.gui.Gui(page=page)
    chart_partial = gui.add_partial("No signal created yet!")
    gui.run()
