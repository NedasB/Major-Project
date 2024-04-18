import pandas as pd

# For the Country Info
country_codes_data = pd.read_csv('countries and codes.csv', header=None)
country_info_sql = """
DROP TABLE IF EXISTS CountryInfo;
CREATE TABLE CountryInfo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL UNIQUE,
    country_name VARCHAR(100)
);
INSERT INTO CountryInfo (country_code, country_name) VALUES
""" + ",\n".join(["('{}', '{}')".format(row[0], row[1].replace("'", "''")) for index, row in country_codes_data.iterrows()]) + ";"

# For Predicted Temperatures
predicted_temps_data = pd.read_csv('predicted_temperatures_2015_2026.csv')
predicted_temps_sql = """
DROP TABLE IF EXISTS PredictedTemperatures;
CREATE TABLE PredictedTemperatures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(3),
    year YEAR,
    predicted_temperature FLOAT,
    FOREIGN KEY (country_code) REFERENCES CountryInfo(country_code)
);
INSERT INTO PredictedTemperatures (country_code, year, predicted_temperature) VALUES
""" + ",\n".join(["('{}', {}, {})".format(row['country'], row['year'], row['predicted_temperature']) for index, row in predicted_temps_data.iterrows()]) + ";"

# Write to files
with open('country_info_full.sql', 'w') as file:
    file.write(country_info_sql)

with open('predicted_temperatures_full.sql', 'w') as file:
    file.write(predicted_temps_sql)

