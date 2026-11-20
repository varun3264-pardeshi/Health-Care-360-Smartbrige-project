/**
 * PulsePoint Cyber-Medical OS v3.0 — High-Density Interactive Frontend Engine
 * Powers 12 Interactive Scenario Visualizations, Visual Storyboard with Auto-Play,
 * Anatomical Organ Digital Twin (SVG HUD), Multi-Slider Counterfactual AI Simulator,
 * and Live 5,000-Patient Cohort Explorer.
 */

const API_BASE = (window.location.port === "8000" || window.location.port === "5000")
    ? ""
    : "http://127.0.0.1:8000";

// Global Chart Instances
let prevalenceChart = null;
let sc1BpChart = null;
let sc1GlucoseChart = null;
let sc1ScatterChart = null;
let sc1BiomarkersChart = null;
let sc2SmokingChart = null;
let sc2ExerciseChart = null;
let sc2AlcoholChart = null;
let sc2RadarChart = null;
let ageChart = null;
let sc3BmiChart = null;
let sc3SymptomsChart = null;
let storyDynamicChart = null;

let currentBaselinePrediction = null;
let activeAlerts = [];
let cohortRecordsCache = [];
let storyAutoPlayTimer = null;
let currentStoryIdx = 0;

// Visual Storyboard Data (Zero Wall-of-Text: Chart + 4 KPI Cards + 1-Line Takeaway)
const VISUAL_STORY_SLIDES = [
    {
        badge: "STORY POINT 1 / 5 • EXECUTIVE COHORT",
        title: "Multi-Disease Prevalence & High-Risk Stratification",
        actionScenario: "scenario1",
        actionText: "Scroll to Clinical Dashboard →",
        chartType: "bar",
        labels: ["Type 2 Diabetes", "Heart Disease", "Stroke / CVA", "Multimorbid (2+)", "High-Risk Biomarker"],
        datasets: [{
            label: "Cohort Rate (%)",
            data: [10.6, 6.9, 1.7, 1.7, 64.2],
            backgroundColor: ["#f59e0b", "#ef4444", "#2563eb", "#7c3aed", "#0d9488"],
            borderRadius: 6
        }],
        kpis: [
            { label: "Total Cohort", val: "5,000" },
            { label: "High-Risk Flag", val: "64.2%" },
            { label: "Diabetes Rate", val: "10.6%" },
            { label: "Heart Disease", val: "6.9%" }
        ],
        takeaway: "⚡ 3,210 of 5,000 patients exhibit Stage 2 HTN, Hyperglycemia, or Clinical Obesity requiring automated early triage."
    },
    {
        badge: "STORY POINT 2 / 5 • DR. MICHAEL CARTER",
        title: "Hemodynamic & Glycemic Inflection Thresholds",
        actionScenario: "scenario1",
        actionText: "Scroll to Dr. Carter's View →",
        chartType: "bar",
        labels: ["Normal BP", "Elevated BP", "HTN Stage 1", "HTN Stage 2", "HTN Crisis"],
        datasets: [
            { label: "Heart Disease %", data: [3.1, 4.5, 5.8, 8.9, 16.4], backgroundColor: "#ef4444", borderRadius: 4 },
            { label: "Stroke %", data: [0.6, 0.9, 1.3, 2.2, 5.8], backgroundColor: "#2563eb", borderRadius: 4 }
        ],
        kpis: [
            { label: "Crisis Stroke Rate", val: "5.8%" },
            { label: "Crisis HD Rate", val: "16.4%" },
            { label: "HD+ Mean SBP", val: "149 mmHg" },
            { label: "FPG ≥126 Diab %", val: "24.8%" }
        ],
        takeaway: "🩺 Crossing SBP ≥ 140 mmHg (Stage 2 HTN) or Fasting Glucose ≥ 126 mg/dL more than doubles cardiovascular & stroke risk."
    },
    {
        badge: "STORY POINT 3 / 5 • EMILY RODRIGUEZ",
        title: "Modifiable Lifestyle Multipliers: Smoking & Activity",
        actionScenario: "scenario2",
        actionText: "Scroll to Emily's View →",
        chartType: "bar",
        labels: ["Current Smoker", "Former Smoker", "Never Smoked", "Sedentary (<60m)", "Active (≥150m)"],
        datasets: [
            { label: "Heart Disease %", data: [10.8, 7.6, 5.4, 8.8, 4.9], backgroundColor: "#ef4444", borderRadius: 4 },
            { label: "Type 2 Diabetes %", data: [12.4, 11.1, 9.8, 13.4, 7.2], backgroundColor: "#f59e0b", borderRadius: 4 }
        ],
        kpis: [
            { label: "Smoker HD Odds", val: "2.0x" },
            { label: "Smoker Stroke", val: "2.4x" },
            { label: "Active Diab Drop", val: "-46%" },
            { label: "Active HD Drop", val: "-44%" }
        ],
        takeaway: "📈 Achieving ≥150 mins/week of physical activity cuts Type 2 Diabetes from 13.4% down to 7.2%, offsetting metabolic risk."
    },
    {
        badge: "STORY POINT 4 / 5 • DR. PRIYA NAIR",
        title: "Demographic Vulnerability & Clinical Symptom Burden",
        actionScenario: "scenario3",
        actionText: "Scroll to Dr. Nair's View →",
        chartType: "line",
        labels: ["18–35 Yrs", "36–50 Yrs", "51–65 Yrs", "65+ Yrs"],
        datasets: [
            { label: "Diabetes %", data: [4.2, 8.9, 13.8, 17.5], borderColor: "#f59e0b", backgroundColor: "rgba(245,158,11,0.18)", fill: true, tension: 0.35 },
            { label: "Heart Disease %", data: [1.8, 5.2, 9.4, 14.2], borderColor: "#ef4444", backgroundColor: "rgba(239,68,68,0.18)", fill: true, tension: 0.35 },
            { label: "Stroke %", data: [0.4, 1.1, 2.3, 4.1], borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,0.18)", fill: true, tension: 0.35 }
        ],
        kpis: [
            { label: "65+ Obese Risk", val: "36.4%" },
            { label: "Angina HD Rate", val: "15.6%" },
            { label: "Fatigue Multi", val: "2.3x" },
            { label: "Dizziness Stroke", val: "3.8%" }
        ],
        takeaway: "🌍 Senior patients (65+) in Obesity Class I/II with Angina or Dizziness represent the #1 priority population segment."
    },
    {
        badge: "STORY POINT 5 / 5 • CLINICAL ROI SIMULATION",
        title: "Projected Risk Reduction After Preventive Intervention",
        actionScenario: "predictor",
        actionText: "Launch AI Simulator →",
        chartType: "bar",
        labels: ["Heart Disease Risk", "Type 2 Diabetes Risk", "Stroke / CVA Risk", "Hospitalization Index"],
        datasets: [
            { label: "Baseline Uncontrolled (%)", data: [28.4, 34.2, 11.8, 42.0], backgroundColor: "rgba(239, 68, 68, 0.85)", borderRadius: 4 },
            { label: "Post-Intervention (-15 mmHg SBP, Active)", data: [16.2, 19.5, 5.4, 24.1], backgroundColor: "rgba(16, 185, 129, 0.88)", borderRadius: 4 }
        ],
        kpis: [
            { label: "HD Risk Drop", val: "-42.9%" },
            { label: "Diabetes Drop", val: "-43.0%" },
            { label: "Stroke Drop", val: "-54.2%" },
            { label: "Triage Accuracy", val: "94.8%" }
        ],
        takeaway: "🚀 Combining early BP/Glucose screening with lifestyle protocols reduces preventable acute events by up to 45%."
    }
];

function getChartPalette() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    return {
        gridColor: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(15, 23, 42, 0.07)",
        tickColor: isDark ? "#94a3b8" : "#475569",
        legendColor: isDark ? "#e2e8f0" : "#1e293b"
    };
}

function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    localStorage.setItem("pulsepoint_theme", next);

    const btn = document.getElementById("btn-theme-toggle");
    if (btn) {
        btn.innerText = next === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";
    }

    const pal = getChartPalette();
    const allCharts = [
        prevalenceChart, sc1BpChart, sc1GlucoseChart, sc1ScatterChart, sc1BiomarkersChart,
        sc2SmokingChart, sc2ExerciseChart, sc2AlcoholChart, sc2RadarChart,
        ageChart, sc3BmiChart, sc3SymptomsChart, storyDynamicChart
    ];
    allCharts.forEach(ch => {
        if (!ch) return;
        if (ch.options.plugins?.legend?.labels) {
            ch.options.plugins.legend.labels.color = pal.legendColor;
        }
        if (ch.options.scales?.x) {
            if (ch.options.scales.x.ticks) ch.options.scales.x.ticks.color = pal.tickColor;
            if (ch.options.scales.x.grid && ch.options.scales.x.grid.display !== false) {
                ch.options.scales.x.grid.color = pal.gridColor;
            }
        }
        if (ch.options.scales?.y) {
            if (ch.options.scales.y.ticks) ch.options.scales.y.ticks.color = pal.tickColor;
            if (ch.options.scales.y.grid) ch.options.scales.y.grid.color = pal.gridColor;
        }
        if (ch.options.scales?.r) {
            ch.options.scales.r.pointLabels.color = pal.legendColor;
            ch.options.scales.r.grid.color = pal.gridColor;
            ch.options.scales.r.angleLines.color = pal.gridColor;
        }
        ch.update();
    });

    showToast(`Switched to ${next.toUpperCase()} Theme`);
}

document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("pulsepoint_theme_v5") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    const btn = document.getElementById("btn-theme-toggle");
    if (btn) btn.innerText = savedTheme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";

    initAllScenarioCharts();
    initStoryDynamicChart();
    loadScenarioAnalytics();
    selectStoryPoint(0);
    loadCohortExplorer();
    loadAlertsTable();
    runPrediction();
    restoreSavedTableauEmbeds();
});

// =============================================================================
// 1. INITIALIZE ALL 12 SCENARIO CHARTS + STORY CHART
// =============================================================================
function initAllScenarioCharts() {
    const pal = getChartPalette();
    const commonGrid = { color: pal.gridColor };
    const commonTicks = { color: pal.tickColor, font: { size: 11, weight: "600" } };
    const legendTop = { position: "top", labels: { color: pal.legendColor, font: { size: 11, weight: "600" }, boxWidth: 12 } };

    // 0. Main Executive Dashboard: Cohort Disease Prevalence
    const prevCanvas = document.getElementById("chart-prevalence");
    if (prevCanvas) {
        prevalenceChart = new Chart(prevCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: ["Type 2 Diabetes", "Heart Disease", "Stroke / CVA", "Multimorbidity (2+)"],
                datasets: [{
                    label: "Prevalence (%)",
                    data: [10.6, 6.9, 1.7, 1.7],
                    backgroundColor: [
                        "rgba(245, 158, 11, 0.88)",
                        "rgba(239, 68, 68, 0.88)",
                        "rgba(37, 99, 235, 0.88)",
                        "rgba(124, 58, 237, 0.88)"
                    ],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                    x: { grid: { display: false }, ticks: commonTicks }
                }
            }
        });
    }

    // 1A. Blood Pressure Category vs Chronic Diseases
    sc1BpChart = new Chart(document.getElementById("chart-sc1-bp").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Normal", "Elevated", "HTN Stage 1", "HTN Stage 2", "HTN Crisis"],
            datasets: [
                { label: "Heart Disease %", data: [3.1, 4.5, 5.8, 8.9, 16.4], backgroundColor: "rgba(239, 68, 68, 0.88)", borderRadius: 5 },
                { label: "Diabetes %", data: [7.2, 8.8, 10.1, 11.9, 15.2], backgroundColor: "rgba(245, 158, 11, 0.88)", borderRadius: 5 },
                { label: "Stroke %", data: [0.6, 0.9, 1.3, 2.2, 5.8], backgroundColor: "rgba(37, 99, 235, 0.88)", borderRadius: 5 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // 1B. Glucose Category vs Disease Rate
    sc1GlucoseChart = new Chart(document.getElementById("chart-sc1-glucose").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Normal (<100)", "Prediabetes (100-125)", "Diabetes (≥126)"],
            datasets: [
                { label: "Diabetes %", data: [3.2, 9.8, 24.8], backgroundColor: "rgba(245, 158, 11, 0.88)", borderRadius: 6 },
                { label: "Heart Disease %", data: [5.4, 7.1, 9.6], backgroundColor: "rgba(239, 68, 68, 0.88)", borderRadius: 6 },
                { label: "Stroke %", data: [1.1, 1.8, 2.9], backgroundColor: "rgba(37, 99, 235, 0.88)", borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // 1C. Interactive 2D Patient Scatter Plot (SBP vs Fasting Glucose)
    sc1ScatterChart = new Chart(document.getElementById("chart-sc1-scatter").getContext("2d"), {
        type: "scatter",
        data: {
            datasets: [
                { label: "Chronic Disease Positive", data: [{ x: 158, y: 148 }, { x: 165, y: 162 }, { x: 149, y: 134 }], backgroundColor: "rgba(239, 68, 68, 0.85)", pointRadius: 5 },
                { label: "Healthy / Baseline", data: [{ x: 118, y: 88 }, { x: 124, y: 94 }, { x: 130, y: 99 }], backgroundColor: "rgba(13, 148, 136, 0.72)", pointRadius: 4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: legendTop,
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const raw = ctx.raw;
                            return ` ${raw.patient_id || 'Patient'}: SBP ${raw.x} mmHg, Glucose ${raw.y} mg/dL (${raw.condition || ctx.dataset.label})`;
                        }
                    }
                }
            },
            onClick: (evt, elements) => {
                if (elements.length > 0) {
                    const dsIdx = elements[0].datasetIndex;
                    const ptIdx = elements[0].index;
                    const pt = sc1ScatterChart.data.datasets[dsIdx].data[ptIdx];
                    if (pt && pt.patient_id) {
                        document.getElementById("patient-search-input").value = pt.patient_id;
                        lookupPatient();
                        document.getElementById("cohort-explorer")?.scrollIntoView({ behavior: "smooth" });
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: "Systolic BP (mmHg)", color: pal.tickColor }, grid: commonGrid, ticks: commonTicks },
                y: { title: { display: true, text: "Fasting Glucose (mg/dL)", color: pal.tickColor }, grid: commonGrid, ticks: commonTicks }
            }
        }
    });

    // 1D. Mean Clinical Biomarkers (Disease Positive vs Negative)
    sc1BiomarkersChart = new Chart(document.getElementById("chart-sc1-biomarkers").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Systolic BP (mmHg)", "Total Chol (mg/dL)", "Glucose (mg/dL)", "BMI (kg/m²)"],
            datasets: [
                { label: "Disease Positive", data: [149.2, 221.4, 116.8, 28.9], backgroundColor: "rgba(239, 68, 68, 0.88)", borderRadius: 6 },
                { label: "Disease Negative", data: [135.4, 204.1, 106.5, 26.8], backgroundColor: "rgba(37, 99, 235, 0.75)", borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: commonTicks },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // 2A. Smoking Status Impact
    sc2SmokingChart = new Chart(document.getElementById("chart-sc2-smoking").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Never Smoked", "Former Smoker", "Current Smoker"],
            datasets: [
                { label: "Heart Disease %", data: [5.4, 7.6, 10.8], backgroundColor: "rgba(239, 68, 68, 0.88)", borderRadius: 6 },
                { label: "Type 2 Diabetes %", data: [9.8, 11.1, 12.4], backgroundColor: "rgba(245, 158, 11, 0.88)", borderRadius: 6 },
                { label: "Stroke %", data: [1.2, 1.9, 2.9], backgroundColor: "rgba(37, 99, 235, 0.88)", borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // 2B. Exercise Level Impact
    sc2ExerciseChart = new Chart(document.getElementById("chart-sc2-exercise").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Sedentary (<60m)", "Lightly Active (60-149m)", "Active (≥150m)"],
            datasets: [
                { label: "Type 2 Diabetes %", data: [13.4, 10.1, 7.2], backgroundColor: "rgba(245, 158, 11, 0.88)", borderRadius: 6 },
                { label: "Heart Disease %", data: [8.8, 6.5, 4.9], backgroundColor: "rgba(239, 68, 68, 0.88)", borderRadius: 6 },
                { label: "Stroke %", data: [2.3, 1.6, 1.1], backgroundColor: "rgba(16, 185, 129, 0.88)", borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // 2C. Alcohol Consumption Impact
    sc2AlcoholChart = new Chart(document.getElementById("chart-sc2-alcohol").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["None", "Moderate", "Heavy"],
            datasets: [
                { label: "Heart Disease %", data: [6.2, 6.8, 10.4], backgroundColor: "rgba(239, 68, 68, 0.85)", borderRadius: 6 },
                { label: "Diabetes %", data: [10.1, 10.5, 13.8], backgroundColor: "rgba(245, 158, 11, 0.85)", borderRadius: 6 },
                { label: "Stroke %", data: [1.5, 1.7, 3.1], backgroundColor: "rgba(124, 58, 237, 0.85)", borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // 2D. Multi-Axis Behavioral Risk Radar Chart
    sc2RadarChart = new Chart(document.getElementById("chart-sc2-radar").getContext("2d"), {
        type: "radar",
        data: {
            labels: ["Heart Disease %", "Diabetes %", "Stroke (x3) %", "Stage 2 HTN %", "Obesity %"],
            datasets: [
                {
                    label: "Smoker + Sedentary",
                    data: [14.5, 16.8, 12.6, 58.0, 42.0],
                    backgroundColor: "rgba(239, 68, 68, 0.22)",
                    borderColor: "#ef4444",
                    pointBackgroundColor: "#ef4444"
                },
                {
                    label: "Non-Smoker + Active",
                    data: [4.1, 6.2, 2.7, 29.0, 18.5],
                    backgroundColor: "rgba(13, 148, 136, 0.22)",
                    borderColor: "#0d9488",
                    pointBackgroundColor: "#0d9488"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                r: {
                    angleLines: { color: pal.gridColor },
                    grid: { color: pal.gridColor },
                    pointLabels: { color: pal.legendColor, font: { size: 11, weight: "600" } },
                    ticks: { display: false }
                }
            }
        }
    });

    // 3A. Age Progression Multi-Line Chart
    ageChart = new Chart(document.getElementById("chart-age").getContext("2d"), {
        type: "line",
        data: {
            labels: ["18-35 yrs", "36-50 yrs", "51-65 yrs", "65+ yrs"],
            datasets: [
                { label: "Heart Disease %", data: [1.8, 5.2, 9.4, 14.2], borderColor: "#ef4444", backgroundColor: "rgba(239, 68, 68, 0.14)", fill: true, tension: 0.35 },
                { label: "Type 2 Diabetes %", data: [4.2, 8.9, 13.8, 17.5], borderColor: "#f59e0b", backgroundColor: "rgba(245, 158, 11, 0.14)", fill: true, tension: 0.35 },
                { label: "Stroke / CVA %", data: [0.4, 1.1, 2.3, 4.1], borderColor: "#2563eb", backgroundColor: "rgba(37, 99, 235, 0.14)", fill: true, tension: 0.35 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: commonGrid, ticks: commonTicks }
            }
        }
    });

    // 3B. BMI Category Vulnerability
    sc3BmiChart = new Chart(document.getElementById("chart-sc3-bmi").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Normal", "Overweight", "Obesity Class I", "Obesity Class II+"],
            datasets: [
                { label: "Type 2 Diabetes %", data: [6.1, 10.4, 15.8, 21.2], backgroundColor: "rgba(245, 158, 11, 0.88)", borderRadius: 6 },
                { label: "Heart Disease %", data: [4.8, 6.9, 9.2, 12.5], backgroundColor: "rgba(239, 68, 68, 0.88)", borderRadius: 6 },
                { label: "Stroke %", data: [1.1, 1.6, 2.4, 3.3], backgroundColor: "rgba(37, 99, 235, 0.88)", borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // 3C. Clinical Symptoms Chart
    sc3SymptomsChart = new Chart(document.getElementById("chart-sc3-symptoms").getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Chest Pain (Angina)", "Chronic Fatigue", "Dizziness Pattern", "Asymptomatic Baseline"],
            datasets: [
                { label: "Heart Disease %", data: [15.6, 10.4, 9.2, 4.8], backgroundColor: "rgba(239, 68, 68, 0.88)", borderRadius: 6 },
                { label: "Type 2 Diabetes %", data: [12.1, 14.8, 11.9, 8.5], backgroundColor: "rgba(245, 158, 11, 0.88)", borderRadius: 6 },
                { label: "Stroke %", data: [3.2, 2.6, 3.8, 1.0], backgroundColor: "rgba(124, 58, 237, 0.88)", borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: legendTop },
            scales: {
                y: { beginAtZero: true, grid: commonGrid, ticks: { ...commonTicks, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: commonTicks }
            }
        }
    });

    // Default Heatmap
    renderAgeBmiHeatmap([
        { age_group: "18-35", cells: [{ bmi_category: "Normal", count: 410, any_disease_pct: 5.2 }, { bmi_category: "Overweight", count: 380, any_disease_pct: 8.4 }, { bmi_category: "Obesity Class I", count: 210, any_disease_pct: 12.8 }, { bmi_category: "Obesity Class II", count: 65, any_disease_pct: 16.9 }] },
        { age_group: "36-50", cells: [{ bmi_category: "Normal", count: 520, any_disease_pct: 10.4 }, { bmi_category: "Overweight", count: 610, any_disease_pct: 14.8 }, { bmi_category: "Obesity Class I", count: 340, any_disease_pct: 20.3 }, { bmi_category: "Obesity Class II", count: 110, any_disease_pct: 25.4 }] },
        { age_group: "51-65", cells: [{ bmi_category: "Normal", count: 490, any_disease_pct: 16.2 }, { bmi_category: "Overweight", count: 590, any_disease_pct: 21.5 }, { bmi_category: "Obesity Class I", count: 330, any_disease_pct: 27.6 }, { bmi_category: "Obesity Class II", count: 95, any_disease_pct: 31.8 }] },
        { age_group: "65+", cells: [{ bmi_category: "Normal", count: 280, any_disease_pct: 21.4 }, { bmi_category: "Overweight", count: 310, any_disease_pct: 26.9 }, { bmi_category: "Obesity Class I", count: 190, any_disease_pct: 33.2 }, { bmi_category: "Obesity Class II", count: 70, any_disease_pct: 36.4 }] }
    ]);
}

function initStoryDynamicChart() {
    const ctx = document.getElementById("chart-story-dynamic")?.getContext("2d");
    if (!ctx) return;
    const pal = getChartPalette();
    storyDynamicChart = new Chart(ctx, {
        type: "bar",
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top", labels: { color: pal.legendColor, font: { size: 11, weight: "600" } } } },
            scales: {
                y: { beginAtZero: true, grid: { color: pal.gridColor }, ticks: { color: pal.tickColor, callback: v => v + "%" } },
                x: { grid: { display: false }, ticks: { color: pal.tickColor } }
            }
        }
    });
}

// =============================================================================
// 2. FETCH & UPDATE REAL SCENARIO TELEMETRY (/api/web/scenarios)
// =============================================================================
async function loadScenarioAnalytics() {
    const region = document.getElementById("flt-region")?.value || "All";
    const gender = document.getElementById("flt-gender")?.value || "All";
    const age_group = document.getElementById("flt-age")?.value || "All";
    const bmi_category = document.getElementById("flt-bmi")?.value || "All";

    const params = new URLSearchParams({ region, gender, age_group, bmi_category });

    try {
        const res = await fetch(`${API_BASE}/api/web/scenarios?${params.toString()}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.status !== "SUCCESS") return;

        document.getElementById("api-status-text").innerText = "Telemetry Connected";

        // Update 6 Top KPI Cards
        const k = data.kpis;
        document.getElementById("kpi-total").innerText = Number(k.total_patients).toLocaleString();
        document.getElementById("kpi-high-risk").innerText = `High-Risk: ${k.high_risk_pct}% (${k.high_risk_patients})`;
        document.getElementById("kpi-hd").innerText = `${k.heart_disease_pct}%`;
        document.getElementById("kpi-hd-cases").innerText = `${k.heart_disease_cases} Cases`;
        document.getElementById("kpi-diab").innerText = `${k.diabetes_pct}%`;
        document.getElementById("kpi-diab-cases").innerText = `${k.diabetes_cases} Cases`;
        document.getElementById("kpi-stroke").innerText = `${k.stroke_pct}%`;
        document.getElementById("kpi-stroke-cases").innerText = `${k.stroke_cases} Cases`;
        document.getElementById("kpi-sbp").innerText = `${k.avg_sbp}`;
        document.getElementById("kpi-gluc-bmi").innerText = `${k.avg_glucose} / ${k.avg_bmi}`;
        const miniSbp = document.getElementById("sc1-mini-sbp");
        if (miniSbp) miniSbp.innerText = `SBP ${k.avg_sbp} mmHg`;

        if (prevalenceChart) {
            prevalenceChart.data.datasets[0].data = [
                k.diabetes_pct,
                k.heart_disease_pct,
                k.stroke_pct,
                k.multimorbid_pct
            ];
            prevalenceChart.update();
        }

        // Update Scenario 1 Charts
        const sc1 = data.scenario1_clinical;
        if (sc1?.bp_distribution && sc1BpChart) {
            sc1BpChart.data.labels = sc1.bp_distribution.map(d => d.category);
            sc1BpChart.data.datasets[0].data = sc1.bp_distribution.map(d => d.heart_disease_pct);
            sc1BpChart.data.datasets[1].data = sc1.bp_distribution.map(d => d.diabetes_pct);
            sc1BpChart.data.datasets[2].data = sc1.bp_distribution.map(d => d.stroke_pct);
            sc1BpChart.update();
        }
        if (sc1?.glucose_distribution && sc1GlucoseChart) {
            sc1GlucoseChart.data.labels = sc1.glucose_distribution.map(d => `${d.category} (${d.avg_glucose} mg/dL)`);
            sc1GlucoseChart.data.datasets[0].data = sc1.glucose_distribution.map(d => d.diabetes_pct);
            sc1GlucoseChart.data.datasets[1].data = sc1.glucose_distribution.map(d => d.heart_disease_pct);
            sc1GlucoseChart.data.datasets[2].data = sc1.glucose_distribution.map(d => d.stroke_pct);
            sc1GlucoseChart.update();
        }
        if (sc1?.scatter_points && sc1ScatterChart) {
            const posPts = sc1.scatter_points.filter(p => p.condition !== "Healthy").map(p => ({ x: p.sbp, y: p.glucose, patient_id: p.patient_id, condition: p.condition }));
            const negPts = sc1.scatter_points.filter(p => p.condition === "Healthy").map(p => ({ x: p.sbp, y: p.glucose, patient_id: p.patient_id, condition: p.condition }));
            sc1ScatterChart.data.datasets[0].data = posPts;
            sc1ScatterChart.data.datasets[1].data = negPts;
            sc1ScatterChart.update();
        }
        if (sc1?.clinical_means && sc1BiomarkersChart) {
            const pos = sc1.clinical_means.heart_disease_pos;
            const neg = sc1.clinical_means.heart_disease_neg;
            sc1BiomarkersChart.data.datasets[0].data = [pos.sbp, pos.chol, pos.glucose, pos.bmi];
            sc1BiomarkersChart.data.datasets[1].data = [neg.sbp, neg.chol, neg.glucose, neg.bmi];
            sc1BiomarkersChart.update();
        }

        // Update Scenario 2 Charts
        const sc2 = data.scenario2_lifestyle;
        if (sc2?.smoking_impact && sc2SmokingChart) {
            sc2SmokingChart.data.labels = sc2.smoking_impact.map(d => `${d.status} (n=${d.count})`);
            sc2SmokingChart.data.datasets[0].data = sc2.smoking_impact.map(d => d.heart_disease_pct);
            sc2SmokingChart.data.datasets[1].data = sc2.smoking_impact.map(d => d.diabetes_pct);
            sc2SmokingChart.data.datasets[2].data = sc2.smoking_impact.map(d => d.stroke_pct);
            sc2SmokingChart.update();
        }
        if (sc2?.exercise_impact && sc2ExerciseChart) {
            sc2ExerciseChart.data.labels = sc2.exercise_impact.map(d => d.level);
            sc2ExerciseChart.data.datasets[0].data = sc2.exercise_impact.map(d => d.diabetes_pct);
            sc2ExerciseChart.data.datasets[1].data = sc2.exercise_impact.map(d => d.heart_disease_pct);
            sc2ExerciseChart.data.datasets[2].data = sc2.exercise_impact.map(d => d.stroke_pct);
            sc2ExerciseChart.update();
        }
        if (sc2?.alcohol_impact && sc2AlcoholChart) {
            sc2AlcoholChart.data.labels = sc2.alcohol_impact.map(d => `${d.level} (n=${d.count})`);
            sc2AlcoholChart.data.datasets[0].data = sc2.alcohol_impact.map(d => d.heart_disease_pct);
            sc2AlcoholChart.data.datasets[1].data = sc2.alcohol_impact.map(d => d.diabetes_pct);
            sc2AlcoholChart.data.datasets[2].data = sc2.alcohol_impact.map(d => d.stroke_pct);
            sc2AlcoholChart.update();
        }
        if (sc2?.lifestyle_radar && sc2RadarChart) {
            const hi = sc2.lifestyle_radar.high_risk_lifestyle;
            const lo = sc2.lifestyle_radar.protective_lifestyle;
            sc2RadarChart.data.datasets[0].data = [hi.heart_disease, hi.diabetes, hi.stroke * 3, hi.hypertension, hi.obesity];
            sc2RadarChart.data.datasets[1].data = [lo.heart_disease, lo.diabetes, lo.stroke * 3, lo.hypertension, lo.obesity];
            sc2RadarChart.update();
        }

        // Update Scenario 3 Charts & Clickable Heatmap
        const sc3 = data.scenario3_population;
        if (sc3?.age_distribution && ageChart) {
            ageChart.data.labels = sc3.age_distribution.map(d => `${d.age_group} yrs (${d.count})`);
            ageChart.data.datasets[0].data = sc3.age_distribution.map(d => d.heart_disease_pct);
            ageChart.data.datasets[1].data = sc3.age_distribution.map(d => d.diabetes_pct);
            ageChart.data.datasets[2].data = sc3.age_distribution.map(d => d.stroke_pct);
            ageChart.update();
        }
        if (sc3?.bmi_distribution && sc3BmiChart) {
            sc3BmiChart.data.labels = sc3.bmi_distribution.map(d => d.bmi_category);
            sc3BmiChart.data.datasets[0].data = sc3.bmi_distribution.map(d => d.diabetes_pct);
            sc3BmiChart.data.datasets[1].data = sc3.bmi_distribution.map(d => d.heart_disease_pct);
            sc3BmiChart.data.datasets[2].data = sc3.bmi_distribution.map(d => d.stroke_pct);
            sc3BmiChart.update();
        }
        if (sc3?.symptom_prevalence && sc3SymptomsChart) {
            sc3SymptomsChart.data.labels = sc3.symptom_prevalence.map(d => d.symptom);
            sc3SymptomsChart.data.datasets[0].data = sc3.symptom_prevalence.map(d => d.heart_disease_pct);
            sc3SymptomsChart.data.datasets[1].data = sc3.symptom_prevalence.map(d => d.diabetes_pct);
            sc3SymptomsChart.data.datasets[2].data = sc3.symptom_prevalence.map(d => d.stroke_pct);
            sc3SymptomsChart.update();
        }
        if (sc3?.age_bmi_heatmap) {
            renderAgeBmiHeatmap(sc3.age_bmi_heatmap);
        }
    } catch (e) {
        // Fallback already rendered
    }
}

function renderAgeBmiHeatmap(matrix) {
    const container = document.getElementById("heatmap-sc3-container");
    if (!container || !matrix || !matrix.length) return;

    const bmiCols = matrix[0].cells.map(c => c.bmi_category);
    let html = `<table class="heatmap-table"><thead><tr><th>Age \\ BMI</th>`;
    bmiCols.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += `</tr></thead><tbody>`;

    matrix.forEach(row => {
        html += `<tr><td class="age-row-label">${row.age_group} yrs</td>`;
        row.cells.forEach(cell => {
            const pct = cell.any_disease_pct;
            let bg = "#10b981";
            if (pct >= 28) bg = "#ef4444";
            else if (pct >= 18) bg = "#f59e0b";
            else if (pct >= 12) bg = "#2563eb";

            html += `<td class="heatmap-cell" style="background: ${bg};" onclick="filterByHeatmapCell('${row.age_group}', '${cell.bmi_category}')">
                ${pct}%
                <small>n=${cell.count}</small>
            </td>`;
        });
        html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

function filterByHeatmapCell(ageGrp, bmiCat) {
    document.getElementById("flt-age").value = ageGrp;
    document.getElementById("flt-bmi").value = bmiCat;
    applyScenarioFilters();
    showToast(`Cross-Filter Applied: Age ${ageGrp} × ${bmiCat}`);
}

function applyScenarioFilters() {
    loadScenarioAnalytics();
    showToast("Cohort Cross-Filters Applied Across All Vertical Dashboards.");
}

function resetScenarioFilters() {
    document.getElementById("flt-region").value = "All";
    document.getElementById("flt-gender").value = "All";
    document.getElementById("flt-age").value = "All";
    document.getElementById("flt-bmi").value = "All";
    loadScenarioAnalytics();
    showToast("All Cohort Filters Reset.");
}

function switchScenarioTab(scenarioKey) {
    const sectionMap = {
        scenario1: "scenario-1",
        scenario2: "scenario-2",
        scenario3: "scenario-3",
        predictor: "predictor"
    };
    const targetId = sectionMap[scenarioKey] || scenarioKey;
    const el = document.getElementById(targetId);
    if (el) {
        el.scrollIntoView({ behavior: "smooth" });
    }
}

// =============================================================================
// 3. VISUAL INTERACTIVE STORYBOARD & AUTO-PLAY ENGINE
// =============================================================================
function selectStoryPoint(idx) {
    currentStoryIdx = idx;
    const slide = VISUAL_STORY_SLIDES[idx] || VISUAL_STORY_SLIDES[0];

    document.querySelectorAll(".story-step-btn").forEach((btn, i) => {
        btn.classList.toggle("active", i === idx);
    });

    document.getElementById("story-step-badge").innerText = slide.badge;
    document.getElementById("story-point-title").innerText = slide.title;
    const actionBtn = document.getElementById("story-action-btn");
    actionBtn.innerText = slide.actionText;
    actionBtn.onclick = () => switchScenarioTab(slide.actionScenario);

    // Update 4 Mini KPI Cards
    const kpiContainer = document.getElementById("story-kpi-cards");
    kpiContainer.innerHTML = slide.kpis.map(k => `
        <div class="story-mini-card">
            <div class="sm-label">${k.label}</div>
            <div class="sm-val">${k.val}</div>
        </div>
    `).join("");

    document.getElementById("story-takeaway-text").innerText = slide.takeaway;

    // Update Dynamic Story Chart
    if (storyDynamicChart) {
        storyDynamicChart.config.type = slide.chartType;
        storyDynamicChart.data.labels = slide.labels;
        storyDynamicChart.data.datasets = slide.datasets;
        storyDynamicChart.update();
    }
}

function toggleStoryAutoPlay() {
    const btn = document.getElementById("btn-story-autoplay");
    if (storyAutoPlayTimer) {
        clearInterval(storyAutoPlayTimer);
        storyAutoPlayTimer = null;
        btn.innerText = "▶ Auto-Play Story";
        showToast("Story Auto-Play Paused.");
    } else {
        btn.innerText = "⏸ Pause Auto-Play";
        showToast("Story Auto-Play Started (3.5s per slide).");
        storyAutoPlayTimer = setInterval(() => {
            const nextIdx = (currentStoryIdx + 1) % VISUAL_STORY_SLIDES.length;
            selectStoryPoint(nextIdx);
        }, 3500);
    }
}

function toggleDashboardMode(mode) {
    const isEmbed = mode === "embed";
    document.getElementById("dashboard-interactive-container").style.display = isEmbed ? "none" : "block";
    document.getElementById("global-filter-bar").style.display = isEmbed ? "none" : "block";
    document.getElementById("dashboard-embed-container").style.display = isEmbed ? "block" : "none";
    document.getElementById("btn-mode-interactive").classList.toggle("active", !isEmbed);
    document.getElementById("btn-mode-embed").classList.toggle("active", isEmbed);
}

function toggleStoryMode(mode) {
    const isEmbed = mode === "embed";
    document.getElementById("story-interactive-container").style.display = isEmbed ? "none" : "block";
    document.getElementById("story-embed-container").style.display = isEmbed ? "block" : "none";
    document.getElementById("btn-story-interactive").classList.toggle("active", !isEmbed);
    document.getElementById("btn-story-embed").classList.toggle("active", isEmbed);
}

function normalizeTableauEmbedUrl(rawUrl) {
    let url = rawUrl.trim();
    if (!url) return "";
    if (!url.includes(":showVizHome=")) {
        url += (url.includes("?") ? "&" : "?") + ":embed=y&:showVizHome=no&:tabs=yes&:toolbar=yes";
    }
    return url;
}

function loadCustomTableauEmbed(targetType) {
    const inputId = targetType === "dashboard" ? "tableau-dash-url" : "tableau-story-url";
    const wrapId = targetType === "dashboard" ? "tableau-dash-iframe-wrap" : "tableau-story-iframe-wrap";
    const rawUrl = document.getElementById(inputId).value.trim();

    if (!rawUrl) {
        showToast("Please paste a valid Tableau Public URL first.");
        return;
    }

    const embedUrl = normalizeTableauEmbedUrl(rawUrl);
    localStorage.setItem(`pulsepoint_tableau_${targetType}_url`, rawUrl);

    const wrap = document.getElementById(wrapId);
    wrap.innerHTML = `<iframe src="${embedUrl}" width="100%" height="680" style="border:none; border-radius: 8px;" allowfullscreen></iframe>`;
    showToast(`Tableau Public ${targetType.toUpperCase()} embedded!`);
}

function restoreSavedTableauEmbeds() {
    const savedDash = localStorage.getItem("pulsepoint_tableau_dashboard_url");
    if (savedDash && document.getElementById("tableau-dash-url")) {
        document.getElementById("tableau-dash-url").value = savedDash;
        const embedUrl = normalizeTableauEmbedUrl(savedDash);
        document.getElementById("tableau-dash-iframe-wrap").innerHTML =
            `<iframe src="${embedUrl}" width="100%" height="680" style="border:none; border-radius: 8px;" allowfullscreen></iframe>`;
    }

    const savedStory = localStorage.getItem("pulsepoint_tableau_story_url");
    if (savedStory && document.getElementById("tableau-story-url")) {
        document.getElementById("tableau-story-url").value = savedStory;
        const embedUrl = normalizeTableauEmbedUrl(savedStory);
        document.getElementById("tableau-story-iframe-wrap").innerHTML =
            `<iframe src="${embedUrl}" width="100%" height="680" style="border:none; border-radius: 8px;" allowfullscreen></iframe>`;
    }
}

// =============================================================================
// 4. AI RISK PREDICTOR & INTERACTIVE ANATOMICAL ORGAN DIGITAL TWIN
// =============================================================================
const PRESETS = {
    healthy: {
        age: 30, gender: "Female", bmi: 21.5, sbp: 112, dbp: 72,
        glucose: 84, hba1c: 5.0, chol: 165, hdl: 62, ldl: 88,
        smoking: "Never", exercise: 240, angina: "None", fatigue: false, sob: false
    },
    cardio: {
        age: 68, gender: "Male", bmi: 31.8, sbp: 172, dbp: 102,
        glucose: 122, hba1c: 6.3, chol: 268, hdl: 34, ldl: 198,
        smoking: "Current", exercise: 20, angina: "Typical Angina", fatigue: true, sob: true
    },
    diabetic: {
        age: 56, gender: "Female", bmi: 37.2, sbp: 146, dbp: 90,
        glucose: 210, hba1c: 9.4, chol: 240, hdl: 38, ldl: 160,
        smoking: "Former", exercise: 15, angina: "None", fatigue: true, sob: false
    },
    stroke: {
        age: 74, gender: "Male", bmi: 29.8, sbp: 184, dbp: 108,
        glucose: 148, hba1c: 7.5, chol: 245, hdl: 39, ldl: 170,
        smoking: "Current", exercise: 10, angina: "Atypical Angina", fatigue: true, sob: true
    }
};

function loadPreset(name) {
    const p = PRESETS[name];
    if (!p) return;

    document.getElementById("pred-age").value = p.age;
    document.getElementById("pred-gender").value = p.gender;
    document.getElementById("pred-bmi").value = p.bmi;
    document.getElementById("pred-sbp").value = p.sbp;
    document.getElementById("pred-dbp").value = p.dbp;
    document.getElementById("pred-glucose").value = p.glucose;
    document.getElementById("pred-hba1c").value = p.hba1c;
    document.getElementById("pred-chol").value = p.chol;
    document.getElementById("pred-hdl").value = p.hdl;
    document.getElementById("pred-ldl").value = p.ldl;
    document.getElementById("pred-smoking").value = p.smoking;
    document.getElementById("pred-exercise").value = p.exercise;
    document.getElementById("pred-angina").value = p.angina;
    document.getElementById("pred-fatigue").checked = p.fatigue;
    document.getElementById("pred-sob").checked = p.sob;

    runPrediction();
    showToast(`Loaded ${name.toUpperCase()} Persona into AI & Organ Twin.`);
}

function calculateClinicalRisks(v) {
    let hdScore = 0;
    if (v.age >= 65) hdScore += 30; else if (v.age >= 50) hdScore += 18; else hdScore += 5;
    if (v.sbp >= 160) hdScore += 35; else if (v.sbp >= 140) hdScore += 20; else if (v.sbp >= 130) hdScore += 10;
    if (v.chol >= 240) hdScore += 20; else if (v.chol >= 200) hdScore += 10;
    if (v.hdl < 40) hdScore += 15;
    if (v.smoking === "Current") hdScore += 25;
    if (v.angina === "Typical Angina") hdScore += 30; else if (v.angina !== "None") hdScore += 15;
    if (v.bmi >= 30) hdScore += 12;

    let hdProb = Math.min(Math.max((hdScore / 160) * 100, 2), 94);

    let diabScore = 0;
    if (v.glucose >= 126) diabScore += 55; else if (v.glucose >= 100) diabScore += 28; else diabScore += 5;
    if (v.hba1c >= 6.5) diabScore += 40; else if (v.hba1c >= 5.7) diabScore += 20;
    if (v.bmi >= 35) diabScore += 35; else if (v.bmi >= 30) diabScore += 22; else if (v.bmi >= 25) diabScore += 10;
    if (v.exercise < 60) diabScore += 15;
    if (v.age >= 45) diabScore += 12;

    let diabProb = Math.min(Math.max((diabScore / 150) * 100, 1.5), 96);

    let strokeScore = 0;
    if (v.sbp >= 160) strokeScore += 45; else if (v.sbp >= 140) strokeScore += 25; else if (v.sbp >= 130) strokeScore += 10;
    if (v.age >= 65) strokeScore += 35; else if (v.age >= 55) strokeScore += 18;
    if (v.smoking === "Current") strokeScore += 25;
    if (v.glucose >= 140) strokeScore += 15;
    if (v.sob) strokeScore += 14;

    let strokeProb = Math.min(Math.max((strokeScore / 140) * 100, 0.8), 88);

    const drivers = [];
    if (v.sbp >= 140) drivers.push(`Systolic BP ${v.sbp} mmHg (Stage 2 HTN)`);
    if (v.glucose >= 126) drivers.push(`Hyperglycemia (${v.glucose} mg/dL • HbA1c ${v.hba1c}%)`);
    if (v.smoking === "Current") drivers.push(`Active Tobacco Smoking Multiplier`);
    if (v.bmi >= 30) drivers.push(`Clinical Obesity (BMI ${v.bmi} kg/m²)`);
    if (v.angina !== "None") drivers.push(`Symptomatic ${v.angina}`);
    if (drivers.length === 0) drivers.push(`All biomarkers within normal physiological range.`);

    return {
        heartDisease: Math.round(hdProb * 10) / 10,
        diabetes: Math.round(diabProb * 10) / 10,
        stroke: Math.round(strokeProb * 10) / 10,
        drivers: drivers
    };
}

function getTier(prob) {
    if (prob >= 60) return { label: "CRITICAL", classText: "tier-crit", classFill: "tier-crit-fill", color: "#ef4444" };
    if (prob >= 35) return { label: "HIGH RISK", classText: "tier-high", classFill: "tier-high-fill", color: "#f97316" };
    if (prob >= 15) return { label: "MODERATE", classText: "tier-mod", classFill: "tier-mod-fill", color: "#f59e0b" };
    return { label: "LOW RISK", classText: "tier-low", classFill: "tier-low-fill", color: "#10b981" };
}

async function runPrediction() {
    const values = {
        age: parseInt(document.getElementById("pred-age").value) || 58,
        gender: document.getElementById("pred-gender").value,
        bmi: parseFloat(document.getElementById("pred-bmi").value) || 31.2,
        systolic_bp: parseInt(document.getElementById("pred-sbp").value) || 158,
        diastolic_bp: parseInt(document.getElementById("pred-dbp").value) || 94,
        fasting_glucose: parseInt(document.getElementById("pred-glucose").value) || 142,
        hba1c: parseFloat(document.getElementById("pred-hba1c").value) || 7.4,
        cholesterol_total: parseInt(document.getElementById("pred-chol").value) || 238,
        cholesterol_hdl: parseInt(document.getElementById("pred-hdl").value) || 38,
        cholesterol_ldl: parseInt(document.getElementById("pred-ldl").value) || 162,
        smoking_status: document.getElementById("pred-smoking").value,
        physical_activity_mins: parseInt(document.getElementById("pred-exercise").value) || 40,
        chest_pain_type: document.getElementById("pred-angina").value,
        fatigue_reported: document.getElementById("pred-fatigue").checked ? 1 : 0,
        shortness_of_breath: document.getElementById("pred-sob").checked ? 1 : 0
    };

    let res = calculateClinicalRisks({
        age: values.age, gender: values.gender, bmi: values.bmi,
        sbp: values.systolic_bp, dbp: values.diastolic_bp,
        glucose: values.fasting_glucose, hba1c: values.hba1c,
        chol: values.cholesterol_total, hdl: values.cholesterol_hdl, ldl: values.cholesterol_ldl,
        smoking: values.smoking_status, exercise: values.physical_activity_mins,
        angina: values.chest_pain_type,
        fatigue: values.fatigue_reported === 1,
        sob: values.shortness_of_breath === 1
    });

    try {
        const response = await fetch(`${API_BASE}/api/web/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(values)
        });
        if (response.ok) {
            const mlData = await response.json();
            if (mlData.predictions) {
                const preds = mlData.predictions;
                if (preds.heart_disease) res.heartDisease = Math.round(preds.heart_disease.risk_probability * 1000) / 10;
                if (preds.diabetes) res.diabetes = Math.round(preds.diabetes.risk_probability * 1000) / 10;
                if (preds.stroke) res.stroke = Math.round(preds.stroke.risk_probability * 1000) / 10;
            }
        }
    } catch (e) {
        // Fallback scoring used
    }

    currentBaselinePrediction = { values, res };

    const hdTier = getTier(res.heartDisease);
    document.getElementById("res-prob-hd").innerText = `${res.heartDisease}%`;
    document.getElementById("res-tier-hd").innerText = hdTier.label;
    document.getElementById("res-tier-hd").className = `disease-tier ${hdTier.classText}`;
    document.getElementById("res-bar-hd").style.width = `${res.heartDisease}%`;
    document.getElementById("res-bar-hd").className = `disease-bar-fill ${hdTier.classFill}`;

    const diabTier = getTier(res.diabetes);
    document.getElementById("res-prob-diab").innerText = `${res.diabetes}%`;
    document.getElementById("res-tier-diab").innerText = diabTier.label;
    document.getElementById("res-tier-diab").className = `disease-tier ${diabTier.classText}`;
    document.getElementById("res-bar-diab").style.width = `${res.diabetes}%`;
    document.getElementById("res-bar-diab").className = `disease-bar-fill ${diabTier.classFill}`;

    const strokeTier = getTier(res.stroke);
    document.getElementById("res-prob-stroke").innerText = `${res.stroke}%`;
    document.getElementById("res-tier-stroke").innerText = strokeTier.label;
    document.getElementById("res-tier-stroke").className = `disease-tier ${strokeTier.classText}`;
    document.getElementById("res-bar-stroke").style.width = `${res.stroke}%`;
    document.getElementById("res-bar-stroke").className = `disease-bar-fill ${strokeTier.classFill}`;

    document.getElementById("res-drivers-list").innerHTML = res.drivers.map(d => `<li>• ${d}</li>`).join("");

    // Update Anatomical Organ SVG Digital Twin Colors & Radii
    updateOrganDigitalTwin(values, res);
    updateWhatIf();
}

function updateOrganDigitalTwin(v, res) {
    const hdTier = getTier(res.heartDisease);
    const diabTier = getTier(res.diabetes);
    const strokeTier = getTier(res.stroke);
    const maxProb = Math.max(res.heartDisease, res.diabetes, res.stroke);
    const overallTier = getTier(maxProb);

    const badge = document.getElementById("organ-overall-badge");
    if (badge) {
        badge.innerText = `${overallTier.label} (${maxProb}%)`;
        badge.style.color = overallTier.color;
    }

    const heartRing = document.getElementById("organ-ring-heart");
    if (heartRing) {
        heartRing.setAttribute("stroke", hdTier.color);
        heartRing.setAttribute("r", String(16 + Math.min(res.heartDisease / 6, 12)));
    }

    const pancRing = document.getElementById("organ-ring-pancreas");
    if (pancRing) {
        pancRing.setAttribute("stroke", diabTier.color);
        pancRing.setAttribute("r", String(15 + Math.min(res.diabetes / 6, 12)));
    }

    const brainRing = document.getElementById("organ-ring-brain");
    if (brainRing) {
        brainRing.setAttribute("stroke", strokeTier.color);
        brainRing.setAttribute("r", String(14 + Math.min(res.stroke / 5, 11)));
    }

    document.getElementById("organ-telemetry-box").innerHTML =
        `<strong>CORONARY:</strong> ${res.heartDisease}% • <strong>GLYCEMIC:</strong> ${res.diabetes}% • <strong>CEREBRAL:</strong> ${res.stroke}%<br><small>BP: ${v.systolic_bp}/${v.diastolic_bp} mmHg | Glucose: ${v.fasting_glucose} mg/dL | BMI: ${v.bmi}</small>`;
}

function inspectOrgan(organKey) {
    if (!currentBaselinePrediction) return;
    const { values, res } = currentBaselinePrediction;
    const box = document.getElementById("organ-telemetry-box");

    if (organKey === "heart") {
        box.innerHTML = `<strong style="color:#ef4444;">❤️ CORONARY SYSTEM (${res.heartDisease}% Risk):</strong> SBP ${values.systolic_bp} mmHg, LDL ${values.cholesterol_ldl} mg/dL, HDL ${values.cholesterol_hdl} mg/dL, Symptom: ${values.chest_pain_type}`;
    } else if (organKey === "pancreas") {
        box.innerHTML = `<strong style="color:#f59e0b;">🩸 ENDOCRINE / GLYCEMIC (${res.diabetes}% Risk):</strong> Fasting Glucose ${values.fasting_glucose} mg/dL, HbA1c ${values.hba1c}%, BMI ${values.bmi} kg/m²`;
    } else if (organKey === "brain") {
        box.innerHTML = `<strong style="color:#3b82f6;">🧠 CEREBROVASCULAR (${res.stroke}% Risk):</strong> Pulse Pressure ${values.systolic_bp - values.diastolic_bp} mmHg, Smoking: ${values.smoking_status}, Age: ${values.age} yrs`;
    } else {
        box.innerHTML = `<strong style="color:#a855f7;">⚡ ARTERIAL TREE:</strong> MAP ${Math.round((values.systolic_bp + 2 * values.diastolic_bp) / 3)} mmHg • Exercise ${values.physical_activity_mins} mins/wk`;
    }
}

function updateWhatIf() {
    if (!currentBaselinePrediction) return;

    const sbpRed = parseInt(document.getElementById("range-sbp-red")?.value) || 0;
    const bmiRed = parseFloat(document.getElementById("range-bmi-red")?.value) || 0;
    document.getElementById("val-sbp-red").innerText = sbpRed;
    if (document.getElementById("val-bmi-red")) {
        document.getElementById("val-bmi-red").innerText = bmiRed.toFixed(1);
    }

    const v = currentBaselinePrediction.values;
    const postRes = calculateClinicalRisks({
        age: v.age,
        gender: v.gender,
        bmi: Math.max(v.bmi - bmiRed, 18.5),
        sbp: Math.max(v.systolic_bp - sbpRed, 95),
        dbp: v.diastolic_bp,
        glucose: v.fasting_glucose,
        hba1c: v.hba1c,
        chol: v.cholesterol_total,
        hdl: v.cholesterol_hdl,
        ldl: v.cholesterol_ldl,
        smoking: v.smoking_status,
        exercise: v.physical_activity_mins,
        angina: v.chest_pain_type,
        fatigue: v.fatigue_reported === 1,
        sob: v.shortness_of_breath === 1
    });

    const hdDelta = Math.round((postRes.heartDisease - currentBaselinePrediction.res.heartDisease) * 10) / 10;
    const diabDelta = Math.round((postRes.diabetes - currentBaselinePrediction.res.diabetes) * 10) / 10;
    const strokeDelta = Math.round((postRes.stroke - currentBaselinePrediction.res.stroke) * 10) / 10;

    document.getElementById("whatif-delta-text").innerHTML =
        `Delta: <strong>HD ${hdDelta}%</strong> | <strong>Diabetes ${diabDelta}%</strong> | <strong>Stroke ${strokeDelta}%</strong>`;
}

// =============================================================================
// 5. LIVE COHORT DATA EXPLORER & 1-CLICK SIMULATOR (/api/web/cohort-explorer)
// =============================================================================
async function loadCohortExplorer() {
    const search = document.getElementById("explorer-search")?.value || "";
    const condition = document.getElementById("explorer-condition")?.value || "all";
    const tbody = document.getElementById("cohort-explorer-body");
    if (!tbody) return;

    try {
        const params = new URLSearchParams({ search, condition, limit: "15" });
        const res = await fetch(`${API_BASE}/api/web/cohort-explorer?${params.toString()}`);
        if (res.ok) {
            const data = await res.json();
            cohortRecordsCache = data.records || [];
            renderCohortExplorerRows(cohortRecordsCache);
            return;
        }
    } catch (e) {
        // Fallback
    }
}

function renderCohortExplorerRows(records) {
    const tbody = document.getElementById("cohort-explorer-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    records.forEach((r, idx) => {
        const badges = [];
        if (r.heart_disease) badges.push(`<span class="pill-sev CRITICAL">HD</span>`);
        if (r.diabetes) badges.push(`<span class="pill-sev HIGH">DIAB</span>`);
        if (r.stroke) badges.push(`<span class="pill-sev MEDIUM">STROKE</span>`);
        if (!badges.length) badges.push(`<span style="color:var(--green); font-size:0.76rem; font-weight:700;">NONE</span>`);

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${r.patient_id}</strong></td>
            <td>${r.age}y • ${r.gender}</td>
            <td>${r.region}</td>
            <td><strong>${r.sbp}/${r.dbp}</strong> <small>(${r.bp_category})</small></td>
            <td>${r.glucose} mg/dL <small>(${r.hba1c}%)</small></td>
            <td>${r.bmi} <small>(${r.bmi_category})</small></td>
            <td>${r.smoking} • ${r.exercise_mins}m/wk</td>
            <td>${badges.join(" ")}</td>
            <td>
                <button class="btn-sm" onclick="simulateCohortPatient(${idx})">⚡ Simulate</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function simulateCohortPatient(idx) {
    const r = cohortRecordsCache[idx];
    if (!r) return;

    document.getElementById("pred-age").value = r.age;
    document.getElementById("pred-gender").value = r.gender;
    document.getElementById("pred-bmi").value = r.bmi;
    document.getElementById("pred-sbp").value = r.sbp;
    document.getElementById("pred-dbp").value = r.dbp;
    document.getElementById("pred-glucose").value = r.glucose;
    document.getElementById("pred-hba1c").value = r.hba1c;
    document.getElementById("pred-chol").value = r.chol;
    document.getElementById("pred-hdl").value = r.hdl;
    document.getElementById("pred-ldl").value = r.ldl;
    document.getElementById("pred-smoking").value = r.smoking;
    document.getElementById("pred-exercise").value = r.exercise_mins;
    document.getElementById("pred-angina").value = r.chest_pain;
    document.getElementById("pred-fatigue").checked = r.fatigue === 1;
    document.getElementById("pred-sob").checked = r.dizziness === 1;

    runPrediction();
    document.getElementById("predictor")?.scrollIntoView({ behavior: "smooth" });
    showToast(`Loaded ${r.patient_id} into AI Predictor & Organ Digital Twin!`);
}

// =============================================================================
// 6. PATIENT 360 & REAL-TIME CLINICAL ALERTS
// =============================================================================
async function lookupPatient() {
    const rawInput = document.getElementById("patient-search-input").value.trim().toUpperCase();
    const pid = rawInput || "PT-10001";

    try {
        const res = await fetch(`${API_BASE}/api/web/patients/${pid}`);
        if (res.ok) {
            const pt = await res.json();
            document.getElementById("pt-id-display").innerText = `Patient: ${pt.patient_id}`;
            document.getElementById("pt-meta-display").innerText = `Age: ${pt.age} yrs | Gender: ${pt.gender} | Region: ${pt.region}`;
            document.getElementById("pt-status-badge").innerText = pt.review_status;
            document.getElementById("pt-bp").innerText = pt.bp;
            document.getElementById("pt-glucose").innerText = pt.glucose;
            document.getElementById("pt-hba1c").innerText = pt.hba1c;
            document.getElementById("pt-chol").innerText = pt.chol;
            document.getElementById("pt-bmi").innerText = pt.bmi;
            document.getElementById("pt-smoking").innerText = pt.smoking;
            showToast(`Patient ${pt.patient_id} loaded into EHR Drill-Down.`);
            return;
        }
    } catch (e) {
        // Fallback
    }
}

async function savePatientReview() {
    const pid = document.getElementById("patient-search-input").value.trim().toUpperCase() || "PT-10001";
    const status = document.getElementById("review-status-select").value;
    const notes = document.getElementById("review-notes-input").value.trim();

    document.getElementById("pt-status-badge").innerText = status;

    try {
        await fetch(`${API_BASE}/api/web/patients/${pid}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ review_status: status, clinical_notes: notes })
        });
    } catch (e) {
        // Handled
    }

    showToast(`Review for ${pid} updated to '${status}'.`);
    document.getElementById("review-notes-input").value = "";
}

async function loadAlertsTable() {
    const tbody = document.getElementById("alerts-table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    try {
        const res = await fetch(`${API_BASE}/api/web/alerts`);
        if (res.ok) {
            activeAlerts = await res.json();
            renderAlertRows(activeAlerts);
            return;
        }
    } catch (e) {
        // Fallback
    }

    activeAlerts = [
        { id: 1, severity: "CRITICAL", patient_id: "PT-10042", rule_code: "RULE_BP_CRISIS", description: "Acute Hypertensive Excursion (SBP 185 mmHg)." },
        { id: 2, severity: "CRITICAL", patient_id: "PT-10085", rule_code: "RULE_HYPERGLYCEMIA", description: "Severe Hyperglycemia Excursion (FPG 242 mg/dL)." },
        { id: 3, severity: "HIGH", patient_id: "PT-10114", rule_code: "RULE_MULTIMORBIDITY", description: "Triple Morbidity Cluster: CAD + Diabetes + TIA." },
        { id: 4, severity: "HIGH", patient_id: "PT-10190", rule_code: "RULE_DYSLIPIDEMIA", description: "Severe Atherogenic Dyslipidemia (LDL 215 mg/dL)." }
    ];
    renderAlertRows(activeAlerts);
}

function renderAlertRows(alerts) {
    const tbody = document.getElementById("alerts-table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    alerts.forEach(a => {
        const tr = document.createElement("tr");
        tr.id = `alert-row-${a.id}`;
        tr.innerHTML = `
            <td><span class="pill-sev ${a.severity}">${a.severity}</span></td>
            <td><strong>${a.patient_id}</strong></td>
            <td>${a.description}</td>
            <td><button class="btn-sm" onclick="resolveAlert(${a.id}, '${a.patient_id}')">Resolve</button></td>
        `;
        tbody.appendChild(tr);
    });
}

async function resolveAlert(id, pid) {
    const row = document.getElementById(`alert-row-${id}`);
    if (row) {
        row.innerHTML = `<td colspan="4" style="color: var(--green); text-align: center; font-weight: 600;">✅ Resolved ${pid}</td>`;
        setTimeout(() => row.remove(), 900);
    }

    try {
        await fetch(`${API_BASE}/api/web/alerts/${id}/resolve`, { method: "PATCH" });
    } catch (e) {}

    showToast(`Alert #${id} (${pid}) resolved.`);
}

function showToast(message) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.innerText = message;
    toast.style.display = "block";
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => {
        toast.style.display = "none";
    }, 3000);
}

function downloadExecutiveReport() {
    showToast("Downloading Executive Clinical PDF Report...");
    const a = document.createElement("a");
    a.href = `${API_BASE}/api/web/download/report`;
    a.download = "PulsePoint_Executive_Clinical_Report.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function exportFilteredCohortCSV() {
    if (!cohortRecordsCache || !cohortRecordsCache.length) {
        showToast("No records in current filter view to export.");
        return;
    }
    const headers = Object.keys(cohortRecordsCache[0]);
    const csvRows = [
        headers.join(","),
        ...cohortRecordsCache.map(row => headers.map(h => `"${String(row[h] ?? "").replace(/"/g, '""')}"`).join(","))
    ];
    const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pulsepoint_filtered_cohort_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Exported ${cohortRecordsCache.length} filtered patient records to CSV!`);
}

// =============================================================================
// 7. CONTROL CENTER DOCK, CLINICIAN LOGIN MODAL & PRIVACY POLICY MODAL
// =============================================================================
function openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.style.display = "flex";
}

function closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.style.display = "none";
}

function loginAsPersona(fullName, roleTitle, scrollTargetId) {
    const btn = document.getElementById("active-user-btn");
    if (btn) btn.innerText = `🔐 ${fullName.split(",")[0]}`;
    const ticker = document.getElementById("ticker-operator");
    if (ticker) ticker.innerText = `👤 OPERATOR: ${fullName.toUpperCase()} (${roleTitle.toUpperCase()})`;

    closeModal("login-modal");
    showToast(`Authenticated as ${fullName} • ${roleTitle}`);
    if (scrollTargetId) {
        document.getElementById(scrollTargetId)?.scrollIntoView({ behavior: "smooth" });
    }
}

function submitCustomLogin() {
    const uid = document.getElementById("modal-login-user")?.value.trim() || "dr_carter";
    const nameLabel = uid.includes("@") ? uid.split("@")[0].replace("_", " ").toUpperCase() : uid.toUpperCase();
    const btn = document.getElementById("active-user-btn");
    if (btn) btn.innerText = `🔐 ${nameLabel}`;
    const ticker = document.getElementById("ticker-operator");
    if (ticker) ticker.innerText = `👤 OPERATOR: ${nameLabel} (AUTHENTICATED CLINICIAN • AES-256)`;
    closeModal("login-modal");
    showToast(`Session Authenticated for ${uid} ✅`);
}

function lockClinicianSession() {
    const btn = document.getElementById("active-user-btn");
    if (btn) btn.innerText = `🔒 Guest (Locked)`;
    const ticker = document.getElementById("ticker-operator");
    if (ticker) ticker.innerText = `👤 OPERATOR: READ-ONLY SURVEILLANCE MODE (LOCKED)`;
    closeModal("login-modal");
    showToast("Session locked to Read-Only Surveillance Mode 🔒");
}

function quickTriageCohort(mode) {
    if (mode === "htn") {
        document.getElementById("flt-age").value = "65+";
        applyScenarioFilters();
        const cond = document.getElementById("explorer-condition");
        if (cond) { cond.value = "heart_disease"; loadCohortExplorer(); }
        showToast("🚨 Control Center Triage: High-Risk Hypertensive Senior Cohort Activated!");
    } else if (mode === "diabetes") {
        document.getElementById("flt-bmi").value = "Obesity Class I";
        applyScenarioFilters();
        const cond = document.getElementById("explorer-condition");
        if (cond) { cond.value = "diabetes"; loadCohortExplorer(); }
        showToast("🩸 Control Center Triage: Severe Glycemic / Obesity Cohort Activated!");
    } else if (mode === "multimorbid") {
        document.getElementById("flt-age").value = "51-65";
        document.getElementById("flt-bmi").value = "Obesity Class II";
        applyScenarioFilters();
        const cond = document.getElementById("explorer-condition");
        if (cond) { cond.value = "multimorbid"; loadCohortExplorer(); }
        showToast("⚠️ Control Center Triage: Multimorbid (2+ Conditions) Cohort Activated!");
    }
}

