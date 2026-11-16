
import { useState } from "react";

import {
  Brain,
  Activity,
  UserRound,
  ClipboardList,
  RotateCcw,
  BarChart3,
  Printer,
  TrendingUp
} from "lucide-react";

import "./App.css";

const API_URL = "http://127.0.0.1:5000";

const fields = [
  ["Age", "Age", "number"],
  ["Gender", "Gender", "select", ["0", "1"]],
  ["Ethnicity", "Ethnicity", "select", ["0", "1", "2", "3"]],
  ["BMI", "BMI", "number"],
  ["Smoking", "Smoking", "binary"],
  ["AlcoholConsumption", "Alcohol Consumption", "number"],
  ["PhysicalActivity", "Physical Activity", "number"],
  ["DietQuality", "Diet Quality", "number"],
  ["FamilyHistoryAlzheimers", "Family History of Alzheimer's", "binary"],
  ["CardiovascularDisease", "Cardiovascular Disease", "binary"],
  ["Diabetes", "Diabetes", "binary"],
  ["Depression", "Depression", "binary"],
  ["HeadInjury", "Head Injury", "binary"],
  ["Hypertension", "Hypertension", "binary"],
  ["MemoryComplaints", "Memory Complaints", "binary"],
  ["BehavioralProblems", "Behavioral Problems", "binary"],
  ["Confusion", "Confusion", "binary"],
  ["Disorientation", "Disorientation", "binary"],
  ["DifficultyCompletingTasks", "Difficulty Completing Tasks", "binary"],
  ["Forgetfulness", "Forgetfulness", "binary"]
];

const initialValues = {
  Age: 70,
  Gender: 0,
  Ethnicity: 0,
  BMI: 24.5,
  Smoking: 0,
  AlcoholConsumption: 5,
  PhysicalActivity: 5,
  DietQuality: 5,
  FamilyHistoryAlzheimers: 0,
  CardiovascularDisease: 0,
  Diabetes: 0,
  Depression: 0,
  HeadInjury: 0,
  Hypertension: 0,
  MemoryComplaints: 0,
  BehavioralProblems: 0,
  Confusion: 0,
  Disorientation: 0,
  DifficultyCompletingTasks: 0,
  Forgetfulness: 0
};

function App() {
  const [formData, setFormData] = useState(initialValues);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle patient input changes
  const handleChange = (name, value) => {
    setFormData(previous => ({
      ...previous,
      [name]: Number(value)
    }));
  };

  // Generate predictions
  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || data.message || "Prediction failed"
        );
      }

      setResults(data.predictions);

    } catch (err) {
      setError(
        err.message || "Unable to connect to backend"
      );
    } finally {
      setLoading(false);
    }
  };

  // Reset patient form
  const resetForm = () => {
    setFormData(initialValues);
    setResults(null);
    setError("");
  };

  // Calculate majority prediction
  const predictionList = results
    ? Object.values(results)
    : [];

  const positiveVotes = predictionList.filter(
    result => Number(result.prediction) === 1
  ).length;

  const negativeVotes = predictionList.filter(
    result => Number(result.prediction) === 0
  ).length;

  const totalModels = predictionList.length;

  const overallPrediction =
    positiveVotes > negativeVotes
      ? "Positive"
      : "Negative";

  const overallClass =
    positiveVotes > negativeVotes ? 1 : 0;

  // Print or save report as PDF
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="app">

      {/* Navigation */}
      <nav className="navbar">
        <div className="brand">
          <Brain size={30} />
          <h2>AlzheimerCare</h2>
        </div>
      </nav>

      {/* Hero section */}
      <section className="hero">
        <Activity size={45} />

        <h1>Alzheimer's Disease Prediction</h1>

        <p>
          Machine learning based prediction
          using individual patient information.
        </p>
      </section>

      {/* Patient form */}
      <main className="container">

        <div className="section-heading">
          <UserRound size={28} />

          <div>
            <h2>Patient Information</h2>
            <p>
              Enter the required patient details below.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>

          <div className="form-grid">

            {fields.map(([name, label, type, options]) => (
              <div className="form-group" key={name}>

                <label>{label}</label>

                {type === "select" ? (
                  <select
                    value={formData[name]}
                    onChange={e =>
                      handleChange(name, e.target.value)
                    }
                  >
                    {options.map(option => (
                      <option
                        key={option}
                        value={option}
                      >
                        {option}
                      </option>
                    ))}
                  </select>

                ) : type === "binary" ? (
                  <select
                    value={formData[name]}
                    onChange={e =>
                      handleChange(name, e.target.value)
                    }
                  >
                    <option value="0">No</option>
                    <option value="1">Yes</option>
                  </select>

                ) : (
                  <input
                    type="number"
                    step="any"
                    min="0"
                    required
                    value={formData[name]}
                    onChange={e =>
                      handleChange(name, e.target.value)
                    }
                  />
                )}

              </div>
            ))}

          </div>

          <div className="buttons">

            <button
              type="submit"
              disabled={loading}
            >
              <ClipboardList size={18} />
              {loading ? "Predicting..." : "Predict"}
            </button>

            <button
              type="button"
              className="reset"
              onClick={resetForm}
            >
              <RotateCcw size={18} />
              Reset
            </button>

          </div>

        </form>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {/* Prediction results */}
        {results && (
          <section className="results">

            <div className="report-header">
              <h2>Alzheimer's Disease Prediction Report</h2>
              <p>
                Generated on: {new Date().toLocaleString()}
              </p>
            </div>

            <h2>Prediction Results</h2>

            <p className="result-description">
              Individual predictions from five
              machine learning models.
            </p>

            {/* Patient information */}
            <div className="patient-report">

              <h3>Patient Information</h3>

              <div className="patient-report-grid">

                {fields.map(([name, label]) => (
                  <div
                    className="patient-report-item"
                    key={name}
                  >
                    <span>{label}</span>
                    <strong>{formData[name]}</strong>
                  </div>
                ))}

              </div>
            </div>

            {/* Individual model predictions */}
            <h3 className="individual-heading">
              Individual Model Predictions
            </h3>

            <div className="result-grid">

              {Object.entries(results).map(
                ([name, result]) => (
                  <div
                    className="result-card"
                    key={name}
                  >
                    <h3>{name}</h3>

                    <h2 className={
                      Number(result.prediction) === 1
                        ? "positive"
                        : "negative"
                    }>
                      {result.result}
                    </h2>

                    <p>
                      Predicted Class: {result.prediction}
                    </p>

                    <p className="probability">
                      Estimated probability for Class 1:

                      <strong>
                        {result.positive_probability}%
                      </strong>
                    </p>

                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${result.positive_probability}%`
                        }}
                      />
                    </div>
                  </div>
                )
              )}

            </div>

            {/* Graphical chart */}
            <div className="chart-section">

              <div className="chart-heading">
                <TrendingUp size={25} />

                <div>
                  <h3>Model Probability Comparison</h3>
                  <p>
                    Comparison of estimated Class 1
                    probabilities across five models.
                  </p>
                </div>
              </div>

              <div className="chart-container">

                {Object.entries(results).map(
                  ([name, result]) => {

                    const probability = Math.max(
                      0,
                      Math.min(
                        100,
                        Number(result.positive_probability) || 0
                      )
                    );

                    return (
                      <div
                        className="chart-row"
                        key={name}
                      >

                        <div className="chart-label">
                          {name}
                        </div>

                        <div className="chart-track">

                          <div
                            className={
                              Number(result.prediction) === 1
                                ? "chart-bar chart-positive"
                                : "chart-bar chart-negative"
                            }
                            style={{
                              width: `${probability}%`
                            }}
                          />

                        </div>

                        <div className="chart-value">
                          {probability.toFixed(2)}%
                        </div>

                      </div>
                    );
                  }
                )}

              </div>

              <div className="chart-legend">
                <span>
                  <i className="legend-positive"></i>
                  Positive prediction
                </span>

                <span>
                  <i className="legend-negative"></i>
                  Negative prediction
                </span>
              </div>

              <p className="chart-note">
                The chart displays each model's estimated
                probability for Class 1. It does not represent
                model accuracy or clinical risk.
              </p>

            </div>

            {/* Overall majority summary */}
            <div className="overall-summary">

              <div className="overall-heading">
                <BarChart3 size={25} />
                <h3>Overall Prediction Summary</h3>
              </div>

              <h2 className={
                overallClass === 1
                  ? "positive"
                  : "negative"
              }>
                {overallPrediction}
              </h2>

              <p>
                Majority prediction based on {totalModels} models.
              </p>

              <div className="vote-summary">

                <div className="vote-item">
                  <strong>{positiveVotes}</strong>
                  <span>Positive Votes</span>
                </div>

                <div className="vote-item">
                  <strong>{negativeVotes}</strong>
                  <span>Negative Votes</span>
                </div>

              </div>
            </div>

            {/* Download report */}
            <button
              type="button"
              className="report-button"
              onClick={handlePrint}
            >
              <Printer size={18} />
              Download Prediction Report
            </button>

            <p className="notice">
              This application is for educational and
              research purposes only. These model predictions
              are not medical diagnoses. Consult a qualified
              healthcare professional for medical assessment.
            </p>

          </section>
        )}

      </main>
    </div>
  );
}

export default App;
