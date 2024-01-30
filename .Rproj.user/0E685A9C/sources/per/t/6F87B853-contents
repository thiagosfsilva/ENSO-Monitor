# NERC analysis of Amazon hydrology

# Load packages
library(arrow)
library(here)
library(ggplot2)
library(lubridate)
library(dplyr)

# Load historical water level data from Fonte Boa
fb_levels <- read_parquet(here('data/historicalLevels_12351000.parquet'))
fb_2023 <- read_parquet(here('data/currentData.parquet'))

# Add months to data
fb_levels$mn <- as.factor(month(fb_levels$dt, label = TRUE))
fb_2023$mn <- as.factor(month(fb_2023$dt, label = TRUE))

# Plot all years
ggplot(fb_levels,aes(doy,level)) +
    geom_line(aes(group=yr,color=mn)) +
    scale_color_discrete()

# We define low level as the average of the lowest 15 days during Sep-Oct
# and high level as the average of the highest 15 days during May-Jun


lows <- fb_levels %>%
    filter(doy >= 244 & doy <= 304) %>%
    group_by(yr) %>%
    arrange(level) %>%
    slice(1:15) %>%
    summarise(min_level = mean(level, na.rm=TRUE)) %>%
    arrange(min_level)

low_2023 <- fb_2023 %>%
    filter(doy >= 244 & doy <= 304) %>%
    arrange(level) %>%
    slice(1:15) %>%
    summarise(min_level = mean(level, na.rm=TRUE))

lows[43,] <- c(2023,low_2023)

lows <- lows %>% arrange(yr)

highs <- fb_levels %>%
    filter(doy >= 121 & doy <= 181) %>%
    group_by(yr) %>%
    arrange(level) %>%
    slice(1:15) %>%
    summarise(max_level = mean(level, na.rm=TRUE))

high_2023 <- fb_2023 %>%
    filter(doy >= 121 & doy <= 181) %>%
    arrange(level) %>%
    slice(1:15) %>%
    summarise(min_level = mean(level, na.rm=TRUE))

highs[43,] <- c(2023,high_2023)

highs <- highs %>% arrange(yr)

print(lows %>% arrange(min_level), n=50)
print(highs %>% arrange(desc(max_level)), n=50)

print(acf(lows$min_level))
print(acf(highs$max_level))

