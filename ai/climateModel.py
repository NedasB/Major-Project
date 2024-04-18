import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from keras_tuner import Hyperband
from tensorflow.keras.callbacks import CSVLogger
import matplotlib.pyplot as plt

# Load the data
file_path = 'official_climate_data.csv' 
data = pd.read_csv(file_path)

# Transform the dataset: melt and convert years
data_melted = data.melt(id_vars=["code", "name"], var_name="year", value_name="temperature")
data_melted["year"] = data_melted["year"].str.slice(0, 4).astype(int)

# Prepare features and target variable
X = data_melted[["code", "year"]]
y = data_melted["temperature"]

# Define the preprocessing for the numerical and categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['year']),
        ('cat', OneHotEncoder(), ['code'])
    ])

# Preprocess the features
X_processed = preprocessor.fit_transform(X)
X_processed = np.array(X_processed.toarray())  # Convert to dense array

def build_model(hp):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(units=hp.Int('units', min_value=32, max_value=512, step=32),
                                    activation='relu', input_shape=[X_processed.shape[1]]))
    for i in range(hp.Int('num_layers', 1, 4)):
        model.add(tf.keras.layers.Dense(units=hp.Int(f'units_{i}', min_value=32, max_value=512, step=32),
                                        activation='relu'))
    model.add(tf.keras.layers.Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

# Initialize the tuner
tuner = Hyperband(
    build_model,
    objective='val_loss',
    max_epochs=100,
    directory='tuner_results',
    project_name='climate_prediction'
)

tuner.search(X_processed, y, epochs=100, validation_split=0.4)

# Get the best hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

# Build the model with the best hyperparameters
model = tuner.hypermodel.build(best_hps)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

# Define CSVLogger callback
csv_logger = CSVLogger('training_log.csv', append=True)

# Fit the model on the training data and include the CSVLogger in callbacks
history = model.fit(X_train, y_train, epochs=100, validation_split=0.2, callbacks=[csv_logger])

# Plotting the training and validation loss
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.show()

# Get final loss and validation loss from the history object
final_loss = history.history['loss'][-1]
final_val_loss = history.history['val_loss'][-1]

# Predict temperatures for the test set
y_pred = model.predict(X_test)

# Calculate the R-squared score
r_squared = r2_score(y_test, y_pred)

# Append final loss and R-squared score to the CSV file
final_metrics = pd.DataFrame({'epoch': ['final'],
                              'loss': [final_loss],
                              'val_loss': [final_val_loss],
                              'R_squared': [r_squared]})
final_metrics.to_csv('training_log.csv', mode='a', index=False, header=False)

# Print final loss and validation loss
print(f'Final training loss: {final_loss}')
print(f'Final validation loss: {final_val_loss}')
print(f'R-squared score: {r_squared}')

# Generate predictions for every country and specific years 2015 to 2025
unique_countries = data_melted['code'].unique()
years = range(2015, 2026)  # Only years 2015 to 2025
predictions = []

for country in unique_countries:
    for year in years:
        # Construct a DataFrame for the inputs to match the training data structure
        input_df = pd.DataFrame({'code': [country], 'year': [year]})
        
        # Preprocess the input in the same way as the training data
        input_processed = preprocessor.transform(input_df)
        input_processed = np.array(input_processed.toarray())  # Convert to dense array
        
        # Make a prediction
        predicted_temperature = model.predict(input_processed)[0][0]
        
        # Append the prediction to the list
        predictions.append({'country': country, 'year': year, 'predicted_temperature': predicted_temperature})

# Convert predictions to a DataFrame and save to CSV
predictions_df = pd.DataFrame(predictions)
predictions_df.to_csv('predicted_temperatures_2015_2026.csv', index=False)
