<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta description="Predicted vs Official Temperature Data Comparison">
    <title>Temperature Data</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
            color: #333;
        }
        h2, h3 {
            color: #444;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007bff;
            color: #ffffff;
            text-transform: uppercase;
        }
        td {
            background-color: #ffffff;
        }
        tr:nth-child(even) td {
            background-color: #f2f2f2;
        }
        tr:hover td {
            background-color: #ddd;
            cursor: pointer;
        }
        .chart-container {
            width: 100%;
            height: 400px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .scrollable-table {
            max-height: 500px; 
            overflow: auto;
        }
    </style>
    <script>
        function createTemperatureChart(predictedTemperatures, officialTemperatures, years) {
            const ctx = document.getElementById('temperatureChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: years,
                    datasets: [{
                        label: 'Predicted Temperature (°C)',
                        data: predictedTemperatures,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: false
                    }, {
                        label: 'Official Temperature (°C)',
                        data: officialTemperatures,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    },
                    maintainAspectRatio: false
                }
            });
        }

        function createHistoricalTemperatureChart(officialTemperatures, years) {
            const ctx = document.getElementById('historicalTemperatureChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: years,
                    datasets: [{
                        label: 'Official Temperature (°C)',
                        data: officialTemperatures,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }
    </script>
</head>
<body>
    <h2>Predicted vs Official Temperature Data Comparison</h2>
    
    <!-- Search form for country name -->
    <form action="" method="get">
        <label for="countryName">Enter Country Name:</label>
        <input type="text" id="countryName" name="countryName" required>
        <input type="submit" value="Search">
    </form>

    <?php
    error_reporting(E_ALL);
    ini_set('display_errors', 1);

    $host = 'localhost';
    $dbname = 'predictionData';
    $username = 'root';
    $password = '';

    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $countryName = isset($_GET['countryName']) ? $_GET['countryName'] : 'Germany';

    $predictedTemperatures = [];
    $officialTemperatures = [];
    $years = [];

    // Fetch predicted temperatures
    $predictedStmt = $pdo->prepare("SELECT pt.year, pt.predicted_temperature
                                    FROM PredictedTemperatures pt
                                    JOIN CountryInfo ci ON pt.country_code = ci.country_code
                                    WHERE ci.country_name = :countryName
                                    ORDER BY pt.year");
    $predictedStmt->bindParam(':countryName', $countryName);
    $predictedStmt->execute();
    $predictedData = $predictedStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch official temperatures for recent years
    $officialStmt = $pdo->prepare("SELECT `2015-07`, `2016-07`, `2017-07`, `2018-07`, `2019-07`, `2020-07`
                                   FROM OfficialAnnualTemperatures
                                   WHERE country_name = :countryName");
    $officialStmt->bindParam(':countryName', $countryName);
    $officialStmt->execute();
    $officialDataRecent = $officialStmt->fetch(PDO::FETCH_ASSOC);

    // Fetch official historical temperatures
    $officialStmt = $pdo->prepare("SELECT * FROM OfficialAnnualTemperatures WHERE country_name = :countryName");
    $officialStmt->bindParam(':countryName', $countryName);
    $officialStmt->execute();
    $officialDataHistorical = $officialStmt->fetch(PDO::FETCH_ASSOC);

    echo "<h3>Temperature Data for " . htmlspecialchars($countryName) . "</h3>";

    // Predicted vs Official Recent Years Table and Chart
    echo "<table>";
    echo "<thead><tr><th>Year</th><th>Predicted Temperature (°C)</th><th>Official Temperature (°C)</th></tr></thead><tbody>";

    foreach ($predictedData as $data) {
        $year = $data['year'];
        $predictedTemp = $data['predicted_temperature'];
        $officialTempKey = $year . '-07';
        $officialTemp = $officialDataRecent[$officialTempKey] ?? 'N/A';

        $predictedTemperatures[] = $predictedTemp;
        $years[] = $year;
        $officialTemperatures[] = $officialTemp;

        echo "<tr>";
        echo "<td>" . htmlspecialchars($year) . "</td>";
        echo "<td>" . htmlspecialchars($predictedTemp) . "</td>";
        echo "<td>" . htmlspecialchars($officialTemp) . "</td>";
        echo "</tr>";
    }

    echo "</tbody></table>";

    echo '<div class="chart-container"><canvas id="temperatureChart"></canvas></div>';

    // Historical Data Table
    echo "<h3>Historical Official Temperatures (1950 - 2020) for " . htmlspecialchars($countryName) . "</h3>";
    echo '<div class="scrollable-table">';
    echo "<table>";
    echo "<thead><tr><th>Year</th><th>Temperature (°C)</th></tr></thead><tbody>";

    $historicalOfficialTemperatures = [];
    $historicalYears = [];
    for ($year = 1950; $year <= 2020; $year++) {
        $tempKey = "{$year}-07";
        $temp = $officialDataHistorical[$tempKey] ?? 'N/A';
        $historicalOfficialTemperatures[] = $temp;
        $historicalYears[] = $year;
        echo "<tr><td>$year</td><td>$temp</td></tr>";
    }

    echo "</tbody></table>";
    echo '</div>';

    echo '<div class="chart-container"><canvas id="historicalTemperatureChart"></canvas></div>';
    ?>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            createTemperatureChart(
                <?php echo json_encode($predictedTemperatures); ?>,
                <?php echo json_encode($officialTemperatures); ?>,
                <?php echo json_encode($years); ?>
            );
            
            createHistoricalTemperatureChart(
                <?php echo json_encode($historicalOfficialTemperatures); ?>,
                <?php echo json_encode($historicalYears); ?>
            );
        });
    </script>
</body>
</html>
