if (!require("irace")) install.packages("irace")

library(irace)

# Caminho do arquivo de cenário
scenario_file <- "scenario.txt" 

# Verifica se o arquivo existe antes de tentar ler
if (!file.exists(scenario_file)) {
  stop("ERRO CRÍTICO: O arquivo 'scenario.txt' não foi encontrado. Verifique o caminho!")
}

# Lê o cenário
scenario <- readScenario(filename = scenario_file)

scenario$targetRunnerLauncher <- "python3" 
scenario$parallel <- 4 

# 3. RODAR O IRACE
cat("Iniciando o IRACE com", scenario$maxExperiments, "experimentos...\n")
irace_results <- irace(scenario = scenario)

save.image("resultado_irace_final.Rdata")

# Exporta a melhor configuração para um texto legível
configurations.print(irace_results, metadata = TRUE)

# Pega a melhor configuração (a primeira da lista)
best_config <- irace_results[1, ]

cat("\n--- MELHORES PARÂMETROS ENCONTRADOS ---\n")
print(best_config)

cat("\nPara usar no seu main_experiments.py:\n")
cat(sprintf("ALPHA = %s\n", best_config$alpha))
cat(sprintf("BETA = %s\n", best_config$beta))
cat(sprintf("TI = %s\n", best_config$Ti))