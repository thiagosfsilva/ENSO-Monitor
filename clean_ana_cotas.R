library(pacman)
p_load('dplyr','here','lubridate','tidyr','stringr','glue','arrow')

# List of stations to process
in_files <- list.files(here('data','conventional'),
                       pattern='csv$',
                       full.names = TRUE)


# Create empy df to hold all stations
out_data <- data.frame(station=factor(), dt=Date(), doy = numeric(),
                       yr = numeric(), level = numeric())


# Create error flag
error_flag = FALSE

for(st in 1:length(in_files)){

    # Load and format raw data
    in_data_raw <- read.delim(in_files[st],
                              #skip = 12,
                              sep = ';',
                              dec = '.',
                              header = T)

    # TEST 1: are the first and last column names correct?
    if (names(in_data_raw)[1]=='EstacaoCodigo' &
        names(in_data_raw)[ncol(in_data_raw)]=='Cota31Status'){
        print('Data reading test passed')
    } else {
        print('Data reading test failed')
        error_flag = TRUE
        break
    }

    in_data <- in_data_raw %>%
        mutate(Data = parse_date_time(Data,orders='m/Y')) %>%
        filter(MediaDiaria==1) %>%
        select(EstacaoCodigo,Data,NivelConsistencia,starts_with('Cota')) %>%
        select(!ends_with('Status'))

    # Clean up data
    in_long <- in_data %>%
        pivot_longer(cols = starts_with('Cota'),
                            names_to='Dia',
                            values_to='Nivel') %>% # stacks dates
        mutate(yr = year(Data),
               mn=month(Data),
               dy = as.numeric(str_extract(Dia,"\\d+"))) %>% # gets Y, m, d as ints
        mutate(dt = as.Date(glue('{yr}-{mn}-{dy}'))) %>%  # Build date
        mutate(doy = yday(dt)) %>% # Add day of year column
        filter(!is.na(dt)) %>% # Remove impossible dates
        filter(!(mn==2 & dy == 29))  # Remove stupid leap days

    # Check data consistency per year
    yr_obs <- in_long %>% group_by(yr) %>%
        summarise(nobs = length(Nivel))
    print(yr_obs, n=50)

    # Deduplicate by taking only NivelConsistencia == 2 if both exist
    ind <- duplicated(in_long$dt)
    in_dedup <- in_long[!ind,]

    # Check data consistency yet again
    yr_obs <- in_dedup %>% group_by(yr) %>%
        summarise(nobs = length(Nivel))
    print(yr_obs, n=50)

    # TEST 2: Did deduping work?
    if (max(yr_obs$nobs <= 365)){
        print('Deduping test passed')
    } else {
        print('Deduping test failed')
        error_flag = TRUE
        break
    }

        # Get only years with complete observations
    full_yrs <- yr_obs %>% filter(nobs==365) %>% select(yr)

    # Remove years without 365 obs
    in_clean <- in_dedup %>% filter(yr %in% full_yrs$yr) %>%
        select('EstacaoCodigo','dt','doy','yr','Nivel') %>%
        rename(level=Nivel,station=EstacaoCodigo)

    # Check data consistency a third time
    yr_obs <- in_clean %>% group_by(yr) %>%
        summarise(nobs = length(level))
    print(yr_obs, n=50)

    # TEST 3: Did removal of incomplete years work?
    if (any(yr_obs$nobs != 365)){
        print('Incomplete year removal test failed')
        error_flag = TRUE
        break
    } else {
        print('Incomplete year removal test passed')
    }

        # We need 'fake' doys since we remove Feb 29th, but the calculated doys will
    # Still go to 366 if calculated using yday()
    nyears <- nrow(yr_obs)
    ydays <- rep(seq(1,365),nyears)

    in_clean$doy <- ydays

    # TEST 5: Did insertion of 'fake' doy work?
    if (max(in_clean$doy > 365)){
        print('"Fake" doy insertion failed')
        error_flag = TRUE
        break
    } else {
        print('"Fake" doy insertion  passed')
    }

    if(!error_flag){
    out_data <- rbind(out_data,in_clean)
    }
}

out_data$station <- as.factor(out_data$station)

# Save result as parquet file
if(!error_flag){
    write_parquet(out_data,here('data',glue('historicalLevels_all.parquet')))
}

### Test plot
library(ggplot2)

ggplot(out_data,aes(doy,level)) +
    geom_line(aes(group=yr)) +
    facet_wrap(vars(station))

