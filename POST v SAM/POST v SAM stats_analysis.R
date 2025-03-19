##### POST v SAM analysis code -------------------------------------------
library(tidyverse) 
library(afex)
library(rstatix)
library(emmeans)

# read in data 
d1 <- read_csv("Cleary POST v SAM.csv")

d1 %>% 
  group_by(Surgery) %>% 
  tally()

# descriptive statistics - Total sample 
d1 %>% 
  select(Group, Age, Height, BodyMass) %>% 
  summarize(across(where(is.numeric), list('mean' = mean,
                                           'sd' = sd))) %>% 
  pivot_longer(cols = everything(),
               names_to = c('Var', 'Stat'),
               names_sep = "_") %>% 
  pivot_wider(names_from = Stat)

# descriptive statistics - by Groups
d1 %>% 
  select(Group, Age, Height, BodyMass) %>% 
  group_by(Group) %>% 
  summarize(across(where(is.numeric), list('mean' = mean,
                                           'sd' = sd))) %>% 
  pivot_longer(cols = 2:ncol(.),
               names_to = c('Var', 'Stat'),
               names_sep = "_") %>% 
  pivot_wider(names_from = Stat)

## calculate time since surgery
tss_d <- na.omit((days(d1$TSS)))
tss_d
tss_m <- time_length(tss_d, unit = 'month')

paste0("Average (SD) of TSS = ", round(mean(tss_m),1), " (", round(sd(tss_m),1),") months")
paste0('Range of TSS = ', round(min(tss_m),1),"-",round(max(tss_m),1), " months" )

### Data Cleaning ------------------------------------------------
# clean into statistical analysis ready format
# first for MVIC data (n = Newtons)
mvic_dat <- d1 %>% 
  # select vars of interest for MVIC data
  select(ID, Group, contains(c("nND", "nDOM"))) %>% 
  pivot_longer(cols = 3:6,
               names_to = c("Leg", "Action"),
               names_sep = "_") %>% 
  pivot_wider(names_from = "Action") %>% 
  # place leg into terms used in the manuscript
  mutate(Group = fct(Group, levels = c("SAM", "POST")),
         Leg_tidy = case_when(Leg == "nND" ~ "O-ND",
                              Leg == "nDOM" ~ "NO-D"),
         .after = Leg) %>% 
  select(-Leg) %>% 
  rename(Leg = Leg_tidy)

# view the dataframe we just created
glimpse(mvic_dat)
head(mvic_dat)

# now for the ultrasound data
us_dat <- d1 %>% 
  # select US variables of interest
  select(ID, Group, contains('mCSA'))  %>% 
  pivot_longer(cols = ND_QuadsmCSA:DOM_HamsmCSA,
               names_to = c("Leg", "Var"),
               names_sep = "_") %>% 
  pivot_wider(names_from = "Var") %>% 
  # correct leg term into what we use in the manuscript
  mutate(Group = fct(Group, levels = c("SAM", "POST")),
         Leg_tidy = case_when(Leg == "ND" ~ "O-ND",
                              Leg == "DOM" ~ "NO-D"),
         .after = Leg) %>% 
  select(-Leg) %>% 
  rename(Leg = Leg_tidy)

# view US data
glimpse(us_dat)
head(us_dat)

# create relative MVIC data by joining the two dataframes
relmvic_dat <- left_join(mvic_dat, us_dat) %>% 
  mutate(QuadsRelMVIC = QuadsMVIC/QuadsmCSA,
         HamsRelMVIC = HamsMVIC/HamsmCSA,
         .keep = 'unused') # remove unused columns

glimpse(relmvic_dat)
head(relmvic_dat)

### Statistics -------------------------------------------------------------
# define custom function for emmeans::eff_size() amd emmeans::emmeans() to return
# simple comparisons and effectsizes 
emm_eff_size <- function(model, term) {
  
  # define comparisons
  emm <- emmeans(model, paste({{term}}))
  
  # return pairwise comps of those 
  pwc <- pairs(emm)
  
  # get sigma
  sigma <- sqrt(model$anova_table[term, 'MSE'])
  
  # get edf
  edf <- df.residual(model$lm)
  
  # effect sizes
  es <- eff_size(emm, sigma = sigma, edf = edf)
  
  
  return(
    list('Estimated Marginal Means'= emm, 
         'Pairwise Comps' = pwc, 
         'Effect Size' = es))
}

##### mCSA models ##### 
# quads mCSA
quads_mcsa_mod <- aov_4(QuadsmCSA ~ Group * (Leg | ID),
                        data = us_dat,
                        anova_table = list(es = "pes",
                                           correction = "none"))
# model assumptions checking
performance::check_sphericity(quads_mcsa_mod)
plot(performance::check_normality(quads_mcsa_mod))

# View model
quads_mcsa_mod

# no interactions or main effects. 
# Return mean diffs and Cohen's d, however, for Results section
emm_eff_size(quads_mcsa_mod, 'Leg')

emm_eff_size(quads_mcsa_mod, 'Group')


hams_mcsa_mod <- aov_4(HamsmCSA ~ Group * (Leg | ID),
                       data = us_dat,
                       anova_table = list(es = "pes",
                                          correction = "none"))
hams_mcsa_mod

emmeans(hams_mcsa_mod, pairwise ~ Leg)
emmeans(hams_mcsa_mod, pairwise ~ Group)

# eff_sizes for post hocs
emm_eff_size(model = hams_mcsa_mod, term = "Leg")
emm_eff_size(model = hams_mcsa_mod, term = "Group")


##### MVIC models ##### 
quads_mvic_mod <- aov_4(QuadsMVIC ~ Group + (Leg | ID),
                        data = mvic_dat,
                        anova_table = list(es = "pes",
                                           correction = "none"))
quads_mvic_mod

emmeans(quads_mvic_mod, pairwise ~ Leg)
emmeans(quads_mvic_mod, pairwise ~ Group)

# eff_sizes for post hocs
emm_eff_size(model = quads_mvic_mod, term = "Leg")
emm_eff_size(model = quads_mvic_mod, term = "Group")

# hams MVIC model
hams_mvic_mod <- aov_4(HamsMVIC ~ Group * (Leg | ID),
                       data = mvic_dat,
                       anova_table = list(es = "pes",
                                          correction = "none"))
hams_mvic_mod

emmeans(hams_mvic_mod, pairwise ~ Leg)
emmeans(hams_mvic_mod, pairwise ~ Group)

emm_eff_size(hams_mvic_mod, term = 'Leg')
emm_eff_size(hams_mvic_mod, term = 'Group')

##### Relative MVIC models #####
quads_relmvic_mod <- aov_4(QuadsRelMVIC ~ Group * (Leg | ID),
                           data = relmvic_dat,
                           anova_table = list(es = "pes",
                                              correction = "none"))
quads_relmvic_mod

emmeans(quads_relmvic_mod, pairwise ~ Leg)
emmeans(quads_relmvic_mod, pairwise ~ Group)

emm_eff_size(model = quads_relmvic_mod, term = "Leg")
emm_eff_size(model = quads_relmvic_mod, term = "Group")

# hams rel mvic
hams_relmvic_mod <- aov_4(HamsRelMVIC ~ Group * (Leg | ID),
                          data = relmvic_dat,
                          anova_table = list(es = "pes",
                                             correction = "none"))
hams_relmvic_mod

emmeans(hams_relmvic_mod, pairwise ~ Leg)
emmeans(hams_relmvic_mod, pairwise ~ Group)

emm_eff_size(hams_relmvic_mod, term = 'Leg')
emm_eff_size(hams_relmvic_mod, term = 'Group')

##
hq_mvic_dat <- mvic_dat %>% 
  mutate(HQ = HamsMVIC/QuadsMVIC)

hq_mvic_mod <- aov_4(HQ ~ Group * (Leg | ID),
                     data = hq_mvic_dat,
                     anova_table = list(es = 'pes',
                                        correction = 'none'))
hq_mvic_mod

emmeans(hq_mvic_mod, ~ Group)
