library(ARTool)      
library(emmeans)     
library(ggplot2)     
library(dplyr)       
library(lme4)
library(MuMIn)
library(effectsize)
library(tidyverse)
library(moments)
# Define bins
bins = c('1st bin', '2nd bin', '3rd bin')

# Load data
df <- read_csv('')

# Descriptives
results_delta <- df %>%
  group_by(individual_bin) %>% 
  summarise(
    mean = mean(Duration_delta, na.rm = TRUE),
    Variance = var(Duration_delta, na.rm = TRUE),
    q1 = quantile(Duration_delta, probs = c(0.25)),
    median = median(Duration_delta, na.rm = TRUE),
    q3 = quantile(Duration_delta, probs = c(0.75)),
    iqr = quantile(Duration_delta, probs = c(0.75)) - quantile(Duration_delta, probs = c(0.25)),                        
    .groups = "drop"                       
  )

results_dur <- df %>%
  group_by(individual_bin) %>% 
  summarise(
    mean = mean(Duration, na.rm = TRUE),
    Variance = var(Duration, na.rm = TRUE),
    q1 = quantile(Duration, probs = c(0.25)),
    median = median(Duration, na.rm = TRUE),
    q3 = quantile(Duration, probs = c(0.75)),
    iqr = quantile(Duration, probs = c(0.75)) - quantile(Duration, probs = c(0.25)),                        
    Count = n(), 
    .groups = "drop"                       
  )

# Histogram
hist(df$Duration)
print(skewness(df$Duration))
df$Duration_log <- log(df$Duration)
hist(df$Duration_log)
print(skewness(df$Duration_log))
shapiro.test(df$Duration_log)

# Model 
df$Task_bin_long <- as.numeric(as.numeric(factor(df$Task_bin_long, 
                                                 levels = c("1st bin", "2nd bin", "3rd bin"))))
model <- lmerTest::lmer(Duration_log ~ individual_bin + (1 | id), 
                             data = df)


summary(model)

