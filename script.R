# irace_runner.R
library(irace)

# Caminho do scenario
scenario_file <- "Problema-de-Localizacao-com-Cobertura-Parcial/scenario.txt"

# Garantir que o target runner seja o Python
# targetRunnerLauncher é usado quando o targetRunner é um script .py
scenario <- readScenario(scenario_file)
scenario$targetRunnerLauncher <- "python3"

# Rodar IRACE
results <- irace(scenario = scenario)

# Mostrar resultados
print(results)
