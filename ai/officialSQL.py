import pandas as pd

def create_sql_from_csv(csv_filename, output_sql_filename):
    # Read the CSV file using pandas
    data = pd.read_csv(csv_filename)

    # Define the SQL to create the table
    create_table_sql = """
DROP TABLE IF EXISTS OfficialAnnualTemperatures;
CREATE TABLE OfficialAnnualTemperatures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(3),
    country_name VARCHAR(100),
"""
    # Adding a column for each year
    year_columns = ",\n".join([f"`{year}` FLOAT" for year in data.columns[2:]])
    create_table_sql += year_columns + "\n);"

    # Generate INSERT statements from the dataframe
    insert_statements = ""
    for index, row in data.iterrows():
        # Prepare row data, properly escaping single quotes
        row_data = [str(x).replace("'", "\\'") for x in row[2:]]
        values_str = "', '".join(row_data)
        country_code = str(row['code']).replace("'", "\\'")
        country_name = str(row['name']).replace("'", "\\'")

        insert_statements += f"INSERT INTO OfficialAnnualTemperatures (country_code, country_name, {', '.join(['`' + col + '`' for col in data.columns[2:]])}) VALUES ('{country_code}', '{country_name}', '{values_str}');\n"

    # Combine the SQL statements
    full_sql = create_table_sql + insert_statements

    # Write the SQL commands to a file
    with open(output_sql_filename, 'w') as file:
        file.write(full_sql)

    print(f"SQL file created: {output_sql_filename}")

csv_file_name = 'official_climate_data.csv'  
sql_output_filename = 'official_annual_temperatures.sql'  
create_sql_from_csv(csv_file_name, sql_output_filename)
