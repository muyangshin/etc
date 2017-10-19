rm(list = ls())

library(readstata13)
library(ggplot2)
library(dplyr)
library(ivpack)
library(stargazer)

setwd("C:/Users/mshin/Downloads/course_files_export/Replication exercise")


# Card --------------------------------------------------------------------

df.card <- read.dta13("card.dta")

# 1.2 Summary Statistics ------------------------------------------------------
# 1
stargazer(df.card[, c("lwage", "educ", "age", "motheduc", "fatheduc", "kww", "iq")],
          nobs = FALSE, median = TRUE, type = "text", title = "Descriptive statistics", digits=3, 
          out = "results/card.1.2.1.tex")

# 2
graph.card <- ggplot(df.card, aes(x = educ, y = lwage)) +
  geom_point(shape = 16) +
  geom_smooth(method = lm, se = F)

ggsave("results/card1.png", graph.card)

# 1.3 Regression ----------------------------------------------------------
# 1
vars <- c("educ", "exper", "expersq", "black", "south", "smsa")
lm.lwage <- lm(paste0("lwage ~ ", paste(vars, collapse = "+")), data = df.card)
summary(lm.lwage, robust = T)

# 4
vars <- c(vars, paste0("reg", 661:668), "smsa66")
lm.lwage2 <- lm(paste0("lwage ~ ", paste(vars, collapse = "+")), data = df.card)

# 5
df.card <- df.card %>%
  mutate(missing.motheduc = is.na(motheduc)) %>%
  mutate(missing.fatheduc = is.na(fatheduc)) %>%
  mutate(motheduc = replace(motheduc, is.na(motheduc), mean(motheduc, na.rm = TRUE))) %>%
  mutate(fatheduc = replace(fatheduc, is.na(fatheduc), mean(fatheduc, na.rm = TRUE)))

vars <- c(vars, "motheduc", "fatheduc", "missing.motheduc", "missing.fatheduc")
lm.lwage3 <- lm(paste0("lwage ~ ", paste(vars, collapse = "+")), data = df.card)

# 6
df.card <- df.card %>%
  mutate(motheduc12 = ifelse(motheduc < 12, 0, ifelse(motheduc == 12, 1, 2))) %>%
  mutate(fatheduc12 = ifelse(fatheduc < 12, 0, ifelse(fatheduc == 12, 1, 2)))

df.card$motheduc12 <- factor(df.card$motheduc12)
df.card$fatheduc12 <- factor(df.card$fatheduc12)

vars <- c(vars, "motheduc12:fatheduc12")
lm.lwage4 <- lm(paste0("lwage ~ ", paste(vars, collapse = "+")), data = df.card)

# 7
vars <- c(vars, "momdad14", "sinmom14")
lm.lwage5 <- lm(paste0("lwage ~ ", paste(vars, collapse = "+")), data = df.card)

# Print
stargazer(lm.lwage, lm.lwage2, lm.lwage3, lm.lwage4, lm.lwage5,
          type = "text", title = "Regression 1.3", out = "results/reg_card.tex",
          column.sep.width = "0pt")


# 1.4 IV ------------------------------------------------------------------
# 3
df.card <- df.card %>%
  mutate(agesq = age^2)

lm.lwage.iv1 <- ivreg(paste0("lwage ~", paste(vars, collapse = "+"), 
                             "| . - educ - exper - expersq + nearc4 + age + agesq"),
                      data = df.card)

# 4
vars <- c(vars, "kww")

lm.lwage.iv2 <- ivreg(paste0("lwage ~", paste(vars, collapse = "+"), 
                             "| . - educ - exper - expersq + nearc4 + age + agesq"),
                      data = df.card)

# 5
lm.lwage.iv3 <- ivreg(paste0("lwage ~", paste(vars, collapse = "+"), 
                             "| . - educ - exper - expersq - kww + nearc4 + age + agesq + iq"),
                      data = df.card)

# 6
vars <- vars[vars != "kww"]

lm.lwage.iv4 <- ivreg(paste0("lwage ~", paste(vars, collapse = "+"), 
                             "| . - educ - exper -expersq + nearc4 + nearc2 + age + agesq"),
                      data = df.card)

# Print
stargazer(lm.lwage.iv1, lm.lwage.iv2, lm.lwage.iv3, lm.lwage.iv4, 
          type = "text", title = "Regression 1.4", out = "results/reg_card_2.tex", column.sep.width = "0pt")


# Hamermesh ---------------------------------------------------------------

df.ham <- read.dta13("CitationTabulations.dta")

# 1
df.ham.summary <- df.ham %>%
  group_by(artid) %>%
  mutate(no_citations = n()) %>%
  summarise(f_related = round(sum(related) * 100 / first(no_citations), 1),
            f_similar = round(sum(similar) * 100 / first(no_citations), 1),
            f_replicated = round(sum(replicated) * 100 / first(no_citations), 1),
            f_inspired = round(sum(inspired) * 100 / first(no_citations), 1)
            )

stargazer(df.ham.summary, summary = F, out = "results/ham_summary.tex")

# 2
df.ham2 <- df.ham %>%
  mutate(is_sim_rep = similar == 1 | replicated == 1) %>%
  group_by(artid, year) %>%
  mutate(no_citations = n()) %>%
  mutate(f_sim_rep = sum(is_sim_rep) * 100 / first(no_citations)) %>%
  group_by(postpubyear) %>%
  summarise(f_sim_rep_mean = mean(f_sim_rep)) %>%
  filter(postpubyear > 0 & postpubyear <= 20)

graph.ham1 <- ggplot(df.ham2, aes(x = postpubyear, y = f_sim_rep_mean)) +
  geom_point(shape = 16) +
  geom_smooth(method = lm, se = F)

ggsave("results/ham1.png", graph.ham1)

# 3
df.ham3 <- df.ham %>%
  group_by(artid, year) %>%
  mutate(no_citations = n()) %>%
  mutate(f_inspired = sum(inspired) * 100 / first(no_citations)) %>%
  group_by(postpubyear) %>%
  summarise(f_inspired_mean = mean(f_inspired), postpubyear2 = first(postpubyear2)) %>%
  filter(postpubyear > 0 & postpubyear <= 20)

graph.ham2 <- ggplot(df.ham3, aes(x = postpubyear, y = f_inspired_mean)) + 
  geom_point(shape = 16) +
  stat_smooth(method = "lm", formula = y ~ x + I(x^2), se = F)

ggsave("results/ham2.png", graph.ham2)