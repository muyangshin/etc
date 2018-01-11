library(dplyr)
library(ggplot2)
library(stargazer)
library(plm)


# A. Assembling the Data ----------------------------------------------------------------

# Directory Information 
df <- data.frame(ID_IPEDS = integer(),
                 year = integer(),
                 degree_bach = logical(),
                 public = logical())

for (year in 2010:2015) {
  df <- df %>%
    bind_rows(read.csv(paste0("data_raw/hd", year, ".csv"), stringsAsFactors = F) %>%
                rename(ID_IPEDS = UNITID) %>%
                mutate(year = year,
                       
                       # bachelor's degree granting institutions
                       degree_bach = INSTCAT %in% c(2, 3),
                       
                       # public institutions
                       public = SECTOR %in% c(1, 4, 7)) %>%
                
                # Restrict to undergraduate institutions in Tennessee
                filter(UGOFFER == 1,
                       STABBR == "TN") %>%
                
                select(ID_IPEDS, year, degree_bach, public)
    )
}

# Student Financial Aid and Net Price
df2 <- data.frame(ID_IPEDS = integer(),
                  year = integer(),
                  enroll_futg = integer(),
                  grant_state = double(),
                  grant_federal = double(),
                  netprice = double())

for (year in 2010:2015) {
  year_filename <- (year %% 100) * 101 + 1
  
  df2 <- df2 %>%
    bind_rows(read.csv(paste0("data_raw/sfa", year_filename, ".csv"), stringsAsFactors = F) %>%
                rename(ID_IPEDS = UNITID,
                       
                       # the total number of first-time, full-time undergraduates
                       enroll_futg = SCUGFFN,
                       
                       # total amunt of state and local grant aid awarded to first-time, full-time undergraduates
                       grant_state = SGRNT_T,
                       
                       # total amunt of federal grant aid awarded to first-time, full-time undergraduates
                       grant_federal = FGRNT_T) %>%
                
                mutate(year = year,
                       
                       # the average cost of attendance minus all grant and scholarship aid: NPIST2 (public), NPGRN2(others)
                       netprice = ifelse(is.na(NPGRN2), NPIST2, NPGRN2)) %>%
                
                select(ID_IPEDS, year, enroll_futg, grant_state, grant_federal, netprice)
    )
}

# Merge 
df <- df %>%
  left_join(df2, by = c("ID_IPEDS", "year"))

rm(df2)

# Filter for colleges for which data exist in all years
df <- df %>%
  filter(!is.na(enroll_futg), !is.na(grant_state), !is.na(grant_federal), !is.na(netprice)) %>%
  group_by(ID_IPEDS) %>%
  mutate(n = n()) %>%
  ungroup() %>%
  filter(n == 6) %>%
  select(-n)

# Save
write.csv(df, "data_clean/data.csv")


# B. Questions ---------------------------------------------------------------
# Construct groups
df.by.group <- df %>%
  mutate(group = paste(ifelse(public, "public", "private"), ifelse(degree_bach, "four-year", "two-year"), 
                       sep = ", "),
         group = factor(group)) %>%
  group_by(group, year) %>%
  summarise(avg_grant_state = mean(grant_state), 
            avg_grant_federal = mean(grant_federal),
            total_enroll_futg = sum(enroll_futg),
            avg_netprice = mean(netprice))

# ggplot theme
my_theme <- theme(legend.title = element_blank(), panel.grid.major = element_line(colour = "grey"),
                  panel.grid.minor = element_blank(), panel.background = element_blank(), axis.line = element_line(colour = "black"),
                  legend.position = "right")

# Question 1
ggplot(df.by.group, aes(x = year, y = avg_grant_state, colour = group, shape = group)) +
  geom_line(size = 1) +
  geom_point(size = 3) +
  xlab("Year") +
  ylab("Average State Grant Aid") +
  my_theme

# Question 2
ggplot(df.by.group, aes(x = year, y = total_enroll_futg, colour = group, shape = group)) +
  geom_line(size = 1) +
  geom_point(size = 3) +
  xlab("Year") +
  ylab("Total Enrollment") +
  my_theme

# Question 3
# Filter for public two-year colleges in 2014 and 2015
df.reg <- df %>% 
  filter(year %in% c(2014, 2015), public == TRUE, degree_bach == FALSE) %>%
  mutate(is_2015 = (year == 2015))

reg.fe <- plm(enroll_futg ~ is_2015, data = df.reg, index = c("ID_IPEDS"), model = "within", effect = "individual")

stargazer(reg.fe,
          title = "Regression Results",
          add.lines = list(c("Fixed Effects", "School")),
          type = "latex", header = FALSE, style = "qje",
          covariate.labels = c("Year 2015"), 
          dep.var.labels = "Enrollment",
          omit.stat = c("adj.rsq"))

# Question 5
ggplot(df.by.group, aes(x = year, y = avg_netprice, colour = group, shape = group)) +
  geom_line(size = 1) +
  geom_point(size = 3) +
  xlab("Year") +
  ylab("Average Net Price") +
  my_theme
